# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.7] - 2026-04-15

### 🔧 Modifié

- AFF1: pouvoir Redimensionner les colonnes (au mieux par drag-and-drop sinon via un menu de configuration de l'affichage)
- AFF2: Popup détail ligne ( manque d'info, qu'est ce que cela signifie ?)
- Extraction et unification du module de logging dans `logging_setup.py`.
- Standardisation des clés de configuration du logging (`log_file`, `log_level`, `log_output`, `log_max_bytes`, `log_backup_count`).
- Support de la clé `log_file` dans le fichier `config.json` pour personnaliser le nom du fichier de log.

## [1.2.6] - 2026-04-15

### 🚀 Ajouté

- Module central d'erreurs API `errors.py` avec `ErrorCode`, `AppError` et construction uniforme des payloads d'erreur.
- Endpoints API4:
  - `GET /api/test` (healthcheck JSON)
  - `GET /api/config` (lecture config runtime publique)
  - `POST /api/config` (mise a jour controlee des parametres autorises)
- Configuration logging runtime dans `config/config.json`:
  - `log_level`, `log_output`, `log_max_bytes`, `log_backup_count`

### 🔧 Modifié

- Migration de `routes.py` vers la couche d'erreurs centralisee (`AppError`) en remplacement de la fonction locale `api_error`.
- `app.py` configure maintenant le logging via `RotatingFileHandler` (console/fichier/both), avec rotation configurable.
- `config.py` conserve les cles existantes lors de `save()` (merge au lieu d'ecrasement complet).
- Alignement documentation/API contract:
  - `openapi.yaml`
  - `API_GUIDE.md`
  - `README.md`
- Renforcement des tests API sur le contrat d'erreur et les endpoints API4.

## [1.2.5] - 2026-04-15

### 🔧 Modifié

- Synchronisation du helper `_helpers/bumpImportantVersion.py` avec le modèle UAM/Fab: configuration locale, scan récursif des balises `Version:` et mise à jour automatique des fichiers tagués.
- Harmonisation des formulations dans `README.md`, `API_GUIDE.md` et `openapi.yaml` pour garder la documentation alignée avec le comportement réel.

## [1.2.4] - 2026-04-15

### 🚀 Ajouté

- Tests API d'erreurs standards pour valider les comportements sur payloads invalides.
- Spécification des routes `/api/templates` et `/api/stats` dans `openapi.yaml`.

### 🔧 Modifié

- Alignement strict de l'implémentation Flask avec la documentation `openapi.yaml`.
- Sécurisation des payload JSON via `request.get_json(silent=True)` pour éviter les réponses HTML d'erreur 400.
- Uniformisation du contrat d'erreur standard (status, message) sur l'ensemble des routes (`api_test_path`, `api_batch_export`).
- Corrections mineures UI (`app.js`) pour la gestion du format des listes de profils.

## [1.2.3] - 2026-04-15

### ✨ Validé / Terminé

- Résolution des chantiers de documentation (DOC1, DOC2, DOC3).
- Fin de la phase de migration (MIG1, MIG2).
- Validation de la nouvelle architecture modulaire.

---

## [1.2.0] - 2026-04-15

### 🚀 Ajouté

- **Modularisation (REF2)** : Découpage du monolithe `app.py` en modules spécialisés :
  - `routes.py` : Endpoints API et Blueprint Flask.
  - `data_manager.py` : Gestion des sources de données (CSV/SQLite).
  - `filters.py` : Moteur de filtrage et tags.
  - `config.py` : Configuration centralisée et templates d'export.
  - `utils.py` : Utilitaires et support JSONC.
- Intégration directe de `jsoncUtils` pour supprimer la dépendance legacy à la V1.
- Support du versioning synchronisé sur les fichiers importants.

### 🔧 Modifié

- Standardisation du contrat d'erreur sur les routes migrées.
- Optimisation de la structure de chargement SQLite.

---

## [1.1.3] - 2026-04-14

### ❌ Retiré

- Suppression du fallback legacy `config.json` (racine) dans le chargement de configuration.

### 🔧 Modifié

- `load_config()` lit désormais uniquement `config/config.json`.

---

## [1.1.2] - 2026-04-14

### ➕ Ajouté

- Fichiers de personnalisation agent projet:
  - `.github/instructions/UnityAssetsManager.instructions.md`
  - `.github/agents/UnityAssetsManager.agent.md`
- Document temporaire de validation REF1: `_helpers/REF1_VALIDATION_TEMP.md`.

### 🔧 Modifié

- Migration de la configuration runtime de `config.json` (racine) vers `config/config.json`.
- Ajout d'une compatibilité de lecture temporaire de l'ancien chemin `config.json` pour transition.
- Externalisation des constantes applicatives de `app.py` vers `app_settings.py`:
  - templates d'export par défaut
  - réglages Flask (`host`, `port`, `debug`, `threaded`, `secret_key`, `max_content_length_mb`)
  - cache TTL et pagination par défaut
- Mise à jour de la documentation et des templates pour refléter le nouveau chemin de configuration.

---

## [1.1.1] - 2026-03-05

### 🐛 Corrigé

- **Détection automatique du séparateur CSV**:
  - Ajout de `sep=None` et `engine='python'` dans `pd.read_csv()`
  - Supporte maintenant automatiquement: `,` `;` `|` `\t`
  - Fix pour fichiers CSV avec séparateur `;` (comme `unity_assets_export.csv`)
  - Détection appliquée dans `load_data()` et `api_test_path()`
  - **HOTFIX**: Suppression de `low_memory=False` (incompatible avec `engine='python'`)

- **DataTables - Erreur "Requested unknown parameter"**:
  - Format de données changé: `to_dict('records')` au lieu de `values.tolist()`
  - Colonnes maintenant définies explicitement avec `columns: [{data: 'col'}]`
  - Sélecteur de colonnes utilise `.visible()` au lieu de filtrage serveur
  - Fix pour l'erreur "Requested unknown parameter '1' for row 0, column 1"

- **Gestion des profils et colonnes**:
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
