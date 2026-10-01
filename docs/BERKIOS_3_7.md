# Berkios 3.7 — Context-Aware AgentLoop

Berkios 3.7 branche le contexte enrichi directement au cycle de décision.

## Phases

- `analyze`
- `propose`
- `repair`

Chaque phase reconstruit un `ProviderContext` à partir des mêmes sources :
- iBook
- graphe
- impact
- LSP
- erreurs
- corrections
- mémoire
- Git

## Run Memory

Les décisions d'analyse et de proposition sont enregistrées dans le run.

## Réparation

Lors d'une réparation, l'échec de vérification est ajouté au contexte
envoyé au provider.

## Suite

La prochaine étape peut introduire `AgentLoop 2`, capable de boucler
automatiquement entre proposition, approbation, application, vérification
et réparation tout en conservant le contexte enrichi à chaque itération.
