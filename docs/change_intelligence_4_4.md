# Berkios 4.4 — Change Intelligence

Berkios relie maintenant le graphe de code au cycle de modification.

## Avant une modification

```text
Demande
  ↓
Analyse du code
  ↓
Graphe des dépendances
  ↓
Impact direct + indirect
  ↓
Risques
  ↓
Plan de modification
  ↓
Approbation
  ↓
Application
  ↓
Vérification ciblée
```

## Vérifications ciblées

Berkios génère une liste de composants à vérifier, avec une priorité.

Une modification d'un composant très utilisé peut donc déclencher une vérification plus large qu'une modification isolée.

L'approbation humaine reste obligatoire pour les changements.
