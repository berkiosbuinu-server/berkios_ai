# Berkios 3.0 — Unified Intelligence

Berkios 3.0 introduit une couche d'intelligence unifiée qui rassemble
les principales sources de contexte du projet.

## Sources

- contexte live iBook
- graphe du projet
- impact des changements
- mémoire sémantique
- mémoire des corrections
- historique d'erreurs
- état Git
- diagnostics

## Snapshot

`IntelligenceSnapshot` constitue un objet de contexte structuré destiné
au planificateur et à l'agent.

Flux conceptuel :

`iBook`
  -> `Live Context`
  -> `Unified Intelligence`
  -> `Agent Planning`
  -> `Change Proposal`
  -> `Review`
  -> `Apply`
  -> `Verify`
  -> `Memory`

Cette couche ne décide pas automatiquement d'autoriser une modification :
les permissions, la revue et la vérification restent des contrôles distincts.

## Prochaine étape

La suite naturelle est de brancher réellement ce snapshot dans le runtime
de l'AgentLoop afin que chaque run commence par une analyse de contexte
unifiée et que ses résultats soient conservés dans Run Memory.
