# ============================================================================
# UnityAssetsManager - tests/test_filters.py
# ============================================================================
# Description: Unit tests for the filtering functionality.
# Version: 1.4.1
# ============================================================================

import pandas as pd
from lib.filters import apply_filter_stack, vectorized_tag_filter, is_tag_column

# Fix path to import filters
# import sys
# from pathlib import Path
# sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
# from filters import apply_filter_stack, vectorized_tag_filter, is_tag_column

SAMPLE_DF = pd.DataFrame(
    [
        {
            "Name": "Asset1",
            "Category": "Tools",
            "Tags": "a, b, c",
            "Price": 10
        }, {
            "Name": "Asset2",
            "Category": "Audio",
            "Tags": "b;d",
            "Price": 20
        }, {
            "Name": "Asset3",
            "Category": "Tools",
            "Tags": "e",
            "Price": 30
        },
    ]
)


def test_is_tag_column():
    assert is_tag_column("Tags")
    assert is_tag_column("Category")
    assert not is_tag_column("Name")
    assert not is_tag_column("Price")


def test_vectorized_tag_filter():
    # Tag 'b' is in Asset1 and Asset2
    res = vectorized_tag_filter(SAMPLE_DF["Tags"], ["b"])
    assert bool(res.iloc[0]) is True
    assert bool(res.iloc[1]) is True
    assert bool(res.iloc[2]) is False

    # Tag 'e' is only in Asset3
    res = vectorized_tag_filter(SAMPLE_DF["Tags"], ["e"])
    assert bool(res.iloc[0]) is False
    assert bool(res.iloc[1]) is False
    assert bool(res.iloc[2]) is True


def test_apply_filter_stack_include():
    stack = [{"mode": "include", "filters": {"Category": {"values": ["Tools"]}}}]
    res = apply_filter_stack(SAMPLE_DF, stack)
    assert len(res) == 2
    assert "Asset1" in res["Name"].values
    assert "Asset3" in res["Name"].values


def test_apply_filter_stack_exclude():
    stack = [{"mode": "exclude", "filters": {"Category": {"values": ["Tools"]}}}]
    res = apply_filter_stack(SAMPLE_DF, stack)
    assert len(res) == 1
    assert "Asset2" in res["Name"].values


def test_apply_filter_stack_with_search():
    stack = [{"mode": "include", "filters": {"Category": {"values": ["Tools"]}}, "search_term": "Asset3"}]
    res = apply_filter_stack(SAMPLE_DF, stack)
    assert len(res) == 1
    assert "Asset3" in res["Name"].values


def test_apply_filter_stack_with_invalid_regex():
    stack = [{"mode": "include", "filters": {"Name": {"search": "[invalid regex", "is_regex": True}}}]
    # Should not crash, should just return empty or handle safely
    res = apply_filter_stack(SAMPLE_DF, stack)
    assert len(res) == 0
