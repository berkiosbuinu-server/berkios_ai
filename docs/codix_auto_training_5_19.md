# Berkios 5.19 — Codix Auto Training

Cette version introduit l'orchestrateur d'entraînement automatique.

## Boucle

```text
Dataset Codix
    ↓
Qualité + consentement
    ↓
Préparation
    ↓
Trainer backend
    ↓
Validation
    ├── régression → REJECTED
    └── succès
          ↓
     Promotion
```

## Garde-fous

L'automatisation ne signifie pas entraînement aveugle.

- consentement explicite configurable ;
- approbation humaine configurable ;
- seuil de qualité du dataset ;
- seuil de validation ;
- détection de régression par rapport au modèle de base ;
- promotion séparée de l'entraînement ;
- provenance et manifest conservés ;
- aucun backend de poids n'est supposé par défaut.

Le backend `adapter` est une interface : il permet de brancher plus tard un véritable
trainer local (par exemple LoRA/QLoRA) sans modifier l'orchestrateur.

Sans trainer enregistré, Berkios prépare le manifest puis s'arrête : aucune fausse
affirmation d'entraînement n'est produite.
