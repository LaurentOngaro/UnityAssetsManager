# ============================================================================
# UnityAssetsManager - routes.py
# ============================================================================
# Description: Web route definitions and API endpoints.
# Version: 1.3.1
# ============================================================================

import logging
import sqlite3
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
from flask import render_template, request, jsonify, send_file, redirect, url_for, Blueprint
from io import BytesIO

from .config import config, PROFILES_DIR, EXPORTS_DIR, SCRIPT_DIR
from .utils import read_json, write_json_normalized, _parse_bool, _parse_int
from .data_manager import dm
from .filters import apply_filter_stack, _build_alias_map_from_profile, filter_invalid_assets
from .errors import AppError, ErrorCode
from .logging_setup import configure_logging

logger = logging.getLogger(__name__)

bp = Blueprint('main', __name__)

_ALLOWED_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
_ALLOWED_LOG_OUTPUTS = {"console", "file", "both"}
_ALLOWED_CONFIG_UPDATE_FIELDS = {"db_table", "show_parser_warnings", "log_level", "log_output", "log_max_bytes", "log_backup_count", }


def _read_version() -> str:
    version_file = SCRIPT_DIR / "VERSION.txt"
    if version_file.exists():
        return version_file.read_text(encoding="utf-8").strip()
    return "unknown"


def _validate_config_patch(payload: dict) -> dict:
    unknown_fields = sorted(set(payload.keys()) - _ALLOWED_CONFIG_UPDATE_FIELDS)
    if unknown_fields:
        raise AppError(ErrorCode.INVALID_PAYLOAD, "Parametres non autorises", 400, details={"unknown_fields": unknown_fields}, )

    patch = {}

    if "db_table" in payload:
        db_table = str(payload.get("db_table") or "").strip()
        if not db_table:
            raise AppError(ErrorCode.INVALID_CONFIG, "db_table ne peut pas etre vide", 400)
        patch["db_table"] = db_table

    if "show_parser_warnings" in payload:
        patch["show_parser_warnings"] = _parse_bool(payload.get("show_parser_warnings"), config.show_parser_warnings)

    if "log_level" in payload:
        log_level = str(payload.get("log_level") or "").strip().upper()
        if log_level not in _ALLOWED_LOG_LEVELS:
            raise AppError(ErrorCode.INVALID_CONFIG, "log_level invalide", 400, details={"allowed": sorted(_ALLOWED_LOG_LEVELS)}, )
        patch["log_level"] = log_level

    if "log_output" in payload:
        log_output = str(payload.get("log_output") or "").strip().lower()
        if log_output not in _ALLOWED_LOG_OUTPUTS:
            raise AppError(ErrorCode.INVALID_CONFIG, "log_output invalide", 400, details={"allowed": sorted(_ALLOWED_LOG_OUTPUTS)}, )
        patch["log_output"] = log_output

    if "log_max_bytes" in payload:
        log_max_bytes = _parse_int(payload.get("log_max_bytes"), -1)
        if log_max_bytes <= 0:
            raise AppError(ErrorCode.INVALID_CONFIG, "log_max_bytes doit etre > 0", 400)
        patch["log_max_bytes"] = log_max_bytes

    if "log_backup_count" in payload:
        log_backup_count = _parse_int(payload.get("log_backup_count"), -1)
        if log_backup_count <= 0:
            raise AppError(ErrorCode.INVALID_CONFIG, "log_backup_count doit etre > 0", 400)
        patch["log_backup_count"] = log_backup_count

    if not patch:
        raise AppError(ErrorCode.INVALID_PAYLOAD, "Aucun parametre a mettre a jour", 400)

    return patch


# --- Profiles Management ---


def save_profile(profile_name, profile_data):
    profile_file = PROFILES_DIR / f"{profile_name}.jsonc"
    write_json_normalized(profile_file, profile_data)


def load_profile(profile_name):
    base = profile_name
    candidates = []
    if base.endswith('.profile'):
        candidates.extend([f"{base}.jsonc", f"{base}"])
    else:
        candidates.extend([f"{base}.jsonc", f"{base}.profile.jsonc", f"{base}.profile"])

    profile_file = None
    for cand in candidates:
        candidate_path = PROFILES_DIR / cand
        if candidate_path.exists():
            profile_file = candidate_path
            break

    if profile_file is None:
        return None

    profile_data = read_json(profile_file)
    if isinstance(profile_data, dict):
        normalized = {"name": profile_data.get("name", profile_name), "columns": []}
        if "columns" in profile_data and isinstance(profile_data["columns"], list):
            normalized["columns"] = profile_data["columns"]
        elif "column_profile" in profile_data and isinstance(profile_data["column_profile"], dict):
            normalized["columns"] = profile_data["column_profile"].get("cols", [])

        for key in ["description", "lastUpdated", "updatedBy", "filter_stack", "column_aliases", "column_profile"]:
            if key in profile_data:
                normalized[key] = profile_data[key]
        return normalized
    return profile_data


def list_profiles():
    try:
        jsonc_profiles = [f.stem for f in PROFILES_DIR.glob("*.jsonc")]
        profile_profiles = [f.stem for f in PROFILES_DIR.glob("*.profile")]
        all_profiles = sorted(list(set(jsonc_profiles + profile_profiles)))
        return all_profiles
    except Exception:
        return []


# --- Routes ---


@bp.route('/')
def index():
    df = dm.get_data()
    if df is None or df.empty:
        return redirect(url_for('main.setup'))
    columns = list(df.columns)
    profiles = list_profiles()
    return render_template(
        'index.html',
        columns=columns,
        profiles=profiles,
        templates=list(config.export_templates.keys()),
        row_count=len(df),
        show_parser_warnings=config.show_parser_warnings
    )


@bp.route('/setup')
def setup():
    profiles = list_profiles()
    return render_template(
        'setup.html',
        data_path=str(config.data_path) if config.data_path else "",
        db_table=config.db_table,
        profiles=profiles,
        show_parser_warnings=config.show_parser_warnings
    )


@bp.route('/api/data', methods=['GET'])
def api_data():
    df = dm.get_data()
    if df is None or df.empty:
        raise AppError(ErrorCode.DATA_NOT_FOUND, "Aucune donnee n'est chargee.", 404)

    draw = int(request.args.get('draw', 1))
    start = int(request.args.get('start', 0))
    length = int(request.args.get('length', config.default_page_size))
    search_value = request.args.get('search[value]', '')
    profile_name = request.args.get('profile', '')
    filter_stack_str = request.args.get('filter_stack')
    alias_map_str = request.args.get('alias_map')
    filter_invalid_assets_enabled = _parse_bool(request.args.get('filter_invalid_assets'), False)

    filtered_df = df
    alias_map = {}
    filter_stack = []

    if filter_stack_str:
        import json
        try:
            filter_stack = json.loads(filter_stack_str)
        except Exception:
            pass

    if alias_map_str:
        import json
        try:
            alias_map = json.loads(alias_map_str)
        except Exception:
            pass

    if profile_name and not filter_stack:
        profile = load_profile(profile_name)
        if profile:
            filter_stack = profile.get('filter_stack', [])
            alias_map = _build_alias_map_from_profile(profile)

    if filter_stack:
        filtered_df = apply_filter_stack(df, filter_stack, alias_map)

    if filter_invalid_assets_enabled:
        filtered_df = filter_invalid_assets(filtered_df, alias_map)

    if search_value:
        search_mask = filtered_df.astype(str).apply(lambda row: row.str.contains(search_value, case=False, na=False).any(), axis=1)
        filtered_df = filtered_df[search_mask]

    # Handle sorting
    order_col_idx = request.args.get('order[0][column]')
    order_dir = request.args.get('order[0][dir]')

    if order_col_idx is not None and order_dir in ['asc', 'desc']:
        col_name_key = f'columns[{order_col_idx}][data]'
        col_name = request.args.get(col_name_key)

        if col_name and col_name in filtered_df.columns:
            ascending = order_dir == 'asc'
            filtered_df = filtered_df.sort_values(by=col_name, ascending=ascending)

    records_total = len(df)
    records_filtered = len(filtered_df)

    paged_df = filtered_df.iloc[start:start + length]
    data = paged_df.fillna('').to_dict('records')

    return jsonify({"draw": draw, "recordsTotal": records_total, "recordsFiltered": records_filtered, "data": data})


@bp.route('/api/profiles', methods=['GET'])
def api_list_profiles():
    return jsonify(list_profiles())


@bp.route('/api/profiles/<name>', methods=['GET'])
def api_get_profile(name):
    profile = load_profile(name)
    if profile:
        return jsonify(profile)
    raise AppError(ErrorCode.PROFILE_NOT_FOUND, f"Profil '{name}' non trouve", 404)


@bp.route('/api/profiles', methods=['POST'])
def api_save_profile():
    data = request.get_json(silent=True)
    if not data or 'name' not in data:
        raise AppError(ErrorCode.INVALID_PAYLOAD, "Nom de profil manquant", 400)
    save_profile(data['name'], data)
    return jsonify({"status": "success", "message": f"Profil '{data['name']}' sauvegardé"})


@bp.route('/api/profiles/<name>', methods=['DELETE'])
def api_delete_profile(name):
    profile_file = PROFILES_DIR / f"{name}.jsonc"
    if not profile_file.exists():
        profile_file = PROFILES_DIR / f"{name}.profile.jsonc"
    if not profile_file.exists():
        profile_file = PROFILES_DIR / f"{name}.profile"

    if profile_file.exists():
        profile_file.unlink()
        return jsonify({"status": "success", "message": f"Profil '{name}' supprimé"})
    raise AppError(ErrorCode.PROFILE_NOT_FOUND, f"Profil '{name}' non trouve", 404)


@bp.route('/api/export', methods=['POST'])
def api_export():
    data = request.get_json(silent=True)
    if not data:
        raise AppError(ErrorCode.INVALID_PAYLOAD, "Donnees manquantes pour l'export", 400)

    template_name = data.get('template')
    profile_name = data.get('profile')

    df = dm.get_data()
    if df is None or df.empty:
        raise AppError(ErrorCode.DATA_NOT_FOUND, "Aucune donnee a exporter", 404)

    filtered_df = df
    filter_stack = data.get('filter_stack', []) or []
    alias_map = data.get('alias_map', {}) or {}
    filter_invalid_assets_enabled = _parse_bool(data.get('filter_invalid_assets'), False)
    export_alias_map = alias_map

    if profile_name:
        profile = load_profile(profile_name)
        if profile:
            profile_filter_stack = profile.get('filter_stack', []) or []
            profile_alias_map = profile.get('column_aliases', {}) or {}
            if not filter_stack:
                filter_stack = profile_filter_stack
            if not alias_map:
                alias_map = _build_alias_map_from_profile(profile)
            if not export_alias_map:
                export_alias_map = profile_alias_map
            logger.debug(
                f"Export using profile '{profile_name}', filter_stack length {len(filter_stack)}, alias_map {alias_map}, export_alias_map {export_alias_map}"
            )
        else:
            logger.warning(f"Profile '{profile_name}' not found, using unfiltered data")

    if filter_stack:
        filtered_df = apply_filter_stack(df, filter_stack, alias_map)
        logger.debug(f"Export filtered rows: {len(filtered_df)} (original {len(df)})")

    if filter_invalid_assets_enabled:
        filtered_df = filter_invalid_assets(filtered_df, alias_map)
        logger.debug(f"Export invalid-asset filter rows: {len(filtered_df)}")

    try:
        if template_name:
            export_content = config.apply_export_template(filtered_df, template_name, export_alias_map)
            ext, mimetype = config.detect_export_format(template_name)
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
            return send_file(BytesIO(export_content.encode('utf-8')), mimetype=mimetype, as_attachment=True, download_name=filename)
        else:
            # Export CSV par défaut
            output = BytesIO()
            filtered_df.to_csv(output, index=False, encoding='utf-8')
            output.seek(0)
            return send_file(output, mimetype='text/csv', as_attachment=True, download_name=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    except Exception as e:
        raise AppError(ErrorCode.EXPORT_ERROR, str(e), 500) from e


@bp.route('/api/reload', methods=['POST'])
def api_reload():
    dm.reload()
    return jsonify({"status": "success", "message": "Données rechargées"})


@bp.route('/api/stats', methods=['GET'])
def api_stats():
    df = dm.get_data()
    if df is None or df.empty:
        raise AppError(ErrorCode.DATA_NOT_FOUND, "Aucune donnee n'est chargee.", 404)
    sample = df.head(5).astype(str).values.tolist()
    stats = {"total_rows": len(df), "total_columns": len(df.columns), "columns": list(df.columns), "sample": sample}
    return jsonify(stats)


@bp.route('/api/test', methods=['GET'])
def api_test():
    data_path = config.data_path
    source_type = None
    if data_path and data_path.exists() and not data_path.is_dir():
        source_type = dm.detect_source_type(data_path)

    df = dm.get_data()
    return jsonify(
        {
            "status": "ok",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": _read_version(),
            "data_path": str(data_path) if data_path else None,
            "source_type": source_type,
            "has_data": df is not None and not df.empty,
        }
    )


@bp.route('/api/setup', methods=['POST'])
def api_setup_save():
    data = request.get_json(silent=True)
    if not data:
        raise AppError(ErrorCode.INVALID_PAYLOAD, "Config manquante", 400)

    new_config = {
        "data_path": data.get('data_path'),
        "db_table": data.get('db_table'),
        "show_parser_warnings": data.get('show_parser_warnings', config.show_parser_warnings),
    }
    config.save(new_config)
    dm.reload()
    return jsonify({"status": "success", "message": "Configuration mise à jour et données rechargées"})


@bp.route('/api/config', methods=['GET'])
def api_get_config():
    return jsonify({"status": "success", "config": config.to_public_runtime_config()})


@bp.route('/api/config', methods=['POST'])
def api_update_config():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data:
        raise AppError(ErrorCode.INVALID_PAYLOAD, "Config manquante", 400)

    config_patch = _validate_config_patch(data)
    config.save(config_patch)

    configure_logging(
        log_level=config.log_level,
        log_output=config.log_output,
        log_max_bytes=config.log_max_bytes,
        log_backup_count=config.log_backup_count,
        log_file_path=SCRIPT_DIR / "app.log",
    )

    return jsonify({"status": "success", "message": "Configuration mise a jour", "config": config.to_public_runtime_config(), })


@bp.route('/api/test-path', methods=['POST'])
def api_test_path():
    data = request.get_json(silent=True)
    if not data:
        raise AppError(ErrorCode.INVALID_PAYLOAD, "Payload JSON manquant", 400)
    path_str = data.get('path')
    if not path_str:
        raise AppError(ErrorCode.INVALID_PAYLOAD, "Path vide", 400)

    path = Path(path_str)
    exists = path.exists()
    is_dir = path.is_dir() if exists else False

    tables = []
    source_type = None
    rows = 0
    cols = 0
    warning = None

    if exists and not is_dir:
        source_type = dm.detect_source_type(path)
        if source_type == 'sqlite':
            tables = dm.list_sqlite_tables(path)
            if tables:
                try:
                    conn = sqlite3.connect(str(path))
                    table_name = tables[0]  # On prend la première par défaut pour le test
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    rows = cursor.fetchone()[0]
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    cols = len(cursor.fetchall())
                    conn.close()
                except Exception as e:
                    logger.warning(f"Erreur meta SQLite: {e}")
        else:
            # CSV: Rapid check
            try:
                # On lit juste le début pour les colonnes
                df_sample = pd.read_csv(path, sep=None, engine='python', nrows=0)
                cols = len(df_sample.columns)
                # Pour les lignes, on compte les sauts de ligne (plus rapide que read_csv complet)
                with open(path, 'rb') as f:
                    rows = sum(1 for _ in f) - 1  # -1 pour le header
            except Exception as e:
                logger.warning(f"Erreur meta CSV: {e}")
                warning = f"Format potentiellement malformé: {e}"

    return jsonify(
        {
            "exists": exists,
            "is_dir": is_dir,
            "type": source_type,
            "source_type": source_type,  # Backwards compatibility
            "tables": tables,
            "rows": max(0, rows),
            "cols": cols,
            "warning": warning
        }
    )


@bp.route('/api/columns', methods=['GET'])
def api_columns():
    df = dm.get_data()
    if df is not None:
        return jsonify(list(df.columns))
    return jsonify([])


@bp.route('/api/templates', methods=['GET'])
def api_templates():
    templates_list = [
        {
            "name": name,
            "description": tpl.get("description", ""),
            "pattern": tpl.get("pattern", "")
        } for name, tpl in config.export_templates.items()
    ]
    return jsonify({"templates": templates_list})


@bp.route('/api/batch-export', methods=['POST'])
def api_batch_export():
    """Headless export for automation."""
    data = request.get_json(silent=True)
    if not data:
        raise AppError(ErrorCode.INVALID_PAYLOAD, "Payload manquant", 400)

    profile_name = data.get('profile')
    template_name = data.get('template')
    filter_stack = data.get('filter_stack', [])
    alias_map = data.get('alias_map', {})
    export_alias_map = alias_map

    # Support for both explicit path or split dir/name
    output_path = data.get('output_path')
    output_dir = data.get('output_dir')
    file_name = data.get('file_name')

    if not template_name:
        raise AppError(ErrorCode.MISSING_PARAMS, "template is required", 400)

    df = dm.get_data()
    if df is None or df.empty:
        raise AppError(ErrorCode.DATA_NOT_FOUND, "Aucune donnee a exporter", 404)

    if profile_name:
        profile = load_profile(profile_name)
        if not profile:
            raise AppError(ErrorCode.PROFILE_NOT_FOUND, f"Profile {profile_name} not found", 404)
        filter_stack = profile.get('filter_stack', [])
        export_alias_map = profile.get('column_aliases', {}) or {}
        alias_map = _build_alias_map_from_profile(profile)
        logger.debug(
            f"Batch export using profile '{profile_name}', filter_stack length {len(filter_stack)}, alias_map {alias_map}, export_alias_map {export_alias_map}"
        )

    filtered_df = apply_filter_stack(df, filter_stack, alias_map)
    logger.debug(f"Batch export filtered rows: {len(filtered_df)} (original {len(df)})")

    filtered_df = filter_invalid_assets(filtered_df, alias_map)
    logger.debug(f"Batch export invalid-asset filter rows: {len(filtered_df)}")

    try:
        export_content = config.apply_export_template(filtered_df, template_name, export_alias_map)
        ext, _ = config.detect_export_format(template_name)

        if output_path:
            out_file = Path(output_path)
        else:
            base_dir = Path(output_dir) if output_dir else EXPORTS_DIR
            name = file_name or f"batch_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            out_file = base_dir / f"{name}.{ext}"

        out_file.parent.mkdir(exist_ok=True, parents=True)
        out_file.write_text(export_content, encoding='utf-8')

        return jsonify({"status": "success", "file": str(out_file), "format": ext, "count": len(filtered_df)})
    except Exception as e:
        logger.error(f"Batch export error: {e}")
        raise AppError(ErrorCode.BATCH_EXPORT_ERROR, str(e), 500) from e
