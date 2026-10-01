# Berkios 5.3 — Provider Agent Loop

Berkios 5.3 connecte le provider sélectionné au cycle agentique.

## Flux

```text
Demande
  ↓
Contexte projet / iBook
  ↓
ProviderEngine
  ↓
OpenAI (ou autre provider)
  ↓
Décision structurée
  ↓
AgentLoop2
  ↓
Proposition
  ↓
Approbation humaine
  ↓
Application
  ↓
Vérification
  ↓
Réparation proposée si échec
```

Le provider ne possède jamais l'autorité d'écrire directement dans le projet.
L'approbation, les permissions et la vérification restent du côté du runtime.

## API

`POST /v1/agent/run`

Exemple :

```json
{
  "request": "Corrige l'erreur dans app.py",
  "active_file": "app.py",
  "max_iterations": 3
}
```

Le provider sélectionné est utilisé. Avec `OPENAI_API_KEY`, OpenAI peut être
sélectionné comme provider distant. D'autres providers peuvent être ajoutés
sans modifier `ProviderAgentRuntime`.

## Sélection

`POST /v1/provider/select`

```json
{"provider": "openai"}
```

Puis :

`POST /v1/agent/run`
