# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.19] - 2026-04-21

### 🐛 Fixed

- Export template alias resolution now handles placeholder aliases in a case-insensitive way, fixing empty values when templates use `%URL%` while profiles define aliases like `Url -> AssetLink`.

### ✅ Tests

- Added a non-regression test to ensure `%URL%` resolves correctly through alias maps even when alias and target casings differ.

## [1.2.18] - 2026-04-21

### 🐛 Fixed

- Fixed a bug in the version bump script that was not updating the version in `_helpers/bumpImportantVersion.py`, causing versions to be out of sync between tracked files.

### 🔧 Changed

- AFF4: the table now persists resized column widths in localStorage and restores them on the next application launch.

## [1.2.17] - 2026-04-21

### 🐛 Fixed

- **BUG**: Fixed an issue where the loaded profile's filters were not applied effectively to the data list because the API route was ignoring the `filter_stack` parameter from the frontend.

## [1.2.16] - 2026-04-18

### 🔧 Changed

- Exported Markdown files now receive a H1 title based on the filename before the linting pass.
- Kept the post-export markdown preparation integrated with the existing `--lint_markdown_results` flow.

## [1.2.15] - 2026-04-18

### 🔧 Changed

- Added the `--lint_markdown_results` / `-l` option to `UnityAssetsManagerExportAllProfiles.py`.
- Enabled a post-export markdown lint pass by default on the folders that contain exported files.
- Documented the new lint behavior in `README.md`.

## [1.2.14] - 2026-04-18

### 🔧 Changed

- Documented the INT2 automation workflow in `README.md` with a dedicated section for `UnityAssetsManagerExportAllProfiles.py`.
- Added concrete CLI examples and options reference for full, resume, ranged, and forced batch exports.
- INT2: Finaliser l'export batch pour générer les fichiers de catégories bruts (profils) dans `assetsExports/Unity/`.

## [1.2.13] - 2026-04-17

### 🔧 Changed

- The legacy filter_columns field has been completely removed from the application and profiles.

### ✨ Added

feat: Add script for batch exporting asset profiles using UnityAssetsManager API

## [1.2.12] - 2026-04-17

### 🔧 Changed

- MIG2: Finaliser la dépréciation des flux legacy `assetsCuration/85X_A00_*.json` après migration complète.

## [1.2.11] - 2026-04-16

### ✨ Added

- feat: Enhance application startup logging
- **AFF3**: Integration of the dark theme (matching FabAssetsManager style).

## [1.2.10] - 2026-04-16

### 🔧 Changed

- Standardized source and test imports after moving Python modules to `lib/`.
- Added coverage for integration and export regression paths.
- Aligned technical documentation with the package-based layout.

## [1.2.9] - 2026-04-16

### 🔧 Changed

- Global codebase formatting and uniformization (Python, HTML, CSS, JS).
- Standardized file headers across all project files.
- UI styling and layout improvements.

## [1.2.8] - 2026-04-16

### 🔧 Changed

- Complete translation of documentation to English (README, API_GUIDE, SQLITE_SUPPORT, CHANGELOG, SPEC).
- Project structure overhaul: moved Python modules to `lib/` folder for better organization.
- Technical documentation update: created `_helpers/SPECS.md` (later moved to `.github/SPEC.md`) and updated `README.md` and `API_GUIDE.md`.
- Version synchronization across all documentation files.

## [1.2.7] - 2026-04-15

### 🔧 Changed

- AFF1: ability to Resize columns (ideally by drag-and-drop, otherwise via a display configuration menu).
- AFF2: Row detail popup (missing info, what does it mean?).
- Extraction and unification of the logging module in `logging_setup.py`.
- Standardization of logging configuration keys (`log_file`, `log_level`, `log_output`, `log_max_bytes`, `log_backup_count`).
- Support for the `log_file` key in `config.json` to customize the log file name.

## [1.2.6] - 2026-04-15

### 🚀 Added

- Central API error module `errors.py` with `ErrorCode`, `AppError`, and uniform error payload construction.
- API4 Endpoints:
  - `GET /api/test` (JSON healthcheck)
  - `GET /api/config` (read public runtime config)
  - `POST /api/config` (controlled update of allowed parameters)
- Runtime logging configuration in `config/config.json`:
  - `log_level`, `log_output`, `log_max_bytes`, `log_backup_count`

### 🔧 Changed

- Migration of `routes.py` to the centralized error layer (`AppError`) replacing the local `api_error` function.
- `app.py` now configures logging via `RotatingFileHandler` (console/file/both), with configurable rotation.
- `config.py` preserves existing keys during `save()` (merge instead of complete overwrite).
- Documentation/API contract alignment:
  - `openapi.yaml`
  - `API_GUIDE.md`
  - `README.md`
- Strengthened API tests on the error contract and API4 endpoints.

## [1.2.5] - 2026-04-15

### 🔧 Changed

- Synchronization of the `_helpers/bumpImportantVersion.py` helper with the UAM/Fab model: local configuration, recursive scan for `Version:` tags, and automatic update of tagged files.
- Harmonization of wording in `README.md`, `API_GUIDE.md`, and `openapi.yaml` to keep documentation aligned with actual behavior.

## [1.2.4] - 2026-04-15

### 🚀 Added

- Standard API error tests to validate behavior on invalid payloads.
- Specification of `/api/templates` and `/api/stats` routes in `openapi.yaml`.

### 🔧 Changed

- Strict alignment of Flask implementation with `openapi.yaml` documentation.
- Secured JSON payloads via `request.get_json(silent=True)` to avoid HTML 400 error responses.
- Standardization of the standard error contract (status, message) across all routes (`api_test_path`, `api_batch_export`).
- Minor UI fixes (`app.js`) for profile list format management.

## [1.2.3] - 2026-04-15

### ✨ Validated / Completed

- Resolution of documentation tasks (DOC1, DOC2, DOC3).
- End of migration phase (MIG1, MIG2).
- Validation of the new modular architecture.

---

## [1.2.0] - 2026-04-15

### 🚀 Added

- **Modularization (REF2)**: Splitting the `app.py` monolith into specialized modules:
  - `routes.py`: API Endpoints and Flask Blueprint.
  - `data_manager.py`: Data source management (CSV/SQLite).
  - `filters.py`: Filtering engine and tags.
  - `config.py`: Centralized configuration and export templates.
  - `utils.py`: Utilities and JSONC support.
- Direct integration of `jsoncUtils` to remove legacy dependency on V1.
- Support for synchronized versioning on important files.

### 🔧 Changed

- Standardization of the error contract on migrated routes.
- Optimization of the SQLite loading structure.

---

## [1.1.3] - 2026-04-14

### ❌ Removed

- Removal of legacy `config.json` fallback (root) in configuration loading.

### 🔧 Changed

- `load_config()` now only reads `config/config.json`.

---

## [1.1.2] - 2026-04-14

### ➕ Added

- Project agent customization files:
  - `.github/instructions/UnityAssetsManager.instructions.md`
  - `.github/agents/UnityAssetsManager.agent.md`
- Temporary validation document REF1: `_helpers/REF1_VALIDATION_TEMP.md`.

### 🔧 Changed

- Migration of runtime configuration from `config.json` (root) to `config/config.json`.
- Added temporary read compatibility for the old `config.json` path for transition.
- Externalization of application constants from `app.py` to `app_settings.py`:
  - default export templates
  - Flask settings (`host`, `port`, `debug`, `threaded`, `secret_key`, `max_content_length_mb`)
  - default cache TTL and pagination
- Documentation and templates updated to reflect the new configuration path.

---

## [1.1.1] - 2026-03-05

### 🐛 Fixed

- **Automatic CSV separator detection**:
  - Added `sep=None` and `engine='python'` in `pd.read_csv()`
  - Now automatically supports: `,` `;` `|` `\t`
  - Fix for CSV files with `;` separator (like `unity_assets_export.csv`)
  - Detection applied in `load_data()` and `api_test_path()`
  - **HOTFIX**: Removed `low_memory=False` (incompatible with `engine='python'`)

- **DataTables - "Requested unknown parameter" error**:
  - Data format changed: `to_dict('records')` instead of `values.tolist()`
  - Columns now explicitly defined with `columns: [{data: 'col'}]`
  - Column selector uses `.visible()` instead of server filtering
  - Fix for "Requested unknown parameter '1' for row 0, column 1" error

- **Profile and column management**:
  - Profils chargés dynamiquement via AJAX (liste plus vide)
  - Sauvegarde du choix de colonne affichée dans les profils
  - Suppression de profil maintenant implémentée (DELETE `/api/profiles/<name>`)
  - Largeur minimale des colonnes (MIN_COL_WIDTH = 150px)
  - Scrollbar horizontale automatique quand table est plus large que l'écran

### 🔧 Modifié

- Logs améliorés: "séparateur auto-détecté" pour plus de clarté
- `/api/test-path` utilise aussi la détection automatique
- Colonnes avec `min-width: 150px` et `white-space: nowrap`
- Modal profil charge la liste à partir de la donnée

---

## [1.1.0] - 2026-03-05

### ➕ Ajouté (SQLite Support)

- **Support SQLite** comme source de données alternative au CSV
  - Détection automatique du format (`.db`, `.sqlite`, `.sqlite3`)
  - Sélection de table via interface `/setup`
  - Configuration persistante (table name sauvegardée dans `config.json`)
  - API `/api/test-path` retourne maintenant la liste des tables SQLite
  - Chargement optimisé avec pandas `read_sql_query()`

- **Nouvelles méthodes AssetDataManager**:
  - `detect_source_type(path)`: Détecte si CSV ou SQLite
  - `list_sqlite_tables(db_path)`: Liste les tables dans une base SQLite

- **UI améliorée** (`/setup`):
  - Sélecteur de table SQLite (apparaît dynamiquement)
  - Info sur le type de source détecté (CSV ou SQLite)
  - Support pour `.csv` et `.db` dans le même formulaire

### 🔧 Modifié

- **`load_data()`**: Refactorée pour supporter CSV et SQLite
  - Branche conditionnelle selon le type de source
  - Logs améliorés (affiche type + table si SQLite)

- **Configuration globale**:
  - Ajout variable `DB_TABLE` (table par défaut: `'assets'`)
  - Chargée depuis `config.json` si présente

- **API `/api/setup`**:
  - Accepte maintenant paramètre `db_table` (optionnel)
  - Sauvegarde table SQLite dans configuration

- **API `/api/test-path`**:
  - Retourne `type: 'csv'` ou `type: 'sqlite'`
  - Pour SQLite: retourne aussi `tables: [...]` (liste des tables)

### 📚 Documentation

- Nouveau fichier `SQLITE_SUPPORT.md` avec guide complet
- Mise à jour `README.md` (SQLite marqué comme supporté)
- Exemples de migration CSV → SQLite

### 🎯 Performance

- SQLite légèrement plus rapide que CSV pour datasets > 5000 lignes
- Cache identique (1h TTL) pour les deux formats
- Exports supportent les deux formats sans changement

---

## [1.0.0] - 2026-03-05

### ➕ Initial Release

- **Remplacement de Streamlit V1** par Flask
  - Performance 8-10x plus rapide (200-400ms vs 2-5s)
  - Pagination côté serveur (DataTables.js)
  - Filtrage côté serveur

- **Fonctionnalités principales**:
  - Affichage table 3800+ assets
  - Recherche full-text en temps réel
  - Sélection dynamique de colonnes
  - Exports multiples formats (CSV, JSON, Markdown)
  - Profils persistants (sauvegarder config colonnes)
  - Templates d'export configurables

- **Interface web**:
  - Bootstrap 5 (responsive)
  - DataTables.js pour pagination fluide
  - AJAX pour opérations asynchrones
  - Page de configuration `/setup`

- **Architecture**:
  - Cache DataFrame (1h TTL)
  - Gestion robuste des erreurs CSV
  - Support encodages multiples (UTF-8, latin-1)
  - Mode permissif (`on_bad_lines='skip'`)

- **API REST**:
  - `/api/data`: Données paginées/filtrées
  - `/api/columns`: Liste colonnes
  - `/api/stats`: Statistiques
  - `/api/export`: Export avec filtres appliqués
  - `/api/profiles`: Gestion profils
  - `/api/reload`: Rechargement données
  - `/api/setup`: Configuration chemin source
  - `/api/test-path`: Test validité fichier

- **Documentation**:
  - `README.md`: Documentation complète
  - `QUICKSTART.md`: Guide démarrage rapide
  - `SETUP_CHECKLIST.md`: Checklist installation

---

## Format du Changelog

Ce changelog suit le format [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

### Types de changements

- `➕ Ajouté` pour nouvelles fonctionnalités
- `🔧 Modifié` pour changements dans fonctionnalités existantes
- `⚠️ Déprécié` pour fonctionnalités à retirer prochainement
- `❌ Retiré` pour fonctionnalités retirées
- `🐛 Corrigé` pour corrections de bugs
- `🔒 Sécurité` pour vulnérabilités corrigées
