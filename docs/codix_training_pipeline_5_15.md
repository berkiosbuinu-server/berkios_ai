# Berkios 5.15 — Codix Training Pipeline

5.15 sépare la collecte des données de leur utilisation pour l'entraînement.

```text
Collecte
   ↓
Review
   ↓
Curation
   ↓
Approbation
   ↓
Dataset
   ↓
Evaluation
   ↓
Export / Training
   ↓
Promotion Codix
```

Une donnée brute ne devient jamais automatiquement une donnée
d'entraînement.

## États d'un exemple

- raw
- reviewed
- approved
- rejected

## États d'un run

- collect
- review
- curate
- evaluate
- export
- train
- promote

## Nettoyage

Chaque exemple peut conserver une liste de redactions et des tags.
La pipeline ne prétend pas détecter automatiquement tous les secrets ou
données personnelles : une étape de revue reste nécessaire.

## Evaluation

Une version ne peut être promue que si son évaluation est explicitement
marquée comme réussie.

Cette couche permet ensuite de connecter un vrai système d'entraînement
local ou externe sans modifier le cœur de Berkios.
