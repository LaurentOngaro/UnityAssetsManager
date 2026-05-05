# 🚀 UnityAssetsManager (UAM)

Version: 1.6.0

Local web application for fast and efficient management of asset inventories with multi-source support (CSV/SQLite), advanced filtering, custom profiles, and flexible exports.

## 🎯 Scope & Integration TerraBloom

> **Architecture Note:** This tool is **strictly specialized for Unity Store assets**. It serves as a “Raw Collection” entry point for the TerraBloom ecosystem. It takes care of filtering the colossal SQLite/CSV database of Unity purchases and generates 29 targeted raw files.
> Standardization and cross-store consolidation (Fab, Synty, etc.) are managed further down the pipeline by asset curation scripts.
> **Complete documentation of the TerraBloom Curation flow:** Voir `[[337_Processus - Audit et curation audit des assets]]`.

## 🚀 Installation

```powershell
# Launch Windows batch
.\start_UnityAssetsManager.bat
```

Launchers use global Python and install dependencies from `requirements.txt` before starting the server.

The server starts by default on **http://localhost:5003**. This port can be changed in `config/config.json`.

## 📖 Usage

### Main Interface

1. **Search** 🔍: Search all fields in real-time (server-side, supports Regex).
2. **Column Selection** 📋: Choose columns to display. Includes a **quick filter** to find columns by name.
3. **Collapsible Panels** 📂: Organize your workspace by collapsing or expanding Message, Controls, Data, and Options sections.
4. **Centralized Messages** 💬: All application alerts and status updates are grouped in a dedicated panel with history.
5. **Dual Pagination** 🔢: Use pagination controls both at the top and bottom of the table for easier navigation.
6. **Column Resizing** ↔️: Hover over the right edge of a header to resize. Widths are **automatically saved** and restored.
7. **Quick Details** 📄: Click any row to open a popup with all asset details.
8. **Advanced Filtering** 🧱: Use the Filter Builder to stack inclusion/exclusion rules on specific columns.
9. **Invalid Asset Filter** 🚫: Toggle a global filter in "Options" to exclude assets with missing links or incomplete display fields.
10. **Child Asset Filter** 👶: Exports automatically exclude rows with a non-null `ParentId` to eliminate duplicates. Use `--get-childs` in batch export or `get_childs: true` in API payloads to include them.
11. **Profiles** 💽: Save/load your preferred setting combinations (columns + filters + aliases).
12. **Export** 💾: Interactive or Batch export (CSV, MD, JSON, TXT).
13. **Dark Theme** 🌙: Modern and comfortable interface.

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

## 🤖 Batch Export Automation

The script `UnityAssetsManagerExportAllProfiles.py`, automates profile exports via `POST /api/batch-export` and writes raw category files to `assetsExports/Unity/`.

Typical usage:

```powershell
# Export all profiles (4 workers by default)
python .\UnityAssetsManagerExportAllProfiles.py

# Resume from the last successful profile
python .\UnityAssetsManagerExportAllProfiles.py --resume

# Export only a subrange of profiles (1-based indexes)
python .\UnityAssetsManagerExportAllProfiles.py --start_index 1 --end_index 10

# Force overwrite and use a specific template
python .\UnityAssetsManagerExportAllProfiles.py --force --template "table markdown avec URL"
```

Main options:

- `--resume`: continue from the last successful cached profile
- `--start_index` / `--end_index`: process only a bounded profile range
- `--workers`: number of parallel export workers
- `--lint_markdown_results` / `-l`: run `run_linters.bat` on exported folders after the batch completes (enabled by default)
- `--no-lint_markdown_results`: disable the post-export markdown lint step
- `--force`: re-export even if output files already exist
- `--url`: target API base URL (default: `http://localhost:5003/api`)
- `--no-reload`: skip initial server-side reload step
- `--get-childs`: include child assets (rows with non-null ParentId); by default these duplicates are excluded
- `--get-childs`: include child assets (rows with non-null ParentId); by default these duplicates are excluded
- `--get-childs`: include child assets (rows with non-null ParentId); by default these duplicates are excluded

Before linting, each exported Markdown file receives a top-level title (`# <filename without extension>`).

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

lib/
├── app_settings.py (default constants)
├── config.py (configuration)
├── data_manager.py (CSV/SQLite loading)
├── errors.py (centralized error handling)
├── filters.py (filtering logic)
├── logging_setup.py (logging configuration)
├── routes.py (API endpoints)
└── utils.py (utility functions)

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
