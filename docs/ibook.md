# Intégration iBook

iBook peut démarrer Berkios séparément puis utiliser `IBookBridge`.

```python
from berkios.ibook.bridge import IBookBridge

bridge = IBookBridge()
bridge.sync_editor(
    workspace="/mon/projet",
    active_file="src/main.py",
    active_content="...",
    cursor={"line": 10, "column": 4},
)
result = bridge.ask("Explique cette erreur et propose une correction.")
```

Le contexte éditeur est une entrée de l'agent, pas une duplication de l'éditeur.
