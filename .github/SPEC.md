# UnityAssetsManager — Specifications & Development Notes

Version: 1.2.8
Last reviewed: 2026-04-16

## Context

Local application for exploring, filtering, and exporting a Unity asset catalog (CSV or SQLite).
Optimized for performance (3800+ lines) with server-side filtering.

---

## Key Features

- **Multi-source**: Support for CSV (automatic separator detection) and SQLite (multi-table management via `/setup`).
- **Responsive Web Interface**: Based on Vanilla JS and DataTables.js for pagination and column resizing.
- **Advanced Filtering**: Full-text search, column filters, and "tags" management.
- **Profiles**: Save and load column and filter configurations (JSON) stored in `profiles/`.
- **Flexible Exports**: Customizable templates (`data/export_templates.jsonc`) for CSV, JSON, Markdown, etc.
- **Performance**: Pagination and filtering executed on the Flask backend for maximum fluidity.

---

## Technical Architecture

### 1. File Structure

- `app.py`: Flask entry point and server configuration.
- `lib/`: Package containing business logic (moved for clarity).
  - `config.py`: Loading and validation of `config/config.json`.
  - `app_settings.py`: Constants and default paths.
  - `data_manager.py`: Data access abstraction (CSV/SQLite) with memory cache.
  - `filters.py`: Filtering engine based on pandas.
  - `routes.py`: API endpoint definitions and template rendering.
  - `logging_setup.py`: Centralized logging configuration (console + file rotation).
  - `utils.py`: JSONC helpers and parsing.
  - `errors.py`: Standardized API error contract.
- `static/`: Frontend assets (CSS, JS).
- `templates/`: Jinja2 templates (`index.html`, `setup.html`).
- `config/`: User configuration files.

### 2. Data Flow

1. The user configures the source (`data_path`) via the `/setup` page.
2. The `AssetDataManager` loads the data and caches it (adjustable TTL).
3. `/api/assets` requests send filtering/pagination criteria.
4. The backend applies the "filter stack" via pandas and returns a JSON result page.
5. The frontend updates the table without reloading the page.

---

## Reference Documentation

- **API Endpoints**: See [API_GUIDE.md](../API_GUIDE.md) for JSON contracts and the exhaustive route list.
- **Migration & SQLite**: See [SQLITE_SUPPORT.md](./SQLITE_SUPPORT.md) for database-specific details.
