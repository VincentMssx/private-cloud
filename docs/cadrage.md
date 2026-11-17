# Cloud familial · première version

Dix personnes importent manuellement leurs fichiers depuis leur téléphone ou leur ordinateur. Chaque personne retrouve ses documents par dossier et ses photos par année. Un seul original alimente ces deux vues. Le stockage et l’analyse restent sous le contrôle de l’administrateur.

## Parcours et critères de réception

| Parcours | Résultat à vérifier avant l’ouverture familiale |
|---|---|
| Accès | L’admin crée, suspend et rétablit les comptes. Sa connexion demande le mot de passe puis le code TOTP. Les codes de secours sont conservés hors du serveur. |
| Fichiers | Créer un dossier, importer, renommer, déplacer et télécharger depuis le navigateur. Les octets téléchargés correspondent à l’original. Un second compte ne peut ni lire le fichier ni voir ses suggestions. |
| Photos | JPEG et PNG consultables par année de prise de vue. Valider aussi HEIC sur un original iPhone. En l’absence de date de prise de vue, utiliser la date du fichier, puis celle d’import si nécessaire. Vérifier la date retenue par Memories sur des exemples connus. |
| Nettoyage | Deux copies exactes renommées sont identifiées par contenu. Deux vues successives d’une même scène peuvent être groupées. Un sujet récurrent photographié à des dates éloignées ne suffit pas à constituer une rafale. |
| Décision | Chaque suggestion indique une raison observable. Montrer les images côte à côte, proposer la plus nette en tenant compte de l’exposition et de la définition, accepter « tout garder ». Une égalité ne justifie pas un choix arbitraire. Ignorer une série la masque jusqu’à sa modification. |
| Corbeille | La validation déplace uniquement les éléments sélectionnés. Restaurer rend l’original au propriétaire. Une tâche planifiée purge après 30 jours. Vérifier le seuil avec des fichiers de test datés. |
| Quotas et métriques | L’admin voit pour chaque utilisateur quota, octets utilisés, nombres de fichiers/photos, corbeille et analyses en attente. Un import dépassant le quota est refusé. Afficher séparément l’occupation physique et l’estimation des gains. |
| Dépannage | L’admin peut entrer temporairement dans l’espace d’un utilisateur après sa première connexion. Contrôler le journal de prise de session. Les actions de cette session sont attribuées à l’utilisateur dans les journaux applicatifs. |
| Reprise | Restaurer une sauvegarde sur une installation isolée. Vérifier la connexion, les quotas, les originaux par empreinte, les dossiers et la corbeille. |

## Trois écrans à valider sur petit écran

| Écran | De haut en bas | Action principale |
|---|---|---|
| Fichiers | Fil d’Ariane, nouveau dossier/import, liste des dossiers puis des fichiers, menu par ligne | Importer dans le dossier courant |
| Trier mes photos | Année, série à examiner, aperçus agrandissables, raisons sous chaque photo, cases de sélection, espace récupérable estimé | Confirmer la mise en corbeille des éléments cochés, ou ignorer la série |
| Administration | Capacité totale, dernier succès de sauvegarde, tableau par utilisateur, erreurs d’analyse | Modifier le quota puis vérifier l’effet sur un nouvel import |

## Architecture et exploitation

Nextcloud gère l’identité, les autorisations et toutes les mutations des originaux. Memories indexe le dossier photo du propriétaire. Duplicate Finder traite les copies exactes. Notre future extension PHP/Vue demandera des analyses par propriétaire, identifiant de fichier, version et version d’algorithme. Un worker Python/OpenCV traitera la file sur CPU, rendra scores et raisons, et pourra reprendre une tâche interrompue. L’extension recontrôlera propriétaire, droits et version du fichier avant toute mise en corbeille. Une suggestion devenue obsolète retourne en analyse.

Le prototype utilise Compose, PostgreSQL, Redis et cron. En production, ajouter Caddy avec HTTPS et des secrets propres à la machine. Prévoir une sauvegarde Restic quotidienne chiffrée des fichiers, de la configuration, des extensions et d’un export PostgreSQL pris au même point de cohérence. Suspendre écritures et tâches pendant la capture ou utiliser des instantanés cohérents. Conserver la clé de récupération séparément. Tester la restauration avant de confier les originaux familiaux au service.

Sur les 2 To tout compris, réserver initialement environ 1 To au serveur et 1 To aux sauvegardes séparées. Plafonner provisoirement la somme des quotas à 700 Go. Mesurer chaque semaine corbeilles, miniatures et historique de sauvegarde. Une sauvegarde peut contenir un original après sa purge de la corbeille. La durée de rétention des sauvegardes sera arrêtée après mesure du renouvellement des fichiers.

## Jeu de référence et calendrier

Annoter localement quelques séries avec le compte propriétaire, la date attendue, le groupe, les doublons exacts, les images floues, les choix acceptables et les raisons. Inclure une scène sombre nette, un arrière-plan volontairement flou, une image sans EXIF et un doublon chez deux propriétaires. Examiner les faux regroupements et les faux positifs avec la famille avant de figer les seuils. Garder les originaux de test privés hors de Git et de la CI.

| Semaine | Jalon |
|---|---|
| 1 | Valider les briques et les imports sur téléphone et PC. |
| 2 | Valider navigation, thème, corbeille et restauration d’une sauvegarde. |
| 3 | Intégrer les groupes exacts et les séries similaires. |
| 4 | Calibrer le flou et les explications sur les séries annotées. |
| 5 | Compléter les métriques, les tests et le déploiement manuel d’une version taguée sur le cloud de test. |
| 6 | Faire essayer la version à deux membres, corriger, tester la reprise et ouvrir les dix comptes. |
