# Berkios 5.24 — Codix Continuous Learning Loop

La boucle continue relie les composants précédents :

```text
Nouveaux exemples approuvés
          ↓
       Dataset
          ↓
     Entraînement
          ↓
       Évaluation
          ↓
 Comparaison baseline
      /          \
  rejet          succès
                   ↓
              Promotion
```

La boucle est provider-neutral et chaque étape est injectable.

Garde-fous :
- nombre minimal de nouveaux exemples ;
- seuil de validation ;
- seuil de régression ;
- promotion automatique désactivée par défaut ;
- état et métriques persistés.
