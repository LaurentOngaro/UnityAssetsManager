# PLAN_ACTIONS - UnityAssetsManager

Ce document ordonne et détaille les étapes d'implémentation selon les Groupes définies dans le fichier `TODO.md`.

**REGLE D'OR : Toujours proposer d'effectuer les corrections de bugs et les corrections immédiates en premier. Elles sont listées dans les section "Corrections immédiates" et "Bugs" du fichier `TODO.md`.**

Chaque fois qu'une modification est teminée:

- dans ce document:
  - ajouter "DONE " en début du titre de la section correspondante (ex: `### 1. [FIL1] Sections de filtres collapsables` devient `### 1. DONE [FIL1] Sections de filtres collapsables`)
  - les sections terminées sont régulièrement effacées de ce document pour ne conserver que les tâches en cours ou à venir
- dans `TODO.md`:
  - cocher la case associée
  - supprimer la tache de la liste des Groupes
  - déplacer la tache au début de la section "Terminés" à la fin du fichier (ex: `### Terminés`)

## Rattachement rapide des sprints aux TODO

- Sprint P2 - API1, API2, API3, DOC1, DOC2, DOC3
- Sprint P3 - MIG2, MIG3
- Sprint P4 - FEAT1, AFF1, AFF2
- Sprint P5 - INT1, INT2, INT3, INT4

## TOP Priorités (pour les corrections immédiates)

### Gestion

### Refactoring

### Contrat API

- API1: vérifier la cohérence entre l'implémentation Flask et `openapi.yaml`.
  - s'assurer que chaque route décrite est présente et que ses paramètres sont alignés.
  - éviter les divergences entre documentation et code.
- API2: ajouter des tests API pour les cas d'erreurs standards.
  - couvrir payload invalide, profil absent, setup invalide et autres erreurs attendues.
  - verrouiller le contrat de réponse d'erreur.
- API3: finaliser le contrat d'erreur uniforme sur toutes les routes.
  - standardiser `error.code`, `error.message`, `error.http_status`, `error.timestamp`, `error.path`, `error.details`.
  - réutiliser la logique déjà stabilisée côté `FabAssetsManager`.

### Documentation

- DOC1: analyser puis fusionner ou prioriser les docs de migration et de suivi.
  - éviter la duplication entre `MIGRATION STATE V1 to V2`, `plan_action_UnityAssetsManager` et `PLAN_ACTIONS`.
  - documents liés: [MIGRATION STATE V1 to V2 .md](MIGRATION%20STATE%20V1%20to%20V2%20.md), [plan_action_UnityAssetsManager.md](plan_action_UnityAssetsManager.md), PLAN_ACTIONS.md.
- DOC2: consolider `README.md`, `API_GUIDE.md` et les docs techniques.
  - réserver chaque doc à son rôle principal.
  - déplacer les détails d'exécution dans le bon fichier.
  - documents liés: [README.md](../README.md), [API_GUIDE.md](../API_GUIDE.md).
- DOC3: garder `SQLITE_SUPPORT.md` orienté setup SQLite uniquement.
  - limiter ce fichier au support d'installation et de configuration SQLite.
  - document lié: [SQLITE_SUPPORT.md](SQLITE_SUPPORT.md).

### Affichage

- AFF1: pouvoir redimensionner les colonnes.
  - prioriser le drag-and-drop ou un menu de configuration si nécessaire.
- AFF2: popup détail ligne.
  - clarifier le contenu attendu et le périmètre de ce panneau.

### Features

- FEAT1: traiter `MIGRATION STATE V1 to V2 .md` comme backlog de parité V1 restant.
  - convertir le document de migration en liste de fonctionnalités à reprendre.
  - document source: [MIGRATION STATE V1 to V2 .md](MIGRATION%20STATE%20V1%20to%20V2%20.md).

### Migration

- MIG2: finaliser la dépréciation des flux legacy `assetsCuration/85X_A00_*.json`.
  - ne conserver ces flux que tant que la migration n'est pas complètement terminée.
- MIG3: archiver V1 (`AssetsManager/assetManager.py`) après validation de la chaîne complète V2.
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

## Regroupement des taches par Sprints

cete répartition est indicative et peut être ajustée en fonction des dépendances et de l'avancement.
Elle n'est pas un classement par priorité mais plutôt une organisation thématique pour structurer les sprints.

### Sprint P2 - Contrat API & Documentation (API1, API2, API3, DOC1, DOC2, DOC3)

- Action: Maintenir `openapi.yaml` en source de verite des endpoints.
- Action: Ajouter exemples de payloads succes/erreur dans `API_GUIDE.md`.
- Action: Verifier les routes:
  - `GET /api/data`
  - `GET /api/columns`
  - `GET /api/profiles`
  - `GET /api/profiles/{name}`
  - `DELETE /api/profiles/{name}`
  - `POST /api/profiles`
  - `POST /api/export`
  - `POST /api/reload`
  - `POST /api/setup`
  - `POST /api/test-path`
- Definition of done: alignement implementation/API_GUIDE/OpenAPI sans divergence fonctionnelle.

### Sprint P4 - Parite V1 restante (FEAT1, AFF1, AFF2)

- Action: Ajouter endpoint `/api/batch-export`.
- Action: Ajouter include/exclude dans filter builder.
- Action: Ajouter tests API associes.
- Definition of done: use-cases automation V1 couverts par V2.

### Sprint P3 - Validation finale (MIG2, MIG3)

- Action: rejouer pipeline complet (Unity + Fab minimum).
- Action: valider exports et docs de bascule.
- Action: preparer deprecation/archivage V1 selon preconditions projet.
- Definition of done: migration V2 operationnelle, documentee, et exploitable en routine.

### Sprint P5 - Raw-First Providers (INT1, INT2, INT3, INT4)

- Action: Integrer service de normalisation raw multi-boutiques.
- Action: Prioriser provider Unity (SQLite, fallback CSV).
- Action: Ajouter provider Fab depuis exports/cache consolides.
- Action: Ajouter providers stores manuels (`raw_assets.md`).
- Definition of done: generation pilotable de `raw_assets_normalized.json` pour Unity + Fab + stores manuels.
