# Berkios 5.10 — iBook Agent SDK Live

5.10 simplifie l'intégration iBook.

Au lieu de manipuler directement l'API :

```python
from berkios.ibook.agent import IBookAgentBridge

agent = IBookAgentBridge()

result = agent.ask(
    "Corrige l'erreur dans ce fichier",
    active_file="app.py",
)

run_id = result["run_id"]

status = agent.status(run_id)
events = agent.events(run_id)

agent.pause(run_id)
agent.cancel(run_id)
```

## Architecture

```text
iBook UI
   ↓
IBookAgentBridge
   ↓
IBookAgentClient
   ↓
Berkios API
   ↓
Agent Runtime
```

Le SDK ne possède aucune permission supplémentaire. Il utilise les contrôles
du runtime Berkios.
