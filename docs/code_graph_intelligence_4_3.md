# Berkios 4.3 — Code Graph Intelligence

Le Code Graph Intelligence transforme les connexions détectées par Berkios en analyse d'impact.

## Questions auxquelles Berkios peut répondre

- Qu'est-ce qui dépend de ce fichier ?
- Qu'est-ce qui dépend indirectement de lui ?
- Quels composants risquent d'être affectés ?
- Quel est le chemin de dépendance ?
- Quel niveau d'impact doit être vérifié avant une modification ?

## Modèle

```text
Fichier A
   │
   ├── importe B
   │      │
   │      └── importe C
   │
   └── dépendance indirecte → C
```

Berkios peut ainsi passer d'une simple explication de code à une compréhension du **système de dépendances du projet**.

Cette information doit alimenter le planner, le Change Engine et le Verification Loop, sans autoriser automatiquement une modification.
