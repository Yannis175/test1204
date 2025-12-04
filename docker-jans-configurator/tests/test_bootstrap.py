"""
Unit tests for bootstrap.py script.

Tests validate:
- Configuration generation logic
- Key generation functions
- Certificate handling
- Context management
- Error handling
"""
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
import tempfile
import os

import pytest


# Add scripts directory to path for importing
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))


class TestEncodeTemplate:
    """Test template encoding functionality."""

    @patch('builtins.open', new_callable=mock_open, read_data='Hello {{name}}')
    @patch('bootstrap.generate_base64_contents')
    @patch('bootstrap.safe_render')
    def test_encode_template_basic(self, mock_render, mock_b64, mock_file):
        """Test basic template encoding."""
        from bootstrap import encode_template
        
        mock_render.return_value = 'Hello World'
        mock_b64.return_value = 'SGVsbG8gV29ybGQ='
        
        ctx = {'config': {'name': 'World'}, 'secret': {}}
        result = encode_template('test.tmpl', ctx)
        
        assert result == 'SGVsbG8gV29ybGQ='
        mock_render.assert_called_once()
        mock_b64.assert_called_once()

    @patch('builtins.open', new_callable=mock_open, read_data='')
    def test_encode_template_empty_file(self, mock_file):
        """Test encoding empty template file."""
        from bootstrap import encode_template
        
        ctx = {'config': {}, 'secret': {}}
        result = encode_template('empty.tmpl', ctx)
        
        assert result is not None

    def test_encode_template_nested_context(self):
        """Test encoding with nested context data."""
        from bootstrap import encode_template
        
        # This would require mocking file operations
        pytest.skip("Requires complex mocking of file and template operations")


class TestOpenIDKeyGeneration:
    """Test OpenID key generation."""

    @patch('bootstrap.exec_cmd')
    def test_generate_openid_keys_success(self, mock_exec):
        """Test successful OpenID key generation."""
        from bootstrap import generate_openid_keys_hourly
        
        mock_exec.return_value = (b'{"keys": []}', b'', 0)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            jks_path = os.path.join(tmpdir, 'test.jks')
            jwks_path = os.path.join(tmpdir, 'test.json')
            
            out, err, code = generate_openid_keys_hourly(
                'password123',
                jks_path,
                jwks_path,
                'CN=Test',
                exp=48
            )
            
            assert code == 0
            mock_exec.assert_called_once()

    @patch('bootstrap.exec_cmd')
    def test_generate_openid_keys_failure(self, mock_exec):
        """Test OpenID key generation failure handling."""
        from bootstrap import generate_openid_keys_hourly
        
        mock_exec.return_value = (b'', b'Error message', 1)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            jks_path = os.path.join(tmpdir, 'test.jks')
            jwks_path = os.path.join(tmpdir, 'test.json')
            
            out, err, code = generate_openid_keys_hourly(
                'password123',
                jks_path,
                jwks_path,
                'CN=Test'
            )
            
            assert code == 1
            assert err == b'Error message'

    @patch('bootstrap.exec_cmd')
    def test_generate_openid_keys_custom_algorithms(self, mock_exec):
        """Test key generation with custom algorithms."""
        from bootstrap import generate_openid_keys_hourly
        
        mock_exec.return_value = (b'{"keys": []}', b'', 0)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            jks_path = os.path.join(tmpdir, 'test.jks')
            jwks_path = os.path.join(tmpdir, 'test.json')
            
            out, err, code = generate_openid_keys_hourly(
                'password123',
                jks_path,
                jwks_path,
                'CN=Test',
                sig_keys='RS256 ES256',
                enc_keys='RSA1_5'
            )
            
            assert code == 0
            call_args = mock_exec.call_args[0][0]
            assert 'RS256 ES256' in call_args
            assert 'RSA1_5' in call_args

    def test_generate_openid_keys_default_algorithms(self):
        """Test default algorithms are used when not specified."""
        from bootstrap import DEFAULT_SIG_KEYS, DEFAULT_ENC_KEYS
        
        assert 'RS256' in DEFAULT_SIG_KEYS
        assert 'ES256' in DEFAULT_SIG_KEYS
        assert 'RSA1_5' in DEFAULT_ENC_KEYS


class TestPKCS12Generation:
    """Test PKCS12 generation."""

    @patch('bootstrap.exec_cmd')
    def test_generate_pkcs12_success(self, mock_exec):
        """Test successful PKCS12 generation."""
        from bootstrap import generate_pkcs12
        
        mock_exec.return_value = (b'', b'', 0)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create dummy cert and key files
            cert_path = os.path.join(tmpdir, 'test.crt')
            key_path = os.path.join(tmpdir, 'test.key')
            Path(cert_path).touch()
            Path(key_path).touch()
            
            with patch('bootstrap.CERTS_DIR', tmpdir):
                generate_pkcs12('test', 'password123', 'example.com')
            
            mock_exec.assert_called_once()
            call_args = mock_exec.call_args[0][0]
            assert 'openssl' in call_args
            assert 'pkcs12' in call_args
            assert 'example.com' in call_args

    @patch('bootstrap.exec_cmd')
    def test_generate_pkcs12_failure(self, mock_exec):
        """Test PKCS12 generation failure."""
        from bootstrap import generate_pkcs12
        
        mock_exec.return_value = (b'', b'Error', 1)
        
        with pytest.raises(AssertionError, match="Failed to generate PKCS12"):
            generate_pkcs12('test', 'password123', 'example.com')


class TestCtxManager:
    """Test CtxManager class."""

    @patch('bootstrap.get_manager')
    def test_ctx_manager_initialization(self, mock_get_manager):
        """Test CtxManager initialization."""
        from bootstrap import CtxManager
        
        mock_manager = Mock()
        mock_manager.config.get_all.return_value = {}
        mock_manager.secret.get_all.return_value = {}
        
        ctx_mgr = CtxManager(mock_manager)
        
        assert ctx_mgr.manager == mock_manager
        assert '_configmap' in ctx_mgr.ctx
        assert '_secret' in ctx_mgr.ctx

    @patch('bootstrap.get_manager')
    def test_set_config_new_value(self, mock_get_manager):
        """Test setting new config value."""
        from bootstrap import CtxManager
        
        mock_manager = Mock()
        mock_manager.config.get_all.return_value = {}
        mock_manager.secret.get_all.return_value = {}
        
        ctx_mgr = CtxManager(mock_manager)
        result = ctx_mgr.set_config('test_key', 'test_value')
        
        assert result == 'test_value'
        assert ctx_mgr.ctx['_configmap']['test_key'] == 'test_value'

    @patch('bootstrap.get_manager')
    def test_set_config_reuse_existing(self, mock_get_manager):
        """Test reusing existing config value."""
        from bootstrap import CtxManager
        
        mock_manager = Mock()
        mock_manager.config.get_all.return_value = {'existing_key': 'existing_value'}
        mock_manager.secret.get_all.return_value = {}
        
        ctx_mgr = CtxManager(mock_manager)
        result = ctx_mgr.set_config('existing_key', 'new_value', reuse_if_exists=True)
        
        assert result == 'existing_value'
        assert ctx_mgr.ctx['_configmap']['existing_key'] == 'existing_value'

    @patch('bootstrap.get_manager')
    def test_set_config_callable_value(self, mock_get_manager):
        """Test setting config with callable value."""
        from bootstrap import CtxManager
        
        mock_manager = Mock()
        mock_manager.config.get_all.return_value = {}
        mock_manager.secret.get_all.return_value = {}
        
        ctx_mgr = CtxManager(mock_manager)
        result = ctx_mgr.set_config('test_key', lambda: 'generated_value')
        
        assert result == 'generated_value'
        assert ctx_mgr.ctx['_configmap']['test_key'] == 'generated_value'

    @patch('bootstrap.get_manager')
    def test_set_config_bytes_value(self, mock_get_manager):
        """Test setting config with bytes value."""
        from bootstrap import CtxManager
        
        mock_manager = Mock()
        mock_manager.config.get_all.return_value = {}
        mock_manager.secret.get_all.return_value = {}
        
        ctx_mgr = CtxManager(mock_manager)
        result = ctx_mgr.set_config('test_key', b'bytes_value')
        
        assert result == 'bytes_value'
        assert ctx_mgr.ctx['_configmap']['test_key'] == 'bytes_value'

    @patch('bootstrap.get_manager')
    def test_set_secret_new_value(self, mock_get_manager):
        """Test setting new secret value."""
        from bootstrap import CtxManager
        
        mock_manager = Mock()
        mock_manager.config.get_all.return_value = {}
        mock_manager.secret.get_all.return_value = {}
        
        ctx_mgr = CtxManager(mock_manager)
        result = ctx_mgr.set_secret('secret_key', 'secret_value')
        
        assert result == 'secret_value'
        assert ctx_mgr.ctx['_secret']['secret_key'] == 'secret_value'

    @patch('bootstrap.get_manager')
    def test_get_config_existing(self, mock_get_manager):
        """Test getting existing config value."""
        from bootstrap import CtxManager
        
        mock_manager = Mock()
        mock_manager.config.get_all.return_value = {}
        mock_manager.secret.get_all.return_value = {}
        
        ctx_mgr = CtxManager(mock_manager)
        ctx_mgr.set_config('test_key', 'test_value')
        
        result = ctx_mgr.get_config('test_key')
        assert result == 'test_value'

    @patch('bootstrap.get_manager')
    def test_get_config_nonexistent_with_default(self, mock_get_manager):
        """Test getting nonexistent config with default value."""
        from bootstrap import CtxManager
        
        mock_manager = Mock()
        mock_manager.config.get_all.return_value = {}
        mock_manager.secret.get_all.return_value = {}
        
        ctx_mgr = CtxManager(mock_manager)
        result = ctx_mgr.get_config('nonexistent', default='default_value')
        
        assert result == 'default_value'

    @patch('bootstrap.get_manager')
    def test_get_secret_existing(self, mock_get_manager):
        """Test getting existing secret value."""
        from bootstrap import CtxManager
        
        mock_manager = Mock()
        mock_manager.config.get_all.return_value = {}
        mock_manager.secret.get_all.return_value = {}
        
        ctx_mgr = CtxManager(mock_manager)
        ctx_mgr.set_secret('secret_key', 'secret_value')
        
        result = ctx_mgr.get_secret('secret_key')
        assert result == 'secret_value'


class TestCtxGenerator:
    """Test CtxGenerator class."""

    @patch('bootstrap.get_manager')
    def test_ctx_generator_initialization(self, mock_get_manager):
        """Test CtxGenerator initialization."""
        from bootstrap import CtxGenerator
        
        mock_manager = Mock()
        mock_manager.config.get_all.return_value = {}
        mock_manager.secret.get_all.return_value = {}
        
        params = {
            '_configmap': {'hostname': 'example.com'},
            '_secret': {'admin_password': 'test123'}
        }
        
        ctx_gen = CtxGenerator(mock_manager, params)
        
        assert ctx_gen.manager == mock_manager
        assert ctx_gen.configmap_params == params['_configmap']
        assert ctx_gen.secret_params == params['_secret']

    @patch('bootstrap.get_manager')
    @patch('bootstrap.get_random_chars')
    def test_transform_base_ctx(self, mock_random, mock_get_manager):
        """Test basic context transformation."""
        from bootstrap import CtxGenerator
        
        mock_manager = Mock()
        mock_manager.config.get_all.return_value = {}
        mock_manager.secret.get_all.return_value = {}
        mock_random.return_value = 'random_salt'
        
        params = {
            '_configmap': {
                'hostname': 'example.com',
                'orgName': 'Test Org',
                'country_code': 'US',
                'state': 'TX',
                'city': 'Austin',
                'admin_email': 'admin@example.com',
                'optional_scopes': []
            },
            '_secret': {
                'admin_password': 'test123'
            }
        }
        
        ctx_gen = CtxGenerator(mock_manager, params)
        
        with patch('bootstrap.ldap_encode') as mock_ldap:
            mock_ldap.return_value = 'encoded_password'
            ctx_gen.transform_base_ctx()
        
        assert ctx_gen.get_config('hostname') == 'example.com'
        assert ctx_gen.get_config('orgName') == 'Test Org'
        assert ctx_gen.get_secret('encoded_admin_password') == 'encoded_password'

    @patch('bootstrap.get_manager')
    def test_transform_redis_ctx(self, mock_get_manager):
        """Test Redis context transformation."""
        from bootstrap import CtxGenerator
        
        mock_manager = Mock()
        mock_manager.config.get_all.return_value = {}
        mock_manager.secret.get_all.return_value = {}
        
        params = {
            '_configmap': {},
            '_secret': {'redis_password': 'redis123'}
        }
        
        ctx_gen = CtxGenerator(mock_manager, params)
        ctx_gen.transform_redis_ctx()
        
        assert ctx_gen.get_secret('redis_password') == 'redis123'

    @patch('bootstrap.get_manager')
    def test_transform_redis_ctx_empty_password(self, mock_get_manager):
        """Test Redis context with empty password."""
        from bootstrap import CtxGenerator
        
        mock_manager = Mock()
        mock_manager.config.get_all.return_value = {}
        mock_manager.secret.get_all.return_value = {}
        
        params = {
            '_configmap': {},
            '_secret': {}
        }
        
        ctx_gen = CtxGenerator(mock_manager, params)
        ctx_gen.transform_redis_ctx()
        
        assert ctx_gen.get_secret('redis_password') == ''


class TestConstantsAndDefaults:
    """Test module constants and default values."""

    def test_default_sig_keys_defined(self):
        """Test default signature keys are defined."""
        from bootstrap import DEFAULT_SIG_KEYS
        
        assert isinstance(DEFAULT_SIG_KEYS, str)
        assert 'RS256' in DEFAULT_SIG_KEYS
        assert 'ES256' in DEFAULT_SIG_KEYS

    def test_default_enc_keys_defined(self):
        """Test default encryption keys are defined."""
        from bootstrap import DEFAULT_ENC_KEYS
        
        assert isinstance(DEFAULT_ENC_KEYS, str)
        assert 'RSA1_5' in DEFAULT_ENC_KEYS

    def test_directory_constants(self):
        """Test directory path constants."""
        from bootstrap import CONFIGURATOR_DIR, DB_DIR, CERTS_DIR, JAVALIBS_DIR
        
        assert CONFIGURATOR_DIR == '/opt/jans/configurator'
        assert JAVALIBS_DIR == f'{CONFIGURATOR_DIR}/javalibs'
        # DB_DIR and CERTS_DIR can be overridden by environment variables

    def test_logger_configured(self):
        """Test logger is properly configured."""
        from bootstrap import logger
        
        assert logger is not None
        assert logger.name == 'configurator'