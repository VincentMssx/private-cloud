<?php
namespace OCA\FamilyTri\Controller;

use OCP\AppFramework\Controller;
use OCP\AppFramework\Http\DataResponse;
use OCP\IRequest;
use OCP\IUserManager;

class AdminController extends Controller {
    public function __construct(IRequest $request, private IUserManager $users) {
        parent::__construct('familytri', $request);
    }

    // Les contrôleurs Nextcloud exigent par défaut le rôle admin et un jeton CSRF.
    public function quota(string $uid, string $unit, string $amount = ''): DataResponse {
        if ($unit === 'default') {
            $quota = 'default';
        } elseif (in_array($unit, ['MB', 'GB'], true) && preg_match('/^[1-9][0-9]{0,6}$/D', $amount)) {
            $quota = $amount.' '.$unit;
        } else {
            return new DataResponse(['message' => 'Choisissez un quota entier positif.'], 400);
        }
        $user = $this->users->get($uid);
        if (!$user) {
            return new DataResponse(['message' => 'Compte introuvable.'], 404);
        }
        $user->setQuota($quota);
        return new DataResponse(['quota' => $user->getQuota()]);
    }
}
