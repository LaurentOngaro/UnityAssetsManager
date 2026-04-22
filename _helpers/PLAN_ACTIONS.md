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

### Sprint 5 - [BUG6/PERF1/PERF2/PERF3/SEC1] Optimisations & Robustesse

Suite à une analyse complète du code (Frontend/Backend/Data), voici des propositions d'améliorations techniques et corrections :

- **BUG6** : Corriger la redirection silencieusement bloquée dans `templates/setup.html` (vérification de `response.status === 'success'`).
- **SEC1** : Sécuriser la route `/api/test-path` pour éviter les accès arbitraires (Path Traversal) sur la machine hôte.
- **PERF1** : Remplacer l'itération ligne par ligne de la recherche globale (`apply(axis=1)`) par une approche vectorisée (ex: `np.column_stack`) pour de meilleures performances sur les grands datasets.
- **PERF2** : Implémenter le filtrage SQL natif pour la source SQLite (éviter le chargement complet de la table en mémoire).
- **PERF3** : Sécuriser les accès concurrents au cache de `AssetDataManager` via un `threading.Lock()` (Flask fonctionnant en mode multi-threadé).

### Standby - [FEAT2]

- Mettre le scraping Unity Store en attente tant que les sprints ci-dessus ne sont pas stables.

### Standby - [IDEA1]

- Garder le filtrage avancé logique en réserve pour une phase dédiée après stabilisation de l'UX.
