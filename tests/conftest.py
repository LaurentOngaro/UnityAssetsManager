# ============================================================================
# UnityAssetsManager - tests/conftest.py
# ============================================================================
# Description: Shared pytest fixtures and configuration.
# Version: 1.2.10
# ============================================================================

import pytest
from .test_unity_assets_manager_helpers import import_unity_assets_manager_module


@pytest.fixture
def mod():
    """Returns the UnityAssetsManager module."""
    return import_unity_assets_manager_module()


@pytest.fixture
def client(mod):
    """Returns a Flask test client."""
    return mod.app.test_client()


@pytest.fixture
def config(mod):
    """Returns the application config object."""
    return mod.config
