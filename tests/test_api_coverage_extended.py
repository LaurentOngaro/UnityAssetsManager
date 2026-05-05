# ============================================================================
# UnityAssetsManager - tests/test_api_coverage_extended.py
# ============================================================================
# Description: Extended API coverage tests for previously untested features.
# Version: 1.6.0
# ============================================================================

from io import BytesIO
from pathlib import Path

import pandas as pd
import pytest

from .test_unity_assets_manager_helpers import import_unity_assets_manager_module

SAMPLE_DF_WITH_PARENTS = pd.DataFrame(
    [
        {
            "DisplayName": "Parent Asset A",
            "DisplayPublisher": "Pub A",
            "DisplayCategory": "Cat 1",
            "Version": "1.0",
            "Url": "https://example.com/a",
            "Slug": "parent-a",
            "ParentId": "",
        }, {
            "DisplayName": "Parent Asset B",
            "DisplayPublisher": "Pub B",
            "DisplayCategory": "Cat 2",
            "Version": "2.0",
            "Url": "https://example.com/b",
            "Slug": "parent-b",
            "ParentId": None,
        }, {
            "DisplayName": "Child Asset A1",
            "DisplayPublisher": "Pub A",
            "DisplayCategory": "Cat 1",
            "Version": "1.1",
            "Url": "https://example.com/a1",
            "Slug": "child-a1",
            "ParentId": "parent-a",
        }, {
            "DisplayName": "Child Asset B1",
            "DisplayPublisher": "Pub B",
            "DisplayCategory": "Cat 2",
            "Version": "2.1",
            "Url": "https://example.com/b1",
            "Slug": "child-b1",
            "ParentId": "parent-b",
        },
    ]
)

SAMPLE_DF_SORTABLE = pd.DataFrame(
    [
        {
            "DisplayName": "Zebra",
            "DisplayPublisher": "Pub C",
            "DisplayCategory": "Cat 3",
            "Price": 30
        }, {
            "DisplayName": "Alpha",
            "DisplayPublisher": "Pub A",
            "DisplayCategory": "Cat 1",
            "Price": 10
        }, {
            "DisplayName": "Beta",
            "DisplayPublisher": "Pub B",
            "DisplayCategory": "Cat 2",
            "Price": 20
        },
    ]
)

# ============================================================================
# 1. get_childs parameter in /api/export
# ============================================================================


def test_export_default_excludes_child_assets(monkeypatch):
    """By default, /api/export must exclude rows with non-null ParentId."""
    mod = import_unity_assets_manager_module()
    import sys
    dm_module = sys.modules.get("lib.data_manager")
    assert dm_module is not None

    monkeypatch.setattr(dm_module.dm, "_df", SAMPLE_DF_WITH_PARENTS.copy())
    monkeypatch.setattr(mod.config, "export_templates", {"CSV test": {"description": "test", "pattern": "%DisplayName%,%DisplayPublisher%"}}, )

    client = mod.app.test_client()
    response = client.post("/api/export", json={"template": "CSV test"})

    assert response.status_code == 200
    text = response.get_data(as_text=True)
    lines = [l for l in text.strip().splitlines() if l and not l.startswith("#")]
    # First line is CSV header, remaining are data rows
    data_lines = lines[1:]
    assert len(data_lines) == 2
    assert any("Parent Asset A" in l for l in data_lines)
    assert any("Parent Asset B" in l for l in data_lines)
    assert not any("Child Asset" in l for l in data_lines)


def test_export_with_get_childs_true_includes_child_assets(monkeypatch):
    """When get_childs=true, /api/export must include child assets."""
    mod = import_unity_assets_manager_module()
    import sys
    dm_module = sys.modules.get("lib.data_manager")
    assert dm_module is not None

    monkeypatch.setattr(dm_module.dm, "_df", SAMPLE_DF_WITH_PARENTS.copy())
    monkeypatch.setattr(mod.config, "export_templates", {"CSV test": {"description": "test", "pattern": "%DisplayName%,%DisplayPublisher%"}}, )

    client = mod.app.test_client()
    response = client.post("/api/export", json={"template": "CSV test", "get_childs": True})

    assert response.status_code == 200
    text = response.get_data(as_text=True)
    lines = [l for l in text.strip().splitlines() if l and not l.startswith("#")]
    data_lines = lines[1:]
    assert len(data_lines) == 4


# ============================================================================
# 2. get_childs parameter in /api/batch-export
# ============================================================================


def test_batch_export_default_excludes_child_assets(monkeypatch, tmp_path):
    """By default, /api/batch-export must exclude rows with non-null ParentId."""
    mod = import_unity_assets_manager_module()
    import sys
    dm_module = sys.modules.get("lib.data_manager")
    assert dm_module is not None

    monkeypatch.setattr(dm_module.dm, "_df", SAMPLE_DF_WITH_PARENTS.copy())
    monkeypatch.setattr(mod.config, "export_templates", {"CSV test": {"description": "test", "pattern": "%DisplayName%"}}, )

    client = mod.app.test_client()
    response = client.post("/api/batch-export", json={"template": "CSV test", "output_dir": str(tmp_path), "file_name": "test_default"}, )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload is not None and payload.get("status") == "success"
    assert payload.get("count") == 2

    out_file = Path(payload["file"])
    exported_df = pd.read_csv(out_file)
    assert len(exported_df) == 2


def test_batch_export_with_get_childs_true_includes_child_assets(monkeypatch, tmp_path):
    """When get_childs=true, /api/batch-export must include child assets."""
    mod = import_unity_assets_manager_module()
    import sys
    dm_module = sys.modules.get("lib.data_manager")
    assert dm_module is not None

    monkeypatch.setattr(dm_module.dm, "_df", SAMPLE_DF_WITH_PARENTS.copy())
    monkeypatch.setattr(mod.config, "export_templates", {"CSV test": {"description": "test", "pattern": "%DisplayName%"}}, )

    client = mod.app.test_client()
    response = client.post(
        "/api/batch-export", json={
            "template": "CSV test",
            "get_childs": True,
            "output_dir": str(tmp_path),
            "file_name": "test_get_childs"
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload is not None and payload.get("status") == "success"
    assert payload.get("count") == 4


# ============================================================================
# 3. filter_child_assets combined with filter_stack
# ============================================================================


def test_batch_export_child_filter_combined_with_filter_stack(monkeypatch, tmp_path):
    """Child filter and filter_stack must work together (stack applied first)."""
    mod = import_unity_assets_manager_module()
    import sys
    dm_module = sys.modules.get("lib.data_manager")
    assert dm_module is not None

    monkeypatch.setattr(dm_module.dm, "_df", SAMPLE_DF_WITH_PARENTS.copy())
    monkeypatch.setattr(mod.config, "export_templates", {"CSV test": {"description": "test", "pattern": "%DisplayName%,%DisplayPublisher%"}}, )

    filter_stack = [{"mode": "include", "filters": {"DisplayPublisher": {"values": ["Pub A"]}}, "search_term": ""}, ]

    client = mod.app.test_client()
    response = client.post(
        "/api/batch-export",
        json={
            "template": "CSV test",
            "filter_stack": filter_stack,
            "output_dir": str(tmp_path),
            "file_name": "test_combined",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload is not None and payload.get("status") == "success"
    assert payload.get("count") == 1

    out_file = Path(payload["file"])
    exported_df = pd.read_csv(out_file)
    assert len(exported_df) == 1
    assert exported_df.iloc[0]["DisplayName"] == "Parent Asset A"


# ============================================================================
# 4. Sorting in /api/data
# ============================================================================


def test_api_data_sort_ascending(monkeypatch):
    """GET /api/data must support ascending sort via order[0][dir]=asc."""
    mod = import_unity_assets_manager_module()
    import sys
    dm_module = sys.modules.get("lib.data_manager")
    assert dm_module is not None

    monkeypatch.setattr(dm_module.dm, "_df", SAMPLE_DF_SORTABLE.copy())

    client = mod.app.test_client()
    response = client.get("/api/data?draw=1&start=0&length=10"
                          "&order[0][column]=0&order[0][dir]=asc"
                          "&columns[0][data]=DisplayName")

    assert response.status_code == 200
    data = response.get_json()
    assert data["recordsFiltered"] == 3
    assert data["data"][0]["DisplayName"] == "Alpha"
    assert data["data"][1]["DisplayName"] == "Beta"
    assert data["data"][2]["DisplayName"] == "Zebra"


def test_api_data_sort_descending(monkeypatch):
    """GET /api/data must support descending sort via order[0][dir]=desc."""
    mod = import_unity_assets_manager_module()
    import sys
    dm_module = sys.modules.get("lib.data_manager")
    assert dm_module is not None

    monkeypatch.setattr(dm_module.dm, "_df", SAMPLE_DF_SORTABLE.copy())

    client = mod.app.test_client()
    response = client.get("/api/data?draw=1&start=0&length=10"
                          "&order[0][column]=0&order[0][dir]=desc"
                          "&columns[0][data]=DisplayName")

    assert response.status_code == 200
    data = response.get_json()
    assert data["data"][0]["DisplayName"] == "Zebra"
    assert data["data"][2]["DisplayName"] == "Alpha"


def test_api_data_sort_invalid_column_ignored(monkeypatch):
    """Invalid sort column must not crash; returns unsorted data."""
    mod = import_unity_assets_manager_module()
    import sys
    dm_module = sys.modules.get("lib.data_manager")
    assert dm_module is not None

    monkeypatch.setattr(dm_module.dm, "_df", SAMPLE_DF_SORTABLE.copy())

    client = mod.app.test_client()
    response = client.get("/api/data?draw=1&start=0&length=10"
                          "&order[0][column]=0&order[0][dir]=asc"
                          "&columns[0][data]=NonExistentColumn")

    assert response.status_code == 200
    data = response.get_json()
    assert data["recordsFiltered"] == 3


# ============================================================================
# 5. /api/data with profile parameter
# ============================================================================


def test_api_data_with_profile_applies_filter_stack(monkeypatch, tmp_path):
    """GET /api/data?profile=X must load and apply the profile's filter_stack."""
    mod = import_unity_assets_manager_module()
    import sys
    dm_module = sys.modules.get("lib.data_manager")
    assert dm_module is not None
    routes_module = sys.modules.get("lib.routes")
    assert routes_module is not None

    monkeypatch.setattr(dm_module.dm, "_df", SAMPLE_DF_SORTABLE.copy())

    profile_file = tmp_path / "TestProfile.jsonc"
    profile_file.write_text(
        '{"name":"TestProfile","columns":["DisplayName"],"filter_stack":[{"mode":"include","filters":{"DisplayPublisher":{"values":["Pub A"]}},"search_term":""}]}',
        encoding="utf-8",
    )

    monkeypatch.setattr(routes_module, "PROFILES_DIR", tmp_path)

    client = mod.app.test_client()
    response = client.get("/api/data?draw=1&start=0&length=10&profile=TestProfile")

    assert response.status_code == 200
    data = response.get_json()
    assert data["recordsFiltered"] == 1
    assert data["data"][0]["DisplayName"] == "Alpha"


# ============================================================================
# 6. Profile CRUD via API
# ============================================================================


def test_api_save_and_get_profile(monkeypatch, tmp_path):
    """POST /api/profiles then GET /api/profiles/<name> must round-trip data."""
    mod = import_unity_assets_manager_module()
    import sys
    routes_module = sys.modules.get("lib.routes")
    assert routes_module is not None
    monkeypatch.setattr(routes_module, "PROFILES_DIR", tmp_path)

    client = mod.app.test_client()
    payload = {
        "name": "RoundTripProfile",
        "columns": ["DisplayName", "Version"],
        "filter_stack": [{
            "mode": "include",
            "filters": {
                "Category": {
                    "values": ["Tools"]
                }
            },
            "search_term": ""
        }],
    }
    resp = client.post("/api/profiles", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"

    resp = client.get("/api/profiles/RoundTripProfile")
    assert resp.status_code == 200
    profile = resp.get_json()
    assert profile["name"] == "RoundTripProfile"
    assert len(profile["columns"]) == 2


def test_api_delete_profile(monkeypatch, tmp_path):
    """DELETE /api/profiles/<name> must remove the profile file."""
    mod = import_unity_assets_manager_module()
    import sys
    routes_module = sys.modules.get("lib.routes")
    assert routes_module is not None
    monkeypatch.setattr(routes_module, "PROFILES_DIR", tmp_path)

    profile_file = tmp_path / "ToDelete.jsonc"
    profile_file.write_text('{"name":"ToDelete","columns":[]}', encoding="utf-8")

    client = mod.app.test_client()
    resp = client.delete("/api/profiles/ToDelete")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"

    resp = client.get("/api/profiles/ToDelete")
    assert resp.status_code == 404


def test_api_delete_nonexistent_profile(monkeypatch, tmp_path):
    """DELETE /api/profiles/<name> must return 404 for missing profiles."""
    mod = import_unity_assets_manager_module()
    import sys
    routes_module = sys.modules.get("lib.routes")
    assert routes_module is not None
    monkeypatch.setattr(routes_module, "PROFILES_DIR", tmp_path)

    client = mod.app.test_client()
    resp = client.delete("/api/profiles/NoSuchProfile")
    assert resp.status_code == 404


# ============================================================================
# 7. sanitize_asset_dataframe and Unicode normalization
# ============================================================================


def test_sanitize_normalizes_special_chars_in_name():
    """sanitize_asset_dataframe must replace special separators in name fields."""
    from lib.utils import sanitize_asset_dataframe

    df = pd.DataFrame([{"Name": "Asset\u30fbPack", "Category": "Tools"}])
    result = sanitize_asset_dataframe(df)

    assert result.iloc[0]["Name"] == "Asset Pack"


def test_sanitize_preserves_non_asset_columns():
    """sanitize_asset_dataframe must not modify columns that don't match asset tokens."""
    from lib.utils import sanitize_asset_dataframe

    df = pd.DataFrame([{"Name": "Test", "Description": "Some unicode: \u00e9\u00e0\u00fc"}])
    result = sanitize_asset_dataframe(df)

    assert result.iloc[0]["Description"] == "Some unicode: \u00e9\u00e0\u00fc"


def test_sanitize_normalizes_slug():
    """sanitize_asset_dataframe must normalize slug columns to ASCII-safe tokens."""
    from lib.utils import sanitize_asset_dataframe

    df = pd.DataFrame([{"Slug": "My Asset Pack!", "Name": "Test"}])
    result = sanitize_asset_dataframe(df)

    assert result.iloc[0]["Slug"] == "my-asset-pack"


def test_sanitize_handles_none_and_empty_df():
    """sanitize_asset_dataframe must handle None and empty DataFrames gracefully."""
    from lib.utils import sanitize_asset_dataframe

    assert sanitize_asset_dataframe(None) is None
    assert sanitize_asset_dataframe(pd.DataFrame()) is not None


# ============================================================================
# 8. /api/reload and /api/templates
# ============================================================================


def test_api_reload_success(monkeypatch):
    """POST /api/reload must return success status."""
    mod = import_unity_assets_manager_module()
    client = mod.app.test_client()

    resp = client.post("/api/reload")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"


def test_api_templates_returns_list(monkeypatch):
    """GET /api/templates must return a list of templates with name/description/pattern."""
    mod = import_unity_assets_manager_module()
    client = mod.app.test_client()

    resp = client.get("/api/templates")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "templates" in data
    assert isinstance(data["templates"], list)
    if data["templates"]:
        tpl = data["templates"][0]
        assert "name" in tpl
        assert "description" in tpl
        assert "pattern" in tpl


# ============================================================================
# 9. Config update with invalid values
# ============================================================================


def test_config_rejects_invalid_log_level(monkeypatch):
    """POST /api/config must reject invalid log_level values."""
    mod = import_unity_assets_manager_module()
    client = mod.app.test_client()

    resp = client.post("/api/config", json={"log_level": "INVALID"})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"]["code"] == "INVALID_CONFIG"


def test_config_rejects_invalid_log_output(monkeypatch):
    """POST /api/config must reject invalid log_output values."""
    mod = import_unity_assets_manager_module()
    client = mod.app.test_client()

    resp = client.post("/api/config", json={"log_output": "invalid"})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"]["code"] == "INVALID_CONFIG"


def test_config_rejects_negative_log_max_bytes(monkeypatch):
    """POST /api/config must reject log_max_bytes <= 0."""
    mod = import_unity_assets_manager_module()
    client = mod.app.test_client()

    resp = client.post("/api/config", json={"log_max_bytes": -1})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"]["code"] == "INVALID_CONFIG"


def test_config_rejects_negative_log_backup_count(monkeypatch):
    """POST /api/config must reject log_backup_count <= 0."""
    mod = import_unity_assets_manager_module()
    client = mod.app.test_client()

    resp = client.post("/api/config", json={"log_backup_count": 0})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"]["code"] == "INVALID_CONFIG"


def test_config_rejects_empty_db_table(monkeypatch):
    """POST /api/config must reject empty db_table."""
    mod = import_unity_assets_manager_module()
    client = mod.app.test_client()

    resp = client.post("/api/config", json={"db_table": ""})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"]["code"] == "INVALID_CONFIG"


# ============================================================================
# 10. JSONC parsing
# ============================================================================


def test_strip_jsonc_removes_line_comments():
    """strip_jsonc must remove // line comments while preserving strings."""
    from lib.utils import strip_jsonc
    import json

    src = '{"name": "test", // this is a comment\n"value": 42}'
    result = strip_jsonc(src)
    parsed = json.loads(result)
    assert parsed["name"] == "test"
    assert parsed["value"] == 42


def test_strip_jsonc_removes_block_comments():
    """strip_jsonc must remove /* */ block comments."""
    from lib.utils import strip_jsonc
    import json

    src = '{"name": /* inline comment */ "test"}'
    result = strip_jsonc(src)
    parsed = json.loads(result)
    assert parsed["name"] == "test"


def test_strip_jsonc_preserves_comments_in_strings():
    """strip_jsonc must NOT remove // that appears inside string literals."""
    from lib.utils import strip_jsonc
    import json

    src = '{"url": "http://example.com"}'
    result = strip_jsonc(src)
    parsed = json.loads(result)
    assert parsed["url"] == "http://example.com"


def test_read_json_with_jsonc(tmp_path):
    """read_json must parse JSONC files with comments."""
    from lib.utils import read_json

    jsonc_file = tmp_path / "test.jsonc"
    jsonc_file.write_text('{\n  "name": "test", // comment\n  "value": 42 /* block */\n}', encoding="utf-8", )

    result = read_json(jsonc_file)
    assert result["name"] == "test"
    assert result["value"] == 42


def test_write_json_normalized_creates_backup(tmp_path):
    """write_json_normalized must create a .bak file when content changes."""
    from lib.utils import write_json_normalized

    json_file = tmp_path / "test.json"
    json_file.write_text('{"old": true}', encoding="utf-8")

    write_json_normalized(json_file, {"new": True}, backup=True)

    bak_file = tmp_path / "test.json.bak"
    assert bak_file.exists()
    assert '"old": true' in bak_file.read_text(encoding="utf-8")
