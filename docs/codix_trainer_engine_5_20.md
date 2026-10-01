# Berkios 5.20 — Codix Trainer Engine

5.20 introduit le moteur d'exécution d'entraînement avec checkpoints et reprise.

## Architecture

```text
Codix Dataset
      ↓
CodixTrainerEngine
      ↓
TrainerBackend
      ├── Local LoRA/QLoRA (à brancher)
      ├── autre backend local
      └── backend personnalisé
      ↓
Checkpoints
      ↓
Validation
      ↓
Promotion
```

## Important

Le moteur est volontairement découplé des bibliothèques ML.
`TrainerBackend` est le contrat d'intégration. L'adaptateur fourni est
un adaptateur de développement et **ne produit pas de poids de modèle**.

Cela permet à Berkios de recevoir ensuite un vrai backend PyTorch/Transformers/PEFT
sans réécrire toute la boucle de gouvernance Codix.

Fonctions :
- epochs ;
- batch size ;
- learning rate ;
- checkpoints périodiques ;
- limite de steps ;
- reprise depuis checkpoint ;
- métriques ;
- artefacts ;
- gestion d'échec/annulation.
