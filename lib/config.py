# ============================================================================
# UnityAssetsManager - config.py
# ============================================================================
# Description: Runtime configuration and export template management.
# Version: 1.2.18
# ============================================================================

import logging
from pathlib import Path
from urllib.parse import urlparse
import pandas as pd
import re
import json
from .utils import read_json, write_json_normalized, _parse_bool, _parse_int
from .app_settings import (
    DEFAULT_DB_TABLE, DEFAULT_EXPORT_TEMPLATES, DEFAULT_FLASK_DEBUG, DEFAULT_SERVER_HOST, DEFAULT_SERVER_PORT, DEFAULT_FLASK_THREADED,
    DEFAULT_MAX_CONTENT_LENGTH_MB, DEFAULT_SECRET_KEY, DEFAULT_SHOW_PARSER_WARNINGS, DEFAULT_CACHE_TTL_SECONDS, DEFAULT_PAGE_SIZE, DEFAULT_LOG_LEVEL,
    DEFAULT_LOG_FILE, DEFAULT_LOG_OUTPUT, DEFAULT_LOG_MAX_BYTES, DEFAULT_LOG_BACKUP_COUNT, build_possible_data_paths
)

logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).parent.parent
PROFILES_DIR = SCRIPT_DIR / "profiles"
EXPORTS_DIR = SCRIPT_DIR / "exports"
CACHE_DIR = SCRIPT_DIR / ".cache"
CONFIG_FILE = SCRIPT_DIR / "config" / "config.json"
TEMPLATES_FILE = SCRIPT_DIR / "data" / "export_templates.jsonc"

# Ensure directories exist
PROFILES_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)
CONFIG_FILE.parent.mkdir(exist_ok=True)

_ALLOWED_LOG_OUTPUTS = {"console", "file", "both"}


def _normalize_alias_candidate(alias_definition) -> tuple[str | None, str | None]:
    """Normalize a single alias candidate into (source_column, transform_name)."""
    if isinstance(alias_definition, dict):
        source = alias_definition.get("source") or alias_definition.get("column")
        transform = alias_definition.get("transform")
        return (str(source) if source else None, str(transform) if transform else None)
    if alias_definition:
        return (str(alias_definition), None)
    return (None, None)


def _resolve_alias_candidates(alias_map: dict, placeholder: str) -> list[tuple[str, str | None]]:
    """Resolve alias candidates in a case-insensitive way."""
    if not isinstance(alias_map, dict) or not placeholder:
        return []

    # Fast path for exact keys first.
    direct = alias_map.get(placeholder)
    candidates = []
    if isinstance(direct, dict) and (direct.get("candidates") or direct.get("choices")):
        raw_candidates = direct.get("candidates") or direct.get("choices") or []
        for candidate in raw_candidates:
            source, transform = _normalize_alias_candidate(candidate)
            if source:
                candidates.append((source, transform))
        return candidates

    source, transform = _normalize_alias_candidate(direct)
    if source:
        return [(source, transform)]

    placeholder_lower = str(placeholder).lower()
    for alias, target in alias_map.items():
        if str(alias).lower() == placeholder_lower and target is not None:
            if isinstance(target, dict) and (target.get("candidates") or target.get("choices")):
                raw_candidates = target.get("candidates") or target.get("choices") or []
                for candidate in raw_candidates:
                    source, transform = _normalize_alias_candidate(candidate)
                    if source:
                        candidates.append((source, transform))
                return candidates
            source, transform = _normalize_alias_candidate(target)
            if source:
                return [(source, transform)]
    return []


def _resolve_column_name(df: pd.DataFrame, col_name: str) -> str | None:
    """Resolve a DataFrame column name case-insensitively."""
    if not col_name:
        return None

    if col_name in df.columns:
        return col_name

    target_lower = str(col_name).lower()
    for existing_col in df.columns:
        if str(existing_col).lower() == target_lower:
            return str(existing_col)
    return None


def _apply_alias_transform(value, transform: str | None, row: pd.Series | None = None) -> str:
    """Apply a declared transform to an export value."""
    if transform is None:
        return value

    transform_name = str(transform).strip().lower()
    val_str = str(value).strip()

    if transform_name == "asset_store_url":
        if not val_str:
            return val_str
        if val_str.startswith("http"):
            return val_str

        # Variant 1: string ending with -NUMBER (e.g. name-12345)
        if "-" in val_str:
            parts = val_str.split("-")
            if parts[-1].isdigit():
                val_str = parts[-1]

        # Variant 2: purely numeric (3-6 digits) is already val_str
        return f"https://assetstore.unity.com/packages/slug/{val_str}"

    if transform_name == "slug_from_url":
        if not val_str:
            return val_str
        parsed = urlparse(val_str)
        path = parsed.path.rstrip("/")
        candidate = val_str
        if path:
            candidate = path.split("/")[-1]

        # Apply the same extraction logic: if it's a full slug with ID, take only the ID
        if "-" in candidate:
            parts = candidate.split("-")
            if parts[-1].isdigit():
                return parts[-1]
        return candidate

    return value


def _normalize_log_output(value, default_value: str = DEFAULT_LOG_OUTPUT) -> str:
    normalized = str(value or default_value).strip().lower()
    if normalized not in _ALLOWED_LOG_OUTPUTS:
        return default_value
    return normalized


class AppConfig:

    def __init__(self):
        self.load()
        self.export_templates = self.load_export_templates()

    def load(self):
        config_data = {}
        if CONFIG_FILE.exists():
            try:
                config_data = read_json(CONFIG_FILE)
            except Exception:
                pass

        self.db_table = config_data.get('db_table', DEFAULT_DB_TABLE)
        self.show_parser_warnings = _parse_bool(config_data.get('show_parser_warnings'), DEFAULT_SHOW_PARSER_WARNINGS)
        self.server_host = config_data.get('server_host', DEFAULT_SERVER_HOST)
        self.server_port = _parse_int(config_data.get('server_port'), DEFAULT_SERVER_PORT)
        self.flask_debug = _parse_bool(config_data.get('flask_debug'), DEFAULT_FLASK_DEBUG)
        self.flask_threaded = _parse_bool(config_data.get('flask_threaded'), DEFAULT_FLASK_THREADED)
        self.secret_key = config_data.get('secret_key', DEFAULT_SECRET_KEY)
        self.max_content_length_mb = _parse_int(config_data.get('max_content_length_mb'), DEFAULT_MAX_CONTENT_LENGTH_MB)
        self.cache_ttl_seconds = _parse_int(config_data.get('cache_ttl_seconds'), DEFAULT_CACHE_TTL_SECONDS)
        self.default_page_size = _parse_int(config_data.get('default_page_size'), DEFAULT_PAGE_SIZE)
        self.log_level = str(config_data.get('log_level', DEFAULT_LOG_LEVEL)).upper()
        self.log_file = str(config_data.get('log_file', DEFAULT_LOG_FILE))
        self.log_output = _normalize_log_output(config_data.get('log_output', DEFAULT_LOG_OUTPUT), DEFAULT_LOG_OUTPUT)
        self.log_max_bytes = _parse_int(config_data.get('log_max_bytes'), DEFAULT_LOG_MAX_BYTES)
        self.log_backup_count = _parse_int(config_data.get('log_backup_count'), DEFAULT_LOG_BACKUP_COUNT)

        # Determine data_path
        self.data_path = None
        if config_data.get('data_path'):
            path = Path(config_data['data_path'])
            if path.exists():
                self.data_path = path

        if self.data_path is None:
            possible_paths = build_possible_data_paths(SCRIPT_DIR)
            for path in possible_paths:
                if path.exists():
                    self.data_path = path
                    break

        if self.data_path is None:
            self.data_path = build_possible_data_paths(SCRIPT_DIR)[0]

    def save(self, config_data):
        existing_config = {}
        if CONFIG_FILE.exists():
            try:
                existing_config = read_json(CONFIG_FILE)
                if not isinstance(existing_config, dict):
                    existing_config = {}
            except Exception:
                existing_config = {}

        merged_config = {**existing_config, **(config_data or {})}
        write_json_normalized(CONFIG_FILE, merged_config)
        self.load()

    def to_public_runtime_config(self) -> dict:
        return {
            "data_path": str(self.data_path) if self.data_path else None,
            "db_table": self.db_table,
            "show_parser_warnings": self.show_parser_warnings,
            "server_host": self.server_host,
            "server_port": self.server_port,
            "flask_debug": self.flask_debug,
            "flask_threaded": self.flask_threaded,
            "max_content_length_mb": self.max_content_length_mb,
            "cache_ttl_seconds": self.cache_ttl_seconds,
            "default_page_size": self.default_page_size,
            "log_level": self.log_level,
            "log_output": self.log_output,
            "log_max_bytes": self.log_max_bytes,
            "log_backup_count": self.log_backup_count,
        }

    def load_export_templates(self):
        if TEMPLATES_FILE.exists():
            try:
                templates = read_json(TEMPLATES_FILE)
                logger.info(f"📋 {len(templates)} templates d'export chargés depuis {TEMPLATES_FILE.name}")
                return templates
            except Exception as e:
                logger.warning(f"⚠️  Erreur lecture templates.jsonc: {e}, utilisant defaults")
                return DEFAULT_EXPORT_TEMPLATES
        else:
            return DEFAULT_EXPORT_TEMPLATES

    def apply_export_template(self, df: pd.DataFrame, template_name: str, alias_map: dict | None = None) -> str:
        if alias_map is None:
            alias_map = {}

        if not self.export_templates:
            raise ValueError("Aucun template d'export disponible")

        if template_name not in self.export_templates:
            raise ValueError(f"Template '{template_name}' non trouvé.")

        template_obj = self.export_templates[template_name]
        pattern = template_obj.get('pattern', '')

        if not pattern:
            raise ValueError(f"Template '{template_name}' n'a pas de pattern défini")

        if 'JSON' in template_name or template_name.lower() == 'json':
            data_list = df.fillna('').astype(str).to_dict('records')
            return json.dumps({"assets": data_list}, indent=2, ensure_ascii=False)

        column_placeholders = re.findall(r'%([^%]+)%', pattern)

        placeholder_to_col = {}
        used_columns = []
        for ph in column_placeholders:
            actual_col = _resolve_column_name(df, ph)
            alias_transform = None
            alias_candidates = []

            if actual_col is None:
                alias_candidates = _resolve_alias_candidates(alias_map, ph)
                for alias_target, candidate_transform in alias_candidates:
                    resolved_col = _resolve_column_name(df, alias_target)
                    if resolved_col is not None:
                        actual_col = resolved_col
                        alias_transform = candidate_transform
                        break

            if actual_col is not None:
                placeholder_to_col[ph] = (actual_col, alias_transform)
                used_columns.append(ph)
            else:
                if alias_candidates:
                    raise ValueError(f"Colonne manquante pour le placeholder '%{ph}%': aucune source correspondante dans {list(df.columns)}")
                logger.warning(f"Export template placeholder '%{ph}%' could not be resolved (alias_map={alias_map}, df columns={list(df.columns)})")

        logger.debug(f"Export template '{template_name}' mapping: {placeholder_to_col}")
        header_lines = []
        is_markdown_table = '|' in pattern and '{' not in pattern

        if is_markdown_table:
            header = '| ' + ' | '.join(used_columns) + ' |'
            separator = '|' + '|'.join(['---' for _ in used_columns]) + '|'
            header_lines = [header, separator]
        elif ',' in pattern and '[' not in pattern and '(' not in pattern:
            header = ','.join(used_columns)
            header_lines = [header]
        elif pattern.strip().startswith('-') or pattern.strip().startswith('*'):
            header = f"<!-- Colonnes: {', '.join(used_columns)} -->"
            header_lines = [header]
        else:
            header = f"# Colonnes: {', '.join(used_columns)}"
            header_lines = [header]

        lines = []
        for row_idx, (_, row) in enumerate(df.iterrows()):
            line = pattern
            for ph, (actual_col, alias_transform) in placeholder_to_col.items():
                placeholder = f"%{ph}%"
                raw_value = row.get(actual_col, "")
                value = str(raw_value) if pd.notna(raw_value) else ""
                value = _apply_alias_transform(value, alias_transform, row)
                if is_markdown_table and '|' in value:
                    value = value.replace('|', '-')
                line = line.replace(placeholder, value)
                logger.debug(f"Row {row_idx}: placeholder %{ph}% -> column '{actual_col}' -> value '{value}'")
            line = re.sub(r'%[^%]*%', '', line)
            lines.append(line)

        return "\n".join(header_lines + lines)

    def detect_export_format(self, template_name: str) -> tuple[str, str]:
        ext, mimetype = 'txt', 'text/plain'
        if template_name in self.export_templates:
            template_obj = self.export_templates[template_name]
            pattern = template_obj.get('pattern', '').lower()
            name_lower = template_name.lower()

            if 'json' in name_lower:
                ext, mimetype = 'json', 'application/json'
            elif any(x in name_lower for x in ['markdown', 'liste', 'table']):
                ext, mimetype = 'md', 'text/markdown'
            elif 'csv' in name_lower:
                ext, mimetype = 'csv', 'text/csv'
            elif '|' in pattern and '{' not in pattern:
                ext, mimetype = 'md', 'text/markdown'
            elif pattern.strip().startswith(('-', '*')):
                ext, mimetype = 'md', 'text/markdown'
            elif ',' in pattern and '[' not in pattern and '(' not in pattern:
                ext, mimetype = 'csv', 'text/csv'
            elif ('{' in pattern or '[' in pattern) and '](' not in pattern:
                ext, mimetype = 'json', 'application/json'
        return ext, mimetype


# Global instance
config = AppConfig()
