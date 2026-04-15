---
description: "Instructions générales pour le développement du projet UnityAssetsManager"
applyTo: "**/*.{py,js,html,css,md}"
---

# Projet UnityAssetsManager

## Objectif du projet

Application locale (Python/Flask + Vanilla JS/HTML) pour explorer, filtrer et exporter un catalogue d'assets Unity (CSV/SQLite), avec profils persistants et exports template.

## Architecture & Conventions

1. **Backend (Python)** :

- `app.py` expose l'application Flask.
- `app_settings.py` centralise les constantes applicatives.
- Le fichier de configuration runtime est `config/config.json`.
- Les templates d'export sont chargés depuis `data/export_templates.jsonc`.

2. **Frontend (Vanilla)** :

- Templates Flask dans `templates/`.
- JavaScript applicatif dans `static/js/app.js`.
- CSS applicatif dans `static/css/style.css`.
- Aucun framework JS (React, Vue, etc.) ne doit etre ajoute.

3. **Organisation du travail** :

- Lire et appliquer les priorités de `TODO.md`.
- Lire `_helpers/PLAN_ACTIONS.md` avant toute tache non triviale.
- Une fois une tache terminee, cocher la case correspondante dans `TODO.md`.
- Dans `_helpers/PLAN_ACTIONS.md`, prefixer la tache finalisee avec `DONE `.

## Regles de codage

- Modifications ciblees pour limiter les regressions.
- Python: style PEP8, type hints quand pertinent.
- JavaScript: code lisible, sans surcharge inutile.
- Garder le contrat d'erreur API uniforme (`error.code`, `error.message`, `error.http_status`, `error.timestamp`, `error.path`, `error.details`).

## Versioning et Changelog

A chaque modification significative:

1. Documenter les changements dans `CHANGELOG.md`.
2. Mettre a jour la version via `python _helpers/bumpImportantVersion.py` (`patch` par defaut, `--scope minor|major` si necessaire).
3. Ne pas modifier manuellement `VERSION.txt` quand le helper peut le faire.
