# Berkios 2.7 — LSP + Project Graph

Berkios 2.7 relie la mémoire sémantique au graphe structurel du projet.

## Graphe

Les premiers nœuds supportés sont :
- `file`
- `symbol`
- `module`

Les relations incluent :
- `defines`
- `imports`

Le graphe est persisté dans `.berkios/graph.json`.

## LSP

Une façade `LSPService` normalise :
- diagnostics
- definition
- references

Le transport reste découplé afin qu'iBook puisse fournir un serveur LSP réel
sans modifier le cœur de Berkios.

## Direction

La prochaine évolution peut relier directement :
`fichier → symbole → référence → dépendance → erreur → correction → commit`

et injecter ces relations dans le contexte de l'agent.
