# Berkios 5.2 — Provider Decision Integration

Berkios peut maintenant utiliser un provider IA réel pour produire une décision structurée.

## OpenAI

Le provider OpenAI utilise la Responses API et Structured Outputs.

Variables :
- `OPENAI_API_KEY` : clé API, jamais stockée dans le projet.
- `BERKIOS_OPENAI_MODEL` : modèle à utiliser. Par défaut : `gpt-5.6-luna`.

Installation :

```bash
pip install -e .
```

ou installez `openai` manuellement.

## Architecture

```text
AgentContext
    ↓
ProviderEngine
    ↓
OpenAIProvider
    ↓
Responses API
    ↓
Decision JSON
    ↓
ProviderDecisionIntegration
    ↓
Decision canonique Berkios
    ↓
Runtime / permissions / approval / verification
```

Le provider n'a pas le droit de contourner les permissions de Berkios.
La mémoire historique ne constitue jamais une autorisation.

## Multi-provider

Le contrat `AIProvider` reste indépendant du fournisseur.
OpenAI est le premier provider distant opérationnel. D'autres adaptateurs
peuvent être ajoutés sans modifier le moteur de décision.
