"""
Unit tests for settings.py configuration.

Tests validate:
- Logging configuration
- Log levels
- Log formats
- Handler configuration
"""
import sys
from pathlib import Path

import pytest


# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))


class TestLoggingConfiguration:
    """Test logging configuration."""

    def test_logging_config_exists(self):
        """Verify LOGGING_CONFIG is defined."""
        from settings import LOGGING_CONFIG
        
        assert LOGGING_CONFIG is not None
        assert isinstance(LOGGING_CONFIG, dict)

    def test_logging_version_specified(self):
        """Verify logging config version is specified."""
        from settings import LOGGING_CONFIG
        
        assert 'version' in LOGGING_CONFIG
        assert LOGGING_CONFIG['version'] == 1

    def test_formatters_defined(self):
        """Verify formatters are defined."""
        from settings import LOGGING_CONFIG
        
        assert 'formatters' in LOGGING_CONFIG
        assert 'default' in LOGGING_CONFIG['formatters']

    def test_formatter_includes_required_fields(self):
        """Verify formatter includes required fields."""
        from settings import LOGGING_CONFIG
        
        default_format = LOGGING_CONFIG['formatters']['default']['format']
        
        # Should include level, name, timestamp, message
        assert '%(levelname)s' in default_format
        assert '%(name)s' in default_format
        assert '%(asctime)s' in default_format
        assert '%(message)s' in default_format

    def test_handlers_defined(self):
        """Verify handlers are defined."""
        from settings import LOGGING_CONFIG
        
        assert 'handlers' in LOGGING_CONFIG
        assert 'console' in LOGGING_CONFIG['handlers']

    def test_console_handler_uses_stream(self):
        """Verify console handler uses StreamHandler."""
        from settings import LOGGING_CONFIG
        
        console_handler = LOGGING_CONFIG['handlers']['console']
        assert console_handler['class'] == 'logging.StreamHandler'
        assert console_handler['formatter'] == 'default'

    def test_loggers_defined(self):
        """Verify loggers are defined."""
        from settings import LOGGING_CONFIG
        
        assert 'loggers' in LOGGING_CONFIG
        assert 'jans.pycloudlib' in LOGGING_CONFIG['loggers']
        assert 'configurator' in LOGGING_CONFIG['loggers']

    def test_pycloudlib_logger_configuration(self):
        """Verify jans.pycloudlib logger configuration."""
        from settings import LOGGING_CONFIG
        
        pycloudlib_logger = LOGGING_CONFIG['loggers']['jans.pycloudlib']
        
        assert 'console' in pycloudlib_logger['handlers']
        assert pycloudlib_logger['level'] == 'INFO'
        assert pycloudlib_logger['propagate'] is True

    def test_configurator_logger_configuration(self):
        """Verify configurator logger configuration."""
        from settings import LOGGING_CONFIG
        
        configurator_logger = LOGGING_CONFIG['loggers']['configurator']
        
        assert 'console' in configurator_logger['handlers']
        assert configurator_logger['level'] == 'INFO'
        assert configurator_logger['propagate'] is False

    def test_logging_levels_appropriate(self):
        """Verify logging levels are appropriate for production."""
        from settings import LOGGING_CONFIG
        
        for logger_name, logger_config in LOGGING_CONFIG['loggers'].items():
            level = logger_config.get('level', 'INFO')
            # Should not use DEBUG in production default config
            assert level in ['INFO', 'WARNING', 'ERROR', 'CRITICAL'], \
                f"Logger '{logger_name}' should not default to DEBUG level"


class TestLoggingIntegration:
    """Test logging integration with the application."""

    def test_logging_config_can_be_applied(self):
        """Verify logging config can be applied without errors."""
        import logging.config
        from settings import LOGGING_CONFIG
        
        # Should not raise an exception
        logging.config.dictConfig(LOGGING_CONFIG)

    def test_configured_loggers_work(self):
        """Verify configured loggers can be instantiated."""
        import logging.config
        import logging
        from settings import LOGGING_CONFIG
        
        logging.config.dictConfig(LOGGING_CONFIG)
        
        pycloudlib_logger = logging.getLogger('jans.pycloudlib')
        configurator_logger = logging.getLogger('configurator')
        
        assert pycloudlib_logger is not None
        assert configurator_logger is not None
        assert pycloudlib_logger.level == logging.INFO
        assert configurator_logger.level == logging.INFO