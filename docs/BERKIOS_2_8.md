# Berkios 2.8 — Project Graph Intelligence

Berkios 2.8 transforme le graphe du projet en source de raisonnement.

## Impact

`ProjectGraphIntelligence.impact(node_id)` calcule :
- relations directes
- relations indirectes
- fichiers affectés
- symboles affectés

## Contexte

`GraphContextComposer` produit un contexte compact orienté impact,
destiné à être injecté dans le raisonnement de l'agent.

## Exemple conceptuel

`file:services/user.py`
  -> définit `UserService`
  -> importe `repositories/user.py`
  -> dépend de `UserRepository`

Une modification de `UserService` peut ainsi fournir à l'agent
une première carte des zones potentiellement concernées.

## Prochaine étape

Connecter automatiquement :
- changements proposés
- impact du graphe
- diagnostics LSP
- historique d'erreurs
- mémoire des corrections
- vérification

afin que Berkios puisse produire un plan de modification fondé sur
la structure réelle du projet.
