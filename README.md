# 🚀 UnityAssetsManager - Flask Edition

Version: 1.2.11

Local web application for fast and efficient management of asset inventories (3800+ lines) with multi-source support (CSV/SQLite), advanced filtering, custom profiles, and flexible exports.

## Improvements over V1 (Streamlit)

| Aspect              | V1 Streamlit         | V2 Flask                 |
| ------------------- | -------------------- | ------------------------ |
| **Table Display**   | 2-5 seconds          | 200-400ms                |
| **Filtering**       | Refilters all (slow) | Server-side (fast)       |
| **Pagination**      | Slow Streamlit       | Native DataTables.js     |
| **Exports**         | Via Streamlit (slow) | Direct HTTP (fast)       |
| **Multi-source**    | Basic CSV + SQLite   | CSV + SQLite with tables |
| **Profiles**        | Manual JSONC         | UI + REST API            |
| **Scalability**     | Difficult            | Excellent                |
| **Responsive**      | Limited              | Bootstrap 5 (responsive) |

## 🚀 Installation

```powershell
# Launch Windows batch
.\start_UnityAssetsManager.bat
```

Launchers use global Python and install dependencies from `requirements.txt` before starting the server.

The server starts by default on **http://localhost:5003**. This port can be changed in `config/config.json`.

## 📖 Usage

### Main Interface

1. **Search** 🔍: Search all fields in real-time (server-side)
2. **Column Selection** 📋: Choose columns to display (Ctrl+click for multiple selection)
3. **Pagination**: 25/50/100/250 lines per page (DataTables)
4. **Column Resizing** ↔️: Hover over the right edge of a header to resize (Sensitive area: 10px).
5. **Quick Details** 📄: Click any row to open a popup with all asset details.
6. **Profiles** 💽: Save/load your preferred settings
7. **Export** 💾:
   - Standard CSV / semicolon separator
   - CSV with URL
   - JSON
   - Markdown table

### Keyboard Shortcuts

- **Ctrl+F**: Browser search (within the displayed page)
- **Ctrl+C**: Copy the table (from browser)

## 🔧 Configuration

### Data Path

Configure the source via the `/setup` page (recommended) or by editing `config/config.json`:

```json
{
  "data_path": "H:/path/to/unity_assets_export.csv",
  "db_table": "assets",
  "log_level": "INFO",
  "log_output": "console",
  "log_max_bytes": 1048576,
  "log_backup_count": 3
}
```

Runtime logging parameters:

- `log_level`: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- `log_output`: `console`, `file`, `both`
- `log_max_bytes`: max log file size before rotation
- `log_backup_count`: number of kept archive files

**Supported Sources:**

- ✅ **Local CSV** (`.csv`) with **automatic separator detection** (`,`, `;`, `|`, `\t`)
- ✅ **CSV with multiple encodings** (UTF-8, latin-1, cp1252)
- ✅ **SQLite** (`.db`, `.sqlite`, `.sqlite3`) with **table selection**
  - `/setup` interface to choose the table
  - Persistent config in `config/config.json` (`data_path` + `db_table`)
  - Multi-table support (automatic dropdown)
  - **Full Guide**: See `./_helpers/SQLITE_SUPPORT.md` for CSV→SQLite migration, API, troubleshooting, and benchmarks

### Directories

- `profiles/`: JSON profiles (format: `ProfileName.json`)
- `exports/`: Exported files
- `.cache/`: Internal cache (1h TTL)

## 📊 API & Technical Documentation

- **Full API Guide**: [API_GUIDE.md](./API_GUIDE.md) (Endpoints, JSON format, payloads, batch-export).
- **Specifications & Architecture**: [.github/SPEC.md](.github/SPEC.md).
- **Contributing**: [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md).
- **Security**: [.github/SECURITY.md](.github/SECURITY.md).
- **SQLite Support & Migration**: [SQLITE_SUPPORT.md](./_helpers/SQLITE_SUPPORT.md).
- **Quality Check**: [tests/test_manual_checklist.py](./tests/test_manual_checklist.py).

## 🎯 Usage Examples

### Filtered Search

```
Search "Unreal" in the bar → Displays only assets containing "Unreal"
```

### Filtered Export

1. Filter to "2000 rows" using search
2. Click "Export"
3. Choose format (JSON, CSV, Markdown, etc.)
4. Download

### Profiles

1. Configure visible columns
2. Click "Profile" → "Save profile"
3. Name it (e.g., "WebView")
4. Later: load the same profile to reuse

## ⚙️ Performance

### Applied Optimizations

- **DataFrame Cache** (1h): No CSV reloading on every request
- **Server-side DataTables**: Server-side pagination/filtering
- **Compression**: Automatic GZip
- **Column Lazy-loading**: Display only selected columns

### Benchmarks (3800 assets, 20 columns)

```
Operation              V1 (Streamlit)    V2 (Flask)    Gain
---------------------------------------------------------------
Load interface         5-8s              ~800ms        8-10x
Search 1000            2-3s              100-150ms     15-20x
Change page            1-2s              50-100ms      20x
Full CSV Export        3-4s              300-500ms     10x
```

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"

```powershell
pip install -r requirements.txt
```

## 🎯 Exemples d'utilisation

### Recherche filtrée

```
Chercher "Unreal" dans la barre → Affiche seulement les assets contenant "Unreal"
```

### Export filtré

1. Filtrer à "2000 lignes" avec recherche
2. Cliquer "Exporter"
3. Choisir format (JSON, CSV, Markdown, etc)
4. Télécharger

### Profils

1. Configurer colonnes visibles
2. Cliquer "Profil" → "Enregistrer profil"
3. Nommer (ex: "WebView")
4. Plus tard: charger le même profil pour réutiliser

## ⚙️ Performance

### Optimisations appliquées

- **Cache DataFrame** (1h): Pas de rechargement CSV à chaque requête
- **DataTables côté serveur**: Pagination/filtrage côté serveur
- **Compression**: GZip automatique
- **Lazy-loading colonnes**: Afficher seulement les sélectionnées

### Benchmarks (3800 assets, 20 colonnes)

```
Opération              V1 (Streamlit)    V2 (Flask)    Gain
---------------------------------------------------------------
Charger interface      5-8s              ~800ms        8-10x
Rechercher 1000        2-3s              100-150ms     15-20x
Changer page           1-2s              50-100ms      20x
Export CSV complet     3-4s              300-500ms     10x
```

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"

```powershell
pip install -r requirements.txt
```

### "Fichier source non trouvé"

Configurer `data_path` via `/setup` ou dans `config/config.json`.

### Port 5003 déjà utilisé

```python
app.run(port=5004)  # Changer port
```

ou bien modifier `server_port` dans `config/config.json`

### Ne vois pas mes données

1. Vérifier `data_path` dans `config/config.json`
2. Cliquer 🔄 Recharger (navbar)
3. Vérifier la console (F12 → Console)

## 📝 Notes techniques

### Stack

- **Backend**: Flask 3.0 (Python)
- **Frontend**: Bootstrap 5 + DataTables.js (AJAX pagination)
- **Data**: Pandas (chargement/filtrage CSV/SQLite)
- **Export**: Templates JSONC configurables (11 formats)

### Architecture

```text
app.py (point d'entrée Flask)
config.py (configuration)
data_manager.py (chargement CSV/SQLite)
filters.py (logique de filtrage)
routes.py (endpoints API)
utils.py (fonctions utilitaires)

templates/
├── base.html (layout)
├── setup.html (page config)
└── index.html (tableau + filter builder)

static/
├── css/style.css
└── js/app.js (DataTables + Ajax)

data/
└── export_templates.jsonc (11 templates configurables)

profiles/
└── *.profile.jsonc (profils V1/V2 compatibles)
```

### Documentation technique

- **Backlog principal**: [`TODO.md`](TODO.md) - Vue priorisée des tâches à faire
- **Plan d'action**: [`_helpers/PLAN_ACTIONS.md`](./_helpers/PLAN_ACTIONS.md) - Vue détaillée et ordonnée des tâches
- **Migration V1→V2**: [Migration V1→V2](./_helpers/MIGRATION%20STATE%20V1%20to%20V2%20.md) - Matrice complète, gaps, roadmap
- **Support SQLite**: [`_helpers/SQLITE_SUPPORT.md`](./_helpers/SQLITE_SUPPORT.md) - Guide SQLite
- **Test**: [`tests/test_manual_checklist.py`](./tests/test_manual_checklist.py)

### Validation rapide

```powershell
python -m pytest tests/test_export_non_regression.py -v
python -m pytest tests/test_manual_checklist.py -v
python _helpers/bumpImportantVersion.py --scope patch --dry-run
```

### Prochaines améliorations

Le backlog TODO est centralisé dans [`TODO.md`](TODO.md).

## 📄 License

TerraBloom Project

## 🤝 Support

Pour les bugs: Créer un issue dans le repo TerraBloom
