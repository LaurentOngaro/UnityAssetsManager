# ============================================================================
# UnityAssetsManager - tests/test_data_manager.py
# ============================================================================
# Description: Unit tests for the data manager (AssetDataManager).
# Version: 1.2.13
# ============================================================================

import sqlite3
import sys
from pathlib import Path

# Setup paths to find lib
current_dir = Path(__file__).resolve().parent
if str(current_dir.parent) not in sys.path:
    sys.path.insert(0, str(current_dir.parent))

# pylint: disable=wrong-import-position
from lib.data_manager import AssetDataManager  # type: ignore # noqa: E402


def test_detect_source_type():
    dm = AssetDataManager()
    assert dm.detect_source_type(Path("test.sqlite")) == "sqlite"
    assert dm.detect_source_type(Path("test.db")) == "sqlite"
    assert dm.detect_source_type(Path("test.csv")) == "csv"
    assert dm.detect_source_type(Path("test.txt")) == "csv"


def test_sqlite_loading(tmp_path, monkeypatch):
    dm = AssetDataManager()

    # Create dummy sqlite db
    db_path = tmp_path / "test_assets.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE assets (id INTEGER, name TEXT)")
    conn.execute("INSERT INTO assets VALUES (1, 'asset1'), (2, 'asset2')")
    conn.commit()
    conn.close()

    from lib.config import config as app_config  # type: ignore
    monkeypatch.setattr(app_config, "data_path", str(db_path))
    monkeypatch.setattr(app_config, "db_table", "assets")

    df = dm.load_data(force_reload=True)
    assert not df.empty
    assert len(df) == 2
    assert "asset1" in df["name"].values


def test_csv_loading(tmp_path, monkeypatch):
    dm = AssetDataManager()

    # Create dummy csv
    csv_path = tmp_path / "test_assets.csv"
    csv_path.write_text("id,name\n1,asset1\n2,asset2\n")

    from lib.config import config as app_config  # type: ignore
    monkeypatch.setattr(app_config, "data_path", str(csv_path))

    df = dm.load_data(force_reload=True)
    assert not df.empty
    assert len(df) == 2
    assert "asset1" in df["name"].values
