# UnityAssetsManager — Spécifications & Notes de Développement

Version: 1.2.8
Last reviewed: 2026-04-16

## Contexte

Application locale permettant d'explorer, filtrer et exporter un catalogue d'assets Unity (CSV ou SQLite).
Optimisée pour la performance (3800+ lignes) avec filtrage côté serveur.

---

## Fonctionnalités principales

- **Multi-source** : Support CSV (détection automatique du séparateur) et SQLite (gestion multi-tables via `/setup`).
- **Interface Web réactive** : Basée sur Vanilla JS et DataTables.js pour la pagination et le redimensionnement des colonnes.
- **Filtrage avancé** : Recherche plein texte, filtres par colonnes, gestion de "tags".
- **Profils** : Sauvegarde et chargement de configurations de colonnes et filtres (JSON) stockés dans `profiles/`.
- **Exports flexibles** : Templates personnalisables (`data/export_templates.jsonc`) pour CSV, JSON, Markdown, etc.
- **Performance** : Pagination et filtrage exécutés sur le backend Flask pour une fluidité maximale.

---

## Architecture Technique

### 1. Structure des fichiers

- `app.py` : Point d'entrée Flask et configuration du serveur.
- `lib/` : Package contenant la logique métier (déplacée pour plus de clarté).
  - `config.py` : Chargement et validation de `config/config.json`.
  - `app_settings.py` : Constantes et chemins par défaut.
  - `data_manager.py` : Abstraction de l'accès aux données (CSV/SQLite) avec cache mémoire.
  - `filters.py` : Moteur de filtrage basé sur pandas.
  - `routes.py` : Définition des endpoints API et rendu des templates.
  - `logging_setup.py` : Configuration centralisée des logs (console + rotation fichier).
  - `utils.py` : Helpers JSONC et parsing.
  - `errors.py` : Contrat d'erreur API standardisé.
- `static/` : Assets frontend (CSS, JS).
- `templates/` : Templates Jinja2 (`index.html`, `setup.html`).
- `config/` : Fichiers de configuration utilisateur.

### 2. Flux de données

1. L'utilisateur configure la source (`data_path`) via la page `/setup`.
2. Le `AssetDataManager` charge les données et les met en cache (TTL réglable).
3. Les requêtes `/api/assets` envoient des critères de filtrage/pagination.
4. Le backend applique la "filter stack" via pandas et retourne une page de résultats JSON.
5. Le frontend met à jour le tableau sans recharger la page.

---

## Endpoints API

### Configuration & Diagnostics

```
GET  /api/test    (Healthcheck)
GET  /api/config  (Lecture config publique)
POST /api/config  (Mise à jour des paramètres)
```

### Données & Filtrage

```
GET  /api/assets   (Récupération paginée/filtrée)
GET  /api/columns  (Liste des colonnes de la source)
GET  /api/stats    (Statistiques sur les assets)
```

### Profils & Exports

```
GET  /api/profiles   (Liste des profils)
POST /api/profiles  (Sauvegarde de profil)
GET  /api/export-templates (Liste des formats d'export)
POST /api/export    (Génération de fichier export)
```
