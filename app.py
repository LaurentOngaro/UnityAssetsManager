# ============================================================================
# UnityAssetsManager
# ============================================================================
# Description:
#   Gestionnaire d'assets (3800+ lignes) avec interface web rapide
#   - Pagination côté serveur (DataTables.js)
#   - Filtrage côté serveur
#   - Exports: CSV, JSON, Markdown
#   - Profils persistants
#   - Templates d'export configurables
#
# Performance:
#   - Affichage table: 200-400ms (vs 2-5s V1)
#   - Filtrage: requête côté serveur
#   - Exports: génération rapide
#
# Dependencies: flask, pandas, openpyxl (optionnel)
#
# Usage:
#   python app.py
#   Ouverture: http://localhost:5003 (par défaut)
# REMARQUE : 5003 est le port par défaut de l'interface Web, mais il peut être modifié dans `config/config.json`

# Configuration:
#   - DATA_PATH: chemin vers CSV/SQLite source
#   - DB_TABLE: nom de la table SQLite (si applicable)
#   - PROFILES_DIR: répertoire des profils
#   - EXPORTS_DIR: répertoire des exports
#
# Version: 1.1.3
# ============================================================================

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd
from io import BytesIO
import re
import warnings
from typing import Any
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from flask_cors import CORS
import logging

from app_settings import (
    ASSETS_CSV_FILE, DEFAULT_CACHE_TTL_SECONDS, DEFAULT_DB_TABLE, DEFAULT_EXPORT_TEMPLATES, DEFAULT_FLASK_DEBUG, DEFAULT_FLASK_HOST,
    DEFAULT_FLASK_PORT, DEFAULT_FLASK_THREADED, DEFAULT_MAX_CONTENT_LENGTH_MB, DEFAULT_PAGE_SIZE, DEFAULT_SECRET_KEY, DEFAULT_SHOW_PARSER_WARNINGS,
    build_possible_data_paths,
)


def api_error(code: str, message: str, http_status: int, details: dict | None = None):
    """Build a consistent API error payload across all routes."""
    payload = {
        "error": {
            "code": code,
            "message": message,
            "http_status": http_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": request.path,
            "details": details or {}
        }
    }
    return jsonify(payload), http_status


# =====================================
# SETUP CHEMINS ET IMPORTS
# =====================================
SCRIPT_DIR = Path(__file__).parent
HELPERS_DIR = SCRIPT_DIR.parent.parent
ASSET_MANAGER_V1 = HELPERS_DIR / "04_Assets" / "assetManager.py"

sys.path.insert(0, str(HELPERS_DIR))

# Réutiliser les utilitaires du V1
try:
    from lib.jsoncUtils import read_json, write_json_normalized  # type: ignore[reportMissingImports]
except ImportError:
    from _Helpers.lib.jsoncUtils import read_json, write_json_normalized  # type: ignore[reportMissingImports]

# =====================================
# CONFIGURATION
# =====================================

# Déterminer DATA_PATH: Chercher assets.csv dans plusieurs emplacements
POSSIBLE_PATHS = build_possible_data_paths(SCRIPT_DIR)

DATA_PATH = None
for path in POSSIBLE_PATHS:
    if path.exists():
        DATA_PATH = path
        print(f"Fichier source trouvé: {DATA_PATH}")
        break

if DATA_PATH is None:
    print(f"⚠️  ATTENTION: Aucun fichier contenant {ASSETS_CSV_FILE} trouvé. Chemins vérifiés:")
    for path in POSSIBLE_PATHS:
        print(f"  - {path}")
    print("Utilisant le premier chemin comme default (créera une erreur si fichier absent)")
    DATA_PATH = POSSIBLE_PATHS[0]

PROFILES_DIR = SCRIPT_DIR / "profiles"
EXPORTS_DIR = SCRIPT_DIR / "exports"
CACHE_DIR = SCRIPT_DIR / ".cache"
CONFIG_FILE = SCRIPT_DIR / "config" / "config.json"
TEMPLATES_FILE = SCRIPT_DIR / "data" / "export_templates.jsonc"

CONFIG_FILE.parent.mkdir(exist_ok=True)

# Créer les répertoires
PROFILES_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

# =====================================
# GESTION DES TEMPLATES D'EXPORT
# =====================================


def load_export_templates():
    """Charger les templates d'export depuis le fichier JSONC ou utiliser les defaults"""
    global export_templates

    if TEMPLATES_FILE.exists():
        try:
            templates = read_json(TEMPLATES_FILE)
            logger.info(f"📋 {len(templates)} templates d'export chargés depuis {TEMPLATES_FILE.name}")
            return templates
        except Exception as e:
            logger.warning(f"⚠️  Erreur lecture templates.jsonc: {e}, utilisant defaults")
            return DEFAULT_EXPORT_TEMPLATES
    else:
        logger.info(f"📋 Fichier templates.jsonc absent, utilisant {len(DEFAULT_EXPORT_TEMPLATES)} templates par défaut")
        return DEFAULT_EXPORT_TEMPLATES


def apply_export_template(df: pd.DataFrame, template_name: str, url_pattern: str | None = None) -> str:
    """Appliquer un template d'export à un DataFrame.

    Remplace les placeholders %ColumnName% par les valeurs du DataFrame.
    Retourne une string formatée (CSV, Markdown, texte simple, ou JSON).
    """
    if not export_templates:
        raise ValueError("Aucun template d'export disponible")

    if template_name not in export_templates:
        raise ValueError(f"Template '{template_name}' non trouvé. Disponibles: {list(export_templates.keys())}")

    template_obj = export_templates[template_name]
    pattern = template_obj.get('pattern', '')

    if not pattern:
        raise ValueError(f"Template '{template_name}' n'a pas de pattern défini")

    # Cas spécial: JSON
    if 'JSON' in template_name or template_name.lower() == 'json':
        # Convertir en liste de dicts et retourner JSON
        data_list = df.fillna('').astype(str).to_dict('records')
        return json.dumps({"assets": data_list}, indent=2, ensure_ascii=False)

    # Extraire les noms de colonnes du pattern
    import re
    column_placeholders = re.findall(r'%([^%]+)%', pattern)
    # Filtrer pour ne garder que les colonnes qui existent dans le DataFrame
    used_columns = [col for col in column_placeholders if col in df.columns]

    # Déterminer le format et créer l'en-tête
    header_lines = []

    # Déterminer si c'est un format Markdown table (pour échapper les pipes)
    is_markdown_table = '|' in pattern and '{' not in pattern

    # Markdown table : format avec pipes
    if is_markdown_table:
        # En-tête : | Col1 | Col2 | Col3 |
        header = '| ' + ' | '.join(used_columns) + ' |'
        # Séparateur : |---|---|---|
        separator = '|' + '|'.join(['---' for _ in used_columns]) + '|'
        header_lines = [header, separator]

    # CSV : en-tête simple avec virgules
    elif ',' in pattern and '[' not in pattern and '(' not in pattern:
        header = ','.join(used_columns)
        header_lines = [header]

    # Markdown liste ou texte simple : commentaire avec les colonnes
    elif pattern.strip().startswith('-') or pattern.strip().startswith('*'):
        # Pour les listes Markdown, ajouter un commentaire HTML
        header = f"<!-- Colonnes: {', '.join(used_columns)} -->"
        header_lines = [header]

    # Texte simple : commentaire simple
    else:
        header = f"# Colonnes: {', '.join(used_columns)}"
        header_lines = [header]

    # Cas standard: appliquer pattern ligne par ligne
    lines = []
    for _, row in df.iterrows():
        line = pattern
        # Remplacer tous les placeholders %ColumnName%
        for col in df.columns:
            placeholder = f"%{col}%"
            value = str(row[col]) if pd.notna(row[col]) else ""

            # Si c'est un tableau Markdown, échapper les pipes pour ne pas casser le format
            if is_markdown_table and '|' in value:
                value = value.replace('|', '-')

            line = line.replace(placeholder, value)

        # Remplacer les placeholders manquants par vide
        # (pour les colonnes du pattern qui n'existent pas dans le DF)
        line = re.sub(r'%[^%]*%', '', line)

        lines.append(line)

    # Combiner en-tête et lignes
    result_lines = header_lines + lines
    return "\n".join(result_lines)


def _parse_bool(value: Any, default: bool) -> bool:
    """Convertir une valeur potentiellement typée en booléen."""
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _parse_int(value: Any, default: int) -> int:
    """Convertir une valeur potentiellement typée en entier."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def load_config():
    """Charger la configuration depuis config/config.json."""
    if CONFIG_FILE.exists():
        try:
            return read_json(CONFIG_FILE)
        except Exception:
            return {}

    return {}


def save_config(config_data):
    """Sauvegarder la configuration dans config/config.json."""
    CONFIG_FILE.parent.mkdir(exist_ok=True)
    write_json_normalized(CONFIG_FILE, config_data)


# Charger config et override DATA_PATH si défini
config = load_config()
DB_TABLE = config.get('db_table', DEFAULT_DB_TABLE)
# flag pour afficher ou non les warnings de parsing CSV
show_parser_warnings = _parse_bool(config.get('show_parser_warnings'), DEFAULT_SHOW_PARSER_WARNINGS)

FLASK_HOST = config.get('flask_host', DEFAULT_FLASK_HOST)
FLASK_PORT = _parse_int(config.get('flask_port'), DEFAULT_FLASK_PORT)
FLASK_DEBUG = _parse_bool(config.get('flask_debug'), DEFAULT_FLASK_DEBUG)
FLASK_THREADED = _parse_bool(config.get('flask_threaded'), DEFAULT_FLASK_THREADED)
SECRET_KEY = config.get('secret_key', DEFAULT_SECRET_KEY)
MAX_CONTENT_LENGTH_MB = _parse_int(config.get('max_content_length_mb'), DEFAULT_MAX_CONTENT_LENGTH_MB)
CACHE_TTL_SECONDS = _parse_int(config.get('cache_ttl_seconds'), DEFAULT_CACHE_TTL_SECONDS)
DEFAULT_PAGE_SIZE_VALUE = _parse_int(config.get('default_page_size'), DEFAULT_PAGE_SIZE)

if config.get('data_path'):
    config_path = Path(config['data_path'])
    if config_path.exists():
        DATA_PATH = config_path
        print(f"Chemin depuis config: {DATA_PATH}")
        if config.get('db_table'):
            DB_TABLE = config['db_table']
            print(f"Table SQLite: {DB_TABLE}")

# Configuration Flask
app = Flask(__name__, template_folder=str(SCRIPT_DIR / "templates"), static_folder=str(SCRIPT_DIR / "static"))
app.config['SECRET_KEY'] = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH_MB * 1024 * 1024
CORS(app)

# Logger
logging.basicConfig(level=logging.INFO, stream=sys.stdout, encoding='utf-8')
logger = logging.getLogger(__name__)

# Réduire verbosité werkzeug (moins de logs HTTP)
logging.getLogger('werkzeug').setLevel(logging.WARNING)  # Afficher seulement warnings/errors

# Charger les templates d'export
export_templates = load_export_templates()

# =====================================
# GESTION DES DONNÉES
# =====================================


class AssetDataManager:
    """Gestionnaire de données assets avec cache et filtrage côté serveur"""

    _instance: "AssetDataManager | None" = None
    _df: pd.DataFrame | None = None
    _loaded_at: datetime | None = None
    _source_type: str | None = None  # 'csv' ou 'sqlite'

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def detect_source_type(path: Path) -> str:
        """Détecter si source est CSV ou SQLite"""
        suffix = path.suffix.lower()
        if suffix in ['.db', '.sqlite', '.sqlite3']:
            return 'sqlite'
        return 'csv'

    @staticmethod
    def list_sqlite_tables(db_path: Path) -> list[str]:
        """Lister les tables dans une base SQLite"""
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            return tables
        except Exception as e:
            logger.error(f"Erreur listing tables SQLite: {e}")
            return []

    @classmethod
    def load_data(cls, force_reload: bool = False) -> pd.DataFrame:
        """Charger données depuis CSV ou SQLite avec cache (1h)"""
        instance = cls()

        if not force_reload and instance._df is not None and instance._loaded_at is not None:
            age = (datetime.now() - instance._loaded_at).total_seconds()
            if age < CACHE_TTL_SECONDS:
                return instance._df

        try:
            # S'assurer que DATA_PATH est un Path object
            if DATA_PATH is None:
                logger.error("DATA_PATH est None")
                return pd.DataFrame()

            data_path = DATA_PATH if isinstance(DATA_PATH, Path) else Path(str(DATA_PATH))

            logger.info(f"Chargement données: {data_path}")
            if not data_path.exists():
                logger.error(f"Fichier non trouvé: {data_path}")
                return pd.DataFrame()

            # Détecter le type de source
            source_type = cls.detect_source_type(data_path)
            instance._source_type = source_type
            logger.info(f"Type de source détecté: {source_type.upper()}")

            # === SQLITE ===
            if source_type == 'sqlite':
                try:
                    conn = sqlite3.connect(str(data_path))

                    # Lister les tables disponibles
                    tables = cls.list_sqlite_tables(data_path)
                    logger.info(f"Tables disponibles: {tables}")

                    # Utiliser la table configurée ou la première disponible
                    table_name = DB_TABLE if DB_TABLE in tables else (tables[0] if tables else None)

                    if not table_name:
                        logger.error("Aucune table trouvée dans la base SQLite")
                        return pd.DataFrame()

                    logger.info(f"Chargement depuis table: {table_name}")
                    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                    conn.close()

                    logger.info(f"Données SQLite chargées: {len(df)} lignes, {len(df.columns)} colonnes (table: {table_name})")

                except Exception as e:
                    logger.error(f"❌ Erreur chargement SQLite: {e}")
                    return pd.DataFrame()

            # === CSV ===
            else:
                # Tentative 1: Lecture avec détection automatique du séparateur
                try:
                    # pendant la lecture on peut choisir d'ignorer les ParserWarning
                    # lorsque l'application tourne en production
                    with warnings.catch_warnings():
                        if not show_parser_warnings:
                            warnings.simplefilter('ignore', pd.errors.ParserWarning)
                        df = pd.read_csv(
                            data_path,
                            sep=None,  # Détection automatique du séparateur (,;|\t)
                            engine='python',  # Nécessaire pour sep=None
                            dtype_backend='numpy_nullable',
                            on_bad_lines='warn',  # Afficher warning mais continuer
                            encoding='utf-8'
                        )
                    logger.info(f"Données CSV chargées (séparateur auto-détecté): {len(df)} lignes, {len(df.columns)} colonnes")
                except UnicodeDecodeError:
                    # Tentative 2: Encodage différent
                    logger.warning("Tentative avec encodage latin-1...")
                    with warnings.catch_warnings():
                        if not show_parser_warnings:
                            warnings.simplefilter('ignore', pd.errors.ParserWarning)
                        df = pd.read_csv(
                            data_path, sep=None, engine='python', dtype_backend='numpy_nullable', on_bad_lines='warn', encoding='latin-1'
                        )
                    logger.info(f"Données chargées (latin-1, séparateur auto): {len(df)} lignes, {len(df.columns)} colonnes")
                except Exception as parse_error:
                    # Tentative 3: Mode permissif (skip bad lines)
                    logger.warning(f"Erreur parsing standard: {parse_error}")
                    logger.warning("Tentative avec skip bad lines...")
                    df = pd.read_csv(data_path, sep=None, engine='python', dtype_backend='numpy_nullable', on_bad_lines='skip', encoding='utf-8')
                    logger.warning(f"⚠️ Données chargées (lignes malformées ignorées): {len(df)} lignes, {len(df.columns)} colonnes")

            instance._df = df
            instance._loaded_at = datetime.now()
            return df

        except Exception as e:
            logger.error(f"❌ Erreur chargement: {e}")
            logger.error(f"Vérifiez le format du fichier: {DATA_PATH}")
            return pd.DataFrame()

    @classmethod
    def get_data(cls) -> pd.DataFrame:
        """Retourner données (charger si nécessaire)"""
        instance = cls()
        if instance._df is None:
            return instance.load_data()
        return instance._df

    @classmethod
    def reload(cls):
        """Forcer rechargement"""
        instance = cls()
        instance.load_data(force_reload=True)


dm = AssetDataManager()

# =====================================
# UTILITAIRES DE FILTRAGE
# =====================================


def is_tag_column(name: str) -> bool:
    """Déterminer si une colonne doit être traitée comme une colonne de tags.

    La logique est identique à la version historique V1 : on recherche des
    motifs communs dans le nom de la colonne (@@@). Cela permet d'appliquer
    un filtrage vectorisé plus performant pour les colonnes "Tags" qui sont
    stockées sous forme de chaîne séparée par des points-virgules.
    """
    if not isinstance(name, str):
        return False
    n = name.lower()
    # utiliser le même ensemble de motifs que la version historique
    patterns = [r"tag", r"tags", r"category", r"categories", r"genre"]
    return any(re.search(pat, n) for pat in patterns)


def tokenize_cell(cell: str):
    """Scinder une cellule de type tag en tokens en supprimant espaces.

    Cela est utilisé comme fallback si le regex global échoue.
    """
    if not isinstance(cell, str):
        return []
    return [t.strip() for t in re.split(r"[;,|]", cell) if t.strip()]


def vectorized_tag_filter(series: pd.Series, selected_tags: list) -> pd.Series:
    """Filtrage vectorisé pour colonnes de tags.

    Straight portage depuis V1. Retourne une Series booléenne indiquant quelles
    lignes contiennent au moins un des tags demandés.
    """
    if not selected_tags:
        return pd.Series(True, index=series.index)

    escaped_tags = [re.escape(str(tag)) for tag in selected_tags]
    pattern = '|'.join(rf'(?:^|[;,|\s]){tag}(?:[;,|\s]|$)' for tag in escaped_tags)
    try:
        return series.astype(str).str.contains(pattern, case=False, na=False, regex=True)
    except re.error:
        # fallback non-regex
        return series.astype(str).apply(lambda s: any(t in tokenize_cell(s) for t in selected_tags))


def _find_col(cols: list, target: str, alias_map: dict | None = None) -> str | None:
    """Recherche insensible à la casse dans une liste de colonnes.

    Si un alias_map est fourni, il est d'abord utilisé pour traduire la cible.
    """
    if not target:
        return None
    tgt = str(target)
    # match direct
    for c in cols:
        if isinstance(c, str) and c.lower() == tgt.lower():
            return c
    # éventuellement utiliser l'alias_map
    if alias_map:
        canon = alias_map.get(tgt) or alias_map.get(tgt.lower())
        if canon:
            for c in cols:
                if isinstance(c, str) and c.lower() == str(canon).lower():
                    return c
    return None


def _build_alias_map_from_profile(profile: dict | None) -> dict:
    """Construit un mapping alias->canonique à partir d'un profil JSON.

    Le format est { "alias": "CanonicalName" }.
    """
    if not profile or not isinstance(profile, dict):
        return {}
    raw = profile.get('column_aliases') or {}
    if not isinstance(raw, dict):
        return {}
    return {str(k): str(v) for k, v in raw.items()}


def _resolve_col_name(name: str, cols: list, alias_map: dict | None = None) -> str | None:
    """Résout un nom (ou alias) vers la colonne réelle existante dans `cols`.

    Cherche une correspondance insensible à la casse, puis utilise alias_map si
    nécessaire.
    """
    if not name:
        return None
    resolved = _find_col(cols, name, alias_map)
    return resolved


def apply_filter_stack(df: pd.DataFrame, filter_stack: list | None, alias_map: dict | None = None) -> pd.DataFrame:
    """Applique une stack de filtres (profil) à un DataFrame.

    - `filter_stack` est une liste d'objets contenant utilisateurs:
        { mode: 'include'|'exclude', filters: {col: {search, values, is_regex}},
          search_term: str, is_regex: bool }
    - Si `alias_map` est fourni, les noms de colonnes du filtre sont résolus
      via `_resolve_col_name`.
    - La fonction renvoie un nouveau DataFrame filtré.
    """
    if df is None or df.empty:
        return df

    alias_map = alias_map or {}
    filtered_df = df.copy()

    for filter_item in (filter_stack or []):
        mode = filter_item.get('mode', 'include')
        filters = filter_item.get('filters', {}) or {}
        item_search_term = filter_item.get('search_term', '')
        item_mask = pd.Series(True, index=filtered_df.index)

        # appliquer chaque filtre de colonne
        for col, filter_data in filters.items():
            resolved_col = _resolve_col_name(col, list(filtered_df.columns), alias_map)
            if not resolved_col or resolved_col not in filtered_df.columns:
                continue

            search_val = filter_data.get('search', '')
            is_regex = filter_data.get('is_regex', False)
            selected = filter_data.get('values', []) or []

            col_mask = pd.Series(False, index=filtered_df.index)

            if search_val:
                try:
                    if is_regex:
                        col_mask = filtered_df[resolved_col].astype(str).str.contains(search_val, case=False, na=False, regex=True)
                    else:
                        col_mask = filtered_df[resolved_col].astype(str).str.contains(search_val, case=False, na=False)
                except re.error:
                    col_mask = pd.Series(False, index=filtered_df.index)
            elif selected:
                if is_tag_column(resolved_col):
                    if '[Vide]' in selected:
                        selected_clean = [v for v in selected if v != '[Vide]']
                        col_mask = filtered_df[resolved_col].isna() | vectorized_tag_filter(filtered_df[resolved_col], selected_clean)
                    else:
                        col_mask = vectorized_tag_filter(filtered_df[resolved_col], selected)
                else:
                    if '[Vide]' in selected:
                        selected_clean = [v for v in selected if v != '[Vide]']
                        col_mask = filtered_df[resolved_col].isin(selected_clean) | filtered_df[resolved_col].isna()
                    else:
                        col_mask = filtered_df[resolved_col].isin(selected)

            item_mask &= col_mask

        # recherche globale pour l'item
        if item_search_term:
            item_search_regex = filter_item.get('is_regex', False)
            try:
                if '__search_blob__' in filtered_df.columns:
                    if item_search_regex:
                        search_mask = filtered_df['__search_blob__'].str.contains(item_search_term.lower(), case=False, na=False, regex=True)
                    else:
                        search_mask = filtered_df['__search_blob__'].str.contains(item_search_term.lower(), case=False, na=False, regex=False)
                else:
                    if item_search_regex:
                        search_mask = filtered_df.astype(str).apply(
                            lambda row: row.str.contains(item_search_term, case=False, na=False, regex=True).any(), axis=1
                        )
                    else:
                        search_mask = filtered_df.astype(str).apply(
                            lambda row: row.str.contains(item_search_term, case=False, na=False).any(), axis=1
                        )  #
                item_mask &= search_mask
            except re.error:
                pass

        # appliquer include/exclude
        if mode == 'include':
            filtered_df = filtered_df[item_mask]
        else:
            filtered_df = filtered_df[~item_mask]

    return filtered_df


# =====================================
# PROFILS
# =====================================


def save_profile(profile_name, profile_data):
    """Écrire un profil sur disque (JSONC)."""
    # toujours utiliser extension .jsonc pour être cohérent
    profile_file = PROFILES_DIR / f"{profile_name}.jsonc"
    write_json_normalized(profile_file, profile_data)
    logger.info(f"Profil sauvegardé: {profile_name} -> {profile_file.name} ({len(profile_data.get('columns', []))} colonnes)")


def load_profile(profile_name):
    """Charger un profil depuis fichier.

    Le paramètre peut être soit la base (sans extension) soit inclure
    ".profile". On tente plusieurs variantes pour retrouver le fichier réel
    sur disque : `<base>.jsonc`, `<base>.profile.jsonc`, `<base>.profile`.
    Si trouvé, on normalise la structure pour renvoyer un dict avec un champ
    `columns` utilisable par le front-end.
    """
    # construire les variantes possibles de noms de fichier
    base = profile_name
    candidates = []
    if base.endswith('.profile'):
        candidates.append(f"{base}.jsonc")  # nom.profile.jsonc
        candidates.append(f"{base}")  # nom.profile
    else:
        candidates.append(f"{base}.jsonc")  # nom.jsonc (éventuel)
        candidates.append(f"{base}.profile.jsonc")
        candidates.append(f"{base}.profile")

    profile_file = None
    for cand in candidates:
        candidate_path = PROFILES_DIR / cand
        if candidate_path.exists():
            profile_file = candidate_path
            break

    if profile_file is None:
        logger.warning(f"❌ Aucun fichier de profil trouvé parmi: {candidates}")
        return None

    logger.info(f"📖 Chargement du fichier: {profile_file}")
    profile_data = read_json(profile_file)
    logger.info(f"📖 Données brutes lues: type={type(profile_data)}, keys={list(profile_data.keys()) if isinstance(profile_data, dict) else 'N/A'}")

    # normaliser
    if isinstance(profile_data, dict):
        normalized = {"name": profile_data.get("name", profile_name), "columns": []}
        if "columns" in profile_data and isinstance(profile_data["columns"], list):
            normalized["columns"] = profile_data["columns"]
        elif "column_profile" in profile_data and isinstance(profile_data["column_profile"], dict):
            normalized["columns"] = profile_data["column_profile"].get("cols", [])
        else:
            logger.warning("⚠️ Pas de colonnes trouvées dans le profil, liste vide renvoyée")

        # conserver champs additionnels
        for key in ["description", "lastUpdated", "updatedBy", "filter_columns", "filter_stack", "column_aliases", "column_profile"]:
            if key in profile_data:
                normalized[key] = profile_data[key]

        logger.info(f"📖 Profil normalisé: columns={len(normalized['columns'])}")
        return normalized

    return profile_data


def list_profiles():
    """Lister tous les profils"""
    try:
        # Chercher les fichiers .jsonc et .profile
        jsonc_profiles = [f.stem for f in PROFILES_DIR.glob("*.jsonc")]
        profile_profiles = [f.stem for f in PROFILES_DIR.glob("*.profile")]

        # Combiner et dédupliquer
        all_profiles = list(set(jsonc_profiles + profile_profiles))
        all_profiles = sorted(all_profiles)

        logger.info(f"Profils listés: {len(all_profiles)} trouvés")
        logger.debug(f"   .jsonc: {jsonc_profiles}")
        logger.debug(f"   .profile: {profile_profiles}")
        return all_profiles
    except Exception as e:
        logger.error(f"❌ Erreur listing profils: {e}")
        return []


def detect_export_format(template_name: str) -> tuple[str, str]:
    """Déterminer extension et MIME type à partir du template d'export."""
    ext = 'txt'
    mimetype = 'text/plain'

    if template_name in export_templates:
        template_obj = export_templates[template_name]
        pattern = template_obj.get('pattern', '').lower()
        template_name_lower = template_name.lower()

        # 1. Vérifier d'abord le nom explicite du template
        if 'json' in template_name_lower:
            ext = 'json'
            mimetype = 'application/json'
        elif 'markdown' in template_name_lower or 'liste' in template_name_lower or 'table' in template_name_lower:
            ext = 'md'
            mimetype = 'text/markdown'
        elif 'csv' in template_name_lower:
            ext = 'csv'
            mimetype = 'text/csv'
        # 2. Si pas trouvé, analyser le pattern
        elif '|' in pattern and '{' not in pattern:
            ext = 'md'
            mimetype = 'text/markdown'
        elif pattern.strip().startswith('-') or pattern.strip().startswith('*'):
            ext = 'md'
            mimetype = 'text/markdown'
        elif ',' in pattern and '[' not in pattern and '(' not in pattern:
            ext = 'csv'
            mimetype = 'text/csv'
        elif ('{' in pattern or '[' in pattern) and '](' not in pattern:
            ext = 'json'
            mimetype = 'application/json'

    return ext, mimetype


# =====================================
# ROUTES API
# =====================================


@app.route('/')
def index():
    """Page principale"""
    df = dm.get_data()

    # Vérifier si les données sont disponibles
    if df is None or df.empty:
        # Rediriger vers page de configuration
        return redirect(url_for('setup'))

    columns = list(df.columns)
    profiles = list_profiles()

    return render_template(
        'index.html',
        columns=columns,
        profiles=profiles,
        templates=list(export_templates.keys()),
        row_count=len(df),
        show_parser_warnings=show_parser_warnings
    )


@app.route('/api/data', methods=['GET'])
def api_data():
    """API: retourner données avec pagination/filtrage côté serveur"""
    df = dm.get_data()

    if df.empty:
        return jsonify({"draw": request.args.get('draw', 1, type=int), "recordsTotal": 0, "recordsFiltered": 0, "data": []})

    # Récupérer parameters DataTables
    draw = request.args.get('draw', 1, type=int)
    start = request.args.get('start', 0, type=int)
    length = request.args.get('length', DEFAULT_PAGE_SIZE_VALUE, type=int)
    search_value = request.args.get('search[value]', '')
    # DataTables envoie aussi un flag regex
    is_regex = request.args.get('search[regex]', 'false').lower() == 'true'

    # Appliquer filtrage
    filtered_df = df.copy()

    # recherche textuelle classique (sur TOUTES les colonnes)
    if search_value:
        logger.debug(f"🔍 Recherche globale: '{search_value}' (regex={is_regex})")
        # Conversion en string pour la recherche, puis application du masque
        # On utilise une approche plus robuste pour éviter les erreurs de type
        mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search_value, case=False, na=False, regex=is_regex)).any(axis=1)
        filtered_df = filtered_df[mask]
        logger.debug(f"🔍 Résultats après recherche globale: {len(filtered_df)} lignes")

    # paramètres de filtre avancés (profil)
    raw_filter_stack = request.args.get('filter_stack')
    raw_alias_map = request.args.get('alias_map')
    filter_stack = []
    alias_map = {}
    try:
        if raw_filter_stack:
            filter_stack = json.loads(raw_filter_stack)
        if raw_alias_map:
            alias_map = json.loads(raw_alias_map)
    except Exception as e:
        logger.warning(f"⚠️ Impossible de parser les paramètres de filtre: {e}")

    if filter_stack:
        logger.debug(f"Application filter_stack ({len(filter_stack)} items) avec alias_map keys={list(alias_map.keys())}")
        filtered_df = apply_filter_stack(filtered_df, filter_stack, alias_map)

    # Pagination
    records_filtered = len(filtered_df)
    paginated_df = filtered_df.iloc[start:start + length]

    # Convertir en JSON-safe (remplacer NaN/Nat) - Retourner comme objets
    data = paginated_df.fillna('').astype(str).to_dict('records')

    return jsonify({"draw": draw, "recordsTotal": len(df), "recordsFiltered": records_filtered, "data": data})


@app.route('/api/columns', methods=['GET'])
def api_columns():
    """API: lister les colonnes disponibles"""
    df = dm.get_data()
    return jsonify({"columns": list(df.columns), "count": len(df.columns)})


@app.route('/api/profiles', methods=['GET'])
def api_profiles():
    """API: lister les profils"""
    profiles = list_profiles()
    logger.debug(f"📋 Profils trouvés: {profiles} (dossier: {PROFILES_DIR})")
    return jsonify({"profiles": profiles})


@app.route('/api/templates', methods=['GET'])
def api_templates():
    """API: lister les templates d'export disponibles"""
    templates_list = [
        {
            "name": name,
            "description": obj.get('description', ''),
            "pattern": obj.get('pattern', '')
        } for name, obj in export_templates.items()
    ]
    logger.debug(f"📋 Templates retournés: {len(templates_list)} disponibles")
    return jsonify({"templates": templates_list})


@app.route('/api/config', methods=['POST'])
def api_update_config():
    """API: mettre à jour la configuration (clé unique pour l'instant)"""
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            raise ValueError("JSON invalid for config")
        # mettre à jour et réagir aux clés connues
        global show_parser_warnings
        for k, v in data.items():
            config[k] = v
            if k == 'show_parser_warnings':
                show_parser_warnings = bool(v)
        save_config(config)
        logger.info(f"⚙️ Configuration mise à jour: {data}")
        return jsonify({"success": True, "config": config})
    except Exception as e:
        logger.error(f"❌ Erreur mise à jour config: {e}")
        return api_error("CONFIG_UPDATE_FAILED", "Impossible de mettre a jour la configuration", 400, {"exception": str(e)})


@app.route('/api/profiles/<name>', methods=['GET'])
def api_profile_detail(name):
    """API: détail d'un profil"""
    logger.info(f"📖 [API] Demande de profil: {name}")
    profile = load_profile(name)

    if profile:
        logger.info("[API] Profil trouvé")
        logger.info(f"   Type: {type(profile)}")

        if isinstance(profile, dict):
            logger.info(f"   Keys: {list(profile.keys())}")
            if 'columns' in profile:
                cols = profile['columns']
                logger.info(f"   ✅ Clé 'columns' trouvée: {len(cols) if cols else 0} colonnes")
                if cols:
                    logger.debug(f"      Colonnes: {cols[:3]}..." if len(cols) > 3 else f"      Colonnes: {cols}")
            else:
                logger.warning("   ⚠️ Profil sans colonne explicite")

        return jsonify(profile)

    logger.warning(f"❌ [API] Profil non trouvé: {name}")
    return api_error("PROFILE_NOT_FOUND", "Profil non trouve", 404, {"profile": name})


@app.route('/api/profiles/<name>', methods=['DELETE'])
def api_delete_profile(name):
    """API: supprimer un profil"""
    # Essayer .jsonc puis .profile
    profile_file = PROFILES_DIR / f"{name}.jsonc"
    if not profile_file.exists():
        profile_file = PROFILES_DIR / f"{name}.profile"

    if profile_file.exists():
        profile_file.unlink()
        logger.info(f"Profil supprimé: {name} ({profile_file.name})")
        return jsonify({"success": True, "name": name})

    logger.warning(f"❌ Profil non trouvé pour suppression: {name}")
    return api_error("PROFILE_NOT_FOUND", "Profil non trouve", 404, {"profile": name})


@app.route('/api/profiles', methods=['POST'])
def api_save_profile():
    """API: sauvegarder un profil"""
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            return api_error("INVALID_PAYLOAD", "JSON invalide ou manquant", 400)
        name = data.get('name')
        if not name:
            logger.warning("❌ Nom de profil manquant")
            return api_error("MISSING_PROFILE_NAME", "Nom de profil requis", 400)

        logger.info(f"💾 Sauvegarde demandée: profil '{name}'")
        save_profile(name, data)
        return jsonify({"success": True, "name": name})
    except Exception as e:
        logger.error(f"❌ Erreur sauvegarde profil: {e}", exc_info=True)
        return api_error("PROFILE_SAVE_FAILED", "Erreur lors de la sauvegarde du profil", 500, {"exception": str(e)})


@app.route('/api/export', methods=['POST'])
def api_export():
    """API: exporter les données avec filtres appliqués"""
    try:
        df = dm.get_data()
        data = request.get_json()

        if not isinstance(data, dict):
            logger.warning("Export: JSON invalide ou manquant")
            return api_error("INVALID_PAYLOAD", "JSON invalide ou manquant", 400)

        template_name = data.get('template', 'CSV standard')
        # format_type = data.get('format', 'csv')
        columns = data.get('columns', [])
        search_value = data.get('search', '')

        # lire paramètres avancés de filtrage
        # filter_columns = data.get('filter_columns', [])
        filter_stack = data.get('filter_stack', [])
        alias_map = data.get('alias_map', {})

        logger.debug(f"Export demandé: template={template_name}, cols={len(columns)}, search='{search_value}', filters={len(filter_stack)}")

        # Appliquer filtrage recherche (même logique que /api/data)
        export_df = df.copy()
        if search_value:
            mask = export_df.astype(str).apply(lambda x: x.str.contains(search_value, case=False, na=False)).any(axis=1)
            export_df = export_df[mask]
            logger.info(f"Export: filtre recherche '{search_value}' appliqué, {len(export_df)} lignes")

        # Appliquer stack de filtres si fourni
        if filter_stack:
            try:
                logger.debug(f"Export: appliquant filter_stack ({len(filter_stack)} items)")
                export_df = apply_filter_stack(export_df, filter_stack, alias_map)
                logger.info(f"Export: après filter_stack, {len(export_df)} lignes")
            except Exception as e:
                logger.error(f"Erreur application filtres avant export: {e}", exc_info=True)
                return api_error("EXPORT_FILTER_ERROR", "Erreur lors de l'application des filtres", 400, {"exception": str(e)})

        # Filtrer colonnes
        if columns:
            valid_cols = [c for c in columns if c in export_df.columns]
            if not valid_cols:
                logger.warning(f"Export: aucune colonne valide parmi {columns}")
                valid_cols = list(export_df.columns)
            export_df = export_df[valid_cols]

        logger.info(f"Export: préparant {len(export_df)} lignes × {len(export_df.columns)} colonnes")

        # Appliquer template
        url_pattern = data.get('url_pattern')
        try:
            output = apply_export_template(export_df, template_name, url_pattern)
        except Exception as e:
            logger.error(f"Erreur génération template '{template_name}': {e}", exc_info=True)
            return api_error(
                "EXPORT_TEMPLATE_ERROR", "Erreur de generation du template d'export", 400, {
                    "template": template_name,
                    "exception": str(e)
                }
            )

        # Déterminer l'extension et le MIME type en analysant le template
        ext, mimetype = detect_export_format(template_name)

        # Préparer nom de fichier
        filename = f"assets_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"

        logger.info(f"Export: génération fichier {filename} ({len(output)} caractères)")

        return send_file(BytesIO(output.encode('utf-8')), mimetype=mimetype, as_attachment=True, download_name=filename)

    except Exception as e:
        logger.error(f"Erreur glob export: {e}", exc_info=True)
        return api_error("EXPORT_FAILED", "Erreur lors de l'export", 500, {"exception": str(e)})


@app.route('/api/batch-export', methods=['POST'])
def api_batch_export():
    """API: exporter les données en mode headless vers un fichier local."""
    try:
        df = dm.get_data()
        data = request.get_json()

        if not isinstance(data, dict):
            logger.warning("Batch export: JSON invalide ou manquant")
            return api_error("INVALID_PAYLOAD", "JSON invalide ou manquant", 400)

        template_name = data.get('template', 'CSV standard')
        columns = data.get('columns', [])
        search_value = data.get('search', '')

        filter_stack = data.get('filter_stack', [])
        alias_map = data.get('alias_map', {})

        logger.info(f"Batch export demandé: template={template_name}, cols={len(columns)}, search='{search_value}', filters={len(filter_stack)}")

        export_df = df.copy()

        if search_value:
            mask = export_df.astype(str).apply(lambda x: x.str.contains(search_value, case=False, na=False)).any(axis=1)
            export_df = export_df[mask]

        if filter_stack:
            try:
                export_df = apply_filter_stack(export_df, filter_stack, alias_map)
            except Exception as e:
                logger.error(f"Erreur application filtres avant batch export: {e}", exc_info=True)
                return api_error("EXPORT_FILTER_ERROR", "Erreur lors de l'application des filtres", 400, {"exception": str(e)})

        if columns:
            valid_cols = [c for c in columns if c in export_df.columns]
            if not valid_cols:
                logger.warning(f"Batch export: aucune colonne valide parmi {columns}")
                valid_cols = list(export_df.columns)
            export_df = export_df[valid_cols]

        url_pattern = data.get('url_pattern')
        try:
            output = apply_export_template(export_df, template_name, url_pattern)
        except Exception as e:
            logger.error(f"Erreur génération template batch '{template_name}': {e}", exc_info=True)
            return api_error(
                "EXPORT_TEMPLATE_ERROR", "Erreur de generation du template d'export", 400, {
                    "template": template_name,
                    "exception": str(e)
                }
            )

        ext, _ = detect_export_format(template_name)

        requested_filename = str(data.get('file_name', '')).strip()
        if requested_filename:
            safe_name = Path(requested_filename).name
            if Path(safe_name).suffix:
                filename = safe_name
            else:
                filename = f"{safe_name}.{ext}"
        else:
            filename = f"assets_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"

        output_dir_raw = str(data.get('output_dir', '')).strip()
        if output_dir_raw:
            output_dir = Path(output_dir_raw)
            if not output_dir.is_absolute():
                output_dir = (SCRIPT_DIR / output_dir).resolve()
        else:
            output_dir = EXPORTS_DIR

        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / filename
        output_path.write_text(output, encoding='utf-8')

        logger.info(f"Batch export écrit: {output_path}")

        return jsonify(
            {
                "success": True,
                "path": str(output_path),
                "filename": filename,
                "rows": len(export_df),
                "columns": len(export_df.columns),
                "template": template_name,
                "bytes": len(output.encode('utf-8'))
            }
        )

    except Exception as e:
        logger.error(f"Erreur batch export: {e}", exc_info=True)
        return api_error("BATCH_EXPORT_FAILED", "Erreur lors du batch export", 500, {"exception": str(e)})


@app.route('/api/stats', methods=['GET'])
def api_stats():
    """API: statistiques sur les données"""
    df = dm.get_data()

    if df.empty:
        return api_error("NO_DATA", "Pas de donnees", 400)

    stats = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": list(df.columns),
        "sample": df.head(5).fillna('').astype(str).values.tolist()
    }

    return jsonify(stats)


@app.route('/api/reload', methods=['POST'])
def api_reload():
    """API: recharger les données depuis le fichier"""
    dm.reload()
    df = dm.get_data()
    return jsonify({"success": True, "rows": len(df), "columns": len(df.columns)})


@app.route('/setup')
def setup():
    """Page de configuration du chemin de données"""
    current_path = str(DATA_PATH)
    current_path_exists = Path(current_path).exists()

    # Eviter les doublons visuels quand plusieurs chemins candidats resolvent vers
    # la meme destination (ex: absolu + relatif pointant au meme fichier).
    unique_searched_paths = []
    seen_paths = set()
    for candidate in POSSIBLE_PATHS:
        resolved = str(candidate.resolve())
        if resolved in seen_paths:
            continue
        seen_paths.add(resolved)
        unique_searched_paths.append(candidate)

    return render_template(
        'setup.html',
        filename=ASSETS_CSV_FILE,
        searched_paths=unique_searched_paths,
        current_path=current_path,
        current_path_exists=current_path_exists
    )


@app.route('/api/setup', methods=['POST'])
def api_setup():
    """API: sauvegarder la configuration du chemin (CSV ou SQLite)"""
    try:
        data = request.get_json()
        new_path = data.get('data_path')
        db_table = data.get('db_table', DEFAULT_DB_TABLE)

        if not new_path:
            return api_error("MISSING_DATA_PATH", "Chemin requis", 400)

        path_obj = Path(new_path)
        if not path_obj.exists():
            return api_error("DATA_PATH_NOT_FOUND", "Fichier introuvable", 400, {"path": str(path_obj)})

        # Sauvegarder dans config
        config = load_config()
        config['data_path'] = str(path_obj)

        # Si SQLite, sauvegarder le nom de la table
        source_type = AssetDataManager.detect_source_type(path_obj)
        if source_type == 'sqlite':
            config['db_table'] = db_table
            logger.info(f"Table SQLite configurée: {db_table}")

        save_config(config)

        # Mettre à jour DATA_PATH + DB_TABLE globaux et recharger
        global DATA_PATH, DB_TABLE
        DATA_PATH = path_obj
        logger.info(f"DATA_PATH mis à jour (type={type(DATA_PATH).__name__}): {DATA_PATH}")

        if source_type == 'sqlite':
            DB_TABLE = db_table
            logger.info(f"DB_TABLE mis à jour: {DB_TABLE}")

        # Créer une instance pour recharger
        try:
            logger.info("🔄 Rechargement des données en cours...")
            AssetDataManager.reload()
            logger.info("Rechargement réussi")
        except Exception as reload_error:
            logger.error(f"⚠️ Vérification du rechargement: {reload_error}")
            # Continuer en cas d'erreur, ça va se charger à la première requête

        return jsonify(
            {
                "success": True,
                "data_path": str(DATA_PATH),
                "source_type": source_type,
                "db_table": DB_TABLE if source_type == 'sqlite' else None
            }
        )

    except Exception as e:
        logger.error(f"❌ Erreur /api/setup: {str(e)}", exc_info=True)
        return api_error("SETUP_FAILED", "Erreur lors de la sauvegarde de la configuration", 500, {"exception": str(e)})


@app.route('/api/test-path', methods=['POST'])
def api_test_path():
    """API: tester si un chemin existe et est lisible (CSV ou SQLite)"""
    data = request.get_json()
    if not isinstance(data, dict):
        return api_error("INVALID_PAYLOAD", "JSON invalide ou manquant", 400)
    test_path = data.get('path')

    if not test_path:
        return jsonify({"exists": False, "code": "PATH_EMPTY", "message": "Chemin requis"})

    path_obj = Path(test_path)
    if not path_obj.exists():
        return jsonify({"exists": False, "code": "PATH_NOT_FOUND", "message": "Chemin introuvable"})

    # Détecter le type
    source_type = AssetDataManager.detect_source_type(path_obj)

    # === SQLITE ===
    if source_type == 'sqlite':
        try:
            tables = AssetDataManager.list_sqlite_tables(path_obj)
            if not tables:
                return jsonify({"exists": False, "code": "SQLITE_NO_TABLE", "message": "Aucune table detectee dans la base SQLite"})

            # Lire la première table pour avoir stats
            conn = sqlite3.connect(str(path_obj))
            first_table = tables[0]
            test_df = pd.read_sql_query(f"SELECT * FROM {first_table} LIMIT 5", conn)
            row_count = pd.read_sql_query(f"SELECT COUNT(*) as cnt FROM {first_table}", conn).iloc[0]['cnt']
            conn.close()

            return jsonify({"exists": True, "type": "sqlite", "tables": tables, "rows": int(row_count), "cols": len(test_df.columns)})
        except Exception as e:
            logger.warning(f"Test chemin SQLite invalide: {e}")
            return jsonify({"exists": False, "code": "SQLITE_READ_ERROR", "message": "Fichier SQLite invalide ou non lisible"})

    # === CSV ===
    else:
        encodings_to_try = ["utf-8", "latin-1"]
        last_error: Exception | None = None

        for encoding in encodings_to_try:
            try:
                # Vérifier rapidement l'entête/structure sur un petit échantillon.
                test_df = pd.read_csv(path_obj, sep=None, engine='python', nrows=5, encoding=encoding)

                warning_message = None
                try:
                    # Compter les lignes en mode strict quand possible.
                    full_df_rows = len(pd.read_csv(path_obj, sep=None, engine='python', encoding=encoding))
                except pd.errors.ParserError as parse_error:
                    # Si quelques lignes sont malformées, rester compatible avec le chargement réel.
                    logger.info(f"Test chemin CSV parse warning ({encoding}): {parse_error}")
                    full_df_rows = len(pd.read_csv(path_obj, sep=None, engine='python', encoding=encoding, on_bad_lines='skip'))
                    warning_message = "Certaines lignes CSV sont malformees et seront ignorees"

                payload = {"exists": True, "type": "csv", "rows": int(full_df_rows), "cols": len(test_df.columns)}
                if warning_message:
                    payload["warning"] = warning_message
                return jsonify(payload)

            except UnicodeDecodeError as e:
                last_error = e
                continue
            except Exception as e:
                last_error = e
                continue

        if isinstance(last_error, UnicodeDecodeError):
            logger.warning(f"Test chemin CSV encodage invalide: {last_error}")
            return jsonify({"exists": False, "code": "CSV_ENCODING_ERROR", "message": "CSV illisible (encodage non supporte)"})

        if isinstance(last_error, pd.errors.ParserError):
            logger.warning(f"Test chemin CSV parse error: {last_error}")
            return jsonify({"exists": False, "code": "CSV_PARSE_ERROR", "message": "CSV invalide (format ou guillemets)"})

        logger.warning(f"Test chemin CSV invalide: {last_error}")
        return jsonify({"exists": False, "code": "CSV_READ_ERROR", "message": "Impossible de lire le fichier CSV"})


# =====================================
# GESTION ERREURS
# =====================================


@app.errorhandler(404)
def not_found(error):
    return api_error("NOT_FOUND", "Page non trouvee", 404)


@app.errorhandler(500)
def server_error(error):
    logger.error(f"Erreur serveur: {error}")
    return api_error("SERVER_ERROR", "Erreur serveur", 500)


# =====================================
# MAIN
# =====================================

if __name__ == '__main__':
    logger.info("Demarrage UnityAssetsManager Flask")
    logger.info(f"Source données: {DATA_PATH}")
    logger.info(f"Profils: {PROFILES_DIR}")
    logger.info(f"Exports: {EXPORTS_DIR}")

    # Précharger données
    dm.load_data()

    app.run(debug=FLASK_DEBUG, host=FLASK_HOST, port=FLASK_PORT, threaded=FLASK_THREADED)
