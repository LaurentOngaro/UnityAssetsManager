# Changelog

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
