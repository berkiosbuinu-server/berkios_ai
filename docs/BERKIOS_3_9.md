# Berkios 3.9 — Error-Guided Repair

Berkios 3.9 enrichit les réparations avec les connaissances historiques.

## Contexte de réparation

Une réparation peut recevoir :
- l'échec actuel
- diagnostic
- erreurs historiques similaires
- corrections déjà effectuées
- mémoire sémantique
- fichiers affectés
- symboles affectés

## Flux

`verification failure`
  -> `ErrorGuidedRepairContext`
  -> `provider`
  -> `repair decision`
  -> `repair proposal`

Les informations historiques servent de contexte et ne valent pas
autorisation automatique.

## Suite

La prochaine étape peut enregistrer automatiquement les réparations
réussies dans Correction Memory et relier la correction au run,
aux fichiers et au commit Git.
