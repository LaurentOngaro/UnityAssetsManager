# ============================================================================
# UnityAssetsManager - tests/test_api_errors.py
# ============================================================================
# Description: Unit tests for API error handling.
# Version: 1.6.0
# ============================================================================

from .test_unity_assets_manager_helpers import import_unity_assets_manager_module


def _assert_error_contract(payload, expected_code: str, expected_status: int):
    assert payload is not None
    assert "error" in payload
    assert payload["error"]["code"] == expected_code
    assert payload["error"]["http_status"] == expected_status
    assert "message" in payload["error"]
    assert "timestamp" in payload["error"]
    assert "path" in payload["error"]
    assert "details" in payload["error"]


def test_api_errors_contract(monkeypatch, tmp_path):
    mod = import_unity_assets_manager_module()
    client = mod.app.test_client()

    # 1. Invalid Payload (setup)
    resp = client.post("/api/setup", data="not a json", content_type="application/json")
    assert resp.status_code == 400
    data = resp.get_json()
    _assert_error_contract(data, "INVALID_PAYLOAD", 400)

    # 2. Profile absent (GET)
    resp = client.get("/api/profiles/this_profile_does_not_exist")
    assert resp.status_code == 404
    data = resp.get_json()
    _assert_error_contract(data, "PROFILE_NOT_FOUND", 404)

    # 3. Batch export missing template
    resp = client.post("/api/batch-export", json={"profile": "some_profile"})
    assert resp.status_code == 400
    data = resp.get_json()
    _assert_error_contract(data, "MISSING_PARAMS", 400)

    # 4. Batch export missing profile
    resp = client.post("/api/batch-export", json={"template": "JSON batch", "profile": "non_existent"})
    assert resp.status_code == 404
    data = resp.get_json()
    _assert_error_contract(data, "PROFILE_NOT_FOUND", 404)

    # 5. Export with missing data
    resp = client.post("/api/export", data="not a json", content_type="application/json")
    assert resp.status_code == 400
    data = resp.get_json()
    _assert_error_contract(data, "INVALID_PAYLOAD", 400)

    # 6. Test-path empty path
    resp = client.post("/api/test-path", json={"path": ""})
    assert resp.status_code == 400
    data = resp.get_json()
    _assert_error_contract(data, "INVALID_PAYLOAD", 400)

    # 7. Test-path invalid payload
    resp = client.post("/api/test-path", data="not json", content_type="application/json")
    assert resp.status_code == 400
    data = resp.get_json()
    _assert_error_contract(data, "INVALID_PAYLOAD", 400)

    # 8. Test-path SEC1: Invalid extension (path traversal prevention)
    resp = client.post("/api/test-path", json={"path": "C:/Windows/System32/cmd.exe"})
    assert resp.status_code == 400
    data = resp.get_json()
    _assert_error_contract(data, "INVALID_PAYLOAD", 400)
    assert "Extension de fichier non autorisée" in data["error"]["message"]


def test_api4_test_and_config_endpoints(monkeypatch):
    mod = import_unity_assets_manager_module()
    client = mod.app.test_client()

    # /api/test health endpoint
    resp = client.get("/api/test")
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload is not None
    assert payload["status"] == "ok"
    assert "timestamp" in payload
    assert "version" in payload

    # Avoid mutating config file during tests by stubbing save().
    def _fake_save(new_values):
        for key, value in new_values.items():
            setattr(mod.config, key, value)

    monkeypatch.setattr(mod.config, "save", _fake_save)

    update_payload = {"log_level": "DEBUG", "log_output": "console", "log_max_bytes": 4096, "log_backup_count": 2, }
    resp = client.post("/api/config", json=update_payload)
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload is not None
    assert payload["status"] == "success"
    assert payload["config"]["log_level"] == "DEBUG"
    assert payload["config"]["log_output"] == "console"
    assert payload["config"]["log_max_bytes"] == 4096
    assert payload["config"]["log_backup_count"] == 2


def test_api4_config_rejects_unknown_fields():
    mod = import_unity_assets_manager_module()
    client = mod.app.test_client()

    resp = client.post("/api/config", json={"not_allowed": True})
    assert resp.status_code == 400
    _assert_error_contract(resp.get_json(), "INVALID_PAYLOAD", 400)
