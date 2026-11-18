# Évaluer le tri sur les photos familiales

Créer un compte de test privé et y importer manuellement un petit lot dans Fichiers. Mélanger rafales, photos indépendantes, scènes sombres nettes, arrière-plans volontairement flous et prises ratées. Attendre que le panneau admin indique que le compte a terminé son analyse.

Depuis le dépôt, utiliser l'identifiant Nextcloud du compte pour exporter les photos analysées. Le document d'annotation omet les prédictions pour permettre un jugement indépendant.

```bash
python3 scripts/calibrer.py export pilote fixtures-private/reference.json
```

Ouvrir le JSON dans VS Code et examiner les originaux. Donner le même nom de `serie` aux clichés d'une même prise et attribuer `""` à un cliché isolé. Marquer `floue` et `a_garder` avec `true` ou `false`. Plusieurs choix à garder sont possibles dans une série. Laisser `null` en cas de doute. Les chemins et annotations restent dans le répertoire privé ignoré par Git.

```bash
python3 scripts/calibrer.py rapport pilote fixtures-private/reference.json
```

Pour les paires et le flou, VP compte les propositions correctes, FP les propositions à tort et FN les cas manqués. Les choix à conserver comptent les accords, désaccords et abstentions sur les groupes proposés dont tous les membres ont été annotés dans la même série. Une modification d'original invalide son annotation. Comparer les résultats sur les mêmes annotations avant de modifier les seuils. Rejouer avec un deuxième lot indépendant après ajustement.
