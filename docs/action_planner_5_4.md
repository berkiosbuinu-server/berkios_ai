# Berkios 5.4 — Action Planner

5.4 transforme une décision structurée en plan d'actions concret.

```text
Provider / DecisionEngine
        ↓
Decision
        ↓
ActionPlanner
        ↓
ActionPlan
        ↓
Permissions / Approval
        ↓
Execution
        ↓
Verification
```

Le planner ne lance aucun outil. Il décrit les actions, dépendances,
capacités, risques et validations nécessaires.

## Exemple

Une décision `analyze_and_propose_change` produit typiquement :

1. analyser le contexte ;
2. lire les fichiers nécessaires ;
3. proposer une modification ;
4. attendre l'approbation ;
5. vérifier la modification.

## API

`POST /v1/action-plan`

```json
{
  "request": "Corrige l'erreur dans app.py",
  "decision": {
    "action": "analyze_and_propose_change",
    "objective": "Corriger l'erreur"
  },
  "context": {
    "active_file": "app.py"
  }
}
```

Le plan reste soumis aux permissions du runtime et ne constitue jamais
une autorisation implicite.
