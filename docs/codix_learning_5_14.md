# Berkios 5.14 — Codix Learning Architecture

Codix est l'identité IA spécialisée de Berkios, pas nécessairement un modèle
avec ses propres poids. Son backend peut être OpenAI, un autre provider,
un endpoint personnalisé ou, plus tard, un modèle local entraîné par Berkios.

```text
iBook work
   ↓
provider outputs + tests + explicit feedback
   ↓
consent
   ↓
Codix dataset
   ↓
evals
   ↓
optimization / training
   ↓
Codix version
```

Le système ne collecte pas automatiquement le travail des utilisateurs pour
l'entraînement. L'apprentissage nécessite un consentement explicite et chaque
exemple conserve sa provenance.

Sources possibles : données publiques sous licence, exemples de providers,
corrections validées, tests, feedback développeur et données synthétiques.

Le dataset peut être exporté en JSONL vers une infrastructure d'entraînement.
