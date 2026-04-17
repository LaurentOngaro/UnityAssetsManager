# ============================================================================
# UnityAssetsManager - tests/test_api_integration.py
# ============================================================================
# Description: Integration tests for data retrieval and filtering endpoints.
# Version: 1.2.12
# ============================================================================

import pytest
import pandas as pd

SAMPLE_DATA = [
    {
        "DisplayName": "Asset A",
        "DisplayPublisher": "Pub A",
        "DisplayCategory": "Cat 1"
    }, {
        "DisplayName": "Asset B",
        "DisplayPublisher": "Pub B",
        "DisplayCategory": "Cat 2"
    },
]


@pytest.fixture
def mock_data(monkeypatch):
    import sys
    dm_module = sys.modules.get("lib.data_manager")
    assert dm_module is not None
    monkeypatch.setattr(dm_module.dm, "_df", pd.DataFrame(SAMPLE_DATA))
    return dm_module.dm


def test_api_data_listing(client, mock_data):
    """Test standard paginated data retrieval."""
    resp = client.get("/api/data?draw=1&start=0&length=10")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["recordsTotal"] == 2
    assert len(data["data"]) == 2
    assert data["data"][0]["DisplayName"] == "Asset A"


def test_api_columns(client, mock_data):
    """Test columns retrieval."""
    resp = client.get("/api/columns")
    assert resp.status_code == 200
    cols = resp.get_json()
    assert "DisplayName" in cols
    assert "DisplayPublisher" in cols


def test_api_stats(client, mock_data):
    """Test statistics endpoint."""
    resp = client.get("/api/stats")
    assert resp.status_code == 200
    stats = resp.get_json()
    assert stats["total_rows"] == 2
    assert stats["total_columns"] == 3
