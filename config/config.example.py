# ============================================================================
# config.example.py - Configuration exemple
# ============================================================================
# Copier en config.py et adapter pour votre environnement
# ============================================================================

# Chemins des données
DATA_PATH = "H:/Sync/PKM_PROJECTS/TerraBloom/_Fichiers/assets.csv"

# Ou pour SQLite:
# DATA_PATH = "path/to/assets.db"
# DB_TABLE = "assets"

# Configuration serveur Flask
FLASK_DEBUG = True
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5003

# Répertoires
PROFILES_DIR = "profiles"
EXPORTS_DIR = "exports"
CACHE_DIR = ".cache"

# Cache
CACHE_TTL_SECONDS = 3600  # 1 heure
CACHE_MAX_ENTRIES = 100

# DataTables
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 500

# Export
EXPORT_MAX_ROWS = None  # None = pas de limite
EXPORT_TEMPLATES = {
    "CSV standard": {
        "separator": ","
    },
    "CSV with URL": {
        "separator": ",",
        "include_url": True
    },
    "JSON": {
        "format": "json"
    },
    "Markdown": {
        "format": "markdown"
    }
}

# Sécurité
MAX_UPLOAD_SIZE_MB = 100
ALLOWED_EXTENSIONS = {"csv", "xlsx", "json"}

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "logs/unityAssetsManager.log"

# Recherche
FULL_TEXT_SEARCH = True
MIN_SEARCH_LENGTH = 1

# Colonnes par défaut (si None, affiche toutes)
DEFAULT_COLUMNS = None
# Ou spécifier:
# DEFAULT_COLUMNS = ["DisplayName", "DisplayCategory", "DisplayPublisher", "Version"]
