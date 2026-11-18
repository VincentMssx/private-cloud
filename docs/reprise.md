# Sauvegarder et restaurer Maison

Depuis la racine du dépôt, `python3 tests/corbeille.py` crée un compte jetable et vérifie la purge à J+31 et la restauration à J+29. `python3 tests/reprise.py` sauvegarde toute l’instance locale et démarre une copie sur un port libre, avec une base et des volumes distincts. Le test ouvre le compte restauré, lit son quota et compare les octets de deux fichiers, dont un restauré depuis la corbeille. Réserver environ trois fois la taille de l’instance pour cet exercice. L’application source s’arrête pendant la capture. Les comptes et volumes créés par le test sont nettoyés à la fin.

## Conserver une sauvegarde

Créer un répertoire sur un disque de sauvegarde et un fichier de clé à accès restreint. Garder une copie de la clé dans un gestionnaire de mots de passe accessible en cas de perte du serveur. Avec un disque monté, vérifier le point de montage avec `mountpoint` avant le lancement.

```bash
export RESTIC_REPOSITORY=/mnt/disque-sauvegarde/maison
export RESTIC_PASSWORD_FILE="$HOME/.config/maison/restic.key"
mkdir -p "$RESTIC_REPOSITORY" "$(dirname "$RESTIC_PASSWORD_FILE")"
(umask 077; set -C; openssl rand -base64 36 > "$RESTIC_PASSWORD_FILE")
ops/backup.sh init
ops/backup.sh
ops/backup.sh snapshots
ops/monitor.sh
```

Pour un dépôt objet, utiliser `RESTIC_REPOSITORY=s3:https://hote-du-service/nom-du-bucket` et exporter `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` et la région demandée par le fournisseur. Le compte de sauvegarde doit pouvoir lister, lire, écrire et purger les objets du bucket dédié.

Chaque capture comprend le volume Nextcloud, les rôles PostgreSQL, la base, la configuration de connexion et la révision du logiciel. L’application et cron reprennent après la capture. Une interruption normale déclenche aussi leur redémarrage. Le premier transfert d’un grand volume peut prolonger cette indisponibilité. Mesurer sa durée avant de charger les archives familiales. Restic vérifie les métadonnées et conserve sept points quotidiens et quatre hebdomadaires. Ces durées provisoires entrent dans le dimensionnement du dépôt. Les copies archivées suivent leur propre rétention après la purge de la corbeille.

## Ouvrir une copie de secours

Depuis un clone à la révision archivée, construire l’image d’analyse si nécessaire avec `docker compose build analysis` (ou `docker build -t famille-analysis:local worker` sur une machine de reprise vierge). Charger les variables du dépôt, puis choisir un nom de projet neuf et un port libre.

```bash
ops/restore.sh maison-reprise-exercice 18090
```

Le script vérifie l’intégrité de tous les fichiers restaurés. Accéder à <http://127.0.0.1:18090> avec les identifiants sauvegardés. Les secrets restaurés et l’export SQL sont dans `backups/maison-reprise-exercice/`. L’accès HTTP est limité à la boucle locale, et cron reste arrêté sur cette copie. Pour cibler une date précise, passer en troisième argument l’identifiant affiché par `ops/backup.sh snapshots`. En cas de révision différente, le script affiche le commit à utiliser.

Après vérification, arrêter la copie avec la commande suivante. Elle conserve les volumes pour un nouvel examen.

```bash
docker compose -f compose.yaml --env-file backups/maison-reprise-exercice/.env \
  -p maison-reprise-exercice stop
```

Pour reprendre le service public après un sinistre, garder l’ancienne instance hors ligne, valider les originaux et les accès dans la copie, puis raccorder le proxy HTTPS, rétablir le domaine et démarrer cron sur le projet restauré. Tester cette bascule avec le domaine et le stockage retenus avant l’ouverture des dix comptes.
