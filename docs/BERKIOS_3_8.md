# Berkios 3.8 — AgentLoop 2

Berkios 3.8 introduit une boucle agentique bornée.

## Cycle

`Analyze`
  -> `Propose`
  -> `Approval Required`
  -> `Apply`
  -> `Verify`
  -> `Completed`

En cas d'échec :

`Verify`
  -> `Repairing`
  -> `Repair Proposal`
  -> `Approval Required`
  -> `Apply`
  -> `Verify`

## Contrôles

- le nombre d'itérations est borné ;
- l'approbation n'est pas automatique ;
- les permissions restent séparées ;
- chaque décision est enregistrée dans le run ;
- l'échec de vérification est réinjecté dans le contexte du provider.

## Suite

La prochaine étape peut ajouter la gestion persistante des itérations
et la détection structurée des erreurs afin que chaque réparation soit
guidée par Error Intelligence et Correction Memory.
