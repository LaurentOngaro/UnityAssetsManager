# Refactoring & Modularisation de UnityAssetsManager

## Contexte

Le fichier principal `app.py` est actuellement un monolithe (environ 750 lignes) qui mélange logique de configuration, accès aux données (Pandas/SQLite), filtrage avancé et définition des routes web Flask.

L'objectif est d'aligner l'architecture de `UnityAssetsManager` sur celle de `FabAssetsManager` (plus récente, modulaire et épurée). Cette refonte facilitera grandement la maintenance en unifiant la structure des deux applications.

## Objectifs de la Refonte

### 1. Modularisation (Séparation des préoccupations)

Découper le monolithe en plusieurs modules distincts :

- **`app.py`** : Point d'entrée, initialisation Flask et enregistrement des routes.
- **`config.py`** : Gestion des paramètres (`config.json`), des chemins et stockage des templates d'export (`DEFAULT_EXPORT_TEMPLATES`).
- **`data_manager.py`** : Isolation de la classe `AssetDataManager` et logique d'accès (SQLite / CSV).
- **`filters.py`** : Logique de filtrage (ex: `apply_filter_stack`, `vectorized_tag_filter`).
- **`routes.py`** : Tous les endpoints API et le rendu des templates web.
- **`utils.py`** : Fonctions génériques et utilitaires de parsing.

### 2. Suppression de la dette technique (Legacy V1)

Le code actuel fait appel à un hack `sys.path.insert(0, str(HELPERS_DIR))` pour importer `lib.jsoncUtils` de la version V1.

- **Action :** Intégrer définitivement les fonctions `read_json` et `write_json_normalized` dans le nouveau fichier `utils.py` du projet pour le rendre 100% autonome.

### 3. Suppression de l'état global et sécurisation

Le code manipule des variables globales (`DATA_PATH`, `show_parser_warnings`) dans le contexte d'une application web, ce qui pose problème en cas de requêtes concurrentes.

- **Action :** Utiliser une classe de Configuration ou stocker l'état dans l'objet `app.config` de Flask.

### 4. Optimisation de l'usage de SQLite

Actuellement, si une source SQLite est configurée, `AssetDataManager` charge **la totalité de la base** dans la RAM via Pandas (`SELECT * FROM table`).

- **Action :** Tirer parti du moteur SQL. Déléguer la pagination (`LIMIT`/`OFFSET`) et le filtrage (`WHERE`) à SQLite lorsque c'est la source active. Pandas sera alors conservé uniquement pour le mode CSV ou la gestion des exports complexes.

## Suivi

Ce chantier est suivi dans :

- `TODO.md` (Section Refactoring, ticket REF2)
- `_helpers/PLAN_ACTIONS.md` (Nouveau Sprint d'optimisation)
