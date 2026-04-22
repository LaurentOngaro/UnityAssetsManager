# ============================================================================
# UnityAssetsManager - tests/test_export_non_regression.py
# ============================================================================
# Description: Tests de non-régression pour les templates d'export.
# Version: 1.5.0
# ============================================================================

from io import BytesIO
from pathlib import Path

import pandas as pd
import pytest

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


@pytest.mark.parametrize(
    "template_name,pattern,expected_ext,expected_mime,expected_fragment",
    [
        ("CSV regression", "%DisplayName%,%Version%", "csv", "text/csv", "DisplayName,Version"),  #
        ("Markdown regression", "| %DisplayName% | %Version% |", "md", "text/markdown", "| DisplayName | Version |"),  #
        ("JSON regression", "%DisplayName%", "json", "application/json", '"assets"'),  #
        ("TXT regression", "%DisplayName% - %Version%", "txt", "text/plain", "Tree Pack - 1.0"),
    ],
)
def test_api_export_template_non_regression(monkeypatch, template_name, pattern, expected_ext, expected_mime, expected_fragment, ):
    """Ensure each export family keeps expected extension/mime/content contract."""
    mod = import_unity_assets_manager_module()
    import sys
    dm_module = sys.modules.get("lib.data_manager")
    assert dm_module is not None, "lib.data_manager not loaded"

    monkeypatch.setattr(dm_module.dm, "_df", SAMPLE_DF.copy())
    monkeypatch.setattr(mod.config, "export_templates", {template_name: {"description": "Template de test", "pattern": pattern, }})

    client = mod.app.test_client()
    response = client.post(
        "/api/export",
        json={
            "template": template_name,
            "columns": ["DisplayName", "Version", "Url"],
            "search": "",
            "filter_stack": [],
            "alias_map": {},
        },
    )

    assert response.status_code == 200

    content_disposition = response.headers.get("Content-Disposition", "")
    assert f".{expected_ext}" in content_disposition

    content_type = response.headers.get("Content-Type", "")
    assert expected_mime in content_type

    text = response.get_data(as_text=True)
    assert expected_fragment in text


@pytest.mark.parametrize(
    "template_name,pattern,expected_ext", [
        ("CSV batch", "%DisplayName%,%Version%", "csv"), ("Markdown batch", "| %DisplayName% | %Version% |", "md"),
        ("JSON batch", "%DisplayName%", "json"), ("TXT batch", "%DisplayName% - %Version%", "txt"),
    ],
)
def test_api_batch_export_writes_expected_extension(monkeypatch, tmp_path, template_name, pattern, expected_ext, ):
    """Headless export must keep extension inference stable for automation flows."""
    mod = import_unity_assets_manager_module()
    import sys
    dm_module = sys.modules.get("lib.data_manager")
    assert dm_module is not None, "lib.data_manager not loaded"

    monkeypatch.setattr(dm_module.dm, "_df", SAMPLE_DF.copy())
    monkeypatch.setattr(mod.config, "export_templates", {template_name: {"description": "Template de test", "pattern": pattern, }})

    client = mod.app.test_client()
    response = client.post(
        "/api/batch-export",
        json={
            "template": template_name,
            "columns": ["DisplayName", "Version", "Url"],
            "filter_stack": [],
            "alias_map": {},
            "output_dir": str(tmp_path),
            "file_name": "non_regression_export",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload is not None and payload.get("status") == "success"

    out_file = Path(payload["file"])
    assert out_file.exists()
    assert out_file.suffix == f".{expected_ext}"


def test_batch_export_applies_include_exclude_stack(monkeypatch, tmp_path):
    """Non-regression for include/exclude order in batch export mode."""
    mod = import_unity_assets_manager_module()
    import sys
    dm_module = sys.modules.get("lib.data_manager")
    assert dm_module is not None, "lib.data_manager not loaded"

    monkeypatch.setattr(dm_module.dm, "_df", SAMPLE_DF.copy())
    monkeypatch.setattr(
        mod.config, "export_templates",
        {"CSV stack": {
            "description": "Template CSV de test",
            "pattern": "%DisplayName%,%DisplayPublisher%,%DisplayCategory%",
        }}
    )

    filter_stack = [
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
    ]

    client = mod.app.test_client()
    response = client.post(
        "/api/batch-export",
        json={
            "template": "CSV stack",
            "columns": ["DisplayName", "DisplayPublisher", "DisplayCategory"],
            "filter_stack": filter_stack,
            "alias_map": {},
            "output_dir": str(tmp_path),
            "file_name": "stack_check",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload is not None and payload.get("status") == "success"

    out_file = Path(payload["file"])
    assert out_file.exists()

    exported_df = pd.read_csv(out_file)
    assert len(exported_df) == 1
    assert exported_df.iloc[0]["DisplayName"] == "Tree Pack"


def test_api_export_applies_filter_stack(monkeypatch):
    """The interactive export endpoint must export only the currently filtered rows."""
    mod = import_unity_assets_manager_module()
    import sys
    dm_module = sys.modules.get("lib.data_manager")
    assert dm_module is not None, "lib.data_manager not loaded"

    monkeypatch.setattr(dm_module.dm, "_df", SAMPLE_DF.copy())
    monkeypatch.setattr(
        mod.config, "export_templates",
        {"CSV export": {
            "description": "Template CSV de test",
            "pattern": "%DisplayName%,%DisplayPublisher%,%DisplayCategory%",
        }}
    )

    filter_stack = [
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
    ]

    client = mod.app.test_client()
    response = client.post("/api/export", json={"template": "CSV export", "filter_stack": filter_stack, "alias_map": {}, }, )

    assert response.status_code == 200

    exported_df = pd.read_csv(BytesIO(response.data))
    assert len(exported_df) == 1
    assert exported_df.iloc[0]["DisplayName"] == "Tree Pack"


def test_api_export_filters_invalid_assets_when_enabled(monkeypatch):
    """FEAT4: export must skip invalid assets when the option is enabled."""
    mod = import_unity_assets_manager_module()
    import sys
    dm_module = sys.modules.get("lib.data_manager")
    assert dm_module is not None, "lib.data_manager not loaded"

    df = pd.DataFrame(
        [
            {
                "DisplayName": "Valid Asset",
                "DisplayPublisher": "PublisherA",
                "DisplayCategory": "Tools",
                "Url": "https://example.com/valid",
                "Slug": "",
            }, {
                "DisplayName": "Invalid Missing Link",
                "DisplayPublisher": "PublisherB",
                "DisplayCategory": "Tools",
                "Url": "",
                "Slug": "",
            },
        ]
    )

    monkeypatch.setattr(dm_module.dm, "_df", df)
    monkeypatch.setattr(
        mod.config, "export_templates",
        {"CSV FEAT4": {
            "description": "Template CSV FEAT4",
            "pattern": "%DisplayName%,%DisplayPublisher%,%DisplayCategory%",
        }},
    )

    client = mod.app.test_client()
    response = client.post("/api/export", json={"template": "CSV FEAT4", "filter_stack": [], "alias_map": {}, "filter_invalid_assets": True, }, )

    assert response.status_code == 200
    exported_df = pd.read_csv(BytesIO(response.data))
    assert len(exported_df) == 1
    assert exported_df.iloc[0]["DisplayName"] == "Valid Asset"


def test_batch_export_always_filters_invalid_assets(monkeypatch, tmp_path):
    """Batch export must always skip invalid assets to reduce automation noise."""
    mod = import_unity_assets_manager_module()
    import sys
    dm_module = sys.modules.get("lib.data_manager")
    assert dm_module is not None, "lib.data_manager not loaded"

    df = pd.DataFrame(
        [
            {
                "DisplayName": "Valid Asset",
                "DisplayPublisher": "PublisherA",
                "DisplayCategory": "Tools",
                "Url": "https://example.com/valid",
                "Slug": "",
            }, {
                "DisplayName": "Invalid Missing Link",
                "DisplayPublisher": "PublisherB",
                "DisplayCategory": "Tools",
                "Url": "",
                "Slug": "",
            },
        ]
    )

    monkeypatch.setattr(dm_module.dm, "_df", df)
    monkeypatch.setattr(
        mod.config, "export_templates",
        {"CSV FEAT4 Batch": {
            "description": "Template CSV FEAT4 batch",
            "pattern": "%DisplayName%,%DisplayPublisher%,%DisplayCategory%",
        }},
    )

    client = mod.app.test_client()
    response = client.post(
        "/api/batch-export",
        json={
            "template": "CSV FEAT4 Batch",
            "filter_stack": [],
            "alias_map": {},
            "output_dir": str(tmp_path),
            "file_name": "feat4_batch_always",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload is not None and payload.get("status") == "success"
    assert payload.get("count") == 1

    out_file = Path(payload["file"])
    exported_df = pd.read_csv(out_file)
    assert len(exported_df) == 1
    assert exported_df.iloc[0]["DisplayName"] == "Valid Asset"


def test_export_template_resolves_uppercase_url_alias_case_insensitive(monkeypatch):
    """%URL% must resolve via alias map even when alias key casing differs."""
    mod = import_unity_assets_manager_module()

    df = pd.DataFrame([{"DisplayName": "Tree Pack", "AssetLink": "https://example.com/tree-pack", }])

    monkeypatch.setattr(
        mod.config, "export_templates",
        {"Markdown URL Alias": {
            "description": "Template de test alias URL",
            "pattern": "| [%DisplayName%](%URL%) |",
        }},
    )

    content = mod.config.apply_export_template(df, "Markdown URL Alias", alias_map={"Url": "assetLink"})
    assert "https://example.com/tree-pack" in content


def test_export_template_resolves_url_from_candidate_aliases(monkeypatch):
    """%URL% must resolve from declarative candidates when AssetLink exists."""
    mod = import_unity_assets_manager_module()

    df = pd.DataFrame([{"DisplayName": "Tree Pack", "AssetLink": "https://example.com/tree-pack"}])

    monkeypatch.setattr(
        mod.config, "export_templates",
        {"Markdown URL Candidates": {
            "description": "Template de test alias candidates URL",
            "pattern": "| [%DisplayName%](%URL%) |",
        }},
    )

    alias_map = {"Url": {"candidates": [{"source": "AssetLink"}, {"source": "Slug", "transform": "asset_store_url"}, ]}}

    content = mod.config.apply_export_template(df, "Markdown URL Candidates", alias_map=alias_map)
    assert "https://example.com/tree-pack" in content


def test_export_template_resolves_url_from_slug_variant_complex(monkeypatch):
    """%URL% must extract the numeric ID from a complex slug 'name-id'."""
    mod = import_unity_assets_manager_module()
    df = pd.DataFrame([{"DisplayName": "Test", "Slug": "my-asset-pack-302531"}])
    monkeypatch.setattr(mod.config, "export_templates", {"T": {"pattern": "%Url%"}})
    alias_map = {"Url": {"candidates": [{"source": "Slug", "transform": "asset_store_url"}]}}
    content = mod.config.apply_export_template(df, "T", alias_map=alias_map)
    assert "https://assetstore.unity.com/packages/slug/302531" in content


def test_export_template_resolves_url_from_slug_variant_numeric(monkeypatch):
    """%URL% must use a purely numeric slug as is."""
    mod = import_unity_assets_manager_module()
    df = pd.DataFrame([{"DisplayName": "Test", "Slug": "302531"}])
    monkeypatch.setattr(mod.config, "export_templates", {"T": {"pattern": "%Url%"}})
    alias_map = {"Url": {"candidates": [{"source": "Slug", "transform": "asset_store_url"}]}}
    content = mod.config.apply_export_template(df, "T", alias_map=alias_map)
    assert "https://assetstore.unity.com/packages/slug/302531" in content


def test_export_template_resolves_slug_from_url_variant_complex(monkeypatch):
    """%Slug% must extract ID from URL even if it's a full name-id slug in the path."""
    mod = import_unity_assets_manager_module()
    df = pd.DataFrame([{"DisplayName": "Test", "Url": "https://assetstore.unity.com/packages/slug/my-asset-pack-302531"}])
    monkeypatch.setattr(mod.config, "export_templates", {"T": {"pattern": "%Slug%"}})
    alias_map = {"Slug": {"candidates": [{"source": "Url", "transform": "slug_from_url"}]}}
    content = mod.config.apply_export_template(df, "T", alias_map=alias_map)
    assert "302531" in content


def test_export_template_raises_when_url_candidates_missing(monkeypatch):
    """%URL% must fail explicitly when neither AssetLink nor Slug is available."""
    mod = import_unity_assets_manager_module()

    df = pd.DataFrame([{"DisplayName": "Tree Pack", "DisplayPublisher": "PublisherA"}])

    monkeypatch.setattr(
        mod.config, "export_templates",
        {"Markdown URL Missing": {
            "description": "Template de test alias missing",
            "pattern": "| [%DisplayName%](%URL%) |",
        }},
    )

    alias_map = {"Url": {"candidates": [{"source": "AssetLink"}, {"source": "Slug", "transform": "asset_store_url"}, ]}}

    with pytest.raises(ValueError, match="Colonne manquante"):
        mod.config.apply_export_template(df, "Markdown URL Missing", alias_map=alias_map)


def test_api_test_path_accepts_csv_with_late_malformed_lines(tmp_path):
    """Setup path check must accept CSV even if some later rows are malformed."""
    mod = import_unity_assets_manager_module()

    csv_path = tmp_path / "late_bad_rows.csv"
    csv_path.write_text("A;B\n"
                        "1;ok\n"
                        "2;ok\n"
                        "3;ok\n"
                        "4;ok\n"
                        "5;ok\n"
                        "6;ok\n"
                        "\"bad;line\n"
                        "7;ok\n", encoding="utf-8")

    client = mod.app.test_client()
    response = client.post("/api/test-path", json={"path": str(csv_path)})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload is not None
    assert payload.get("exists") is True
    assert payload.get("type") == "csv"
    assert payload.get("cols") == 2
    assert int(payload.get("rows", 0)) >= 1
    assert "warning" in payload
