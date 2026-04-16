# ============================================================================
# UnityAssetsManager - filters.py
# ============================================================================
# Description: Filtering engine and search logic (filter stacks, tags).
# Version: 1.2.9
# ============================================================================

import pandas as pd
import re


def is_tag_column(name: str) -> bool:
    """Determine if a column should be treated as a tag column."""
    if not isinstance(name, str):
        return False
    n = name.lower()
    patterns = [r"tag", r"tags", r"category", r"categories", r"genre"]
    return any(re.search(pat, n) for pat in patterns)


def tokenize_cell(cell: str):
    """Split tag cell into tokens."""
    if not isinstance(cell, str):
        return []
    return [t.strip() for t in re.split(r"[;,|]", cell) if t.strip()]


def vectorized_tag_filter(series: pd.Series, selected_tags: list) -> pd.Series:
    """Vectorized filtering for tag columns."""
    if not selected_tags:
        return pd.Series(True, index=series.index)
    escaped_tags = [re.escape(str(tag)) for tag in selected_tags]
    pattern = '|'.join(rf'(?:^|[;,|\s]){tag}(?:[;,|\s]|$)' for tag in escaped_tags)
    try:
        return series.astype(str).str.contains(pattern, case=False, na=False, regex=True)
    except Exception:
        return series.astype(str).apply(lambda s: any(t in tokenize_cell(s) for t in selected_tags))


def _find_col(cols: list, target: str, alias_map: dict | None = None) -> str | None:
    if not target:
        return None
    tgt = str(target)
    for c in cols:
        if isinstance(c, str) and c.lower() == tgt.lower():
            return c
    if alias_map:
        canon = alias_map.get(tgt) or alias_map.get(tgt.lower())
        if canon:
            for c in cols:
                if isinstance(c, str) and c.lower() == str(canon).lower():
                    return c
    return None


def _build_alias_map_from_profile(profile: dict | None) -> dict:
    if not profile or not isinstance(profile, dict):
        return {}
    raw = profile.get('column_aliases') or {}
    if not isinstance(raw, dict):
        return {}
    return {str(k): str(v) for k, v in raw.items()}


def _resolve_col_name(name: str, cols: list, alias_map: dict | None = None) -> str | None:
    if not name:
        return None
    return _find_col(cols, name, alias_map)


def apply_filter_stack(df: pd.DataFrame, filter_stack: list | None, alias_map: dict | None = None) -> pd.DataFrame:
    """Apply a stack of filters to a DataFrame."""
    if df is None or df.empty:
        return df

    alias_map = alias_map or {}
    filtered_df = df.copy()

    for filter_item in (filter_stack or []):
        mode = filter_item.get('mode', 'include')
        filters = filter_item.get('filters', {}) or {}
        item_search_term = filter_item.get('search_term', '')
        item_mask = pd.Series(True, index=filtered_df.index)

        for col, filter_data in filters.items():
            resolved_col = _resolve_col_name(col, list(filtered_df.columns), alias_map)
            if not resolved_col or resolved_col not in filtered_df.columns:
                continue

            search_val = filter_data.get('search', '')
            is_regex = filter_data.get('is_regex', False)
            selected = filter_data.get('values', []) or []
            col_mask = pd.Series(False, index=filtered_df.index)

            if search_val:
                try:
                    col_mask = filtered_df[resolved_col].astype(str).str.contains(search_val, case=False, na=False, regex=is_regex)
                except Exception:
                    col_mask = pd.Series(False, index=filtered_df.index)
            elif selected:
                if is_tag_column(resolved_col):
                    if '[Vide]' in selected:
                        selected_clean = [v for v in selected if v != '[Vide]']
                        col_mask = filtered_df[resolved_col].isna() | vectorized_tag_filter(filtered_df[resolved_col], selected_clean)
                    else:
                        col_mask = vectorized_tag_filter(filtered_df[resolved_col], selected)
                else:
                    if '[Vide]' in selected:
                        selected_clean = [v for v in selected if v != '[Vide]']
                        col_mask = filtered_df[resolved_col].isin(selected_clean) | filtered_df[resolved_col].isna()
                    else:
                        col_mask = filtered_df[resolved_col].isin(selected)
            item_mask &= col_mask

        if item_search_term:
            item_search_regex = filter_item.get('is_regex', False)
            try:
                if '__search_blob__' in filtered_df.columns:
                    search_mask = filtered_df['__search_blob__'].str.contains(item_search_term.lower(), case=False, na=False, regex=item_search_regex)
                else:
                    search_mask = filtered_df.astype(str).apply(
                        lambda row: row.str.contains(item_search_term, case=False, na=False, regex=item_search_regex).any(), axis=1
                    )
                item_mask &= search_mask
            except re.error:
                pass

        if mode == 'include':
            filtered_df = filtered_df[item_mask]
        else:
            filtered_df = filtered_df[~item_mask]
    return filtered_df
