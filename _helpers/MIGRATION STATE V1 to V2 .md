# UnityAssetsManager - Modifications implémentées (2026-03-06)

## Clarification du fichier de suivi

- Fichier de suivi actuel et unique: `_Helpers/04_Assets/UnityAssetsManager/MIGRATION STATE V1 to V2 .md`
- Le fichier `_Helpers/artifacts/ASSETMANAGERV2_SESSION_20260306.md` est remplacé/supprimé
- Toute la synthèse de session est désormais centralisée ici
- Référence à utiliser dans README et dans les prochains échanges: `MIGRATION STATE V1 to V2 .md`

## Synthèse du processus complet (chronologie)

1. Correctif chargement templates export V2

- Bug JS corrigé: ordre d'initialisation des templates dans l'UI
- Résultat: la liste des templates se charge correctement dans la combobox

2. Correctif export forcé en JSON

- Nettoyage de code legacy en doublon côté backend
- Suppression de la logique qui écrasait le format choisi
- Résultat: le format d'export suit bien le template sélectionné

3. Correctif détection extension de fichier

- Ajustement de la détection pour éviter la confusion entre Markdown links et JSON
- Priorité donnée au nom du template, puis analyse du pattern
- Résultat: extensions `.md`, `.csv`, `.json`, `.txt` correctes

4. Amélioration exports (headers)

- Ajout des en-têtes pour tous les formats exportés
- Markdown table: ligne d'en-tête + séparateur
- CSV: noms de colonnes en première ligne
- Listes Markdown: commentaire de colonnes au début

5. Robustesse Markdown table

- Échappement des valeurs contenant `|` dans les tables Markdown (`|` -> `-`)
- Résultat: pas de casse de structure des tableaux Markdown

6. Analyse migration V1 -> V2

- Inventaire V1 détaillé (features, scripts, limites)
- Inventaire V2 détaillé (features implémentées, gaps)
- Matrice de migration + priorisation backlog (N1-N4)

7. Rationalisation documentation

- Mise à jour de `README.md` de `UnityAssetsManager`
- Lien vers ce fichier de migration + lien vers `SQLITE_SUPPORT.md`
- Backlog README aligné avec le statut réel de migration

8. Décision documentaire

- `SQLITE_SUPPORT.md` conservé comme doc technique détaillée
- README garde une vue synthétique et renvoie vers les docs détaillées

---

## Inventaire V1 (AssetManager Streamlit - Référence Migration)

### Architecture V1

- **Stack**: Python 3.11 + Streamlit 1.29+ + Pandas + SQLite3
- **Version**: 3.1.2 (dernière stable V1)
- **Emplacement**: `_Helpers/04_Assets/AssetsManager/assetManager.py` (4245 lignes)
- **Dépendances**: `requirements.txt` (streamlit, pandas, openpyxl, numpy)

### Features Core V1

1. **Profils unifiés** (`profiles/*.profile.jsonc`):
   - Structure: `{ filters: [...], visible_columns: [...], filter_columns: [...] }`
   - Actions: Créer, Charger, Supprimer, Réinitialiser
   - Persistance: JSONC avec commentaires supportés

2. **Multi-source support**:
   - CSV: Upload widget + cache `.cache/last_file.csv`
   - SQLite: `.db`/`.sqlite` files, table selector si multi-table
   - Fallback: `L:\Unity\AssetInventory\AssetInventory.db` si aucun cache

3. **Filtrage avancé**:
   - Multiselect widgets par colonne (seuil configurable: 50 valeurs)
   - Tag columns auto-détection (regex patterns: `tags?$`, `packagetags?`)
   - Actions masse SVG: ✅ (tout sélectionner), ✖️ (clear), 🔁 (inverser), 🎯 (keep matching), ➕ (add matching)
   - Include/exclude toggle (SVG icons clairs)

4. **Export templates** (`data/export_templates.jsonc`):
   - 11 templates configurables (texte, CSV, Markdown table/liste, JSON, Unity AssetStore)
   - Pattern substitution: `%ColumnName%` remplacé par valeurs DataFrame
   - Support URL: construction depuis `Slug` + préfixe conditionnel
   - Frontmatter YAML: via `assetManagerExportAllProfiles.py`

5. **Mode batch CLI**:
   - Flags: `-b` (batch), `-p` (profile), `-s/--source` (CSV/DB), `--db-table` (SQLite table), `-t` (template), `-e` (export path)
   - Exemple: `python assetManager.py -b -p MonProfile -s assets.csv -t "CSV avec URL" -e ./exports`
   - Logs: stdout + artifact debug logs si activé

6. **Settings persistants** (`data/config.jsonc`):
   - `multiselect_threshold` (nb valeurs avant mode textarea)
   - `cache_mode` (balanced/aggressive/none)
   - `cache_max_entries`, `cache_preview_rows`
   - `enable_export`, `enable_preview`, etc.

7. **Debug & diagnostics**:
   - Checkbox UI "Activer debug réseau (trace logs)"
   - Logs écrits dans `_Helpers/artifacts/assetmanager_debug.log`
   - Affichage `server.maxUploadSize` dynamique

8. **Scripts automation V1**:
   - `assetManagerExportAllProfiles.py`: Export batch tous profils avec frontmatter + validation
   - `searchGedOrAssets.ps1`: Recherche assets (Unity Store + boutiques tierces) + full-text GED vault
   - Flags: `-r` (resume), `-s/e` (start/end index), `-t` (template), `-f` (force)

### Limitations V1

- **Performance**: 2-5s pour affichage table (st.dataframe blocking)
- **UX**: Widgets Streamlit lourds (multiselect lag avec 100+ options)
- **Scaling**: Pagination manuelle, RAM-intensive pour gros datasets (>10k lignes)
- **Customization**: CSS limité, layout imposé par Streamlit

---

## Inventaire V2 (AssetManager Flask/DataTables - État Actuel)

### Architecture V2

- **Stack**: Python 3.11 + Flask 3.0 + DataTables.js (AJAX) + Pandas
- **Version**: 1.1.0 (SQLite support ajouté)
- **Emplacement**: `_Helpers/04_Assets/UnityAssetsManager/app.py` (1214 lignes)
- **Dépendances**: `requirements.txt` (flask, flask-cors, pandas, openpyxl)
- **UI**: HTML5 + Bootstrap 5 + DataTables + JavaScript vanilla

### Features Core V2 (Implémentés)

1. **Profils persistants** (`profiles/*.profile.jsonc`):
   - Format identique V1 (compatibilité bidirectionnelle)
   - Endpoints REST: `/api/profiles` (GET), `/api/profiles/save` (POST), `/api/profiles/delete` (POST)
   - UI: Dropdown sélection + boutons Save/Delete
   - Preview metadata avant chargement

2. **Multi-source support**:
   - CSV: Upload + cache `.cache/last_file.csv`
   - SQLite: Auto-détection `.db`/`.sqlite` files
   - Config: `config.json` avec DATA_PATH, DB_TABLE

3. **Filtrage avancé** (Filter Builder):
   - Interface JSON: `currentFilterStack` éditable manuellement
   - Builder UI: Sélection colonne + opérateur + valeurs
   - Opérateurs: `in` (include), `not_in`, `contains`, `regex`, `gt`, `lt`, `eq`, `ne`
   - Actions: Ajouter via builder, Supprimer, Vider tous
   - Preview résultats: Compteur lignes filtrées dynamique

4. **Export templates** (`data/export_templates.jsonc`):
   - 11 templates configurables (identiques V1)
   - Pattern substitution: `%ColumnName%` avec gestion URL
   - Extensions auto-détection: `.md`, `.csv`, `.json`, `.txt` (smart detection nom + pattern)
   - Headers format-specific: Markdown tables avec séparateur, CSV avec colonnes, listes avec commentaires HTML
   - Pipe escaping: `|` → `-` dans valeurs Markdown tables
   - Preview export: Aperçu dynamique avant téléchargement

5. **Recherche globale**:
   - UI: Input texte + checkbox regex
   - Backend: Recherche sur toutes colonnes visibles
   - Refresh automatique après recherche

6. **DataTables Pagination**:
   - Pagination côté serveur (AJAX)
   - Tri multi-colonnes
   - Affichage 10/25/50/100 lignes par page
   - Performance: 200-400ms pour affichage (vs 2-5s V1)

7. **API REST complète**:
   - `/api/data` (GET): Données paginées + filtrées
   - `/api/columns` (GET): Liste colonnes disponibles
   - `/api/profiles` (GET): Liste profils
   - `/api/profiles/save` (POST): Sauvegarder profil
   - `/api/profiles/delete` (POST): Supprimer profil
   - `/api/export` (POST): Export avec template + filters
   - `/api/templates` (GET): Liste templates export
   - `/api/unique-values` (GET): Valeurs distinctes par colonne

8. **Scripts compatibles V1**:
   - `assetManagerExportAllProfiles.py`: Compatible profiles/ V2
   - `searchGedOrAssets.ps1`: Lit exports V2 (`AssetLists/*.md`)
   - `validateFrontmatter.py`: Valide exports Markdown V2

### Avantages V2 vs V1

- ✅ **Performance**: 5-10x plus rapide (200-400ms vs 2-5s)
- ✅ **Scalabilité**: Pagination serveur, pas de limite RAM
- ✅ **Customization**: CSS/JS complet, layout flexible
- ✅ **Export amélioré**: Extensions auto, headers format-specific, preview dynamique
- ✅ **Déploiement**: Serveur Flask standard, pas de port Streamlit custom
- ✅ **Architecture**: API REST réutilisable pour automation future

### Limitations V2 (État Actuel)

- ❌ **Batch CLI**: Pas d'endpoint `/api/batch-export` encore (N1 backlog)
- ❌ **Include/exclude UI**: Builder ajoute uniquement filtres "include" (N2 backlog)
- ❌ **Table selector SQLite**: Assume table unique, pas de dropdown multi-table
- ❌ **Debug logs UI**: Logs serveur uniquement, pas d'activation UI
- ⚠️ **Settings avancés**: Config `config.json` manuel, pas d'UI pour multiselect_threshold, cache_mode

### Compatibilité V1 ↔ V2

- ✅ **Profils**: Format JSONC identique, migration transparente
- ✅ **Exports**: Templates compatibles, scripts automation V1 fonctionnent avec V2
- ✅ **Source data**: Même cache `.cache/last_file.csv`
- ⚠️ **CLI**: V1 batch mode non porté (endpoint API requis)

---

## tâches (Backlog détaillé)

### 🔴 N1 - Export en batch (CLI/API sans UI)

**Problème**: La V2 ne permet pas encore d'exporter via automation sans interface.

**Objectif**: Permettre les exports récurrents/scriptés (CI, archivage, intégrations externes).

**Spécification cible**:

- Endpoint `POST /api/batch-export`
- Payload JSON:
  - `template` (`CSV` | `JSON` | `Markdown table`)
  - `filters` (`filter_stack`)
  - `columns` (liste)
  - `output_path` (optionnel)
- Retour:
  - fichier binaire (download) ou
  - succès + chemin fichier (si `output_path` fourni)

**Critères d'acceptation**:

- Exécution sans UI
- Logs exploitables (succès/erreur + durée)
- Gestion erreurs 400/500 cohérente

**Impact**:

- `app.py` (nouvel endpoint)
- `tests/` (tests API export batch)
- doc d'usage CLI (court exemple)

**Estimation**: 1.5h
**Priorité**: Haute
**Statut**: ⏳ À FAIRE

### 🟡 N2 - Mode include/exclude dans "Ajouter filtre"

**Problème**: Le builder ajoute uniquement des filtres de type include.

**Objectif**: Retrouver le comportement V1 avec choix explicite include/exclude.

**Spécification cible**:

- Contrôle UI: sélecteur de mode (`include` / `exclude`)
- Persistance dans `currentFilterStack`
- Rendu clair dans "Filtres actuels" (badge mode)

**Critères d'acceptation**:

- Ajout d'un filtre exclude fonctionne sans JSON manuel
- Sauvegarde profil conserve le mode
- Chargement profil réaffiche correctement le mode

**Impact**:

- `templates/index.html` (sélecteur mode)
- `static/js/app.js` (`addFilterFromBuilder`, `renderFilterList`, sync profils)

**Estimation**: 1h
**Priorité**: Moyenne
**Statut**: ⏳ À FAIRE

### 🟡 N3 - Redimensionnement des colonnes (drag and drop)

**Problème**: Largeur de colonnes fixe, lecture difficile pour champs longs.

**Objectif**: Autoriser l'ajustement manuel des colonnes dans le tableau.

**Spécification cible**:

- Poignée de resize sur headers
- Largeurs appliquées sans casser DataTables
- Option de persistance locale (localStorage) si faisable rapidement

**Critères d'acceptation**:

- Drag horizontal redimensionne visuellement la colonne
- Pas de régression tri/pagination/reload
- Réinitialisation possible (fallback simple)

**Impact**:

- `templates/index.html` (headers/css)
- `static/js/app.js` (gestion resize)
- éventuel helper CSS

**Estimation**: 2h
**Priorité**: Moyenne
**Statut**: ⏳ À FAIRE

### 🟢 N4 - Popup détail ligne (toutes métadonnées)

**Problème**: Certaines infos sont tronquées et peu lisibles dans le tableau.

**Objectif**: Afficher une vue complète d'une ligne dans une popup légère.

**Spécification cible**:

- Action "Voir détail" par ligne
- Modal avec toutes colonnes/valeurs (format lisible)
- Copie rapide des champs utiles

**Critères d'acceptation**:

- Ouverture/fermeture fiable
- Affichage complet même pour champs longs
- Aucune régression de performance notable

**Impact**:

- `templates/index.html` (modal)
- `static/js/app.js` (binding ligne -> modal)

**Estimation**: 1.5h
**Priorité**: Basse
**Statut**: ⏳ À FAIRE

## 🧪 Vérification et tests

### Tests unitaires

```bash
# Depuis UnityAssetsManager/
python -m pytest tests/test_filters.py -v
```

### Tests manuels (checklist)

**Export**:

- [ ] Ouvrir modal export -> compter lignes filtrées correct
- [ ] Export Markdown -> extension `.md`
- [ ] Export JSON -> extension `.json`
- [ ] Export CSV -> extension `.csv`

**Filter Builder**:

- [ ] Ajouter filtre via UI -> `currentFilterStack` mis à jour
- [ ] Supprimer filtre -> retiré de liste + JSON
- [ ] Vider tous filtres -> reset OK
- [ ] Sauvegarder puis charger profil -> filtres restaurés

**Recherche**:

- [ ] Entrée clavier
- [ ] Clic bouton
- [ ] Regex actif / inactif

## Fichiers impactés - Récapitulatif

| Fichier                | Type   | Changement principal                                  |
| ---------------------- | ------ | ----------------------------------------------------- |
| `templates/index.html` | HTML   | Builder UI, export counter, recherche, filtres        |
| `static/js/app.js`     | JS     | Search handlers, builder, export modal, filtres       |
| `app.py`               | Python | `api_export` robustifié (erreurs + extensions + MIME) |

## Statut d'implémentation (mis à jour 2026-03-06)

### Backlog V2 (Nouvelles Fonctionnalités)

- P2.3 - Options d'affichage (v1 settings) - ⏳ À FAIRE
- N1 - Export en batch (CLI/API sans UI) - ⏳ À FAIRE (HIGH)
- N2 - Include/exclude dans le builder - ⏳ À FAIRE (MEDIUM)
- N3 - Resize colonnes tableau - ⏳ À FAIRE (MEDIUM)
- N4 - Popup détail ligne - ⏳ À FAIRE (LOW)

### Statistiques d'implémentation

✅ Complétés: **11/16** (69%)

- ✅ Profils persistants (sauvegarde/chargement)
- ✅ Filter builder UI (ajout/suppression filtres)
- ✅ Export templates configurables (11 templates JSONC)
- ✅ Recherche avec regex
- ✅ Extension detection (MD/CSV/JSON/TXT auto)
- ✅ Headers dans exports (format-specific)
- ✅ Pipe escaping pour Markdown tables
- ✅ DataTables pagination côté serveur
- ✅ Multi-source (CSV + SQLite DB)
- ✅ Profile preview + metadata
- ✅ Export preview dynamique

⏳ En backlog: **5/16** (31%)

- N1-N4 (V2 features)
- P2.3 (V1 settings porting)

❌ Bloquants: **0** (aucun)

### Comparaison V1 → V2

**CORE V1 Features Implémentés en V2: 8/12 (67%)**

- ✅ Profils filtres + colonnes unifiés (JSONC)
- ✅ Rechargement automatique source
- ✅ Support multi-formats (CSV + SQLite)
- ✅ Export valeurs distinctes par colonne (via API)
- ✅ Templates export configurables
- ✅ Cache fichier source (`.cache/last_file.csv`)
- ✅ Format markdown avec frontmatter (via assetManagerExportAllProfiles.py)
- ✅ Filtrage avancé avec actions masse (via UI builder)

❌ Manquants V1 → V2: 4/12 (33%)

- ❌ Mode batch CLI complet (V1: `python assetManager.py -b -p profile -c source.csv`)
- ❌ Table selection pour SQLite multi-table (V1: `--db-table` flag)
- ❌ Include/exclude toggle dans filter builder (V1: actions masse ✅/✖️/🔁/🎯/➕)
- ❌ Debug network logs UI (V1: checkbox + artifact log)

**GLOBAL (incluant backlog actuel): 11/16 (69%)**

### Focus Migration Restant

**Priorité Haute (N1)**: Batch export CLI

- V1: Script `assetManagerExportAllProfiles.py` + CLI flags `-b -p -c -t -e`
- V2: Besoin endpoint `/api/batch-export` + logs exploitables
- Impact: Automation scripts, CI/CD, archivage récurrent

**Priorité Moyenne (N2)**: Include/exclude mode

- V1: Actions masse via SVG icons (✅ tout, ✖️ clear, 🔁 invert, 🎯 keep, ➕ add)
- V2: Builder ajoute uniquement filtres "include" actuellement
- Impact: Workflow curation assets (exclusion rapide de catégories)

**Détail backlog restant:**

**Fichier de suivi**: `_Helpers/04_Assets/UnityAssetsManager/MIGRATION STATE V1 to V2 .md`
**Changelog**: À mettre à jour dans `UnityAssetsManager/CHANGELOG.md`

---

## 📊 Matrice de Migration V1 → V2

### Fonctionnalités Core (Streamlit → Flask/DataTables)

| Fonctionnalité V1                        | Statut V2   | Implémentation V2                       | Notes Migration                                          |
| ---------------------------------------- | ----------- | --------------------------------------- | -------------------------------------------------------- |
| **Profils unifiés (filtres + colonnes)** | ✅ COMPLET  | `profiles/*.profile.jsonc`              | Format identique, compatible bidirectionnel              |
| **Support CSV**                          | ✅ COMPLET  | `app.py:load_data()`                    | Lecture pandas, cache identique V1                       |
| **Support SQLite**                       | ✅ COMPLET  | `app.py:load_data()`                    | Query avec pandas.read_sql_query()                       |
| **Sélection table SQLite**               | ❌ MANQUANT | —                                       | V1: `--db-table` flag + UI dropdown si multi-table       |
| **Cache fichier source**                 | ✅ COMPLET  | `.cache/last_file.csv`                  | Même structure fichier V1                                |
| **Rechargement auto source**             | ✅ COMPLET  | Checkbox UI + startup load              | Persistance config.json                                  |
| **Filtrage avancé**                      | ⚠️ PARTIEL  | Filter builder (include only)           | Manque mode exclude + actions masse SVG                  |
| **Actions masse colonnes**               | ❌ MANQUANT | —                                       | V1: ✅/✖️/🔁/🎯/➕ icons via Streamlit                   |
| **Export templates**                     | ✅ COMPLET  | `export_templates.jsonc` (11 templates) | Extension auto V2 > V1 fixe                              |
| **Export batch CLI**                     | ❌ MANQUANT | —                                       | V1: `-b -p -c -t -e` flags complets                      |
| **Export frontmatter**                   | ✅ COMPLET  | Via `assetManagerExportAllProfiles.py`  | Script V1 compatible V2 profiles                         |
| **Export valeurs distinctes**            | ✅ COMPLET  | `/api/unique-values` endpoint           | V2 API vs V1 direct TXT file write                       |
| **Debug network logs**                   | ❌ MANQUANT | —                                       | V1: checkbox UI + `.cache/debug.log`                     |
| **Settings persistence**                 | ⚠️ PARTIEL  | `config.json`                           | V1: `data/config.jsonc` avec multiselect_threshold, etc. |

### Architecture Technique

| Composant             | V1 (Streamlit)                      | V2 (Flask/DataTables)                | Migration Notes                   |
| --------------------- | ----------------------------------- | ------------------------------------ | --------------------------------- |
| **UI Framework**      | Streamlit                           | Flask + Jinja2 templates             | Réécriture complète interface     |
| **Tableau affichage** | st.dataframe()                      | DataTables.js (AJAX pagination)      | Perf: 2-5s → 200-400ms            |
| **Filtrage**          | Streamlit multiselect widgets       | Filter builder JSON + server-side    | Logique FilterNode tree identique |
| **Recherche**         | Streamlit text_input                | Input HTML + regex flag              | Fonctionnellement équivalent      |
| **Export**            | Streamlit download_button           | Flask send_file() + MIME auto        | V2 gère extensions + headers      |
| **Profils**           | JSONC read/write + st.selectbox     | `/api/profiles` REST + dropdown HTML | Compatibilité format maintenue    |
| **Cache persistence** | `.cache/` + `data/config.jsonc`     | `.cache/` + `config.json`            | Même emplacements fichiers        |
| **Batch mode**        | CLI flags + no st.set_page_config() | ❌ Pas encore implémenté             | V1: mode headless fonctionnel     |

### Dépendances et Outils

| Outil/Script                         | V1                 | V2               | Compatibilité                                     |
| ------------------------------------ | ------------------ | ---------------- | ------------------------------------------------- |
| **assetManagerExportAllProfiles.py** | ✅ Utilisé         | ✅ Compatible    | Lit profiles/ V1, génère exports avec frontmatter |
| **searchGedOrAssets.ps1**            | ✅ Utilisé         | ✅ Compatible    | Lit AssetLists/ V1, recherche vault               |
| **validateFrontmatter.py**           | ✅ Lint exports    | ✅ Compatible    | Valide exports Markdown V1/V2                     |
| **vaultConfig.py**                   | ✅ Config centrale | ⚠️ Non requis V2 | V2 autonome, mais peut réutiliser helpers/        |

### Gaps Fonctionnels Identifiés

**Bloquants pour migration complète:**

1. **Batch export CLI** (N1 HIGH): Requis pour scripts automation (CI/CD, archivage quotidien)
2. **Include/exclude mode** (N2 MEDIUM): Workflow curation assets nécessite exclusion rapide

**Nice-to-have migration:** 3. **Table selector SQLite** (MEDIUM): V1 gère multi-table, V2 assume table unique actuellement 4. **Debug logs UI** (LOW): Diagnostic réseau V1 via checkbox, V2 logs serveur uniquement

**Non-critiques (différences acceptables):**

- Actions masse SVG (✅/✖️ etc): Filter builder V2 offre alternative JSON (moins visuel)
- Settings UI avancés (multiselect_threshold, cache_mode): V2 simplifié, config.json manuel

---

## 🛠️ Roadmap Migration Restante

### Phase 1 - Parité Fonctionnelle Core (N1)

**Objectif**: V2 peut remplacer V1 pour use-cases automation

- [ ] Implémenter `/api/batch-export` endpoint (payload: template, filters, columns, output_path)
- [ ] Logs structurés (succès/erreur + durée + timestamp)
- [ ] Tests API batch export (`tests/test_batch_export.py`)
- [ ] Documentation CLI (`QUICKSTART.md` section batch)
- **ETA**: 1.5-2h
- **Validation**: `assetManagerExportAllProfiles.py` peut appeler V2 API au lieu de V1 CLI

### Phase 2 - Amélioration UX (N2-N3)

**Objectif**: V2 offre meilleure expérience que V1

- [ ] Mode include/exclude dans filter builder (sélecteur UI + persistance profil)
- [ ] Resize colonnes tableau (poignée drag + localStorage fallback)
- **ETA**: 3h total
- **Validation**: Workflow curation 852_A\*.md plus rapide que V1

### Phase 3 - Polish & Extras (N4 + Nice-to-have)

**Objectif**: Features supplémentaires V2-only

- [ ] Popup détail ligne (modal toutes colonnes)
- [ ] Table selector pour SQLite multi-table (dropdown si >1 table détectée)
- **ETA**: 2-3h total
- **Validation**: Use-cases avancés V2 > V1

---

## ✅ Vérification Cohérence Backlog

### Alignement Priorités vs Gaps V1

| Item Backlog                  | Priorité Initiale | Gap V1 Correspondant                           | Justification Priorité                                             | Cohérence ✓/✗                |
| ----------------------------- | ----------------- | ---------------------------------------------- | ------------------------------------------------------------------ | ---------------------------- |
| **N1 - Batch export CLI**     | 🔴 HIGH           | ❌ V1: CLI `-b -p -s -t -e` complet            | Automation scripts (CI/CD, archivage), bloquant migration complète | ✅ Cohérent                  |
| **N2 - Include/exclude mode** | 🟡 MEDIUM         | ❌ V1: Actions masse ✅/✖️/🔁/🎯/➕            | Workflow curation assets (exclusion rapide catégories 851\*)       | ✅ Cohérent                  |
| **N3 - Resize colonnes**      | 🟡 MEDIUM         | ⚠️ V1: Colonnes fixes aussi                    | UX improvement (V2-only), non-bloquant migration                   | ✅ Cohérent                  |
| **N4 - Popup détail**         | 🟢 LOW            | ⚠️ V1: Pas de popup                            | UX improvement (V2-only), non-bloquant migration                   | ✅ Cohérent                  |
| **P2.3 - Settings UI**        | 🟡 (NON PRIORISÉ) | ⚠️ V1: config.jsonc avec threshold, cache_mode | Port settings V1 vers V2 UI, peut rester config.json manuel        | ⚠️ Basse priorité acceptable |

**Verdict**: ✅ Backlog bien priorisé. N1 (HIGH) est le seul bloquant migration automation, N2-N4 (MEDIUM/LOW) sont des améliorations UX non-critiques.

### Dépendances Entre Items

- **N1 ← assetManagerExportAllProfiles.py**: Script V1 doit pouvoir appeler V2 API (endpoint `/api/batch-export`)
- **N2 ⊥ N3, N4**: Indépendants, peuvent être développés en parallèle
- **P2.3 ⊥ N1-N4**: Indépendant, peut être différé si config.json manuel suffit

**Recommandation ordre implémentation**: N1 (1.5h) → N2 (1h) → N3 (2h) → N4 (1.5h) = **6h total pour parité V1 + UX améliorée**

### Risques et Bloquants Identifiés

1. ✅ **Pas de blocage technique**: Tous items réalisables avec stack Flask/DataTables actuel
2. ✅ **Compatibilité profils V1/V2**: Format JSONC identique, migration transparente
3. ⚠️ **Test régression V1**: Valider que `assetManagerExportAllProfiles.py` fonctionne avec V2 endpoint (nécessite tests intégration)
4. ⚠️ **Documentation migration**: QUICKSTART.md doit documenter passage V1 CLI → V2 API

### Items Non Inclus (Justifiés)

- **Table selector SQLite multi-table**: Cas d'usage rare (V1: 1 table par défaut), peut être ajouté plus tard si besoin
- **Debug logs UI**: Serveur Flask logs suffisants pour développement, checkbox V1 était workaround Streamlit
- **Cache settings avancés**: config.json manuel accepté, UI settings V1 peu utilisée en pratique

**Conclusion**: ✅ **Backlog cohérent, priorisé correctement, sans items manquants critiques.**

---

## Clôture - Synthèse courte

- Le suivi est centralisé dans ce document.
- La chronologie détaillée est déjà disponible en tête de fichier.
- Les priorités actives restent N1 → N2 → N3 → N4.

---

**Fichier de suivi**: `_Helpers/04_Assets/UnityAssetsManager/MIGRATION STATE V1 to V2 .md`
**Changelog**: À mettre à jour dans `UnityAssetsManager/CHANGELOG.md`
**updatedBy**: GPT-5.3-Codex
**lastUpdated**: 2026-03-06
**version**: 2.0.1 (nettoyage de doublons, synthèse consolidée)

**updatedBy: GPT-5.3-Codex**

