# Nuage familial

Prototype local de validation pour dix espaces privés. Nextcloud gère les originaux, les dossiers et les quotas. Memories affiche la galerie et Duplicate Finder repère les fichiers identiques. Les parcours prévus, les écrans et les critères de réception sont décrits dans le [cadrage](docs/cadrage.md).

## Tester sur son PC avec VS Code

### 1. Ouvrir le projet

Sous **Windows**, installer [VS Code](https://code.visualstudio.com/) et son extension [WSL](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-wsl), puis [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) avec le moteur WSL 2. Dans **Settings → Resources → WSL Integration**, activer sa distribution Ubuntu. Ouvrir le terminal Ubuntu et cloner le projet dans son dossier personnel Linux. Sous **Linux**, utiliser Bash, Docker Engine et le plugin Compose v2.

```bash
cd ~
git clone --branch work https://github.com/VincentMssx/private-cloud.git
cd private-cloud
code .
```

Si le projet est déjà cloné, ouvrir son dossier dans VS Code. Pour récupérer cette version, dans un arbre de travail propre, utiliser `git fetch origin`, `git switch work` puis `git pull --ff-only`. Sur Windows, vérifier que VS Code affiche **WSL: Ubuntu** en bas à gauche, puis ouvrir **Terminal → Nouveau terminal**.

### 2. Essayer la maquette Maison

Ouvrir [l’aperçu PC et téléphone](docs/maison/apercu.webp) pour voir les quatre vues. Pour manipuler la [maquette interactive](docs/maison/index.html), ouvrir ce fichier HTML dans son navigateur ou lancer depuis le terminal de VS Code :

```bash
python3 -m http.server 8001 --bind 127.0.0.1 --directory docs/maison
```

Ouvrir <http://localhost:8001>, entrer dans un dossier, puis choisir **Trier mes photos**. Comparer les deux clichés, en agrandir un, en sélectionner un et confirmer son déplacement. **Corbeille → Restaurer** permet de le retrouver. « Essayer avec ma photo » charge une image depuis le PC et simule le flou sur la seconde prise. Tout reste dans l’onglet et se réinitialise au rechargement. Réduire la fenêtre pour essayer la navigation mobile. Le serveur de maquette s’arrête avec **Ctrl+C**.

### 3. Démarrer l’application Nextcloud

Depuis la racine du dépôt dans le terminal Bash, vérifier les prérequis et lancer l’installation :

```bash
docker info
docker compose version
command -v git python3 curl openssl sha256sum tar
bash scripts/local.sh
docker compose ps
```

Le premier démarrage télécharge les images, construit le service OpenCV et initialise les volumes. À la fin, Nextcloud doit indiquer `installed: true` et `maintenance: false`. Les services `app`, `db`, `redis`, `cron` et `analysis` doivent être démarrés.

Ouvrir <http://localhost:8090>. Dans VS Code, ouvrir le fichier local `.env` créé au premier démarrage. Se connecter avec **admin** et la valeur de `ADMIN_PASSWORD`. Associer son application TOTP et conserver les codes de récupération hors du serveur. Garder `.env` en local aussi longtemps que les volumes existent.

### 4. Vérifier les deux espaces

1. Depuis le menu du profil admin, ouvrir **Comptes** et créer deux utilisateurs ordinaires. Ouvrir une fenêtre privée avec le premier compte.
2. Dans **Fichiers**, créer un dossier et importer `tests/mire.jpg`, `tests/mire-floue.jpg` et `tests/mire.heic`. Ouvrir **Memories** pour retrouver les photos, puis **Trier mes photos**. L’analyse se fait en arrière-plan après indexation et peut prendre plusieurs passages de cron.
3. Sélectionner un cliché, confirmer la mise à la corbeille, puis le restaurer depuis **Fichiers → Fichiers supprimés**. Se connecter avec le second compte et vérifier que les fichiers du premier restent privés.
4. Dans la fenêtre de l’admin, suivre **Paramètres d’administration → Espaces familiaux**. Vérifier les compteurs du premier compte, ouvrir **Modifier le quota**, saisir une petite limite et l’enregistrer. Essayer d’importer un fichier plus gros que l’espace restant avec ce compte, puis rétablir le quota voulu.

La limite affichée est celle appliquée par Nextcloud. Le volume actif additionne les fichiers personnels et la colonne « dont photos » compte les images parmi ces fichiers. Les deux compteurs d’analyse suivent les photos compatibles déjà indexées par Memories. L’espace libre affiché en tête de panneau est celui du volume physique qui héberge les données Nextcloud. Les miniatures et les autres données du volume réduisent aussi cet espace.

### Arrêter, reprendre et dépanner

- **Suspendre ou reprendre** avec `docker compose stop` et `docker compose start`. Les comptes et fichiers restent dans les volumes Docker. L’option `down -v` supprime ces volumes.
- **Mettre à jour** avec `git pull --ff-only` puis `bash scripts/local.sh`. Le script copie l’extension depuis le dépôt et applique les migrations nécessaires.
- **Docker indisponible** : démarrer le moteur et, sous Windows, vérifier l’intégration de la distribution WSL utilisée dans VS Code.
- **Page inaccessible** : vérifier que le port 8090 est libre, puis consulter `docker compose ps` et `docker compose logs --tail=50 app db`.
- **Photos en attente** : vérifier `docker compose ps`, puis `docker compose logs --tail=50 cron analysis`. L’application écoute sur la boucle locale du PC. Un essai depuis un vrai téléphone demandera un accès HTTPS approprié.

## Vérification

```sh
python3 tests/parcours.py
docker compose ps
```

Le test crée deux comptes temporaires et utilise une mire synthétique datée de 2020. Il supprime ses propres comptes à la fin. Les actions GitHub reprennent cette installation et ce test sur une machine vierge. Pour évaluer les suggestions avec des contenus familiaux, conserver ceux-ci dans `fixtures-private/`, exclu de Git.

## Exploitation locale

Utiliser `docker compose exec -u www-data app php occ` pour les commandes Nextcloud. La purge de la corbeille utilise cron et la règle `30, 30`. Le conteneur cron doit fonctionner pour traiter les échéances. Les utilisateurs et quotas se gèrent depuis les paramètres d’administration. Pour le dépannage, Impersonate journalise la prise de session.

En cas de perte de l’application TOTP, utiliser un code de secours. Si tous les facteurs sont perdus, l’opérateur disposant du terminal serveur peut consulter `occ twofactorauth:state admin` et la commande `occ twofactorauth:disable --help` avant de réinitialiser le facteur concerné, puis réinscrire l’appareil. Réserver cet accès au responsable du serveur.

Consulter les [résultats de l’essai local](docs/validation.md) et la [maquette des trois écrans](docs/ecrans.html). Ouvrir la maquette dans un navigateur pour comparer les vues à différentes largeurs.

## Trier mes photos

Ouvrir **Trier mes photos** dans la navigation Nextcloud après l’import. Memories indexe les originaux et cron analyse les aperçus, par lots de 32. Les services utilisent le CPU du serveur. L’image du worker se construit au lancement de `scripts/local.sh`. Elle contient Python et OpenCV.

Les suggestions présentent les séries similaires et les clichés isolés à faible netteté. Le filtre par année utilise la date indexée par Memories. Toucher un aperçu ouvre son fichier. Cocher les photos, puis confirmer pour les déplacer vers la corbeille Nextcloud. « Ignorer cette suggestion » mémorise la décision pour cette version des fichiers. Une série dont tous les clichés sont cochés conserve le bouton de suppression désactivé.

Le service d’analyse reçoit uniquement les aperçus via le réseau Docker. Il calcule une empreinte visuelle, la variation des contours et la proportion de pixels sombres ou clairs. L’extension rapproche deux cadrages si leur date est distante d’au plus 90 secondes et leur empreinte suffisamment proche. Les scores sont indicatifs. Une égalité laisse le choix à l’utilisateur. Les copies exactes peuvent aussi être consultées dans Duplicate Finder indépendamment de la date.

Pour rejouer les tests, exécuter `python3 tests/parcours.py`, puis `docker compose exec -T analysis python -m unittest test_analysis`. Le test d’interface `python3 tests/tri.py` nécessite Playwright pour Python et Chromium ou Google Chrome. La variable `CHROME_BIN` permet d’indiquer le chemin du navigateur.
