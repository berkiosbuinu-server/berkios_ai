# Berkios 4.7 — Engineering Loop

Berkios possède maintenant une orchestration unifiée des briques précédentes.

```text
Comprendre
   ↓
Explorer les connexions
   ↓
Analyser l'impact
   ↓
Planifier
   ↓
Approbation
   ↓
Modifier
   ↓
Vérifier
   ├── succès → terminé
   └── échec → réparation
                    ↓
                 nouvelle vérification
```

## États

- analyzing
- planning
- waiting_approval
- approved
- verifying
- completed
- repairing
- repair_required

Cette couche ne remplace pas le Runtime Agent : elle fournit une orchestration spécialisée
pour les workflows de compréhension et d'ingénierie du code.
