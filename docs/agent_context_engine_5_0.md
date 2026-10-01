# Berkios 5.0 — Agent Context Engine

Berkios transforme maintenant le contexte fusionné en **contexte priorisé pour l'agent**.

## Priorisation

Le contexte est organisé selon sa proximité avec la demande :

```text
Demande / sélection
        ↓
Diagnostics
        ↓
Impact / plan de changement
        ↓
Rôle et connexions du code
        ↓
Compréhension globale
        ↓
Mémoire historique
```

Chaque section possède une priorité et une raison d'inclusion.

## Contraintes

L'agent doit :
- respecter les permissions ;
- ne pas transformer l'historique en autorisation ;
- proposer avant une modification protégée ;
- vérifier après application.

## Résultat

Un fournisseur IA reçoit un contexte structuré, priorisé et explicable,
au lieu d'un mélange arbitraire de fichiers et de texte.
