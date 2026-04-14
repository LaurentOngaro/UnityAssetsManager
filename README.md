# 🚀 UnityAssetsManager - Flask Edition

File version: 1.1.1

Application web locale pour la gestion rapide et efficace d'inventaires d'assets (3800+ lignes) avec support multi-source (CSV/SQLite), filtrage avancé, profils personnalisés et exports flexibles.

**Performance haute vitesse pour gestion d'assets 3800+ lignes**

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

**📊 Migration V1→V2**: Voir `MIGRATION STATE V1 to V2.md` pour matrice complète, gaps fonctionnels et roadmap restante.

## 🚀 Installation

```powershell
# Lancer le batch Windows
.\start_UnityAssetsManager.bat
```

Les lanceurs utilisent Python global et installent les dépendances depuis `requirements.txt` avant de démarrer le serveur.

Le serveur démarre sur **http://localhost:5003** par défaut.
REMARQUE : 5003 est le port par défaut de l'interface Web, mais il peut être modifié dans `config/config.json`

## 📖 Utilisation

### Interface principale

1. **Recherche** 🔍: Cherche dans tous les champs en temps réel (côté serveur)
2. **Sélection colonnes** 📋: Choisir les colonnes à afficher (Ctrl+Click pour multiples)
3. **Pagination**: 25/50/100/250 lignes par page (DataTables)
4. **Export** 💾:
   - CSV standard/sémicolon
   - CSV avec URL
   - JSON
   - Markdown table
5. **Profils** 💽: Sauvegarder/charger vos réglages préférés

### Clavier

- **Ctrl+F**: Recherche navigateur (dans la page affichée)
- **Ctrl+C**: Copier le tableau (depuis le navigateur)

## 🔧 Configuration

### Chemin des données

Éditer `app.py` ligne ~40:

```python
DATA_PATH = Path.home() / "Sync" / "PKM_PROJECTS" / "TerraBloom" / "_Fichiers" / "assets.csv"
```

**Sources supportées:**

- ✅ **CSV local** (`.csv`) avec **détection automatique du séparateur** (`,`, `;`, `|`, `\t`)
- ✅ **CSV avec encodage multiple** (UTF-8, latin-1, cp1252)
- ✅ **SQLite** (`.db`, `.sqlite`, `.sqlite3`) avec **sélection de table**
  - Interface `/setup` pour choisir la table
  - Config persistante dans `config.json` (DATA_PATH + DB_TABLE)
  - Support multi-tables (dropdown automatique)
  - **Guide complet**: Voir `_Helpers/SQLITE_SUPPORT.md` pour migration CSV→SQLite, API, troubleshooting et benchmarks

### Répertoires

- `profiles/`: Profils JSON (format: `NomProfil.json`)
- `exports/`: Fichiers exportés
- `.cache/`: Cache interne (1h TTL)

## 📊 API Endpoints

| Url             | Méthode  | Description                      |
| --------------- | -------- | -------------------------------- |
| `/`             | GET      | Page principale                  |
| `/api/data`     | GET      | Données avec pagination/filtrage |
| `/api/columns`  | GET      | Liste des colonnes               |
| `/api/stats`    | GET      | Statistiques                     |
| `/api/export`   | POST     | Exporter données                 |
| `/api/profiles` | GET/POST | Gérer profils                    |
| `/api/reload`   | POST     | Recharger données                |

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

Éditer `DATA_PATH` dans `app.py`

### Port 5003 déjà utilisé

```python
app.run(port=5004)  # Changer port
```

ou bien modifier `FLASK_PORT` dans `config/config.json`

### Ne vois pas mes données

1. Vérifier `DATA_PATH` pointe vers le bon fichier
2. Cliquer 🔄 Recharger (navbar)
3. Vérifier la console (F12 → Console)

## 📝 Notes techniques

### Stack

- **Backend**: Flask 3.0 (Python)
- **Frontend**: Bootstrap 5 + DataTables.js (AJAX pagination)
- **Data**: Pandas (chargement/filtrage CSV/SQLite)
- **Export**: Templates JSONC configurables (11 formats)

### Architecture

```
app.py (serveur Flask, 1214 lignes)
├── /api/data → AssetDataManager.get_data()
├── /api/export → apply_export_template()
├── /api/profiles → load_profile() / save_profile()
└── /api/templates → load_export_templates()

templates/
├── base.html (layout)
└── index.html (tableau + filter builder)

static/
├── css/style.css
└── js/app.js (DataTables + Ajax + export preview)

data/
└── export_templates.jsonc (11 templates configurables)

profiles/
└── *.profile.jsonc (profils V1/V2 compatibles)
```

### Documentation technique

- **Migration V1→V2**: [`MIGRATION STATE V1 to V2.md`](MIGRATION%20STATE%20V1%20to%20V2%20.md) - Matrice complète, gaps, roadmap (8/12 features V1 = 67% parité)
- **Support SQLite**: `_Helpers/SQLITE_SUPPORT.md` - Guide configuration, migration CSV→SQLite, API, troubleshooting, benchmarks
- **Setup**: [`SETUP_CHECKLIST.md`](SETUP_CHECKLIST.md) - Checklist installation et configuration
- **Quickstart**: [`QUICKSTART.md`](QUICKSTART.md) - Guide démarrage rapide
- **Checklist manuelle scriptée**: [`_helpers/MANUAL_CHECKLIST.md`](_helpers/MANUAL_CHECKLIST.md)

### Validation rapide

```powershell
python -m pytest _Helpers/04_Assets/UnityAssetsManager/tests/test_export_non_regression.py -v
pwsh -NoProfile -File _Helpers/04_Assets/UnityAssetsManager/_helpers/runManualChecklist.ps1
python _Helpers/04_Assets/UnityAssetsManager/_helpers/bumpImportantVersion.py --scope patch --dry-run
```

### Prochaines améliorations

Le backlog TODO est centralisé dans [`TODO.md`](TODO.md).

## 📄 License

TerraBloom Project

## 🤝 Support

Pour les bugs: Créer un issue dans le repo TerraBloom

**Documentation complète:**

- Guide migration: [`MIGRATION STATE V1 to V2.md`](MIGRATION%20STATE%20V1%20to%20V2%20.md)
- Support SQLite: [`SQLITE_SUPPORT.md`](SQLITE_SUPPORT.md)
- Setup: [`SETUP_CHECKLIST.md`](SETUP_CHECKLIST.md)
- Quickstart: [`QUICKSTART.md`](QUICKSTART.md)

---

**Version**: 1.1.1
**Dernière mise à jour**: 2026-03-06
**Status**: Production (69% features V2, 67% parité V1)
