# Berkios 3.3 — Runtime Orchestration

Berkios 3.3 connecte `AgentRuntime` aux principaux moteurs d'exécution.

## Orchestrateur

`RuntimeOrchestrator` coordonne :
- AgentRuntime
- permissions
- propositions de changement
- vérification
- sélection de provider

## Flux

`request`
  -> `intelligence`
  -> `planning`
  -> `proposal`
  -> `permission`
  -> `approval`
  -> `apply`
  -> `verify`
  -> `complete/fail`

Les moteurs restent injectables : l'orchestrateur ne dépend pas
d'une implémentation unique.

## iBook

Le bridge expose les étapes principales pour permettre à iBook
d'afficher un workflow agentique contrôlable.

## Suite

La prochaine évolution peut connecter directement `ChangeEngine`
et `VerificationEngine` pour effectuer un vrai cycle proposition →
application → vérification → réparation, avec ProviderEngine utilisé
pour produire les décisions.
