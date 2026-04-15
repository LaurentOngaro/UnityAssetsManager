from .test_unity_assets_manager_helpers import import_unity_assets_manager_module


def test_api_errors_contract(monkeypatch, tmp_path):
    mod = import_unity_assets_manager_module()
    client = mod.app.test_client()

    # 1. Invalid Payload (setup)
    resp = client.post("/api/setup", data="not a json", content_type="application/json")
    assert resp.status_code == 400
    data = resp.get_json()
    assert data is not None
    assert "error" in data
    assert data["error"]["code"] == "INVALID_PAYLOAD"
    assert "timestamp" in data["error"]

    # 2. Profile absent (GET)
    resp = client.get("/api/profiles/this_profile_does_not_exist")
    assert resp.status_code == 404
    data = resp.get_json()
    assert data["error"]["code"] == "PROFILE_NOT_FOUND"

    # 3. Batch export missing template
    resp = client.post("/api/batch-export", json={"profile": "some_profile"})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"]["code"] == "MISSING_PARAMS"

    # 4. Batch export missing profile
    resp = client.post("/api/batch-export", json={"template": "JSON batch", "profile": "non_existent"})
    assert resp.status_code == 404
    data = resp.get_json()
    assert data["error"]["code"] == "PROFILE_NOT_FOUND"

    # 5. Export with missing data
    resp = client.post("/api/export", data="not a json", content_type="application/json")
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"]["code"] == "INVALID_PAYLOAD"

    # 6. Test-path empty path
    resp = client.post("/api/test-path", json={"path": ""})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"]["code"] == "INVALID_PAYLOAD"

    # 7. Test-path invalid payload
    resp = client.post("/api/test-path", data="not json", content_type="application/json")
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"]["code"] == "INVALID_PAYLOAD"
