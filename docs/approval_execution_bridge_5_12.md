# Berkios 5.12 — Approval-to-Execution Bridge

5.12 relie une approbation à une étape précise.

```text
Approval Request
      ↓
Binding
      ↓
run_id + step_id + action_id
      ↓
Approve / Reject
      ↓
événement du run
```

Une approbation n'est donc pas globale.

Elle est liée à :
- un run ;
- une étape ;
- une action.

Le runtime peut ainsi savoir exactement quelle opération a été autorisée.

Les événements :
- `approval.approved`
- `approval.rejected`

sont ajoutés au run concerné.
