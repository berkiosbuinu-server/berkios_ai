# Berkios 4.1 — Code Explainer

Berkios explique un fichier, un symbole ou une sélection iBook.

Il reconstruit :
- le rôle et le but ;
- les fonctions/classes ;
- les entrées et sorties ;
- les imports et dépendances ;
- les appels ;
- les connexions ;
- le flux ;
- les risques ;
- les suggestions ;
- le niveau de confiance.

Architecture :
iBook → sélection/fichier/symbole → Code Explainer → AST + Code Index + Project Graph + LSP + Memory + Provider IA.

L'analyse structurelle Python est locale et déterministe. Le fournisseur IA peut ensuite enrichir l'explication avec le contexte du projet.
