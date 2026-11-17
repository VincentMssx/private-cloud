<?php
namespace OCA\FamilyTri\Controller;

use OCA\FamilyTri\Service\Catalogue;
use OCA\FamilyTri\Service\Suggestions;
use OCP\AppFramework\Controller;
use OCP\AppFramework\Http\Attribute\NoAdminRequired;
use OCP\AppFramework\Http\Attribute\NoCSRFRequired;
use OCP\AppFramework\Http\TemplateResponse;
use OCP\AppFramework\Http\DataResponse;
use OCP\IConfig;
use OCP\IRequest;
use OCP\IURLGenerator;

class PageController extends Controller {
    public function __construct(IRequest $request, private string $userId, private Catalogue $catalogue,
        private Suggestions $suggestions, private IConfig $config, private IURLGenerator $url) {
        parent::__construct('familytri', $request);
    }

    #[NoAdminRequired]
    #[NoCSRFRequired]
    public function index(string $year = ''): TemplateResponse {
        $photos = $this->catalogue->photos($this->userId);
        $years = array_unique(array_map(fn ($p) => substr($p['datetaken'],0,4), $photos));
        rsort($years);
        $ignored = array_flip($this->config->getUserKeys($this->userId, 'familytri'));
        $groups = array_filter($this->suggestions->groups($photos), fn ($g, $key) =>
            !isset($ignored[$key]) && ($year === '' || substr($g['items'][0]['datetaken'],0,4) === $year), ARRAY_FILTER_USE_BOTH);
        return new TemplateResponse('familytri', 'review', ['groups'=>array_slice($groups,0,24,true),
            'years'=>$years, 'year'=>$year, 'count'=>count($groups), 'uid'=>$this->userId,'url'=>$this->url]);
    }

    #[NoAdminRequired]
    public function ignore(string $key): DataResponse {
        if (!preg_match('/^[a-f0-9]{64}$/D', $key) ||
            !isset($this->suggestions->groups($this->catalogue->photos($this->userId))[$key])) {
            return new DataResponse([], 409);
        }
        $this->config->setUserValue($this->userId, 'familytri', $key, '1');
        return new DataResponse([]);
    }
}
