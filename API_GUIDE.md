# API Guide - UnityAssetsManager

**Version:** 1.2.7

## Overview

UnityAssetsManager propose une API Flask locale pour explorer des assets Unity (CSV/SQLite), appliquer des filtres, gérer des profils et exporter des résultats.

- Base URL: `http://localhost:5003`
- Format principal: JSON
- Authentification: aucune (usage local)
Remarque: 5003 est le port HTTP par défaut de l'interface web. Il peut être modifié dans `config/config.json`.

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

### Health UI (implicite)

- `GET /`
- Retour: page HTML principale.

### Health API (automation)

- `GET /api/test`
- But: healthcheck JSON pour scripts et CI locale.

Exemple de retour:

```json
{
  "status": "ok",
  "timestamp": "2026-04-15T11:15:00.000000+00:00",
  "version": "1.2.5",
  "data_path": "H:/.../unity_assets_export.csv",
  "source_type": "csv",
  "has_data": true
}
```

### Donnees

- `GET /api/data`
- But: données paginées + filtrées (DataTables côté serveur).
- Paramètres courants:
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
- But: exporter les données filtrées (CSV/MD/JSON/TXT selon le template).

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
- Cas d'usage: scripts PowerShell/Python, intégration de pipeline, génération récurrente.

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

- `output_dir` est optionnel (défaut: dossier `exports` de l'application).
- si `file_name` n'a pas d'extension, l'extension est déduite du template.
- si `output_dir` est relatif, il est résolu depuis le dossier de l'application.

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
