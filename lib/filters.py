# ============================================================================
# UnityAssetsManager - filters.py
# ============================================================================
# Description: Filtering engine and search logic (filter stacks, tags).
# Version: 1.3.0
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
    alias_map = {}
    for key, value in raw.items():
        if isinstance(value, dict):
            source = value.get('source') or value.get('column')
            if not source:
                candidates = value.get('candidates') or value.get('choices') or []
                for candidate in candidates:
                    if isinstance(candidate, dict):
                        source = candidate.get('source') or candidate.get('column')
                    elif candidate:
                        source = candidate
                    if source:
                        break
            if source:
                alias_map[str(key)] = str(source)
        elif value is not None:
            alias_map[str(key)] = str(value)
    return alias_map


def _resolve_col_name(name: str, cols: list, alias_map: dict | None = None) -> str | None:
    if not name:
        return None
    return _find_col(cols, name, alias_map)


def _resolve_first_col(cols: list, candidates: list[str], alias_map: dict | None = None) -> str | None:
    for candidate in candidates:
        resolved = _resolve_col_name(candidate, cols, alias_map)
        if resolved:
            return resolved
    return None


def _missing_mask(series: pd.Series) -> pd.Series:
    text = series.astype(str).str.strip()
    return series.isna() | text.eq('') | text.str.lower().isin({'nan', 'none', 'null'})


def filter_invalid_assets(df: pd.DataFrame, alias_map: dict | None = None) -> pd.DataFrame:
    """Remove rows that are missing required identity fields for exports/UI usage."""
    if df is None or df.empty:
        return df

    cols = list(df.columns)
    aliases = alias_map or {}

    name_col = _resolve_first_col(cols, ['DisplayName', 'Name', 'AssetName'], aliases)
    category_col = _resolve_first_col(cols, ['DisplayCategory', 'Category', 'AssetCategory'], aliases)
    publisher_col = _resolve_first_col(cols, ['DisplayPublisher', 'Publisher', 'AssetPublisher'], aliases)
    slug_col = _resolve_first_col(cols, ['Slug', 'AssetSlug', 'DisplaySlug'], aliases)
    url_col = _resolve_first_col(cols, ['Url', 'URL', 'AssetLink', 'AssetUrl', 'AssetURL', 'Link'], aliases)

    index = df.index
    missing_name = _missing_mask(df[name_col]) if name_col else pd.Series(True, index=index)
    missing_category = _missing_mask(df[category_col]) if category_col else pd.Series(True, index=index)
    missing_publisher = _missing_mask(df[publisher_col]) if publisher_col else pd.Series(True, index=index)
    missing_slug = _missing_mask(df[slug_col]) if slug_col else pd.Series(True, index=index)
    missing_url = _missing_mask(df[url_col]) if url_col else pd.Series(True, index=index)

    valid_slug_or_url = ~(missing_slug & missing_url)
    has_required_display_fields = ~(missing_name | missing_category | missing_publisher)
    valid_mask = valid_slug_or_url & has_required_display_fields
    return df[valid_mask]


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
