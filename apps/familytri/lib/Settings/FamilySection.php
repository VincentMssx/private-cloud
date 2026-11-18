<?php
namespace OCA\FamilyTri\Settings;

use OCP\IURLGenerator;
use OCP\Settings\IIconSection;

class FamilySection implements IIconSection {
    public function __construct(private IURLGenerator $url) {}
    public function getID(): string { return 'familytri'; }
    public function getName(): string { return 'Espaces familiaux'; }
    public function getPriority(): int { return 70; }
    public function getIcon(): string { return $this->url->imagePath('core', 'places/files.svg'); }
}
