# ============================================================================
# UnityAssetsManager - errors.py
# ============================================================================
# Description: Centralized API error contract and helpers.
# Version: 1.2.10
# ============================================================================

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from flask import has_request_context, jsonify, request


class ErrorCode(str, Enum):
    INVALID_PAYLOAD = "INVALID_PAYLOAD"
    PROFILE_NOT_FOUND = "PROFILE_NOT_FOUND"
    DATA_NOT_FOUND = "DATA_NOT_FOUND"
    EXPORT_ERROR = "EXPORT_ERROR"
    BATCH_EXPORT_ERROR = "BATCH_EXPORT_ERROR"
    MISSING_PARAMS = "MISSING_PARAMS"
    INVALID_CONFIG = "INVALID_CONFIG"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    HTTP_ERROR = "HTTP_ERROR"


class AppError(Exception):

    def __init__(self, code: ErrorCode | str, message: str, http_status: int, details: dict[str, Any] | None = None, ) -> None:
        self.code = code.value if isinstance(code, ErrorCode) else str(code)
        self.message = message
        self.http_status = http_status
        self.details = details or {}
        super().__init__(message)


def build_error_payload(code: ErrorCode | str, message: str, http_status: int, details: dict[str, Any] | None = None, ) -> dict[str, Any]:
    path = request.path if has_request_context() else ""
    code_value = code.value if isinstance(code, ErrorCode) else str(code)
    return {
        "error": {
            "code": code_value,
            "message": message,
            "http_status": http_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": path,
            "details": details or {},
        }
    }


def create_error_response(code: ErrorCode | str, message: str, http_status: int, details: dict[str, Any] | None = None, ):
    payload = build_error_payload(code=code, message=message, http_status=http_status, details=details)
    return jsonify(payload), http_status
