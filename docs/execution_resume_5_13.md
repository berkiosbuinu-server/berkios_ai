# Berkios 5.13 — Execution Resume

5.13 ajoute des checkpoints de run.

```text
Run
 ↓
étapes terminées
 ↓
checkpoint
 ↓
approbation / pause / interruption
 ↓
reprise
 ↓
uniquement les étapes restantes
```

Le resumer distingue :
- étapes terminées ;
- étapes bloquées ;
- prochaine étape ;
- étapes actuellement prêtes.

Une étape déjà validée n'est pas rejouée lors de la reprise.

## API

`POST /v1/execution/checkpoint`

Le checkpoint est calculé à partir du run et de son plan.
