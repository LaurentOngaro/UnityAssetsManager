# PLAN_ACTIONS - UnityAssetsManager

## Objectif

Converger vers une structure et un contrat API de niveau FabAssetsManager, tout en restant oriente Unity/TerraBloom et pipeline raw-first.

## Sprint P0 - Stabilisation

- Action: Verifier nomenclature `UnityAssetsManager` dans le code actif.
- Action: Verifier que les routes critiques renvoient un contrat d'erreur uniforme.
- Livrable: rapport de recherche + correction des references actives legacy.
- Definition of done: aucune reference active legacy dans le scope applicatif (hors docs historiques de migration).

## Sprint P1 - Modularisation & Optimisation (Alignement FabAssetsManager)

- Action: Découper le monolithe `app.py` en modules séparés (routes, data_manager, config, filters).
- Action: Supprimer la dépendance legacy à la V1 (`lib.jsoncUtils`) en migrant les utilitaires.
- Action: Optimiser le chargement SQLite (éviter le `SELECT *` total dans la RAM).
- Livrable: Code refactorisé, robuste et plus maintenable, détaillé dans `REFACTORING_MODULARIZATION.md`.
- Definition of done: Les tests, l'interface et l'API fonctionnent à l'identique avec la nouvelle architecture.

## Sprint P2 - Contrat API

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

## Sprint P3 - Raw-First Providers

- Action: Integrer service de normalisation raw multi-boutiques.
- Action: Prioriser provider Unity (SQLite, fallback CSV).
- Action: Ajouter provider Fab depuis exports/cache consolides.
- Action: Ajouter providers stores manuels (`raw_assets.md`).
- Definition of done: generation pilotable de `raw_assets_normalized.json` pour Unity + Fab + stores manuels.

## Sprint P4 - Parite V1 restante

- Action: Ajouter endpoint `/api/batch-export`.
- Action: Ajouter include/exclude dans filter builder.
- Action: Ajouter tests API associes.
- Definition of done: use-cases automation V1 couverts par V2.

## Sprint P5 - Validation finale

- Action: rejouer pipeline complet (Unity + Fab minimum).
- Action: valider exports et docs de bascule.
- Action: preparer deprecation/archivage V1 selon preconditions projet.
- Definition of done: migration V2 operationnelle, documentee, et exploitable en routine.
