# Berkios 5.6 — Tool Execution Planner

5.6 ajoute une couche entre les capacités et l'exécution réelle.

```text
Decision
  ↓
ActionPlan
  ↓
CapabilityResolver
  ↓
ExecutionPlanner
  ↓
ordre + dépendances + blocages
  ↓
Permissions / Approval
  ↓
Tool Execution
  ↓
Verification
```

L'ExecutionPlanner ne lance aucun outil.

Il détermine notamment :
- quelles étapes sont prêtes ;
- quelles étapes sont bloquées ;
- les dépendances ;
- les points d'approbation ;
- les besoins de vérification.

Une capacité disponible ne signifie donc toujours pas qu'une action est
autorisée.

## API

`POST /v1/execution-plan`

Le corps contient un `plan` issu de `/v1/action-plan`.
