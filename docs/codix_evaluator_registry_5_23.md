# Berkios 5.23 — Codix Evaluator & Model Registry

5.23 ajoute une évaluation indépendante et un registre persistant des versions Codix.

```text
Candidate model
      ↓
Evaluation set séparé
      ↓
CodixEvaluator
      ↓
Score + failures
      ↓
Compare avec baseline
      ↓
Validated / Rejected
      ↓
Model Registry
      ↓
Promotion
```

Principes :
- le jeu d'évaluation est distinct du dataset d'entraînement ;
- une nouvelle version doit passer son seuil ;
- une régression par rapport à la baseline peut bloquer la promotion ;
- toutes les versions restent enregistrées ;
- une seule version peut être marquée active dans le registre ;
- l'évaluation est indépendante du fournisseur du modèle.
