# Berkios 3.2 — Canonical AgentRuntime

Berkios 3.2 introduit `AgentRuntime` comme point d'entrée canonique
pour les runs de développement.

## Responsabilités

- créer un run
- préparer le contexte d'intelligence
- gérer les états
- enregistrer les transitions
- enregistrer les décisions
- enregistrer les vérifications
- terminer ou échouer un run
- transmettre les événements à Run Memory lorsqu'elle est disponible

## États

`idle`
-> `analyzing`
-> `planning`
-> `proposing`
-> `waiting_approval`
-> `applying`
-> `verifying`
-> `completed` / `failed`

## Architecture

`iBook -> SDK -> AgentRuntime -> Unified Intelligence -> AgentLoop`

Les prochaines versions pourront faire de `AgentRuntime` le point
de raccordement unique pour permissions, provider engine, change engine,
verification engine et événements temps réel.
