# ============================================================================
# UnityAssetsManager - tests/test_manual_checklist.py
# ============================================================================
# Description: Integration test coverage for the manual checklist flow.
# Version: 1.2.14
# ============================================================================

from __future__ import annotations

import sys
import uuid
from pathlib import Path

import pandas as pd

from .test_unity_assets_manager_helpers import import_unity_assets_manager_module

SAMPLE_DF = pd.DataFrame(
    [
        {
            "DisplayName": "Tree Pack",
            "DisplayPublisher": "PublisherA",
            "DisplayCategory": "Tools",
            "Version": "1.0",
            "Url": "https://example.com/tree-pack",
        }, {
            "DisplayName": "Rock Pack",
            "DisplayPublisher": "PublisherB",
            "DisplayCategory": "Tools",
            "Version": "2.0",
            "Url": "https://example.com/rock-pack",
        }, {
            "DisplayName": "Music Pack",
            "DisplayPublisher": "PublisherC",
            "DisplayCategory": "Audio",
            "Version": "3.0",
            "Url": "https://example.com/music-pack",
        },
    ]
)

EXPORT_CASES = (("CSV sans URL", "csv"), ("table markdown sans URL", "md"), ("liste markdown sans URL", "md"), ("texte simple sans URL", "txt"), )


def _assert_export_content(exported_path: Path, expected_ext: str) -> None:
    if expected_ext == "csv":
        exported_df = pd.read_csv(exported_path)
        assert len(exported_df) == 1
        assert exported_df.iloc[0]["DisplayName"] == "Tree Pack"
        return

    content = exported_path.read_text(encoding="utf-8")
    assert "Tree Pack" in content
    assert "Rock Pack" not in content


def test_manual_checklist_api_flow(monkeypatch, tmp_path):
    """Replacement pytest coverage for the old manual checklist helper."""
    mod = import_unity_assets_manager_module()
    routes_module = sys.modules.get("lib.routes")
    assert routes_module is not None, "routes module not loaded"

    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(routes_module, "PROFILES_DIR", profiles_dir, raising=False)
    monkeypatch.setattr(routes_module.dm, "get_data", lambda: SAMPLE_DF.copy())

    client = mod.app.test_client()
    profile_name = f"manual_checklist_{uuid.uuid4().hex}"
    profile_payload = {
        "name":
        profile_name,
        "columns": ["DisplayName", "DisplayPublisher", "DisplayCategory", "Version"],
        "filter_stack": [
            {
                "mode": "include",
                "filters": {
                    "DisplayCategory": {
                        "values": ["Tools"],
                    }
                },
                "search_term": "",
            }, {
                "mode": "exclude",
                "filters": {
                    "DisplayPublisher": {
                        "values": ["PublisherB"],
                    }
                },
                "search_term": "",
            },
        ],
    }

    try:
        profiles_response = client.get("/api/profiles")
        assert profiles_response.status_code == 200
        assert isinstance(profiles_response.get_json(), list)

        save_response = client.post("/api/profiles", json=profile_payload)
        assert save_response.status_code == 200
        assert save_response.get_json() == {"status": "success", "message": f"Profil '{profile_name}' sauvegardé", }

        loaded_response = client.get(f"/api/profiles/{profile_name}")
        assert loaded_response.status_code == 200
        loaded_profile = loaded_response.get_json()
        assert loaded_profile is not None
        assert loaded_profile.get("name") == profile_name
        modes = [step.get("mode") for step in loaded_profile.get("filter_stack", [])]
        assert "include" in modes
        assert "exclude" in modes

        for template_name, expected_ext in EXPORT_CASES:
            export_name = f"manual_checklist_{expected_ext}_{uuid.uuid4().hex}.{expected_ext}"
            output_path = tmp_path / export_name
            batch_response = client.post(
                "/api/batch-export", json={
                    "profile": profile_name,
                    "template": template_name,
                    "output_path": str(output_path),
                },
            )

            assert batch_response.status_code == 200
            batch_payload = batch_response.get_json()
            assert batch_payload is not None
            assert batch_payload.get("status") == "success"

            exported_path = Path(batch_payload["file"])
            assert exported_path.exists()
            assert exported_path.suffix == f".{expected_ext}"
            _assert_export_content(exported_path, expected_ext)

    finally:
        client.delete(f"/api/profiles/{profile_name}")
