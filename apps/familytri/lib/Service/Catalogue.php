<?php
namespace OCA\FamilyTri\Service;

use OCP\IDBConnection;

/** PostgreSQL, Nextcloud 34 et index Memories. Une ligne concerne un original privé. */
class Catalogue {
    public function __construct(private IDBConnection $db) {}

    private const SOURCE = " FROM *PREFIX*filecache f
        JOIN *PREFIX*storages s ON s.numeric_id=f.storage
        JOIN *PREFIX*memories m ON m.fileid=f.fileid AND NOT m.orphan
        JOIN *PREFIX*mimetypes t ON t.id=f.mimetype
        LEFT JOIN *PREFIX*familytri_scores a ON a.fileid=f.fileid AND a.etag=f.etag
        WHERE f.path LIKE 'files/%' AND s.id LIKE 'home::%'
        AND t.mimetype IN ('image/jpeg','image/png','image/heic','image/heif')";

    public function pending(): array {
        return $this->db->executeQuery('SELECT DISTINCT f.fileid, f.etag, s.id' . self::SOURCE .
            ' AND (a.fileid IS NULL OR (a.retry_at>0 AND a.retry_at<=?))
              ORDER BY f.fileid LIMIT 32', [time()])->fetchAllAssociative();
    }

    public function save(array $row, ?array $scores): void {
        $this->db->executeStatement('INSERT INTO *PREFIX*familytri_scores
            (fileid,etag,phash,sharp,clipped,retry_at) VALUES (?,?,?,?,?,?)
            ON CONFLICT (fileid) DO UPDATE SET etag=excluded.etag,phash=excluded.phash,
            sharp=excluded.sharp,clipped=excluded.clipped,retry_at=excluded.retry_at',
            [$row['fileid'], $row['etag'], $scores['hash'] ?? '', $scores['sharp'] ?? 0,
             $scores['clipped'] ?? 0, $scores === null ? time()+3600 : 0]);
    }

    public function photos(string $uid): array {
        return $this->db->executeQuery('SELECT DISTINCT f.fileid, f.path, f.etag, f.size,
            m.datetaken, m.w, m.h, a.phash, a.sharp, a.clipped' . self::SOURCE .
            ' AND s.id=? AND a.retry_at=0 ORDER BY m.datetaken, f.fileid',
            ['home::'.$uid])->fetchAllAssociative();
    }
}
