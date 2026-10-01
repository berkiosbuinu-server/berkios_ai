# Berkios 5.9 — Live Agent Bridge

5.9 ajoute une interface dédiée à iBook pour suivre un run d'exécution.

```text
Berkios Runtime
      ↓
ExecutionRun
      ↓
Live Agent Bridge
      ↓
iBook
```

iBook peut obtenir :
- état du run ;
- étape courante ;
- dernier événement ;
- nombre de résultats ;
- événements depuis un index donné.

iBook peut aussi demander :
- pause ;
- annulation.

## API

`POST /v1/live/runs`
`POST /v1/live/events`
`POST /v1/live/pause`
`POST /v1/live/cancel`

Le bridge ne crée pas de nouvelle autorisation : il expose seulement
les contrôles déjà détenus par le runtime.
