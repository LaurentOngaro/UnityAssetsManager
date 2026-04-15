# ============================================================================
# UnityAssetsManager - config.py
# ============================================================================
# Description: Gestion de la configuration runtime et des templates d'export.
# Version: 1.2.6
# ============================================================================

import logging
from pathlib import Path
import pandas as pd
import re
import json
from utils import read_json, write_json_normalized, _parse_bool, _parse_int
from app_settings import (
    DEFAULT_DB_TABLE, DEFAULT_EXPORT_TEMPLATES, DEFAULT_FLASK_DEBUG, DEFAULT_FLASK_HOST, DEFAULT_FLASK_PORT, DEFAULT_FLASK_THREADED,
    DEFAULT_MAX_CONTENT_LENGTH_MB, DEFAULT_SECRET_KEY, DEFAULT_SHOW_PARSER_WARNINGS, DEFAULT_CACHE_TTL_SECONDS, DEFAULT_PAGE_SIZE, DEFAULT_LOG_LEVEL,
    DEFAULT_LOG_OUTPUT, DEFAULT_LOG_MAX_BYTES, DEFAULT_LOG_BACKUP_COUNT, build_possible_data_paths
)

logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).parent
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
        self.flask_host = config_data.get('flask_host', DEFAULT_FLASK_HOST)
        self.flask_port = _parse_int(config_data.get('flask_port'), DEFAULT_FLASK_PORT)
        self.flask_debug = _parse_bool(config_data.get('flask_debug'), DEFAULT_FLASK_DEBUG)
        self.flask_threaded = _parse_bool(config_data.get('flask_threaded'), DEFAULT_FLASK_THREADED)
        self.secret_key = config_data.get('secret_key', DEFAULT_SECRET_KEY)
        self.max_content_length_mb = _parse_int(config_data.get('max_content_length_mb'), DEFAULT_MAX_CONTENT_LENGTH_MB)
        self.cache_ttl_seconds = _parse_int(config_data.get('cache_ttl_seconds'), DEFAULT_CACHE_TTL_SECONDS)
        self.default_page_size = _parse_int(config_data.get('default_page_size'), DEFAULT_PAGE_SIZE)
        self.log_level = str(config_data.get('log_level', DEFAULT_LOG_LEVEL)).upper()
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
            "flask_host": self.flask_host,
            "flask_port": self.flask_port,
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

    def apply_export_template(self, df: pd.DataFrame, template_name: str) -> str:
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
        used_columns = [col for col in column_placeholders if col in df.columns]

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
        for _, row in df.iterrows():
            line = pattern
            for col in df.columns:
                placeholder = f"%{col}%"
                value = str(row[col]) if pd.notna(row[col]) else ""
                if is_markdown_table and '|' in value:
                    value = value.replace('|', '-')
                line = line.replace(placeholder, value)
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
