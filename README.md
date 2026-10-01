# Berkios 2.6 — Semantic Project Memory

Berkios ajoute une mémoire sémantique persistante du projet.

Elle peut mémoriser :
- décisions d'architecture
- conventions de code
- dépendances
- relations entre modules
- raisons de corrections
- notes et préférences du projet

Les connaissances sont recherchables et peuvent être rappelées comme contexte
lorsqu'une demande concerne une partie du projet.

Mémoire :
`.berkios/semantic_memory.json`

API :
- `GET /v1/memory/semantic`
- `GET /v1/project/relations`


## Berkios 5.2
Provider Decision Integration ajoute le premier provider distant opérationnel : OpenAI.
Le cœur reste multi-provider et peut accueillir des providers locaux ou d'autres fournisseurs.


## Berkios 5.3
Provider Agent Loop connecte le provider sélectionné au cycle agentique.
OpenAI peut maintenant participer au flux complet de décision, tandis que
l'approbation, les permissions, l'application et la vérification restent
contrôlées par le runtime.


## Berkios 5.4
Action Planner : transforme une décision provider en plan d'actions structuré
avec dépendances, capacités, risques, approbation et vérification.


## Berkios 5.5
Capability Resolver : relie chaque étape d'un ActionPlan à une capacité
Berkios disponible, sans confondre capacité technique et autorisation.


## Berkios 5.6
Execution Planner : transforme les capacités résolues en séquence d'exécution
avec états, dépendances, blocages, approbation et vérification.


## Berkios 5.7
Tool Executor : exécution contrôlée des capacités READY, avec résultats,
erreurs et respect des étapes d'approbation.


## Berkios 5.8
Execution Events & Run Control : runs d'exécution, événements structurés,
pause, annulation et résultats consommables par iBook.


## Berkios 5.9
Live Agent Bridge : interface dédiée à iBook pour suivre les runs,
consulter les événements et contrôler pause/annulation.


## Berkios 5.10
iBook Agent SDK Live : façade Python pour lancer un agent Berkios, suivre
ses événements et contrôler ses runs depuis iBook.


## Berkios 5.11
Approval Center : demandes d'approbation structurées pour iBook, avec
cibles, changements, risques et décision explicite.


## Berkios 5.12
Approval-to-Execution Bridge : liaison précise entre une approbation iBook
et une étape déterminée d'un run, avec événements d'approbation.


## Berkios 5.13
Execution Resume : checkpoints et reprise d'un run sans rejouer les étapes
déjà terminées.


## Berkios 5.14 — Codix
Codix est une identité IA spécialisée code, indépendante du provider.
Ajout d'un dataset de learning avec consentement explicite, provenance et évaluations.


## Berkios 5.15 — Codix Training Pipeline
Pipeline séparée de collecte, revue, curation, évaluation, export et
promotion des données Codix.


## Berkios 5.25 — Production Foundation

Berkios can now be packaged as a production-oriented Docker Compose stack with PostgreSQL, Redis, API, worker foundation, Nginx and ACME-ready certificate paths.

See `docs/deployment_5_25.md` for deployment steps and the current durability boundary.


## Berkios 5.26 — Durable Runtime Foundation

PostgreSQL persistence and Redis event publishing are now available through `berkios.persistence` and `RuntimePersistence`. Production Compose uses PostgreSQL/Redis; local development falls back to SQLite when no database URL is configured.


## Berkios 5.27 — Durable Execution

Execution runs, approvals and live events are now connected to the 5.26 persistence layer. Runtime services are shared singletons, persisted runs can be restored after restart, and iBook live events can fall back to durable storage.


## Berkios 5.28 — Distributed Job Runtime

Redis-backed jobs and worker execution foundation.

## Berkios 5.35.0 — Durable Job Recovery

Le runtime de jobs devient durable : PostgreSQL conserve l'état des jobs,
les workers utilisent un lease temporaire, et les jobs dont le worker disparaît
sont récupérés puis remis en file. Au redémarrage, les jobs restés `queued` sont
réinjectés dans Redis. Les tentatives sont comptées avec une limite configurable
(`max_attempts`, 3 par défaut).

Cette version réduit la fenêtre de perte d'un job après un crash worker. Le
scheduler distribué complet, le heartbeat en cours d'exécution et le routage
avancé multi-worker restent des étapes ultérieures.
