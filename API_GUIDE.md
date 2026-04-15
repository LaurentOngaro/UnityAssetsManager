# API Guide - UnityAssetsManager

**Version:** 1.1.3

## Overview

UnityAssetsManager expose une API Flask locale pour explorer des assets Unity (CSV/SQLite), appliquer des filtres, gerer des profils et exporter des resultats.

- Base URL: `http://localhost:5003`
- Format principal: JSON
- Authentification: aucune (usage local)
NOTE: 5003 is the default port for the web interface, but the it can be changed in `config/config.json`

## Contrat d'erreur standard

Toutes les routes API critiques renvoient un format d'erreur homogene:

```json
{
  "error": {
    "code": "INVALID_PAYLOAD",
    "message": "JSON invalide ou manquant",
    "http_status": 400,
    "timestamp": "2026-04-12T10:22:11.000000+00:00",
    "path": "/api/export",
    "details": {}
  }
}
```

Champs:

- `error.code`: identifiant stable pour integration.
- `error.message`: message lisible humain.
- `error.http_status`: code HTTP associe.
- `error.timestamp`: horodatage UTC ISO8601.
- `error.path`: route API cible.
- `error.details`: contexte supplementaire (optionnel).

## Endpoints principaux

### Health (implicite)

- `GET /`
- Retour: page HTML principale.

### Donnees

- `GET /api/data`
- But: donnees paginees + filtrees (DataTables server-side).
- Parametres usuels:
  - `draw`, `start`, `length`
  - `search[value]`, `search[regex]`
  - `filter_stack` (JSON string)
  - `alias_map` (JSON string)

### Colonnes

- `GET /api/columns`
- Retour: colonnes disponibles.

### Templates

- `GET /api/templates`
- Retour: liste des templates d'export (nom, description, pattern).

### Profils

- `GET /api/profiles`
- `GET /api/profiles/{name}`
- `POST /api/profiles`
- `DELETE /api/profiles/{name}`

Payload de sauvegarde profil (`POST /api/profiles`):

```json
{
  "name": "MyProfile",
  "columns": ["DisplayName", "DisplayPublisher"],
  "filter_columns": ["DisplayCategory"],
  "filter_stack": []
}
```

### Export

- `POST /api/export`
- But: exporter les donnees apres filtres (csv/md/json/txt selon template).

Payload type:

```json
{
  "template": "CSV avec URL",
  "columns": ["DisplayName", "Url", "Version"],
  "search": "tool",
  "filter_columns": ["DisplayCategory"],
  "filter_stack": [],
  "alias_map": {}
}
```

Retour:

- Success: fichier binaire en telechargement.
- Error: contrat d'erreur standard.

### Batch export headless

- `POST /api/batch-export`
- But: exporter en mode automation (sans UI) vers un fichier local.
- Cas d'usage: scripts PowerShell/Python, integration pipeline, generation recurrente.

Payload type:

```json
{
  "template": "CSV avec URL",
  "columns": ["DisplayName", "Url", "Version"],
  "search": "tool",
  "filter_stack": [],
  "alias_map": {},
  "output_dir": "exports",
  "file_name": "unity_assets_filtered"
}
```

Notes:

- `output_dir` est optionnel (defaut: dossier `exports` de l'application).
- si `file_name` n'a pas d'extension, l'extension est deduite du template.
- si `output_dir` est relatif, il est resolu depuis le dossier de l'application.

Retour success:

```json
{
  "success": true,
  "path": "H:/.../UnityAssetsManager/exports/unity_assets_filtered.csv",
  "filename": "unity_assets_filtered.csv",
  "rows": 120,
  "columns": 3,
  "template": "CSV avec URL",
  "bytes": 18342
}
```

### Stats et reload

- `GET /api/stats`
- `POST /api/reload`

### Setup source data

- `POST /api/setup`
- But: definir la source de donnees (CSV/SQLite) et table SQLite.

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
  "success": true,
  "data_path": "H:/path/to/assets.db",
  "source_type": "sqlite",
  "db_table": "assets"
}
```

### Test de chemin

- `POST /api/test-path`
- But: verifier qu'un chemin existe et identifier son type (csv/sqlite).

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
    "filter_columns": ["DisplayPublisher"],
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
