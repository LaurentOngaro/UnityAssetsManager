# PLAN D'ACTIONS

Ce document détaille (et décrits les étapes d'implémentation) de certaines des taches présentes dans le fichier `TODO.md`.
Un regroupement par Sprints peut être envisagé dans ce document, selon le nombre de tâches à implémenter.
La priorisation des tâches est définie dans `TODO.md` et doit être respectée pour éviter de se disperser sur des points moins urgents.

## Contexte et Lignes Directrices (Héritées du plan de migration)

- **Séparation des rôles** : Garder une séparation claire entre l'outil applicatif (`UnityAssetsManager`) et le pipeline de curation (`_Helpers/04_Assets/AssetsCuration/`).
- **Nomenclature** : Le nom officiel est `UnityAssetsManager`. Toute ancienne référence (AssetManagerV2, AssetsManagerV2) est dépréciée.

**REGLE D'OR : Toujours proposer d'effectuer les corrections de bugs et les corrections immédiates en premier. Elles sont listées dans les section "Corrections immédiates" et "Bugs" du fichier `TODO.md`.**

Chaque fois qu'une modification est teminée:

- dans ce document:
  - ajouter "DONE " en début du titre de la section correspondante (ex: `### 1. [FIL1] Sections de filtres collapsables` devient `### 1. DONE [FIL1] Sections de filtres collapsables`)
  - les sections terminées sont régulièrement effacées de ce document pour ne conserver que les tâches en cours ou à venir
- dans `TODO.md`:
  - cocher la case associée
  - supprimer la tache de la liste des Groupes
  - déplacer la tache au début de la section "Terminés" à la fin du fichier (ex: `### Terminés`)

## TOP Priorités (pour les corrections immédiates)

### Gestion

### Refactoring

### API

### Documentation

### Affichage

### Features

- [ ] FEAT2:  faire du scrapping direct depuis le unity store
  - ne plus dépendre de l'export CSV ou de la base de donnée SQL de "Assets inventory"
  - reprendre la logique de FAM (cad se baser sur un equivalent de `fetch_fab_library.py`) pour contacter le store Unity
  - voir si le countournement de Cloudflare est nécessaire sur le store Unity
  - récupérer les données à la volée et gérer avec un cache local pour limiter les appels répétitifs

### Migration

 MIG3: archiver V1 (`AssetsManager/assetManager.py`) après validation de la chaîne complète V2.

- l'équivalence des fonctionnalités a été validée par IA, il rester à tester la chaîne complète de bout en bout pour valider la bascule.
- ne fermer V1 qu'une fois la chaîne V2 validée de bout en bout.

### Intégration future

- INT1: intégrer le moteur `buildStoreRawNormalized` comme service dans UnityAssetsManager.
  - préparer l'assemblage raw multi-boutiques dans le projet.
- INT2: ajouter un provider Unity (SQLite prioritaire, CSV fallback) pour produire `raw_assets_normalized.json`.
  - prioriser la source locale Unity et conserver un fallback CSV.
- INT3: ajouter un provider Fab à partir des exports/cache consolidés.
  - réutiliser le dépôt Fab comme source sans le rapatrier.
- INT4: ajouter un provider boutiques manuelles via `raw_assets.md`.
  - permettre une saisie manuelle ponctuelle hors flux automatisé.
