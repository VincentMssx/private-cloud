"""Rejoue l'export annoté avec les mires utilisées par le navigateur."""
import json
from pathlib import Path
import secrets
import subprocess
import tempfile

from parcours import ROOT, dav, occ

uid = "calibration-" + secrets.token_hex(6)
occ("user:add", "--password-from-env", uid, create=True)
try:
    for name in ["mire.jpg", "mire-floue.jpg"]:
        dav(uid, "PUT", f"/remote.php/dav/files/{uid}/{name}", [201], (ROOT/"tests"/name).read_bytes())
    occ("memories:index", "--user", uid)
    job, = json.loads(occ("background-job:list", "-c", r"OCA\FamilyTri\BackgroundJob\Analyse", "--output=json"))
    occ("background-job:execute", job["id"], "--force-execute")
    with tempfile.TemporaryDirectory() as folder:
        ref = Path(folder)/"ref.json"
        cmd = ["python3", "scripts/calibrer.py"]
        subprocess.run(cmd + ["export", uid, ref], check=True)
        data = json.loads(ref.read_text())
        assert len(data["photos"]) == 2
        for row in data["photos"].values():
            blurry = "floue" in row["fichier"]
            row.update(serie="mire", floue=blurry, a_garder=not blurry)
        ref.write_text(json.dumps(data))
        report = json.loads(subprocess.check_output(cmd + ["rapport", uid, ref]))
        assert report["paires de série"] == {"VP": 1, "FN": 0, "FP": 0}, report
        assert report["flou"] == {"VP": 1, "VN": 1}, report
        assert report["choix à conserver"] == {"accords": 1}, report
        print("OK · paire, netteté et préférence sur les deux mires")
finally:
    occ("user:delete", uid)
