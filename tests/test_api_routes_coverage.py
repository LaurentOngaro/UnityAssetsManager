# ============================================================================
# UnityAssetsManager - tests/test_api_routes_coverage.py
# ============================================================================
# Description: Tests for previously uncovered API routes (profiles CRUD,
#              reload, setup, config GET, templates).
# Version: 1.4.1
# ============================================================================

import json
import sys
import pandas as pd
import pytest

from .test_unity_assets_manager_helpers import import_unity_assets_manager_module

SAMPLE_DATA = [
    {
        "DisplayName": "Asset A",
        "DisplayPublisher": "Pub A",
        "DisplayCategory": "Cat 1",
        "Slug": "asset-a",
        "Url": "https://example.com/a"
    }, {
        "DisplayName": "Asset B",
        "DisplayPublisher": "Pub B",
        "DisplayCategory": "Cat 2",
        "Slug": "asset-b",
        "Url": "https://example.com/b"
    },
]


@pytest.fixture
def mock_data(monkeypatch):
    dm_module = sys.modules.get("lib.data_manager")
    assert dm_module is not None
    monkeypatch.setattr(dm_module.dm, "_df", pd.DataFrame(SAMPLE_DATA))
    return dm_module.dm


# --- GET /api/profiles ---


def test_api_list_profiles_returns_array(client):
    resp = client.get("/api/profiles")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    # Should contain at least some profiles from the profiles/ directory
    assert len(data) > 0


# --- GET /api/profiles/<name> ---


def test_api_get_profile_returns_profile(client):
    resp = client.get("/api/profiles")
    profiles = resp.get_json()
    assert len(profiles) > 0
    first_profile = profiles[0]

    resp = client.get(f"/api/profiles/{first_profile}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "name" in data
    assert "columns" in data


def test_api_get_profile_not_found(client):
    resp = client.get("/api/profiles/nonexistent_profile_xyz")
    assert resp.status_code == 404
    data = resp.get_json()
    assert data["error"]["code"] == "PROFILE_NOT_FOUND"


# --- POST /api/profiles ---


def test_api_save_profile_success(client, tmp_path, monkeypatch):
    routes_module = sys.modules.get("lib.routes")
    assert routes_module is not None
    monkeypatch.setattr(routes_module, "PROFILES_DIR", tmp_path)

    profile_data = {
        "name": "test_profile",
        "columns": ["DisplayName", "Slug"],
        "filter_stack": [],
        "column_aliases": {
            "URL": "Url"
        },
        "description": "Test profile"
    }
    resp = client.post("/api/profiles", json=profile_data)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"

    # Verify file was created
    profile_file = tmp_path / "test_profile.jsonc"
    assert profile_file.exists()


def test_api_save_profile_missing_name(client):
    resp = client.post("/api/profiles", json={"columns": ["DisplayName"]})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"]["code"] == "INVALID_PAYLOAD"


def test_api_save_profile_empty_payload(client):
    resp = client.post("/api/profiles", data="not json", content_type="application/json")
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"]["code"] == "INVALID_PAYLOAD"


# --- DELETE /api/profiles/<name> ---


def test_api_delete_profile_success(client, tmp_path, monkeypatch):
    routes_module = sys.modules.get("lib.routes")
    assert routes_module is not None
    monkeypatch.setattr(routes_module, "PROFILES_DIR", tmp_path)

    # Create a profile first
    profile_file = tmp_path / "to_delete.jsonc"
    profile_file.write_text(json.dumps({"name": "to_delete", "columns": []}), encoding="utf-8")

    resp = client.delete("/api/profiles/to_delete")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"
    assert not profile_file.exists()


def test_api_delete_profile_not_found(client):
    resp = client.delete("/api/profiles/nonexistent_profile_xyz")
    assert resp.status_code == 404
    data = resp.get_json()
    assert data["error"]["code"] == "PROFILE_NOT_FOUND"


# --- POST /api/reload ---


def test_api_reload_success(client, mock_data):
    resp = client.post("/api/reload")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"
    assert "message" in data


# --- POST /api/setup ---


def test_api_setup_success(client, monkeypatch, tmp_path):
    mod = import_unity_assets_manager_module()
    dm_module = sys.modules.get("lib.data_manager")
    assert dm_module is not None

    # Create a dummy CSV file
    csv_file = tmp_path / "test_data.csv"
    csv_file.write_text("DisplayName,Slug\nTest Asset,test-asset\n", encoding="utf-8")

    def _fake_save(new_values):
        for key, value in new_values.items():
            setattr(mod.config, key, value)

    monkeypatch.setattr(mod.config, "save", _fake_save)
    monkeypatch.setattr(dm_module.dm, "reload", lambda: None)

    resp = client.post("/api/setup", json={"data_path": str(csv_file), "db_table": "assets", "show_parser_warnings": False})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"


def test_api_setup_invalid_path(client):
    resp = client.post("/api/setup", json={"data_path": "/nonexistent/path/to/file.csv"})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"]["code"] == "INVALID_CONFIG"
    assert "path" in data["error"]["details"]


def test_api_setup_directory_path(client, tmp_path):
    resp = client.post("/api/setup", json={"data_path": str(tmp_path)})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"]["code"] == "INVALID_CONFIG"


def test_api_setup_empty_payload(client):
    resp = client.post("/api/setup", data="not json", content_type="application/json")
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"]["code"] == "INVALID_PAYLOAD"


# --- GET /api/config ---


def test_api_get_config_returns_config(client):
    resp = client.get("/api/config")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"
    assert "config" in data
    cfg = data["config"]
    assert "data_path" in cfg
    assert "db_table" in cfg
    assert "log_level" in cfg


# --- GET /api/templates ---


def test_api_templates_returns_list(client):
    resp = client.get("/api/templates")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "templates" in data
    assert isinstance(data["templates"], list)
    assert len(data["templates"]) > 0

    # Check template structure
    template = data["templates"][0]
    assert "name" in template
    assert "description" in template
    assert "pattern" in template


# --- GET /api/columns with no data ---


def test_api_columns_no_data_raises_404(monkeypatch):
    mod = import_unity_assets_manager_module()
    client = mod.app.test_client()

    dm_module = sys.modules.get("lib.data_manager")
    assert dm_module is not None
    monkeypatch.setattr(dm_module.dm, "_df", pd.DataFrame())

    resp = client.get("/api/columns")
    assert resp.status_code == 404
    data = resp.get_json()
    assert data["error"]["code"] == "DATA_NOT_FOUND"
