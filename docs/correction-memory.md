# Correction Memory

Exemple de connaissance :

```text
TypeError dans src/service.py:84
→ cause identifiée
→ correction appliquée
→ tests validés
→ commit 4f91...
→ corrigé le 30 septembre 2026
```

Le but est que Berkios puisse dire à l'agent :

> Une erreur similaire a déjà été corrigée dans ce projet.
> La correction concernait `src/service.py` et avait été validée par les tests.
> Le commit associé est disponible si Git était présent au moment de la capture.

Cette mémoire ne remplace pas la vérification : une correction historique est
un indice/context, pas une autorisation d'appliquer automatiquement le changement.
