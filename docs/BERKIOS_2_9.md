# Berkios 2.9 — Impact-Aware Agent

Berkios 2.9 fait entrer l'intelligence du graphe dans la préparation
des actions de l'agent.

## Flux

`demande`
  -> `cibles`
  -> `analyse d'impact`
  -> `fichiers/symboles affectés`
  -> `risques`
  -> `contexte de planification`
  -> `proposition`

## Objectif

Berkios ne doit plus traiter une modification comme un simple changement
de texte. Il doit considérer la structure du projet avant de proposer
une action.

## Risques actuels

Le planner signale notamment :
- impact important sur plusieurs fichiers
- cascade sur de nombreux symboles

Ces signaux sont informatifs : ils ne remplacent pas les diagnostics LSP,
les tests ou la validation humaine.

## Suite

La prochaine étape consiste à faire fusionner automatiquement :
- contexte live iBook
- graphe d'impact
- LSP
- mémoire des corrections
- historique des erreurs
- Git
- vérification

dans un plan d'agent unique.
