# ============================================================================
# UnityAssetsManager - routes.py
# ============================================================================
# Description: Définition des routes web et des endpoints API.
# Version: 1.2.5
# ============================================================================

import logging
import sqlite3
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
from flask import render_template, request, jsonify, send_file, redirect, url_for, Blueprint
from io import BytesIO

from config import config, PROFILES_DIR, EXPORTS_DIR
from utils import read_json, write_json_normalized
from data_manager import dm
from filters import apply_filter_stack, _build_alias_map_from_profile

logger = logging.getLogger(__name__)

bp = Blueprint('main', __name__)


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

        for key in ["description", "lastUpdated", "updatedBy", "filter_columns", "filter_stack", "column_aliases", "column_profile"]:
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
        return api_error("DATA_NOT_FOUND", "Aucune donnée n'est chargée.", 404)

    draw = int(request.args.get('draw', 1))
    start = int(request.args.get('start', 0))
    length = int(request.args.get('length', config.default_page_size))
    search_value = request.args.get('search[value]', '')
    profile_name = request.args.get('profile', '')

    filtered_df = df
    alias_map = {}

    if profile_name:
        profile = load_profile(profile_name)
        if profile:
            filter_stack = profile.get('filter_stack', [])
            alias_map = _build_alias_map_from_profile(profile)
            filtered_df = apply_filter_stack(df, filter_stack, alias_map)

    if search_value:
        search_mask = filtered_df.astype(str).apply(lambda row: row.str.contains(search_value, case=False, na=False).any(), axis=1)
        filtered_df = filtered_df[search_mask]

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
    return api_error("PROFILE_NOT_FOUND", f"Profil '{name}' non trouvé", 404)


@bp.route('/api/profiles', methods=['POST'])
def api_save_profile():
    data = request.get_json(silent=True)
    if not data or 'name' not in data:
        return api_error("INVALID_PAYLOAD", "Nom de profil manquant", 400)
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
    return api_error("PROFILE_NOT_FOUND", f"Profil '{name}' non trouvé", 404)


@bp.route('/api/export', methods=['POST'])
def api_export():
    data = request.get_json(silent=True)
    if not data:
        return api_error("INVALID_PAYLOAD", "Données manquantes pour l'export", 400)

    template_name = data.get('template')
    profile_name = data.get('profile')

    df = dm.get_data()
    if df is None or df.empty:
        return api_error("DATA_NOT_FOUND", "Aucune donnée à exporter", 404)

    filtered_df = df
    if profile_name:
        profile = load_profile(profile_name)
        if profile:
            filter_stack = profile.get('filter_stack', [])
            alias_map = _build_alias_map_from_profile(profile)
            filtered_df = apply_filter_stack(df, filter_stack, alias_map)

    try:
        if template_name:
            export_content = config.apply_export_template(filtered_df, template_name)
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
        return api_error("EXPORT_ERROR", str(e), 500)


@bp.route('/api/reload', methods=['POST'])
def api_reload():
    dm.reload()
    return jsonify({"status": "success", "message": "Données rechargées"})


@bp.route('/api/stats', methods=['GET'])
def api_stats():
    df = dm.get_data()
    if df is None or df.empty:
        return api_error("DATA_NOT_FOUND", "Aucune donnée n'est chargée.", 404)
    sample = df.head(5).astype(str).values.tolist()
    stats = {"total_rows": len(df), "total_columns": len(df.columns), "columns": list(df.columns), "sample": sample}
    return jsonify(stats)


@bp.route('/api/setup', methods=['POST'])
def api_setup_save():
    data = request.get_json(silent=True)
    if not data:
        return api_error("INVALID_PAYLOAD", "Config manquante", 400)

    new_config = {
        "data_path": data.get('data_path'),
        "db_table": data.get('db_table'),
        "show_parser_warnings": data.get('show_parser_warnings', True)
    }
    config.save(new_config)
    dm.reload()
    return jsonify({"status": "success", "message": "Configuration mise à jour et données rechargées"})


@bp.route('/api/test-path', methods=['POST'])
def api_test_path():
    data = request.get_json(silent=True)
    if not data:
        return api_error("INVALID_PAYLOAD", "Payload JSON manquant", 400)
    path_str = data.get('path')
    if not path_str:
        return api_error("INVALID_PAYLOAD", "Path vide", 400)

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
        return api_error("INVALID_PAYLOAD", "Payload manquant", 400)

    profile_name = data.get('profile')
    template_name = data.get('template')
    filter_stack = data.get('filter_stack', [])
    alias_map = data.get('alias_map', {})

    # Support for both explicit path or split dir/name
    output_path = data.get('output_path')
    output_dir = data.get('output_dir')
    file_name = data.get('file_name')

    if not template_name:
        return api_error("MISSING_PARAMS", "template is required", 400)

    df = dm.get_data()

    if profile_name:
        profile = load_profile(profile_name)
        if not profile:
            return api_error("PROFILE_NOT_FOUND", f"Profile {profile_name} not found", 404)
        filter_stack = profile.get('filter_stack', [])
        alias_map = _build_alias_map_from_profile(profile)

    filtered_df = apply_filter_stack(df, filter_stack, alias_map)

    try:
        export_content = config.apply_export_template(filtered_df, template_name)
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
        return api_error("BATCH_EXPORT_ERROR", str(e), 500)
