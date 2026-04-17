# 🚀 UnityAssetsManager (UAM)

Version: 1.2.12

Local web application for fast and efficient management of asset inventories (3900+ lines) with multi-source support (CSV/SQLite), advanced filtering, custom profiles, and flexible exports.

## 🎯 Périmètre & Intégration TerraBloom

> **Note d'Architecture :** Cet outil est **strictement spécialisé pour les assets Unity Store**. Il sert de point d'entrée "Raw Collecte" pour l'écosystème TerraBloom. Il s'occupe de filtrer la colossale base SQLite/CSV des achats Unity et génère 29 fichiers bruts ciblés.
> L'uniformisation et la consolidation inter-stores (Fab, Synty, etc.) sont gérées plus bas dans le pipeline par les scripts d'assets curation.
> **Documentation complète du flux de Curation TerraBloom :** Voir `[[337_Processus - Audit et curation audit des assets]]`.

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
8. **Dark Theme** 🌙: Modern and comfortable interface (aligned with FabAssetsManager).

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

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"

```powershell
pip install -r requirements.txt
```

### Port 5003 already in use

```python
app.run(port=5004)  # Change port
```

or modify `server_port` in `config/config.json`

### Cannot see my data

1. Check `data_path` in `config/config.json`
2. Click 🔄 Reload (navbar)
3. Check the console (F12 → Console)

## 📝 Technical Notes

### Stack

- **Backend**: Flask 3.0 (Python)
- **Frontend**: Bootstrap 5 + DataTables.js (AJAX pagination)
- **Data**: Pandas (CSV/SQLite loading/filtering)
- **Export**: Configurable JSONC templates (11 formats)

### Architecture

```text
app.py (Flask entry point)
config.py (configuration)
data_manager.py (CSV/SQLite loading)
filters.py (filtering logic)
routes.py (API endpoints)
utils.py (utility functions)

templates/
├── base.html (layout)
├── setup.html (config page)
└── index.html (table + filter builder)

static/
├── css/style.css
└── js/app.js (DataTables + Ajax)

data/
└── export_templates.jsonc (11 configurable templates)

profiles/
└── *.profile.jsonc (V1/V2 compatible profiles)
```

### Technical Documentation

- **Main Backlog**: [`TODO.md`](TODO.md) - Prioritized view of tasks to do
- **Action Plan**: [`_helpers/PLAN_ACTIONS.md`](./_helpers/PLAN_ACTIONS.md) - Detailed and ordered view of tasks
- **Migration V1→V2**: [Migration V1→V2](./_helpers/MIGRATION%20STATE%20V1%20to%20V2%20.md) - Complete matrix, gaps, roadmap
- **SQLite Support**: [`_helpers/SQLITE_SUPPORT.md`](./_helpers/SQLITE_SUPPORT.md) - SQLite Guide
- **Test**: [`tests/test_manual_checklist.py`](./tests/test_manual_checklist.py)

### Rapid Validation

```powershell
python -m pytest tests/test_export_non_regression.py -v
python -m pytest tests/test_manual_checklist.py -v
python _helpers/bumpImportantVersion.py --scope patch --dry-run
```

### Upcoming improvements

The TODO backlog is centralized in [`TODO.md`](TODO.md).

## 📄 License

TerraBloom Project

## 🤝 Support

For bugs: Create an issue in the TerraBloom repo
