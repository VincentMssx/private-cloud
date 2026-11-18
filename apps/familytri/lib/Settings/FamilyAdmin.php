<?php
namespace OCA\FamilyTri\Settings;

use OCA\FamilyTri\Service\Usage;
use OCP\AppFramework\Http\TemplateResponse;
use OCP\IConfig;
use OCP\IURLGenerator;
use OCP\Settings\ISettings;

class FamilyAdmin implements ISettings {
    public function __construct(private Usage $usage, private IURLGenerator $url, private IConfig $config) {}

    public function getForm(): TemplateResponse {
        $volume = $this->config->getSystemValueString('datadirectory');
        return new TemplateResponse('familytri', 'admin', [
            'accounts' => $this->usage->accounts(),
            'free' => disk_free_space($volume),
            'capacity' => disk_total_space($volume),
            'quotaUrl' => $this->url->linkToRoute('familytri.admin.quota'),
        ]);
    }

    public function getSection(): string { return 'familytri'; }
    public function getPriority(): int { return 10; }
}
