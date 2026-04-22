# ============================================================================
# UnityAssetsManager - tests/test_profiles_non_regression.py
# ============================================================================
# Description: Non-regression checks for profile structure consistency.
# Version: 1.4.1
# ============================================================================

from pathlib import Path

from lib.utils import read_json


def test_all_profiles_define_column_aliases():
    """PROF1: all profile files must expose a column_aliases object."""
    profiles_dir = Path(__file__).resolve().parents[1] / "profiles"
    profile_files = sorted(profiles_dir.glob("*.jsonc"))

    assert profile_files, "No profile files found"

    for profile_file in profile_files:
        profile_data = read_json(profile_file)
        assert "column_aliases" in profile_data, f"Missing column_aliases in {profile_file.name}"
        assert isinstance(profile_data["column_aliases"], dict), f"column_aliases must be an object in {profile_file.name}"
