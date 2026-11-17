<?php
namespace OCA\FamilyTri\Migration;

use Closure;
use OCP\DB\ISchemaWrapper;
use OCP\Migration\IOutput;
use OCP\Migration\SimpleMigrationStep;

class Version000100Date20261117000000 extends SimpleMigrationStep {
    public function changeSchema(IOutput $output, Closure $schemaClosure, array $options): ?ISchemaWrapper {
        $schema = $schemaClosure();
        $t = $schema->createTable('familytri_scores');
        $t->addColumn('fileid', 'bigint');
        $t->addColumn('etag', 'string', ['length' => 64]);
        $t->addColumn('phash', 'string', ['length' => 16]);
        $t->addColumn('sharp', 'float');
        $t->addColumn('clipped', 'float');
        $t->addColumn('retry_at', 'bigint');
        $t->setPrimaryKey(['fileid']);
        return $schema;
    }
}
