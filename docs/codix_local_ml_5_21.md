# Berkios 5.21 — Codix Local ML Backend

5.21 ajoute un backend local optionnel pour l'entraînement LoRA avec
**PyTorch + Transformers + PEFT**.

## Principe

```text
Codix Dataset
      ↓
LocalMLBackend
      ↓
Tokenizer local
      ↓
Base model local
      ↓
PEFT / LoRA
      ↓
Trainer
      ↓
Codix adapter
```

## Dépendances

Le backend vérifie à l'exécution la présence de :

- PyTorch
- Transformers
- PEFT
- Accelerate (optionnel selon la configuration)
- bitsandbytes (optionnel, notamment pour certaines configurations quantifiées)

Berkios n'importe pas ces dépendances au démarrage. Elles restent optionnelles.

## Sécurité

Le backend utilise `local_files_only=True` pour le modèle et le tokenizer :
il ne télécharge donc pas automatiquement un modèle depuis Internet.

Le développeur doit fournir explicitement un chemin ou identifiant correspondant
à un modèle déjà présent localement.

## Important

Le backend est désormais un **chemin d'entraînement réel**, mais il dépend du
modèle local et de l'environnement matériel. Il ne garantit pas qu'un modèle
arbitraire soit compatible avec LoRA ou avec la mémoire disponible.

Le pipeline de gouvernance 5.19 reste au-dessus :
consentement → qualité → entraînement → validation → promotion.
