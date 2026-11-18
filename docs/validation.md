# Essai local du 17 novembre 2026

La pile installée utilise Nextcloud 34.0.6, Memories 11.1.4, Duplicate Finder 1.10.18, Impersonate 5.0.0 et le fournisseur TOTP 16.0.0 livré avec Nextcloud. Les images Docker sont figées par empreinte dans Compose. Les archives des trois extensions supplémentaires sont vérifiées par SHA-256 avant extraction.

| Essai exécuté | Observation |
|---|---|
| Deux comptes temporaires, un fichier privé | Le propriétaire a téléchargé les octets d’origine. L’autre compte a reçu HTTP 404. |
| Deux JPEG identiques sous des noms différents | Le rapport de Duplicate Finder pour le propriétaire contenait les deux noms. |
| MIME et miniatures | Une mire HEIC encodée en HEVC a été importée puis traitée par la commande de génération d’aperçu Nextcloud. |
| Navigation sur écran étroit | Chromium en 390 × 844 a ouvert Fichiers et Memories après connexion. La galerie a affiché le 6 mai 2020 pour un JPEG EXIF importé en 2026. La racine privée est présélectionnée pour la galerie. |
| Corbeille | La copie a été supprimée via WebDAV puis restaurée depuis la corbeille. La relecture a rendu les mêmes octets. Cron tourne avec la politique de conservation de 30 jours. |
| Quota | Une tentative d’import de 2 Mio avec un quota de 1 Mo a reçu HTTP 507. |
| Accès administrateur | Le formulaire de connexion a redirigé un nouveau membre du groupe admin vers l’enrôlement du second facteur. Le test a ensuite supprimé ce compte temporaire. |

Les tests utilisent des mires synthétiques. Les essais sur de vrais téléphones et le jeu familial permettront de vérifier notamment les variantes HEIC d’iPhone. L’association de l’application TOTP personnelle, l’audit d’une session de dépannage, la purge effective à échéance et la restauration d’une sauvegarde indépendante restent à valider avant l’ouverture aux dix personnes.

La revue des suggestions est maintenant intégrée à Nextcloud. Le test Chromium utilise une mire nette, une copie et une variante floutée. Il vérifie la présence des suggestions chez le propriétaire, leur absence chez un autre utilisateur, la mise à la corbeille, la protection contre une version obsolète et la persistance d’une décision d’ignorer. Les seuils restent à calibrer sur des photos représentatives. Les quotas individuels sont disponibles dans Nextcloud. Le panneau Espaces familiaux complète ces quotas par les volumes actifs et supprimés, les nombres de fichiers et de photos et les états des analyses.

## Espaces familiaux et maquette Maison · 18 novembre 2026

Le test navigateur `tests/admin.py` crée deux comptes temporaires, configure un second facteur puis se connecte avec un code TOTP. L’administrateur voit les deux fichiers actifs du membre dont une photo, ainsi que le document placé dans sa corbeille. Une limite de 1 Mio enregistrée dans le panneau reste affichée après rechargement et bloque un import de 2 Mio. Le membre ne peut ni consulter le panneau ni modifier le quota.

La maquette interactive a été essayée dans Chromium à 1360 × 830 et 390 × 844. Navigation dans les dossiers, création d’un dossier, comparaison et agrandissement, sélection puis confirmation, restauration et choix d’une image locale ont été vérifiés.

Le démarrage du README a également été vérifié depuis un clone GitHub neuf sous Linux, dans un projet Compose isolé et avec des volumes vides. Nextcloud a répondu avec `installed: true`, `maintenance: false` et `needsDbUpgrade: false`. FamilyTri 0.2.0 et Memories 11.1.4 étaient activés.
