<?php
namespace OCA\FamilyTri\Service;

class Suggestions {
    public const LOW_SHARPNESS = 55;

    private function distance(string $left, string $right): int {
        return substr_count(implode('', array_map(
            static fn ($byte) => decbin(ord($byte)),
            str_split(hex2bin($left) ^ hex2bin($right))
        )), '1');
    }

    private function quality(array $photo): float {
        return log(1 + (float)$photo['sharp']) - 2 * (float)$photo['clipped'];
    }

    /** Photos triées par date croissante. Chaque membre doit ressembler à l'ancre. */
    public function groups(array $photos): array {
        $series = [];
        foreach ($photos as $photo) {
            $time = strtotime($photo['datetaken'].' UTC');
            for ($i = count($series)-1; $i >= 0; $i--) {
                $anchor = $series[$i][0];
                if ($time - strtotime($anchor['datetaken'].' UTC') > 90) {
                    break;
                }
                $ratio = ($photo['w'] / max(1, $photo['h'])) / max(0.01, $anchor['w'] / max(1, $anchor['h']));
                if (abs(log(max(0.01, $ratio))) < 0.08 && $this->distance($photo['phash'], $anchor['phash']) <= 10) {
                    $series[$i][] = $photo;
                    continue 2;
                }
            }
            $series[][] = $photo;
        }
        $groups = [];
        foreach (array_reverse($series) as $items) {
            if (count($items) === 1 && $items[0]['sharp'] >= self::LOW_SHARPNESS) {
                continue;
            }
            usort($items, fn ($a, $b) => $this->quality($b) <=> $this->quality($a)
                ?: $a['fileid'] <=> $b['fileid']);
            $best = null;
            if (count($items) > 1 && $this->quality($items[0]) - $this->quality($items[1]) > 0.25) {
                $best = $items[0]['fileid'];
            }
            $key = hash('sha256', json_encode(array_map(fn ($p) => [$p['fileid'],$p['etag']], $items)));
            $groups[$key] = ['items' => $items, 'best' => $best];
        }
        return $groups;
    }
}
