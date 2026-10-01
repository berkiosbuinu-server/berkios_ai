# Berkios 5.22 — Codix Training Manager

Centralise le cycle Codix avec exécution en arrière-plan et état persistant.

```text
Teachers → Curation → Dataset → Manager
                             ↓
                  préparation / entraînement
                             ↓
                         validation
                             ↓
                    READY_TO_PROMOTE
                             ↓
                         Promotion
```

Fonctions : exécution background, progression, persistance disque, reprise de
l'état après redémarrage, annulation, métriques, versions et promotion explicite.
Le manager orchestre les composants 5.19–5.21 et ne remplace pas le backend ML.
