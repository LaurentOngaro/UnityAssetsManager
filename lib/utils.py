# ============================================================================
# UnityAssetsManager - utils.py
# ============================================================================
# Description: Generic utility functions (JSONC, parsing).
# Version: 1.2.20
# ============================================================================

import json
from pathlib import Path
from typing import Any


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
