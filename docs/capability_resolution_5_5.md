# Berkios 5.5 — Capability Resolution

5.5 ajoute une étape entre le plan et l'exécution :

```text
Decision
  ↓
ActionPlan
  ↓
CapabilityResolver
  ↓
Capacités disponibles
  ↓
Permissions / approbation
  ↓
Exécution
```

Le resolver répond à une question précise :
**« quelle capacité de Berkios peut réaliser cette étape ? »**

Il ne répond pas :
**« ai-je le droit de l'exécuter ? »**

Cette seconde question reste contrôlée par le système de permissions et
l'approbation humaine.

## API

`POST /v1/action-plan/resolve`

Le corps contient un `plan` produit par `POST /v1/action-plan`.

La réponse fournit le plan et la résolution des capacités.
