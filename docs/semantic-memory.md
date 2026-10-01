# Semantic Project Memory

La mémoire sémantique complète les trois mémoires précédentes :

```text
Session Memory → conversation courante
Run Memory     → déroulement d'un run
Project Memory → connaissances durables
Semantic Memory → connaissances structurées du projet
Correction Memory → expériences de correction
```

Exemples :

```text
architecture:
  "Le service API ne doit pas accéder directement à l'UI."

convention:
  "Les services utilisent des classes *Service."

dependency:
  "main.py importe berkios.runtime."

decision:
  "Les permissions terminal nécessitent une confirmation."
```

L'objectif est que Berkios puisse rappeler la bonne connaissance au bon moment.
