# Berkios 5.11 — Approval Center

5.11 formalise l'approbation humaine des actions sensibles.

```text
Agent Decision
   ↓
Action Plan
   ↓
Approval Request
   ↓
iBook Approval Center
   ↓
Approve / Reject
   ↓
Execution
```

Une demande d'approbation peut afficher :
- ce que Berkios veut faire ;
- pourquoi ;
- la capacité utilisée ;
- le niveau de risque ;
- les fichiers/cibles ;
- les changements proposés.

## API

`POST /v1/approval/request`
`POST /v1/approval/list`
`POST /v1/approval/decide`

L'approbation est explicite et n'est jamais déduite de l'historique.
