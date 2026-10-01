# Berkios 4.2 — Code Explorer Intelligence

Le Code Explorer complète le Code Explainer.

Pour un symbole, Berkios peut maintenant reconstruire :

- **Définition** — où l'élément est défini ;
- **Utilisé par** — quelles parties du projet le référencent ;
- **Utilise / appelle** — quelles fonctions ou symboles il appelle ;
- **Dépend de** — imports et modules nécessaires ;
- **Fichiers liés** — fichiers concernés ;
- **Impact** — éléments à vérifier avant une modification ;
- **Flux** — résumé des relations ;
- **Pourquoi** — interprétation du rôle de la connexion ;
- **Exemples d'utilisation** — emplacements concrets.

Architecture :

```text
iBook
  │
  └── clic sur fonction / classe / symbole
          │
          ▼
    Berkios Code Explorer
          │
          ├── AST
          ├── Code Index
          ├── Project Graph
          ├── LSP
          └── Memory
                │
                ▼
     Utilisé par / Utilise / Dépend de
     Impact / Flux / Pourquoi
```

Les relations sont descriptives : Berkios ne considère pas automatiquement qu'une modification est sûre ou autorisée.
