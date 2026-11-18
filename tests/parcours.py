"""Test d’intégration local, sur deux comptes temporaires créés par ce test."""
import base64
import http.client
import json
import os
from pathlib import Path
import secrets
import subprocess
from xml.etree import ElementTree

BASE = "http://127.0.0.1:8090"
ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
password = secrets.token_urlsafe(28)
created = []


def occ(*args, create=False):
    cmd = ["docker", "compose", "exec", "-T", "-u", "www-data"]
    if create:
        cmd.extend(["-e", "OC_PASS"])
    result = subprocess.run(cmd + ["app", "php", "occ", *args],
                            env={**os.environ, "OC_PASS": password}, text=True,
                            stdout=subprocess.PIPE)
    if result.returncode:
        raise RuntimeError(f"occ {args[0]}: {result.stdout}")
    return result.stdout


def dav(user, method, path, expected, data=None, *, port=8090, **headers):
    auth = base64.b64encode(f"{user}:{password}".encode()).decode()
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=40)
    try:
        conn.request(method, path, data, {"Authorization": "Basic " + auth, **headers})
        response = conn.getresponse()
        body = response.read()
        if response.status not in expected:
            raise RuntimeError(f"{method} {path}: {response.status}, attendu {expected}, {body[:250]!r}")
        return body
    finally:
        conn.close()


def run():
    config = json.loads(occ("config:list", "system", "--output=json"))["system"]
    assert config["twofactor_enforced"] == "true" and config["twofactor_enforced_groups"] == ["admin"]
    assert config["trashbin_retention_obligation"] == "30, 30"
    first, second = ["essai-" + secrets.token_hex(6) for _ in range(2)]
    for user in (first, second):
        occ("user:add", "--password-from-env", user, create=True)
        created.append(user)
    folder = f"/remote.php/dav/files/{first}/Essai"
    dav(first, "MKCOL", folder, [201])
    image = (ROOT / "tests/mire.jpg").read_bytes()
    for name in ("original.jpg", "copie.jpg"):
        dav(first, "PUT", folder + "/" + name, [201], image)
    assert dav(first, "GET", folder + "/original.jpg", [200]) == image
    dav(second, "GET", folder + "/original.jpg", [403, 404])
    dav(first, "PUT", folder + "/mobile.heic", [201], (ROOT / "tests/mire.heic").read_bytes())
    occ("preview:generate", f"/{first}/files/Essai/mobile.heic")
    occ("memories:index", "--user", first, "--path", "/Essai")
    occ("duplicates:find-all", "--user", first, "--no-interaction")
    report = occ("duplicates:list", "--user", first)
    assert "original.jpg" in report and "copie.jpg" in report, report
    dav(first, "DELETE", folder + "/copie.jpg", [204])
    trash = f"/remote.php/dav/trashbin/{first}/trash/"
    listing = ElementTree.fromstring(dav(first, "PROPFIND", trash, [207], Depth="1"))
    entry = next(e.text for e in listing.iter("{DAV:}href") if "/copie.jpg.d" in e.text)
    dav(first, "MOVE", entry, [201, 204],
        Destination=BASE + f"/remote.php/dav/trashbin/{first}/restore/" + entry.split("/")[-1])
    assert dav(first, "GET", folder + "/copie.jpg", [200]) == image
    occ("user:setting", first, "files", "quota", "1 MB")
    dav(first, "PUT", folder + "/quota.bin", [507], bytes(2 * 1024 * 1024))
    print("OK · import, lecture, isolation, indexation, doublon, restauration et quota")


if __name__ == '__main__':
    try:
        run()
    finally:
        for account in reversed(created):
            occ("user:delete", account)
