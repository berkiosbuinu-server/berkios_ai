# Error Intelligence

## Pourquoi

Un IDE moderne ne doit pas seulement afficher :

```text
Traceback ...
TypeError ...
```

Berkios transforme cette sortie en événement exploitable par le moteur agentique.

## Exemple

```python
events = runtime.errors.ingest_python(traceback_text)

for error in events:
    diagnosis = runtime.errors.diagnose(error.id)
```

Le diagnostic contient :

- type d'erreur
- sévérité
- fichier
- ligne
- commande
- stdout/stderr
- traceback
- causes possibles
- preuves
- fichiers affectés
- actions suggérées

## Boucle

Une erreur devient une entrée de contexte du run. Le provider peut ensuite
produire une `ChangeProposal`, soumise à l'approbation de l'utilisateur avant
application.
