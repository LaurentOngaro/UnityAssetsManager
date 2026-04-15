# ============================================================================
# UnityAssetsManager - tests/test_unity_assets_manager_helpers.py
# ============================================================================
# Description: Tests unitaires pour les utilitaires et le moteur de filtrage.
# Version: 1.2.7
# ============================================================================

import importlib.util
import sys
import types
import uuid
from pathlib import Path


class _FlaskCorsStub:

    @staticmethod
    def CORS(app, *args, **kwargs):
        return app


def import_unity_assets_manager_module():
    """Import UnityAssetsManager `app.py` as an isolated module for tests."""
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    module_name = f"unity_assets_manager_for_test_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(module_name, str(app_path))
    assert spec is not None and spec.loader is not None

    if "flask_cors" not in sys.modules:
        flask_cors_stub = types.ModuleType("flask_cors")
        setattr(flask_cors_stub, "CORS", _FlaskCorsStub.CORS)
        sys.modules["flask_cors"] = flask_cors_stub

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module
