<?php
namespace OCA\FamilyTri\Service;

use OCP\IDBConnection;
use OCP\IUserManager;

class Usage {
    public function __construct(private IDBConnection $db, private IUserManager $users) {}

    public function accounts(): array {
        // Les tailles de dossiers cumulent déjà leurs descendants. Compter les fichiers seulement.
        $rows = $this->db->executeQuery("SELECT s.id,
            COUNT(*) FILTER (WHERE f.path LIKE 'files/%') AS files,
            COUNT(*) FILTER (WHERE f.path LIKE 'files/%' AND t.mimetype LIKE 'image/%') AS photos,
            SUM(GREATEST(f.size,0)) FILTER (WHERE f.path LIKE 'files/%') AS used,
            SUM(GREATEST(f.size,0)) FILTER (WHERE f.path LIKE 'files_trashbin/files/%') AS trash,
            COUNT(*) FILTER (WHERE f.path LIKE 'files/%' AND m.fileid IS NOT NULL
                AND t.mimetype IN ('image/jpeg','image/png','image/heic','image/heif') AND a.fileid IS NULL) AS pending,
            COUNT(*) FILTER (WHERE f.path LIKE 'files/%' AND m.fileid IS NOT NULL AND a.retry_at>0) AS failed
            FROM *PREFIX*filecache f
            JOIN *PREFIX*storages s ON s.numeric_id=f.storage
            JOIN *PREFIX*mimetypes t ON t.id=f.mimetype
            LEFT JOIN *PREFIX*memories m ON m.fileid=f.fileid AND NOT m.orphan
            LEFT JOIN *PREFIX*familytri_scores a ON a.fileid=f.fileid AND a.etag=f.etag
            WHERE s.id LIKE 'home::%' AND t.mimetype<>'httpd/unix-directory'
                AND (f.path LIKE 'files/%' OR f.path LIKE 'files_trashbin/files/%')
            GROUP BY s.id")->fetchAllAssociative();

        $indexed = array_column($rows, null, 'id');
        $accounts = [];
        foreach ($this->users->search('') as $user) {
            $uid = $user->getUID();
            $account = ['uid' => $uid, 'name' => $user->getDisplayName(), 'quota' => $user->getQuota()];
            foreach (['files','photos','used','trash','pending','failed'] as $metric) {
                $account[$metric] = (int)($indexed['home::'.$uid][$metric] ?? 0);
            }
            $accounts[] = $account;
        }
        return $accounts;
    }
}
