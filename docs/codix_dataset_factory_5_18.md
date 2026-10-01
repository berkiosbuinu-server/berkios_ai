# Berkios 5.18 — Codix Dataset Factory

5.18 transforme les candidats Codix approuvés en datasets structurés.

## Pipeline

```text
Teacher outputs
      │
      ▼
Human review / curation
      │
      ▼
Dataset Factory
      │
      ├── Deduplication
      ├── Metadata
      ├── Language
      ├── Task type
      ├── Difficulty
      └── Quality score
      │
      ▼
┌──────────┬────────────┬─────────┐
│  train   │ validation │  test   │
└──────────┴────────────┴─────────┘
      │
      ▼
 JSONL + Manifest
```

## Principes

- Split déterministe grâce à une seed.
- Déduplication par empreinte du triplet tâche/contexte/cible.
- Provenance conservée.
- Le dataset n'effectue aucun entraînement de modèle.
- Les données privées ne deviennent pas réutilisables sans consentement approprié.
- Les ratios train/validation/test sont configurables.
- Un manifest décrit les volumes et la version du dataset.

## Exemple

```python
from berkios.learning.dataset_factory import CodixDatasetFactory

factory = CodixDatasetFactory()
dataset = factory.build(
    approved_candidates,
    dataset_id="codix-code",
    version="0.1",
)
factory.export_jsonl(dataset)
factory.export_manifest(dataset)
```

La prochaine étape est la couche d'évaluation automatisée du dataset avant entraînement.
