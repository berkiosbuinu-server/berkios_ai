# Berkios 3.6 — Context-Aware Provider

Berkios 3.6 construit le contexte présenté au provider avant chaque
décision agentique.

## Contexte fourni

- Unified Intelligence
- graphe et impact
- diagnostics/LSP disponibles
- historique des erreurs
- corrections connues
- mémoire sémantique
- état et contexte iBook
- fichier actif
- sélection
- fichiers récents

## Flux

`iBook context`
  + `project intelligence`
  + `LSP`
  + `error/correction memory`
  -> `ProviderContext`
  -> `Provider`
  -> `AgentDecision`

Le provider reste soumis aux contrôles de permission, de revue et
de vérification.

## Suite

La prochaine étape est de brancher ce contexte directement à l'AgentLoop
pour que chaque décision de planification, proposition et réparation
utilise automatiquement le même contexte enrichi.
