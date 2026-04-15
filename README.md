# 🚀 UnityAssetsManager - Flask Edition

Version: 1.2.5

Application web locale pour la gestion rapide et efficace d'inventaires d'assets (3800+ lignes) avec support multi-source (CSV/SQLite), filtrage avancé, profils personnalisés et exports flexibles.

## Améliorations par rapport à V1 (Streamlit)

| Aspect              | V1 Streamlit         | V2 Flask                 |
| ------------------- | -------------------- | ------------------------ |
| **Affichage table** | 2-5 secondes         | 200-400ms                |
| **Filtrage**        | Refiltre tout (lent) | Côté serveur (rapide)    |
| **Pagination**      | Streamlit lent       | DataTables.js natif      |
| **Exports**         | Via Streamlit (lent) | HTTP direct (rapide)     |
| **Multi-source**    | CSV + SQLite basic   | CSV + SQLite avec tables |
| **Profils**         | JSONC manuel         | UI + API REST            |
| **Scalabilité**     | Difficile            | Excellente               |
| **Responsif**       | Limité               | Bootstrap 5 (responsive) |

## 🚀 Installation

```powershell
# Lancer le batch Windows
.\start_UnityAssetsManager.bat
```

Les lanceurs utilisent Python global et installent les dépendances depuis `requirements.txt` avant de démarrer le serveur.

Le serveur démarre par défaut sur **http://localhost:5003**. Ce port peut être modifié dans `config/config.json`.

## 📖 Utilisation

### Interface principale

1. **Recherche** 🔍: Cherche dans tous les champs en temps réel (côté serveur)
2. **Sélection colonnes** 📋: Choisir les colonnes à afficher (Ctrl+clic pour sélection multiple)
3. **Pagination**: 25/50/100/250 lignes par page (DataTables)
4. **Profils** 💽: Sauvegarder/charger vos réglages préférés
5. **Export** 💾:

- CSV standard / séparateur point-virgule
- CSV avec URL
- JSON
- Markdown table

### Clavier

- **Ctrl+F**: Recherche navigateur (dans la page affichée)
- **Ctrl+C**: Copier le tableau (depuis le navigateur)

## 🔧 Configuration

### Chemin des données

Configurer la source via la page `/setup` (recommandé) ou en éditant `config/config.json`:

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

Parametres logging runtime:

- `log_level`: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- `log_output`: `console`, `file`, `both`
- `log_max_bytes`: taille max d'un fichier log avant rotation
- `log_backup_count`: nombre de fichiers archives gardes

**Sources supportées:**

- ✅ **CSV local** (`.csv`) avec **détection automatique du séparateur** (`,`, `;`, `|`, `\t`)
- ✅ **CSV avec encodage multiple** (UTF-8, latin-1, cp1252)
- ✅ **SQLite** (`.db`, `.sqlite`, `.sqlite3`) avec **sélection de table**
  - Interface `/setup` pour choisir la table
  - Config persistante dans `config/config.json` (`data_path` + `db_table`)
  - Support multi-tables (dropdown automatique)
  - **Guide complet**: Voir `./_helpers/SQLITE_SUPPORT.md` pour migration CSV→SQLite, API, troubleshooting et benchmarks

### Répertoires

- `profiles/`: Profils JSON (format: `NomProfil.json`)
- `exports/`: Fichiers exportés
- `.cache/`: Cache interne (1h TTL)

## 📊 API & Documentation technique

- **Guide API Complet**: [API_GUIDE.md](./API_GUIDE.md) (Endpoints, format JSON, payloads, batch-export).
- Endpoints API4 disponibles: `GET /api/test`, `GET /api/config`, `POST /api/config`.
- **Setup SQLite & Migration**: [SQLITE_SUPPORT.md](./_helpers/SQLITE_SUPPORT.md).
- **Test Qualité**: [tests/test_manual_checklist.py](./tests/test_manual_checklist.py).

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

ou bien modifier `flask_port` dans `config/config.json`

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

---

**Version**: 1.2.7
**Dernière mise à jour**: 2026-04-15
**Status**: Production (Architecture modulaire, API stabilisée)
