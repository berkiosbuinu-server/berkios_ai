# Berkios 5.8 — Execution Events & Run Control

5.8 introduit un run d'exécution contrôlable.

```text
Execution Plan
      ↓
Execution Run
      ↓
started
  ↓
step.started
  ↓
step.completed / step.failed
  ↓
waiting_approval / completed / failed / cancelled
```

## États

- `created`
- `running`
- `waiting_approval`
- `paused`
- `completed`
- `failed`
- `cancelled`

Les événements sont structurés et peuvent être consommés par iBook.

Le controller peut :
- créer un run ;
- exécuter un plan ;
- consulter son état ;
- mettre en pause ;
- annuler ;
- conserver les résultats et événements.

Le provider n'obtient pas le contrôle du run.
