# Berkios 3.5 — Provider-Driven Agent Cycle

Berkios 3.5 connecte le Provider Engine au cycle de modification.

## Décision normalisée

`AgentDecision` expose :
- action
- reason
- proposal
- repair
- metadata

## Flux

`request + context`
  -> `provider`
  -> `decision`
  -> `proposal`
  -> `permission/review`
  -> `apply`
  -> `verify`

En cas d'échec :

`verification_failure`
  -> `provider`
  -> `repair decision`
  -> `repair proposal`

Le provider ne contourne pas les permissions ni la revue.

## Suite

La prochaine étape consiste à relier cette décision au contexte unifié
et à Error Intelligence, afin que le provider reçoive automatiquement
les diagnostics, l'impact, les corrections historiques et le code
concerné avant de proposer une action.
