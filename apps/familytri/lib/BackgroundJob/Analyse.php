<?php
namespace OCA\FamilyTri\BackgroundJob;

use OCA\FamilyTri\Service\Catalogue;
use OCP\AppFramework\Utility\ITimeFactory;
use OCP\BackgroundJob\TimedJob;
use OCP\Files\File;
use OCP\Files\IRootFolder;
use OCP\Http\Client\IClientService;
use OCP\IPreview;
use Psr\Log\LoggerInterface;

class Analyse extends TimedJob {
    public function __construct(ITimeFactory $time, private Catalogue $catalogue,
        private IRootFolder $root, private IPreview $preview, private IClientService $http,
        private LoggerInterface $log) {
        parent::__construct($time);
        $this->setInterval(60);
        $this->setAllowParallelRuns(false);
    }

    protected function run($argument): void {
        $client = $this->http->newClient();
        foreach ($this->catalogue->pending() as $row) {
            try {
                $uid = substr($row['id'], strlen('home::'));
                $file = $this->root->getUserFolder($uid)->getFirstNodeById((int)$row['fileid']);
                if (!$file instanceof File || $file->getEtag() !== $row['etag']) {
                    continue;
                }
                $image = $this->preview->getPreview($file, 512, 512, false, IPreview::MODE_COVER);
                $response = $client->post('http://analysis:8091/measure', [
                    'proxy' => '', 'body' => $image->getContent(), 'timeout' => 6,
                    'nextcloud' => ['allow_local_address' => true],
                ]);
                $scores = json_decode($response->getBody(), true, flags: JSON_THROW_ON_ERROR);
                $this->catalogue->save($row, $scores);
            } catch (\Exception $e) {
                $this->catalogue->save($row, null);
                $this->log->warning('Analyse photo différée pour le fichier {id}', ['id' => $row['fileid'], 'exception' => $e]);
            }
        }
    }
}
