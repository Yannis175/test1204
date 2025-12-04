"""
Shared pytest fixtures and configuration for docker-jans-configurator tests.

This module provides common fixtures used across multiple test files.
"""
import os
import sys
from pathlib import Path

import pytest


# Add scripts directory to Python path for importing modules
@pytest.fixture(scope="session", autouse=True)
def add_scripts_to_path():
    """Add scripts directory to Python path."""
    scripts_dir = Path(__file__).parent.parent / 'scripts'
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))


@pytest.fixture
def project_root():
    """Provide project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def dockerfile_path(project_root):
    """Provide Dockerfile path."""
    return project_root / 'Dockerfile'


@pytest.fixture
def scripts_dir(project_root):
    """Provide scripts directory path."""
    return project_root / 'scripts'


@pytest.fixture
def requirements_path(project_root):
    """Provide requirements.txt path."""
    return project_root / 'requirements.txt'


@pytest.fixture
def mock_environment():
    """Provide clean environment for tests."""
    original_env = os.environ.copy()
    
    # Set test environment variables
    test_env = {
        'CN_CONFIG_ADAPTER': 'consul',
        'CN_SECRET_ADAPTER': 'vault',
        'CN_WAIT_MAX_TIME': '300',
        'CN_WAIT_SLEEP_DURATION': '10',
    }
    os.environ.update(test_env)
    
    yield test_env
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def temp_certs_dir(tmp_path):
    """Provide temporary certificates directory."""
    certs_dir = tmp_path / 'certs'
    certs_dir.mkdir()
    return certs_dir


@pytest.fixture
def temp_db_dir(tmp_path):
    """Provide temporary database directory."""
    db_dir = tmp_path / 'db'
    db_dir.mkdir()
    return db_dir


@pytest.fixture
def sample_config_ctx():
    """Provide sample configuration context."""
    return {
        'hostname': 'test.example.com',
        'orgName': 'Test Organization',
        'country_code': 'US',
        'state': 'Texas',
        'city': 'Austin',
        'admin_email': 'admin@example.com',
        'optional_scopes': [],
        'auth_sig_keys': 'RS256 RS384 RS512 ES256 ES384 ES512',
        'auth_enc_keys': 'RSA1_5 RSA-OAEP',
        'init_keys_exp': 48,
    }


@pytest.fixture
def sample_secret_ctx():
    """Provide sample secret context."""
    return {
        'admin_password': 'Test123!@#',
        'redis_password': 'redis_secret',
    }