# ============================================================================
# UnityAssetsManager - utils.py
# ============================================================================
# Description: Generic utility functions (JSONC, parsing).
# Version: 1.3.0
# ============================================================================

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

_DISPLAY_SEPARATOR_RE = re.compile(r"[\u30fb\u00b7\u2022\u2219\u2043\u30a0\u30fc\u2010-\u2015\u3000]+")
_SPACE_RE = re.compile(r"\s+")
_IDENTIFIER_RE = re.compile(r"[^A-Za-z0-9]+")
_SAFE_LABEL_PUNCTUATION = {"-", "_", "'", "’", ".", ",", ":", ";", "/", "&", "+"}


def _normalize_unicode_label_char(ch: str) -> str:
    category = unicodedata.category(ch)
    if category[0] in {"L", "N", "M"}:
        return ch
    if ch.isspace():
        return " "
    if ch in _SAFE_LABEL_PUNCTUATION:
        return ch
    return " "


def strip_jsonc(src: str) -> str:
    """Strip // and /* */ comments from src while preserving string literals."""
    out = []
    i = 0
    n = len(src)
    in_string = False
    string_delim = ''
    escape = False
    in_line_comment = False
    in_block_comment = False

    while i < n:
        ch = src[i]
        if in_line_comment:
            if ch == '\n':
                in_line_comment = False
                out.append(ch)
            i += 1
            continue
        if in_block_comment:
            if ch == '*' and i + 1 < n and src[i + 1] == '/':
                in_block_comment = False
                i += 2
            else:
                i += 1
            continue
        if in_string:
            out.append(ch)
            if escape:
                escape = False
            elif ch == '\\':
                escape = True
            elif ch == string_delim:
                in_string = False
            i += 1
            continue
        if ch == '"' or ch == "'":
            in_string = True
            string_delim = ch
            out.append(ch)
            i += 1
            continue
        if ch == '/' and i + 1 < n and src[i + 1] == '/':
            in_line_comment = True
            i += 2
            continue
        if ch == '/' and i + 1 < n and src[i + 1] == '*':
            in_block_comment = True
            i += 2
            continue
        out.append(ch)
        i += 1
    return ''.join(out)


def read_json(path: Path) -> Any:
    """Read a JSON or JSONC file."""
    raw = path.read_text(encoding='utf-8')
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        cleaned = strip_jsonc(raw)
        return json.loads(cleaned)


def write_json_normalized(path: Path, obj: Any, backup: bool = True) -> None:
    """Write canonical JSON."""
    text = json.dumps(obj, ensure_ascii=False, indent=2) + "\n"
    if path.exists():
        src = path.read_text(encoding='utf-8')
        if ('//' in src) or ('/*' in src) or (src.strip() != text.strip()):
            if backup:
                bak = path.with_suffix(path.suffix + '.bak')
                bak.write_text(src, encoding='utf-8')
    path.write_text(text, encoding='utf-8')


def _parse_bool(value: Any, default: bool) -> bool:
    """Convert value to boolean."""
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _parse_int(value: Any, default: int) -> int:
    """Convert value to integer."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def normalize_asset_label_text(value: Any) -> Any:
    """Normalize visible asset labels to ASCII-safe text."""
    if not isinstance(value, str):
        return value

    text = _DISPLAY_SEPARATOR_RE.sub(" ", value)
    text = text.replace("\u200b", " ").replace("\ufeff", " ")
    text = "".join(_normalize_unicode_label_char(ch) for ch in text)
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = _SPACE_RE.sub(" ", text).strip()
    return text


def normalize_asset_identifier_text(value: Any) -> Any:
    """Normalize asset identifiers and slugs to ASCII-safe tokens."""
    if not isinstance(value, str):
        return value

    text = normalize_asset_label_text(value)
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = _IDENTIFIER_RE.sub("-", text)
    text = re.sub(r"-+", "-", text).strip("-").lower()
    return text


def normalize_asset_column_value(column_name: str, value: Any) -> Any:
    """Normalize a value according to the semantics of its column name."""
    if not isinstance(value, str):
        return value

    column = str(column_name or "").lower()
    if any(token in column for token in ("slug", "id", "identifier", "key")):
        return normalize_asset_identifier_text(value)
    if any(token in column for token in ("name", "title", "label", "publisher", "category")):
        return normalize_asset_label_text(value)
    return value


def sanitize_asset_dataframe(df):
    """Normalize asset-like columns in a DataFrame while preserving useful Unicode text."""
    try:
        import pandas as pd  # Local import to avoid forcing pandas for non-data callers.
    except Exception:
        return df

    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return df

    sanitized = df.copy()
    for column in sanitized.columns:
        if not isinstance(column, str):
            continue
        if not any(token in column.lower() for token in ("slug", "id", "identifier", "key", "name", "title", "label", "publisher", "category")):
            continue
        sanitized[column] = sanitized[column].apply(lambda value: normalize_asset_column_value(column, value))

    return sanitized
