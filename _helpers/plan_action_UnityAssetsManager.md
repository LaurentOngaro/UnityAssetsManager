# Plan d'action - UnityAssetsManager

Ce document definit le plan de migration de l'application actuelle vers une version alignee sur FabAssetsManager (structure, documentation, contrat API), tout en conservant les besoins metier Unity/TerraBloom.

## Regles directrices

- Conserver le document `MIGRATION STATE V1 to V2 .md` comme source de suivi des features V1 non implementees en V2.
- Ne pas supprimer une documentation sans avoir cree son equivalent consolide.
- Prioriser la clarte du contrat API et la coherence de structure entre FabAssetsManager et UnityAssetsManager.
- Garder une separation claire entre:
  - application UnityAssetsManager (outil applicatif)
  - pipeline de curation (`_Helpers/04_Assets/AssetsCuration/`)

## Source d'inspiration (FabAssetsManager)

- `TODO.md`: priorisation par blocs fonctionnels et statut explicite.
- `_helpers/PLAN_ACTIONS.md`: decomposition en actions executables, avec objectifs et criteres de fin.
- `API_GUIDE.md` + `openapi.yaml`: contrat API clair, endpoints documentes, erreurs standardisees.

## Objectif cible

Faire converger UnityAssetsManager vers un modele "Fab-like" sans perdre les specificites Unity:

1. Structure de dossier explicite et stable.
2. Contrat API formalise (OpenAPI + guide integration).
3. Documentation exploitable par humain et par IA.
4. Roadmap de migration lisible et actionnable.

## Cadrage nomenclature

- Nom officiel: `UnityAssetsManager`.
- Toute nouvelle reference doit utiliser `UnityAssetsManager`.
- Les anciens noms `AssetManagerV2` et `AssetsManagerV2` sont consideres deprecated.

## Plan de migration par phases

## Phase 0 - Baseline et gel de nomenclature

### P0.1

- Verifier qu'il n'existe plus de references actives `AssetManagerV2`/`AssetsManagerV2`.
- Criteres de fin:
  - recherche globale a zero sur nomenclature legacy (hors historique/archives explicites).

### P0.2

- Verrouiller la convention de nommage dans les docs de pilotage.
- Criteres de fin:
  - dashboard migration et docs setup alignes sur `UnityAssetsManager`.

## Phase 1 - Alignement structure fichiers/dossiers

### P1.1 - Structure applicative cible

Converger vers une structure proche de FabAssetsManager:

- `app.py`
- `config/`
- `assets/` (si cache local applicatif necessaire)
- `static/`
- `templates/`
- `tests/`
- `_helpers/`
- `README.md`
- `TODO.md`
- `API_GUIDE.md`
- `openapi.yaml`
- `CHANGELOG.md`

### P1.2 - Cartographie ecarts

- Produire un tableau "Actuel vs Cible" dans ce plan ou un fichier dedie.
- Criteres de fin:
  - chaque ecart est associe a une action (creer, deplacer, fusionner, supprimer).

## Phase 2 - Contrat API et standardisation erreurs

### P2.1 - OpenAPI

- Creer/mettre a jour `openapi.yaml` pour UnityAssetsManager.
- Criteres de fin:
  - endpoints principaux documentes (data, exports, profils, reload, setup SQLite).

### P2.2 - Guide integration

- Creer `API_GUIDE.md` calque sur FabAssetsManager:
  - quick start
  - workflows cle
  - erreurs standardisees
  - exemples Python.
- Criteres de fin:
  - un consommateur externe peut integrer l'API sans lire le code.

### P2.3 - Contrat d'erreur

- Uniformiser les erreurs API (code/message/http_status/timestamp/details).
- Criteres de fin:
  - erreurs homogenes sur routes critiques.

## Phase 3 - Documentation: produire, fusionner, supprimer

### P3.1 - Docs a produire

- `API_GUIDE.md` (nouveau ou refonte).
- `openapi.yaml` (nouveau ou refonte).
- `TODO.md` (format actionnable par groupe + priorites).
- `_helpers/PLAN_ACTIONS.md` (plan detaille execution, style FabAssetsManager).

### P3.2 - Docs a conserver

- `MIGRATION STATE V1 to V2 .md` (obligatoire, source backlog V1->V2).
- `README.md` (entrypoint utilisateur).
- `SQLITE_SUPPORT.md` (reference technique specifique Unity).

### P3.3 - Docs a synthetiser/fusionner

- Fusionner les redondances entre README, migration state, setup notes.
- Garder:
  - README = vue produit + lancement + liens
  - MIGRATION STATE = historique et backlog migration
  - PLAN_ACTIONS = execution court terme
  - TODO = backlog priorise

### P3.4 - Docs a deprecier/supprimer

- Supprimer ou archiver les docs obsoletes uniquement apres creation de leur remplaçant.
- Criteres de fin:
  - aucun doublon contradictoire sur API, structure, ou mode de lancement.

## Phase 4 - Harmonisation avec le pipeline TerraBloom

### P4.1 - Entree/sortie

- Documenter explicitement les formats d'entree supportes (CSV/SQLite) et sorties (CSV/JSON/Markdown via templates).
- Definir le point de jonction avec la generation `raw_assets_normalized.json`.

### P4.2 - Compatibilite scripts curation

- Verifier la compatibilite avec:
  - `assetManagerExportAllProfiles.py`
  - scripts `AssetsCuration/*`
  - docs process 337 et audit pipeline.

## Phase 5 - Validation et qualite

### P5.1 - Verifications techniques

- Tests/app checks de UnityAssetsManager.
- Verification des routes API critiques.
- Verification des exports generes.

### P5.2 - Verifications documentaires

- Validation frontmatter sur les docs touchees dans `Notes/`.
- Regeneration index Obsidian si des docs `Notes/` sont modifiees.

## Backlog d'execution (format court)

- [x] UAM1: Finaliser nomenclature globale `UnityAssetsManager`.
- [x] UAM2: Produire `TODO.md` structure type FabAssetsManager.
- [x] UAM3: Produire `_helpers/PLAN_ACTIONS.md` type FabAssetsManager.
- [x] UAM4: Produire/mettre a jour `openapi.yaml`.
- [x] UAM5: Produire/mettre a jour `API_GUIDE.md`.
- [x] UAM6: Standardiser erreurs API (contrat unique).
- [ ] UAM7: Nettoyer/synthesiser documentation redondante.
- [ ] UAM8: Valider integration avec pipeline curation TerraBloom.

## Criteres de definition of done

- Nomenclature unifiee (`UnityAssetsManager`) dans le repo actif.
- Contrat API documente (OpenAPI + guide).
- Documentation rationalisee sans doublon contradictoire.
- `MIGRATION STATE V1 to V2 .md` conserve et utilise comme backlog V1 restant.
- Plan actionnable disponible pour execution iterative.
