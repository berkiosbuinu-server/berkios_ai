# Berkios 4.6 — Repair Intelligence

Cette version transforme l'échec d'une vérification en contexte de réparation.

```text
Erreur
  ↓
Diagnostic
  ↓
Preuves
  ↓
Impact
  ↓
Historique des corrections
  ↓
Causes possibles
  ↓
Réparation minimale
  ↓
Approbation
  ↓
Application
  ↓
Vérification
```

## Principes

- Une erreur n'est pas traitée isolément.
- Le changement qui l'a provoquée est conservé dans le contexte.
- Les fichiers affectés sont pris en compte.
- L'historique peut fournir des indices.
- Berkios propose, mais n'auto-applique pas la correction.
- Après correction, les vérifications sont rejouées.
