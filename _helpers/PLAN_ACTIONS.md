# PLAN D'ACTIONS

Ce document détaille (et décrits les étapes d'implémentation) de certaines des taches présentes dans le fichier `TODO.md`.
Un regroupement par Sprints peut être envisagé dans ce document, selon le nombre de tâches à implémenter.
La priorisation des tâches est définie dans `TODO.md` et doit être respectée pour éviter de se disperser sur des points moins urgents.

## Contexte et Lignes Directrices (Héritées du plan de migration)

- **Séparation des rôles** : Garder une séparation claire entre l'outil applicatif (`UnityAssetsManager`) et le pipeline de curation (`_Helpers/04_Assets/AssetsCuration/`).
- **Nomenclature** : Le nom officiel est `UnityAssetsManager`. Toute ancienne référence (AssetManager, AssetManager V1, AssetsManager V2) est dépréciée.

**REGLE D'OR : Toujours proposer d'effectuer les corrections de bugs et les corrections immédiates en premier. Elles sont listées dans les section "Corrections immédiates" et "Bugs" du fichier `TODO.md`.**

Chaque fois qu'une modification est teminée:

- dans ce document:
  - ajouter "DONE " en début du titre de la section correspondante (ex: `### 1. [FIL1] Sections de filtres collapsables` devient `### 1. DONE [FIL1] Sections de filtres collapsables`)
  - les sections terminées sont régulièrement effacées de ce document pour ne conserver que les tâches en cours ou à venir
- dans `TODO.md`:
  - cocher la case associée
  - supprimer la tache de la liste des Groupes
  - déplacer la tache au début de la section "Terminés" à la fin du fichier (ex: `### Terminés`)

## Sprints de travail

Règle de pilotage:

- Les corrections ponctuelles et les petits ajustements restent traités en mode patch.
- Toute évolution visible de l'UX, du contrat API, des exports ou des données doit être regroupée dans un sprint.
- A la fin d'un sprint significatif, utiliser `python _helpers/bumpImportantVersion.py --scope minor`.
- Ne pas multiplier les bumps pour les corrections mineures isolées; les regrouper dans le sprint en cours ou en fin de sprint.

### Sprint 1 - DONE [BUG5/PROF1/FEAT4] Stabilisation export et profils

- BUG5: normalisation stricte des textes d'assets, slugs et identifiants pour supprimer les caractères problématiques.
- PROF1: validation de la présence de `column_aliases` sur les profils et couverture par tests.
- FEAT4: filtre des assets invalides côté UI, export interactif et export batch.

### Sprint 2 - DONE [PAG1/PAG2/AFF5/AFF6/AFF7/AFF8/AFF9/AFF10] Refonte progressive de l'interface

- Revoir la pagination et le sélecteur du nombre d'entrees visibles.
- Recomposer les zones `Message`, `Contrôles`, `Données` et `Options`.
- Isoler la recherche, les colonnes à afficher et les options globales.
- Stabiliser la hiérarchie finale de l'UI avant d'ajouter d'autres fonctionnalités.
- Fix: TypeError reading style during column visibility change.

### Sprint 2.1 - DONE [AFF11/AFF12/AFF13] Finition ergonomie et cohérence visuelle

- AFF11: zone colonnes revue avec actions rapides (`Afficher tous`, `Afficher profil`, `Afficher minimum`, `Inverser`).
- AFF12: zone profils compactée sur une seule ligne avec champs réduits et boutons alignés à droite.
- AFF13: design unifié (titres de sous-sections allégés, boutons harmonisés, thème visuel cohérent).

### Sprint 3 - [REF4/REF2/API4/API3] Consolidation technique

- Garder le contrat d'API stable pendant la refonte de l'interface.
- Vérifier les routes, les erreurs uniformes et la documentation technique.
- Limiter les régressions de performance ou d'automatisation.

### Sprint 4 - [DOC1/DOC2/DOC3/CI1/CI2/MIG1/MIG2/MIG3] Alignement documentaire et technique

- Maintenir la documentation, le versioning et les migrations alignés avec le code.
- Garder les scripts d'automatisation compatibles avec les flux de travail actuels.

### Standby - [FEAT2]

- Mettre le scraping Unity Store en attente tant que les sprints ci-dessus ne sont pas stables.

### Standby - [IDEA1]

- Garder le filtrage avancé logique en réserve pour une phase dédiée après stabilisation de l'UX.
