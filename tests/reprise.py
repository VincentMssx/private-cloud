"""Sauvegarde l'instance locale et vérifie les données d'un compte dans un clone."""
import os
import secrets
import shutil
import socket
import subprocess
from xml.etree import ElementTree
from parcours import ROOT, dav, occ

uid = "reprise-" + secrets.token_hex(6)
project = "maison-" + uid
with socket.socket() as sock:
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
work = ROOT/"backups"/("exercice-"+uid)
work.mkdir(parents=True, mode=0o700)
repo = work/"repo"
repo.mkdir()
key = work/"cle"
key.write_text(secrets.token_urlsafe(40))
key.chmod(0o600)
env = {**os.environ, "RESTIC_REPOSITORY": str(repo), "RESTIC_PASSWORD_FILE": str(key),
       "MAISON_LOCAL_PORT": str(port)}
dc = ["docker", "compose", "-f", "compose.yaml", "-p", project]
files = f"/remote.php/dav/files/{uid}/"
original = secrets.token_bytes(3500)
occ("user:add", "--password-from-env", uid, create=True)
try:
    dav(uid, "MKCOL", files+"Carnet", [201])
    for name in ("temoin.bin", "corbeille.bin"):
        dav(uid, "PUT", files+"Carnet/"+name, [201], original)
    dav(uid, "DELETE", files+"Carnet/corbeille.bin", [204])
    occ("user:setting", uid, "files", "quota", "9 MB")
    env_source = {**env, "MAISON_LOCAL_PORT": "8090"}
    for action in ("init", "backup"):
        subprocess.run(["ops/backup.sh", action], env=env_source, check=True)
    subprocess.run(["ops/monitor.sh"], env=env_source, check=True)
    alarm = subprocess.run(["ops/monitor.sh"], env={**env_source, "DISK_ALERT_PERCENT": "1"})
    assert alarm.returncode == 1
    subprocess.run(["ops/restore.sh", project, str(port)], env=env, check=True)
    assert dav(uid, "GET", files+"Carnet/temoin.bin", [200], port=port) == original
    trash = f"/remote.php/dav/trashbin/{uid}/trash/"
    body = dav(uid, "PROPFIND", trash, [207], port=port, Depth="1")
    entry = next(e.text for e in ElementTree.fromstring(body).iter("{DAV:}href") if "/corbeille.bin.d" in e.text)
    dav(uid, "MOVE", entry, [201, 204], port=port, Destination=f"http://127.0.0.1:{port}/remote.php/dav/trashbin/{uid}/restore/"+entry.split("/")[-1])
    assert dav(uid, "GET", files+"Carnet/corbeille.bin", [200], port=port) == original
    quota = subprocess.check_output(dc+["exec", "-T", "-u", "www-data", "app", "php", "occ",
                                        "user:setting", uid, "files", "quota"], env=env, text=True)
    assert quota.strip() == "9 MB"
    print("OK · connexion, dossier, deux originaux identiques, corbeille et quota restaurés")
finally:
    subprocess.run(dc+["down", "-v"], env=env, check=True)
    # Les objets Restic de cet exercice appartiennent à l'UID du conteneur.
    subprocess.run(["docker", "run", "--rm", "-v", f"{repo}:/exercise", "--entrypoint", "sh",
                    "restic/restic:0.18.1", "-c", "chown -R \"$1:$2\" /exercise", "--",
                    str(os.getuid()), str(os.getgid())], check=True)
    shutil.rmtree(work)
    shutil.rmtree(ROOT/"backups"/project, ignore_errors=True)
    occ("user:delete", uid)
