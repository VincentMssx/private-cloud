# Pilote familial

## Hébergement pour 2 To tout compris

Dimensionner 1 To décimal exploitable pour Maison et 1 To pour le dépôt Restic chez un autre opérateur. Dans le panneau admin, commencer à **65 Gio par personne**. Dix comptes occupent ainsi au plus environ 698 Go d’originaux actifs. Le reste du disque sert notamment à PostgreSQL, aux aperçus et à la corbeille. Le RAID 1 du serveur proposé présente une seule copie logique à l’application. Le dépôt distant permet de restaurer après perte du serveur.

| Configuration indicative | Calcul mensuel à pleine occupation du dépôt |
|---|---|
| Scaleway Elastic Metal EM-A116X-SSD à Paris, deux SSD de 1,024 To en miroir, sauvegarde Cloudflare R2 Standard | **27,99 € + 14,85 USD**. Ajouter **27,99 €** de mise en service au forfait mensuel. |
| Google Compute Engine e2-standard-2 à Paris, disque persistant HDD de 932 Gio, même sauvegarde R2 | **114,84 USD**. VM 56,74 USD, disque 43,25 USD et R2 14,85 USD. |

Parmi ces deux offres, le serveur Scaleway a le coût récurrent le plus bas aux taux de change usuels. Ses SSD hébergent aussi l’index et les miniatures. Les montants proviennent de la réponse du catalogue Scaleway du 29 octobre 2026, du relevé Google du 12 novembre et du tarif R2 consulté le 18 novembre. Pour R2 Standard, le calcul suppose 1 000 Go-mois dont 10 gratuits sur le compte. Au démarrage, seules les données réellement stockées sont facturées. Ajouter selon l’offre la TVA, le domaine, l’IPv4, les transferts du serveur et les opérations au-delà des franchises. Vérifier le stock et le devis TTC avant de commander. [Catalogue Scaleway archivé](https://github.com/scaleway/scaleway-cli/blob/10c2f3906c7c964fa3869319ce66cc5837e65196/internal/namespaces/baremetal/v1/testdata/test-baremetal-list-offer-simple.cassette.yaml) · [Relevé Google](https://github.com/Cyclenerd/google-cloud-pricing-cost-calculator/blob/7274fa29f3e71786f15cdd1ea76bf9897eb7704d/pricing.yml) · [Tarif et exemple R2](https://developers.cloudflare.com/r2/pricing/)

## Réduire le coût

Pour démarrer, garder la pile actuelle sur le PC et consacrer le premier téraoctet aux données, corbeille et aperçus compris. Le second téraoctet accueille la sauvegarde chiffrée. Un disque chez un proche protège aussi contre la perte du logement. Un VPN WireGuard donne accès aux dix comptes sans licence par personne. Il faut qu’au moins un point d’entrée soit joignable, que la connexion montante suffise et que la machine reste allumée pour offrir un service continu.

| Exemple de budget incrémental | Calcul |
|---|---|
| PC et second emplacement déjà équipés, déjà allumés | 0 € de nouvel abonnement. La consommation supplémentaire se mesure à la prise. |
| Mini-PC à 10 W et sauvegarde sur un équipement distant déjà allumé | 7,3 kWh/mois, soit 1,46 €/mois au tarif illustratif de 0,20 €/kWh. À 40 W, compter 5,84 €/mois. |
| Même mini-PC et stockage de sauvegarde loué | Si 1 To revient à 5 € TTC/mois au panier, le total est de 6,46 €/mois. Un chemin distant monté doit être présent au moment de la capture. |
| VPS économique et stockage distant des deux copies | Exemple de budget TTC avec 6 € de VM, 6 € de stockage primaire, 5 € de sauvegarde et 1 € de réseau/nom : 18 €/mois. Relever les quatre prix avant achat. |

Ces exemples supposent les connexions Internet déjà payées, une disponibilité domestique acceptable et les disques disponibles. Un achat de 120 € réparti sur quatre ans ajoute 2,50 €/mois. Une Storage Box parle notamment SFTP. Le script livré prend un dépôt S3 HTTPS ou un répertoire accessible à l’hôte. Prévoir pour la Storage Box un montage fiable avec vérification du point de montage, ou ajouter le transport SFTP et tester la reprise. Pour le VPS économique, conserver PostgreSQL, les miniatures et le worker sur disque local. Un stockage objet primaire pour les originaux demande de configurer Nextcloud et d’étendre la sauvegarde à ces objets avant d’y confier des photos. [Stockage de sauvegarde](https://www.hetzner.com/storage/storage-box/) · [VM](https://www.hetzner.com/cloud/) · [Stockage objet](https://www.hetzner.com/storage/object-storage/) · [Stockage objet primaire dans Nextcloud](https://docs.nextcloud.com/server/latest/admin_manual/configuration_files/primary_storage.html)

Pour un très petit pilote, la franchise R2 Standard couvre 10 Go-mois de sauvegarde dans la limite des opérations gratuites. À 100 Go-mois, le stockage revient à 1,35 USD. À 1 000 Go-mois, il atteint 14,85 USD. [Tarifs R2](https://developers.cloudflare.com/r2/pricing/)

## Préparer le serveur une fois

1. Utiliser un hôte Linux avec Docker Engine, Compose v2, Bash, Python 3, Git, curl, OpenSSL, flock et systemd. Placer le répertoire de données Docker sur le disque prévu pour les originaux. Vérifier que le sous-réseau privé `172.30.50.0/28` est disponible. Pointer le DNS du domaine vers cet hôte et ouvrir TCP 80 et 443 pour Caddy ainsi que SSH pour le déploiement. L’application écoute aussi sur la boucle locale. PostgreSQL, Redis et OpenCV restent sur le réseau Docker.
2. Créer un utilisateur SSH de déploiement autorisé à lancer Docker et à écrire dans `/opt/maison`. Attribuer ce répertoire à cet utilisateur. Ouvrir une session sous ce compte et créer les mots de passe initiaux une seule fois.

```bash
umask 077
mkdir -p /opt/maison/shared
(set -C; { printf 'ADMIN_PASSWORD=%s\n' "$(openssl rand -hex 24)"; printf 'DB_PASSWORD=%s\n' "$(openssl rand -hex 24)"; } > /opt/maison/shared/.env)
```

3. Créer le bucket distant privé et les clés d’accès dédiées. Si la résidence européenne est souhaitée sur R2, sélectionner la juridiction UE et utiliser l’endpoint correspondant. Créer `/etc/maison` et réserver la lecture des fichiers suivants à l’administrateur et, pour les variables cloud et sauvegarde, au compte de déploiement. Les fichiers utilisent le format simple `VARIABLE=valeur`.

| Fichier | Variables |
|---|---|
| `cloud.env` | `MAISON_DOMAIN`, par exemple `maison.exemple.fr` |
| `backup.env` | `RESTIC_REPOSITORY` de la forme `s3:https://endpoint/bucket`, `RESTIC_PASSWORD_FILE`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION` selon le fournisseur |
| `alert.env` | `ALERT_WEBHOOK_URL` pointant vers le récepteur HTTPS de l’admin qui accepte un champ de formulaire `message` |

Générer la clé Restic au chemin indiqué, conserver une seconde copie hors machine et initialiser le dépôt une fois depuis un clone sur le serveur, sous l’utilisateur de déploiement.

```bash
set -a
source /etc/maison/backup.env
set +a
(umask 077; set -C; openssl rand -base64 36 > "$RESTIC_PASSWORD_FILE")
ops/backup.sh init
```

## Déployer depuis GitHub

Dans l’environnement GitHub **production**, enregistrer `DEPLOY_TARGET` (utilisateur@hôte), `DEPLOY_SSH_KEY` et `DEPLOY_KNOWN_HOSTS` (clé hôte OpenSSH vérifiée depuis la console du fournisseur). Les secrets de stockage et la clé Restic restent sur le serveur.

Depuis le commit de la version retenue, pousser un tag du type `maison-prod-v0.1.0`. GitHub Actions rejoue le parcours applicatif et la restauration, envoie le code du tag, puis vérifie le domaine en HTTPS. Le premier déploiement prend une sauvegarde. Les suivants en prennent une avant la mise à jour. Le lien `/opt/maison/current` désigne la dernière version déployée avec succès. En cas de migration défaillante, utiliser le point de reprise et la révision archivée. Le [guide de reprise](reprise.md) décrit cette opération.

Sur le serveur, activer ensuite les unités de la version installée.

```bash
sudo install -m 644 /opt/maison/current/ops/systemd/maison-* /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now maison-backup.timer maison-monitor.timer
systemctl list-timers 'maison-*'
sudo systemctl start maison-monitor.service
```

La sauvegarde démarre à 03 h 15 dans le fuseau du serveur, avec rattrapage après arrêt. Le contrôle horaire déclenche une alerte si les volumes de données dépassent 85 % ou si le dernier instantané atteint 30 h. Une erreur du service de sauvegarde déclenche également l’alerte. Configurer une alerte de consommation chez le fournisseur du bucket à 850 Go pour laisser du temps avant la limite de 1 To. Vérifier la réception sur le canal de l’admin avec `sudo systemctl start maison-alerte@test-manuel.service`. Consulter `journalctl -u maison-backup.service` pour la durée réelle des captures.

## Essai de deux personnes, puis ouverture aux dix comptes

L’admin associe son application TOTP, conserve ses codes de secours, puis crée deux comptes avec un quota de 65 Gio. Un pilote utilise Safari sur iPhone et importe manuellement deux photos dont une HEIC. L’autre utilise Chrome sur Android et un navigateur d’ordinateur pour créer un dossier et y importer des photos et un document. Employer des comptes et des séries distincts.

| Vérification avec chaque personne | Résultat à noter |
|---|---|
| Retrouver son dossier, son document et une année de photos | Appareil, navigateur, année attendue et résultat |
| Comparer une rafale et expliquer le conseil affiché | Choix personnel, conseil de Maison, raison d’un désaccord |
| Garder une série et restaurer une photo supprimée | Photo rouverte depuis son dossier d’origine |
| Vérifier l’accès croisé et le quota depuis le panneau admin | Accès refusé, volume consommé et quota constatés |

Noter les résultats dans un fichier privé et corriger les difficultés rencontrées avant d’élargir l’accès. Après les retours des deux personnes, un cycle quotidien de sauvegarde et une restauration vérifiée depuis le dépôt distant, créer les huit comptes suivants et appliquer leurs quotas. L’import reste manuel sur tous les appareils.
