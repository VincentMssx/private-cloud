# Nuage familial

Prototype local de validation pour dix espaces privés. Nextcloud gère les originaux, les dossiers et les quotas. Memories affiche la galerie et Duplicate Finder repère les fichiers identiques. Les parcours prévus, les écrans et les critères de réception sont décrits dans le [cadrage](docs/cadrage.md).

## Démarrage sur son ordinateur

Depuis un terminal Bash avec Docker Compose v2, Python 3, curl, OpenSSL et sha256sum (Linux ou WSL2), exécuter à la racine du dépôt :

```sh
scripts/local.sh
```

Ouvrir <http://localhost:8090> sur la machine qui exécute Docker. Se connecter avec le compte `admin` et le mot de passe `ADMIN_PASSWORD` du fichier local `.env`, créé au premier démarrage. À la première connexion, associer son application TOTP puis enregistrer les codes de secours hors du serveur. Créer un compte utilisateur distinct pour tester au quotidien. Le port écoute uniquement sur la boucle locale. Un essai depuis un téléphone physique demandera un accès HTTPS de test.

Le script installe les extensions publiées dont les empreintes sont dans `scripts/apps.lock`. Les services utilisent deux volumes Docker persistants. Conserver `.env` aussi longtemps que les volumes existent. Pour suspendre ou reprendre la pile, utiliser `docker compose stop` ou `docker compose start`.

## Vérification

```sh
python3 tests/parcours.py
docker compose ps
```

Le test crée deux comptes temporaires et utilise une mire synthétique datée de 2020. Il supprime ses propres comptes à la fin. Les actions GitHub reprennent cette installation et ce test sur une machine vierge. Pour évaluer le tri futur avec des contenus familiaux, conserver ceux-ci dans `fixtures-private/`, exclu de Git.

## Exploitation locale

Utiliser `docker compose exec -u www-data app php occ` pour les commandes Nextcloud. La purge de la corbeille utilise cron et la règle `30, 30`. Le conteneur cron doit fonctionner pour traiter les échéances. Les utilisateurs et quotas se gèrent depuis les paramètres d’administration. Pour le dépannage, Impersonate journalise la prise de session.

En cas de perte de l’application TOTP, utiliser un code de secours. Si tous les facteurs sont perdus, l’opérateur disposant du terminal serveur peut consulter `occ twofactorauth:state admin` et la commande `occ twofactorauth:disable --help` avant de réinitialiser le facteur concerné, puis réinscrire l’appareil. Réserver cet accès au responsable du serveur.

Consulter les [résultats de l’essai local](docs/validation.md) et la [maquette des trois écrans](docs/ecrans.html). Ouvrir la maquette dans un navigateur pour comparer les vues à différentes largeurs.

## Trier mes photos

Ouvrir **Trier mes photos** dans la navigation Nextcloud après l’import. Memories indexe les originaux et cron analyse les aperçus, par lots de 32. Les services utilisent le CPU du serveur. L’image du worker se construit au lancement de `scripts/local.sh`. Elle contient Python et OpenCV.

Les suggestions présentent les séries similaires et les clichés isolés à faible netteté. Le filtre par année utilise la date indexée par Memories. Toucher un aperçu ouvre son fichier. Cocher les photos, puis confirmer pour les déplacer vers la corbeille Nextcloud. « Ignorer cette suggestion » mémorise la décision pour cette version des fichiers. Une série dont tous les clichés sont cochés conserve le bouton de suppression désactivé.

Le service d’analyse reçoit uniquement les aperçus via le réseau Docker. Il calcule une empreinte visuelle, la variation des contours et la proportion de pixels sombres ou clairs. L’extension rapproche deux cadrages si leur date est distante d’au plus 90 secondes et leur empreinte suffisamment proche. Les scores sont indicatifs. Une égalité laisse le choix à l’utilisateur. Les copies exactes peuvent aussi être consultées dans Duplicate Finder indépendamment de la date.

Pour rejouer les tests, exécuter `python3 tests/parcours.py`, puis `docker compose exec -T analysis python -m unittest test_analysis`. Le test d’interface `python3 tests/tri.py` nécessite Playwright pour Python et Chromium ou Google Chrome. La variable `CHROME_BIN` permet d’indiquer le chemin du navigateur.
