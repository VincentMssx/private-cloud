"""Date deux suppressions d'un compte jetable de part et d'autre de J+30."""
import secrets
import subprocess
from xml.etree import ElementTree
from parcours import BASE, dav, occ

AGE = r"""
require 'lib/base.php';
[$unused,$uid,$item,$days] = $argv;
if (!preg_match('/^purge-[a-f0-9]{12}$/D',$uid)) exit(2);
OC_Util::setupFS($uid);
$db = \OCP\Server::get(\OCP\IDBConnection::class);
$old = $db->executeQuery('SELECT timestamp FROM *PREFIX*files_trash WHERE "user"=? AND id=?',[$uid,$item])->fetchOne();
$new = (string)(time()-86400*(int)$days);
$view = new \OC\Files\View('/'.$uid.'/files_trashbin/files');
if (!$old || !$view->rename('/'.$item.'.d'.$old,'/'.$item.'.d'.$new)) exit(3);
$count = $db->executeStatement('UPDATE *PREFIX*files_trash SET timestamp=? WHERE "user"=? AND id=? AND timestamp=?',[$new,$uid,$item,$old]);
if ($count !== 1) exit(4);
"""

uid = "purge-" + secrets.token_hex(6)
files = f"/remote.php/dav/files/{uid}/"
trash = f"/remote.php/dav/trashbin/{uid}/trash/"
occ("user:add", "--password-from-env", uid, create=True)
try:
    for days in (29, 31):
        name = f"jour-{days}.txt"
        dav(uid, "PUT", files + name, [201], b"original")
        dav(uid, "DELETE", files + name, [204])
        subprocess.run(["docker", "compose", "exec", "-T", "-u", "www-data", "app",
                        "php", "-r", AGE, "--", uid, name, str(days)], check=True)
    occ("trashbin:expire", uid)
    body = dav(uid, "PROPFIND", trash, [207], Depth="1")
    assert b"jour-31" not in body
    entry = next(e.text for e in ElementTree.fromstring(body).iter("{DAV:}href") if "/jour-29.txt.d" in e.text)
    dav(uid, "MOVE", entry, [201, 204],
        Destination=BASE + f"/remote.php/dav/trashbin/{uid}/restore/" + entry.split("/")[-1])
    assert dav(uid, "GET", files+"jour-29.txt", [200]) == b"original"
    print("OK · J+29 restaurable, J+31 purgé")
finally:
    occ("user:delete", uid)
