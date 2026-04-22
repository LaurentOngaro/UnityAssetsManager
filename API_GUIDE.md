# API Guide - UnityAssetsManager

**Version:** 1.4.1

## Overview

UnityAssetsManager provides a local Flask API to explore Unity assets (CSV/SQLite), apply filters, manage profiles, and export results.

- Base URL: `http://localhost:5003`
- Main Format: JSON
- Authentication: None (Local use)
Note: 5003 is the default HTTP port for the web interface. It can be changed in `config/config.json`.

## Standard Error Contract

All critical API routes return a consistent error format:

```json
{
  "error": {
    "code": "INVALID_PAYLOAD",
    "message": "Invalid or missing JSON",
    "http_status": 400,
    "timestamp": "2026-04-12T10:22:11.000000+00:00",
    "path": "/api/export",
    "details": {}
  }
}
```

Fields:

- `error.code`: Stable identifier for integration.
- `error.message`: Human-readable message.
- `error.http_status`: Associated HTTP code.
- `error.timestamp`: ISO8601 UTC timestamp.
- `error.path`: Targeted API route.
- `error.details`: Additional context (optional).

## Main Endpoints

### UI Health (Implicit)

- `GET /`
- Returns: Main HTML page.

### API Health (Automation)

- `GET /api/test`
- Purpose: JSON healthcheck for scripts and local CI.

Example response:

```json
{
  "status": "ok",
  "timestamp": "2026-04-15T11:15:00.000000+00:00",
  "version": "1.2.9",
  "data_path": "H:/.../unity_assets_export.csv",
  "source_type": "csv",
  "has_data": true
}
```

### Data

- `GET /api/data`
- Purpose: Paged + filtered data (Server-side DataTables).
- Common parameters:
  - `draw`, `start`, `length`
  - `search[value]`, `search[regex]`
  - `filter_stack` (JSON string)
  - `alias_map` (JSON string)

### Columns

- `GET /api/columns`
- Returns: Available columns.

### Templates

- `GET /api/templates`
- Returns: List of export templates (name, description, pattern).

### Profiles

- `GET /api/profiles`
- `GET /api/profiles/{name}`
- `POST /api/profiles`
- `DELETE /api/profiles/{name}`

Save profile payload (`POST /api/profiles`):

```json
{
  "name": "MyProfile",
  "columns": ["DisplayName", "DisplayPublisher"],
  "filter_stack": []
}
```

### Export

- `POST /api/export`
- Purpose: Export filtered data (CSV/MD/JSON/TXT depending on template).

Sample payload:

```json
{
  "template": "CSV avec URL",
  "profile": "851_011_Player_Character",
  "filter_stack": [],
  "alias_map": {},
  "filter_invalid_assets": true
}
```

Returns:

- Success: Binary file for download.
- Error: Standard error contract.
- `filter_invalid_assets` is optional for interactive export (`/api/export`) and only applied when `true`.

### Batch export headless

- `POST /api/batch-export`
- Purpose: Export in automation mode (without UI) to a local file.
- Use cases: PowerShell/Python scripts, pipeline integration, recurring generation.

Sample payload:

```json
{
  "template": "CSV avec URL",
  "profile": "851_011_Player_Character",
  "filter_stack": [],
  "alias_map": {},
  "output_path": "H:/.../assetsExports/Unity/Player_Character.csv"
}
```

Notes:

- Use `output_path` for a direct absolute path output.
- Alternatively, use `output_dir` and `file_name` to compose a path inside the application folder.
- If `file_name` has no extension, it's inferred from the template.
- If `output_dir` is relative, it's resolved from the application folder.
- `/api/batch-export` always removes invalid assets (missing both slug+url, or missing one of DisplayName/DisplayCategory/DisplayPublisher).

Retour success:

```json
{
  "status": "success",
  "file": "H:/.../UnityAssetsManager/exports/unity_assets_filtered.csv",
  "format": "csv",
  "count": 120
}
```

### Stats et reload

- `GET /api/stats`
- `POST /api/reload`

### Setup source data

- `POST /api/setup`
- But: définir la source de données (CSV/SQLite) et la table SQLite.

Payload:

```json
{
  "data_path": "H:/path/to/assets.db",
  "db_table": "assets"
}
```

Retour success:

```json
{
  "status": "success",
  "message": "Configuration mise à jour et données rechargées"
}
```

### Configuration runtime

- `GET /api/config`
- But: lire la configuration runtime publique (sans secret).

- `POST /api/config`
- But: mettre a jour des champs autorises a chaud.

Champs acceptes pour `POST /api/config`:

- `db_table`
- `show_parser_warnings`
- `log_level` (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`)
- `log_output` (`console`, `file`, `both`)
- `log_max_bytes`
- `log_backup_count`

Exemple:

```json
{
  "log_level": "DEBUG",
  "log_output": "both",
  "log_max_bytes": 1048576,
  "log_backup_count": 3
}
```

### Test de chemin

- `POST /api/test-path`
- But: vérifier qu'un chemin existe et identifier son type (CSV/SQLite).

Payload:

```json
{
  "path": "H:/path/to/assets.db"
}
```

## Exemples Python

### Lire les colonnes

```python
import requests

base = "http://localhost:5003"
resp = requests.get(f"{base}/api/columns", timeout=20)
resp.raise_for_status()
print(resp.json())
```

### Sauvegarder un profil

```python
import requests

base = "http://localhost:5003"
payload = {
    "name": "PublisherFocus",
    "columns": ["DisplayName", "DisplayPublisher", "Version"],
    "filter_stack": []
}
resp = requests.post(f"{base}/api/profiles", json=payload, timeout=20)
resp.raise_for_status()
print(resp.json())
```

### Tester un setup SQLite

```python
import requests

base = "http://localhost:5003"
payload = {
    "data_path": "H:/Sync/PKM_PROJECTS/TerraBloom/_Helpers/data/assetsExports/Unity/unity_assets_export.db",
    "db_table": "assets"
}
resp = requests.post(f"{base}/api/setup", json=payload, timeout=20)
print(resp.status_code, resp.json())
```
