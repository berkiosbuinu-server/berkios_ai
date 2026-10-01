# Berkios 4.8 — Project Understanding

Berkios peut maintenant construire une compréhension globale du projet avant une tâche.

## Vue globale

- langage(s) ;
- composants ;
- rôle de chaque module ;
- fonctions/classes ;
- dépendances ;
- points d'entrée ;
- architecture ;
- flux ;
- dépendances externes ;
- risques détectés ;
- niveau de confiance.

```text
Projet
  │
  ├── Entrées
  ├── Modules
  │    ├── Services
  │    ├── Modèles
  │    ├── API
  │    └── Utilitaires
  ├── Dépendances
  └── Flux
```

Cette compréhension peut servir de contexte commun au Code Explainer, Code Explorer,
Change Intelligence, Verification Intelligence, Repair Intelligence et aux fournisseurs IA.
