# Berkios 3.1 — Intelligence in the Agent Loop

Berkios 3.1 relie explicitement Unified Intelligence au cycle d'un run.

## Nouveau flux

`request`
  -> `intelligence snapshot`
  -> `analyzing`
  -> `planning`
  -> `proposing`
  -> `approval`
  -> `applying`
  -> `verifying`
  -> `memory`

## Run Memory

Le contexte initial, les transitions, décisions et résultats de vérification
peuvent être enregistrés dans Run Memory.

## iBook

Le bridge expose désormais la préparation d'un run avec :
- fichier actif
- sélection
- cibles du graphe
- contexte d'intelligence

## Prochaine étape

La suite consiste à faire de cette préparation le point d'entrée canonique
de l'AgentRuntime : aucun run de développement ne devrait démarrer avant
la construction de son contexte d'intelligence, sauf mode explicitement
minimal.
