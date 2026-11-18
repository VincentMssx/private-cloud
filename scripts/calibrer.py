"""Comparer les décisions de Maison aux annotations privées d'un compte dédié."""
import argparse
import json
import math
from collections import Counter
from pathlib import Path
import subprocess

QUERY = r"""
require 'lib/base.php';
if (!\OCP\Server::get(\OCP\IUserManager::class)->userExists($argv[1])) exit(2);
$p = \OCP\Server::get(\OCA\FamilyTri\Service\Catalogue::class)->photos($argv[1]);
$groups = (new \OCA\FamilyTri\Service\Suggestions)->groups($p);
echo json_encode(['photos'=>$p, 'groups'=>array_values($groups),
                  'blur'=>\OCA\FamilyTri\Service\Suggestions::LOW_SHARPNESS], JSON_THROW_ON_ERROR);
"""


def evaluate(labels, data):
    current = {p["fileid"]: p for p in data["photos"]}
    groups = {p["fileid"]: i for i, g in enumerate(data["groups"]) for p in g["items"]}
    paired, annotated, predicted = Counter(), Counter(), Counter()
    blur, winners = Counter(), Counter()
    rows = {}
    stale = 0
    for key, row in labels.items():
        photo = current.get(int(key))
        if not photo or row["etag"] != photo["etag"]:
            stale += 1
            continue
        rows[int(key)] = row
        series, group = row["serie"], groups.get(int(key), ("isolé", key))
        if series is not None:
            truth = series or ("isolé", key)
            annotated[truth] += 1
            predicted[group] += 1
            paired[truth, group] += 1
        if row["floue"] is not None:
            if type(row["floue"]) is not bool:
                raise ValueError("floue doit être true, false ou null")
            suggested = float(photo["sharp"]) < data["blur"]
            blur["VP" if suggested and row["floue"] else "FP" if suggested else "FN" if row["floue"] else "VN"] += 1

    def pairs(counts):
        return sum(math.comb(n, 2) for n in counts.values())

    for group in data["groups"]:
        items = [rows.get(p["fileid"]) for p in group["items"]]
        if len(items) < 2 or any(r is None or type(r["a_garder"]) is not bool for r in items):
            continue
        if not all(r["serie"] and r["serie"] == items[0]["serie"] for r in items):
            continue
        best = group["best"]
        winners["abstentions" if best is None else "accords" if rows[best]["a_garder"] else "désaccords"] += 1
    tp = pairs(paired)
    return {"annotations à revoir": stale, "photos analysées": len(current),
            "paires de série": {"VP": tp, "FP": pairs(predicted)-tp, "FN": pairs(annotated)-tp},
            "flou": dict(blur), "choix à conserver": dict(winners)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["export", "rapport"])
    parser.add_argument("compte")
    parser.add_argument("annotations", type=Path)
    args = parser.parse_args()
    result = subprocess.check_output(["docker", "compose", "exec", "-T", "-u", "www-data", "app",
                                      "php", "-r", QUERY, "--", args.compte])
    snapshot = json.loads(result)
    if args.action == "export":
        if not snapshot["photos"]:
            parser.error("Aucune photo analysée pour ce compte")
        labels = {p["fileid"]: {"fichier": p["path"], "etag": p["etag"], "serie": None,
                                "floue": None, "a_garder": None} for p in snapshot["photos"]}
        args.annotations.parent.mkdir(parents=True, exist_ok=True)
        with args.annotations.open("x") as output:
            json.dump({"compte": args.compte, "photos": labels}, output, indent=2, ensure_ascii=False)
    else:
        labels = json.loads(args.annotations.read_text())
        if labels["compte"] != args.compte:
            parser.error("Le compte doit correspondre à l’export")
        print(json.dumps(evaluate(labels["photos"], snapshot), ensure_ascii=False, indent=2))
