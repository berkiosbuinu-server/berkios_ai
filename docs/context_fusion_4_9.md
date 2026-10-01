# Berkios 4.9 — Project Context Fusion

Berkios dispose maintenant d'un contexte unifié.

```text
Project Understanding
       +
Code Explainer
       +
Code Explorer
       +
Graph Impact
       +
Change Plan
       +
Diagnostics
       +
Memory
       ↓
Project Context Snapshot
       ↓
Agent / Provider / iBook
```

Le snapshot contient les informations utiles à une décision sans obliger chaque composant
à reconstruire indépendamment le même contexte.

## Objectif

Quand iBook demande :

> « Modifie cette fonction pour ajouter X »

Berkios peut d'abord réunir :
- compréhension du projet ;
- rôle du fichier ;
- connexions ;
- impact ;
- plan de changement ;
- diagnostics ;
- mémoire pertinente.

Le fournisseur IA reçoit ainsi un contexte structuré plutôt qu'un simple morceau de texte.
