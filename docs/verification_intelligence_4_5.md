# Berkios 4.5 — Verification Intelligence

Berkios relie maintenant le changement, son impact et les résultats de vérification.

```text
Modification
    ↓
Impact
    ↓
Cibles de vérification
    ↓
Analyse syntaxique / tests / checks
    ↓
Résultats reliés au changement
    ↓
Erreur ou validation
    ↓
Réparation guidée
```

## Ce que Berkios peut distinguer

- cible vérifiée ;
- cible ignorée ;
- vérification réussie ;
- erreur liée au changement ;
- prochaine action recommandée.

Le moteur est volontairement local-first et utilise `shell=False` pour les contrôles Python.
Les vérifications qui écrivent ou exécutent des opérations sensibles doivent rester soumises aux permissions du runtime.
