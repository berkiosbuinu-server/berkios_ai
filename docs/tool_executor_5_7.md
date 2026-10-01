# Berkios 5.7 — Tool Executor

5.7 ajoute la première couche d'exécution réelle des capacités.

```text
Decision
  ↓
ActionPlan
  ↓
CapabilityResolver
  ↓
ExecutionPlanner
  ↓
ToolExecutor
  ↓
Tool Result / Event
  ↓
Verification
```

## Règles

Le ToolExecutor :
- n'exécute que les capacités enregistrées ;
- refuse les étapes `BLOCKED` ;
- refuse les étapes `WAITING_APPROVAL` ;
- ne considère pas une capacité comme une autorisation ;
- capture succès, erreurs et durée ;
- permet d'enregistrer des handlers de façon contrôlée.

L'API d'exécution ne permet donc pas de transformer une proposition protégée
en modification automatique.

## Événements

`ExecutionEvent` permet à iBook de suivre le cycle :

```text
execution.started
execution.completed
execution.failed
execution.waiting_approval
```

## API

`POST /v1/execution/ready`

Cette route prépare le plan et exécute uniquement les étapes qui sont
réellement `READY`.
