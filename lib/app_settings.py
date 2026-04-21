# ============================================================================
# UnityAssetsManager - app_settings.py
# ============================================================================
# Description: Configuration constants and default application paths.
# Version: 1.2.18
# ============================================================================

from __future__ import annotations

from pathlib import Path

ASSETS_CSV_FILE = "unity_assets_export.csv"

DEFAULT_DB_TABLE = "assets"
DEFAULT_SHOW_PARSER_WARNINGS = False
DEFAULT_CACHE_TTL_SECONDS = 3600

DEFAULT_SERVER_HOST = "127.0.0.1"
DEFAULT_SERVER_PORT = 5003
DEFAULT_FLASK_DEBUG = True
DEFAULT_FLASK_THREADED = True

DEFAULT_SECRET_KEY = "terrabloom-assets-v2"
DEFAULT_MAX_CONTENT_LENGTH_MB = 100
DEFAULT_PAGE_SIZE = 50
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FILE = "app.log"
DEFAULT_LOG_OUTPUT = "console"
DEFAULT_LOG_MAX_BYTES = 1048576
DEFAULT_LOG_BACKUP_COUNT = 3


def build_possible_data_paths(script_dir: Path, assets_csv_file: str = ASSETS_CSV_FILE) -> list[Path]:
    """Retourner les chemins candidats pour la source de donnees Unity."""
    return [
        Path(f"H:/Sync/PKM_PROJECTS/TerraBloom/_Helpers/data/assetsExports/Unity/{assets_csv_file}"),
        script_dir.parent.parent.parent / f"_Helpers/data/assetsExports/Unity/{assets_csv_file}",
        Path.home() / f"Sync/PKM_PROJECTS/TerraBloom/_Helpers/data/assetsExports/Unity/{assets_csv_file}",
    ]


DEFAULT_EXPORT_TEMPLATES = {
    "texte simple sans URL": {
        "description": "Texte simple - une ligne par asset : NOM - EDITEUR - VERSION",
        "pattern": "%DisplayName% - %DisplayPublisher% - %Version%"
    },
    "CSV sans URL": {
        "description": "CSV - une ligne par asset : NOM,EDITEUR,VERSION",
        "pattern": "%DisplayName%,%DisplayPublisher%,%Version%"
    },
    "table markdown sans URL": {
        "description": "Tableau Markdown : NOM | EDITEUR | VERSION",
        "pattern": "| %DisplayName% | %DisplayPublisher% | %Version% |"
    },
    "liste markdown sans URL": {
        "description": "Liste Markdown a puces (sans liens) : NOM - EDITEUR (VERSION)",
        "pattern": "- %DisplayName% - %DisplayPublisher% (%Version%)"
    },
    "texte simple avec URL": {
        "description": "Texte simple avec URL ajoutee : NOM - URL",
        "pattern": "%DisplayName% - %Url%"
    },
    "CSV avec URL": {
        "description": "CSV incluant la colonne Url : NOM,URL,VERSION",
        "pattern": "%DisplayName%,%Url%,%Version%"
    },
    "table markdown avec URL": {
        "description": "Tableau Markdown avec lien sur le nom : NOM(URL) | EDITEUR | CATEGORIE | TAGS",
        "pattern": "| [%DisplayName%](%Url%) | %DisplayPublisher% | %DisplayCategory% | %PackageTags% |"
    },
    "liste markdown avec URL": {
        "description": "Liste Markdown a puces avec lien sur le nom : NOM(URL) - EDITEUR - CATEGORIE - TAGS",
        "pattern": "- [%DisplayName%](%Url%) - %DisplayPublisher% - %DisplayCategory% - %PackageTags%"
    },
    "Issue tracker - liste markdown": {
        "description": "Modele pour tracker d'issues : NOM(URL) - EDITEUR - VERSION - CATEGORIE - TAGS - AVIS",
        "pattern": "- [%DisplayName%](%Url%) - **%DisplayPublisher%** - %DisplayCategory% - Tags: %PackageTags% - Avis: %AssetRating%"
    },
    "Unity AssetStore - liste Markdown": {
        "description": "Liste optimisee pour Asset Store : NOM(URL) - EDITEUR - vVERSION - Source: SOURCE",
        "pattern": "- [%DisplayName%](%Url%) - %DisplayPublisher% - v%Version% - Source: %PackageSource%"
    },
    "CSV EDITEUR (catalogue editeur)": {
        "description": "CSV pour catalogue editeur : NOM,SLUG,URL,VERSION,CATEGORIE,EDITEUR",
        "pattern": "%DisplayName%,%Slug%,%Url%,%Version%,%DisplayCategory%,%DisplayPublisher%"
    }
}
