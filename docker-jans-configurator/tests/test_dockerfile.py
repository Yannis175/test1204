"""
Unit tests for Dockerfile structure and best practices.

Tests validate:
- Base image specification and pinning
- Layer optimization and caching
- Security best practices
- Build argument handling
- Environment variable configuration
- User and permission management
"""
import re
import os
from pathlib import Path

import pytest


@pytest.fixture
def dockerfile_path():
    """Provide path to the Dockerfile."""
    return Path(__file__).parent.parent / "Dockerfile"


@pytest.fixture
def dockerfile_content(dockerfile_path):
    """Load Dockerfile content."""
    with open(dockerfile_path, 'r') as f:
        return f.read()


@pytest.fixture
def dockerfile_lines(dockerfile_content):
    """Split Dockerfile into lines for line-by-line analysis."""
    return [line.strip() for line in dockerfile_content.split('\n') if line.strip()]


class TestDockerfileStructure:
    """Test Dockerfile structure and organization."""

    def test_dockerfile_exists(self, dockerfile_path):
        """Verify Dockerfile exists in expected location."""
        assert dockerfile_path.exists(), "Dockerfile must exist"
        assert dockerfile_path.is_file(), "Dockerfile must be a file"

    def test_dockerfile_not_empty(self, dockerfile_content):
        """Verify Dockerfile is not empty."""
        assert len(dockerfile_content.strip()) > 0, "Dockerfile cannot be empty"

    def test_dockerfile_has_from_instruction(self, dockerfile_lines):
        """Verify Dockerfile starts with FROM instruction."""
        first_instruction = next(
            (line for line in dockerfile_lines if not line.startswith('#')),
            None
        )
        assert first_instruction is not None, "Dockerfile must have at least one instruction"
        assert first_instruction.startswith('FROM'), "First instruction must be FROM"

    def test_from_instruction_format(self, dockerfile_lines):
        """Verify FROM instruction is properly formatted."""
        from_line = next(
            (line for line in dockerfile_lines if line.startswith('FROM')),
            None
        )
        assert from_line is not None, "FROM instruction must exist"
        # Should have format: FROM image:tag@digest
        assert '@sha256:' in from_line, "FROM must include digest for reproducibility"


class TestBaseImage:
    """Test base image specification and version."""

    def test_base_image_is_liberica_jre(self, dockerfile_lines):
        """Verify base image is BellSoft Liberica JRE Alpine."""
        from_line = next(
            (line for line in dockerfile_lines if line.startswith('FROM')),
            None
        )
        assert 'bellsoft/liberica-openjre-alpine' in from_line, \
            "Must use BellSoft Liberica JRE Alpine as base image"

    def test_base_image_version_specified(self, dockerfile_lines):
        """Verify base image has explicit version tag."""
        from_line = next(
            (line for line in dockerfile_lines if line.startswith('FROM')),
            None
        )
        # Should have format: image:version@digest
        match = re.search(r'bellsoft/liberica-openjre-alpine:([^@]+)', from_line)
        assert match is not None, "Base image must have version tag"
        version = match.group(1)
        assert version, "Version tag cannot be empty"
        assert version != 'latest', "Should not use 'latest' tag"

    def test_base_image_digest_pinned(self, dockerfile_lines):
        """Verify base image is pinned with SHA256 digest."""
        from_line = next(
            (line for line in dockerfile_lines if line.startswith('FROM')),
            None
        )
        assert '@sha256:' in from_line, "Base image must be pinned with SHA256 digest"
        # Extract and validate digest format
        match = re.search(r'@sha256:([a-f0-9]{64})', from_line)
        assert match is not None, "SHA256 digest must be valid (64 hex characters)"

    def test_java_version_is_25(self, dockerfile_lines):
        """Verify Java version is 25 as per the upgrade."""
        from_line = next(
            (line for line in dockerfile_lines if line.startswith('FROM')),
            None
        )
        # The version should be 25-37 or similar
        assert ':25-' in from_line or ':25@' in from_line, \
            "Java version should be 25 after upgrade"

    def test_alpine_variant(self, dockerfile_lines):
        """Verify using Alpine Linux variant for minimal size."""
        from_line = next(
            (line for line in dockerfile_lines if line.startswith('FROM')),
            None
        )
        assert 'alpine' in from_line.lower(), "Should use Alpine variant for minimal image size"


class TestSecurityPractices:
    """Test security best practices in Dockerfile."""

    def test_non_root_user_created(self, dockerfile_content):
        """Verify non-root user is created."""
        assert 'adduser' in dockerfile_content or 'useradd' in dockerfile_content, \
            "Must create non-root user for security"

    def test_user_instruction_present(self, dockerfile_content):
        """Verify USER instruction switches to non-root user."""
        assert re.search(r'^USER \d+', dockerfile_content, re.MULTILINE), \
            "Must switch to non-root user with USER instruction"

    def test_user_instruction_after_setup(self, dockerfile_lines):
        """Verify USER instruction comes after setup commands."""
        user_line_idx = None
        copy_line_idx = None
        
        for idx, line in enumerate(dockerfile_lines):
            if line.startswith('USER '):
                user_line_idx = idx
            if line.startswith('COPY '):
                copy_line_idx = idx
        
        assert user_line_idx is not None, "USER instruction must exist"
        assert copy_line_idx is not None, "COPY instruction must exist"
        assert user_line_idx > copy_line_idx, \
            "USER should come after file copies to ensure proper permissions"

    def test_secrets_not_hardcoded(self, dockerfile_content):
        """Verify no hardcoded secrets in Dockerfile."""
        # Check for common secret patterns
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'api[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
        ]
        
        for pattern in secret_patterns:
            assert not re.search(pattern, dockerfile_content, re.IGNORECASE), \
                f"Potential hardcoded secret found matching pattern: {pattern}"

    def test_tini_as_init_system(self, dockerfile_content):
        """Verify tini is used as init system for proper signal handling."""
        assert 'tini' in dockerfile_content, "Should use tini as init system"
        assert re.search(r'ENTRYPOINT.*tini', dockerfile_content), \
            "ENTRYPOINT should use tini for proper signal handling"


class TestPackageManagement:
    """Test package installation and management."""

    def test_apk_cache_cleaned(self, dockerfile_content):
        """Verify APK cache is cleaned to reduce image size."""
        if 'apk add' in dockerfile_content:
            assert 'rm -rf /var/cache/apk' in dockerfile_content or \
                   '--no-cache' in dockerfile_content, \
                "APK cache should be cleaned or --no-cache flag used"

    def test_build_deps_removed(self, dockerfile_content):
        """Verify build dependencies are removed after use."""
        if '.build-deps' in dockerfile_content:
            assert 'apk del .build-deps' in dockerfile_content, \
                "Build dependencies must be removed to reduce image size"

    def test_pip_timeout_configured(self, dockerfile_content):
        """Verify pip timeout is configured for reliability."""
        if 'pip' in dockerfile_content:
            assert '--timeout' in dockerfile_content or 'PIP_TIMEOUT' in dockerfile_content, \
                "Pip timeout should be configured for reliable builds"

    def test_temp_files_cleaned(self, dockerfile_content):
        """Verify temporary files are cleaned up."""
        if '/tmp/' in dockerfile_content:
            assert 'rm -rf /tmp/' in dockerfile_content, \
                "Temporary files should be cleaned up"


class TestEnvironmentVariables:
    """Test environment variable configuration."""

    def test_cn_version_defined(self, dockerfile_content):
        """Verify CN_VERSION environment variable is defined."""
        assert re.search(r'ENV\s+CN_VERSION', dockerfile_content), \
            "CN_VERSION must be defined"

    def test_cn_build_date_defined(self, dockerfile_content):
        """Verify CN_BUILD_DATE environment variable is defined."""
        assert re.search(r'ENV\s+CN_BUILD_DATE', dockerfile_content), \
            "CN_BUILD_DATE must be defined"

    def test_config_adapter_env_defined(self, dockerfile_content):
        """Verify config adapter environment variables are defined."""
        assert 'CN_CONFIG_ADAPTER' in dockerfile_content, \
            "CN_CONFIG_ADAPTER environment variable must be defined"

    def test_secret_adapter_env_defined(self, dockerfile_content):
        """Verify secret adapter environment variables are defined."""
        assert 'CN_SECRET_ADAPTER' in dockerfile_content, \
            "CN_SECRET_ADAPTER environment variable must be defined"

    def test_wait_timeouts_configured(self, dockerfile_content):
        """Verify wait timeout environment variables are configured."""
        assert 'CN_WAIT_MAX_TIME' in dockerfile_content, \
            "CN_WAIT_MAX_TIME must be configured"
        assert 'CN_WAIT_SLEEP_DURATION' in dockerfile_content, \
            "CN_WAIT_SLEEP_DURATION must be configured"

    def test_env_defaults_reasonable(self, dockerfile_content):
        """Verify environment variable defaults are reasonable."""
        # Check for common misconfigurations
        assert 'localhost' not in dockerfile_content.lower() or \
               'CN_CONFIG_CONSUL_HOST=localhost' in dockerfile_content, \
            "Localhost references should be clearly marked as defaults"


class TestLabels:
    """Test OCI image labels."""

    def test_label_instruction_present(self, dockerfile_content):
        """Verify LABEL instruction is present."""
        assert 'LABEL' in dockerfile_content, "LABEL instruction must be present"

    def test_required_oci_labels(self, dockerfile_content):
        """Verify required OCI labels are present."""
        required_labels = [
            'org.opencontainers.image.url',
            'org.opencontainers.image.authors',
            'org.opencontainers.image.vendor',
            'org.opencontainers.image.version',
            'org.opencontainers.image.title',
            'org.opencontainers.image.description',
        ]
        
        for label in required_labels:
            assert label in dockerfile_content, f"Required OCI label '{label}' must be present"

    def test_image_version_format(self, dockerfile_content):
        """Verify image version label follows semantic versioning."""
        match = re.search(r'org\.opencontainers\.image\.version="([^"]+)"', dockerfile_content)
        assert match is not None, "Image version label must be present"
        version = match.group(1)
        # Should match semantic versioning pattern (X.Y.Z or X.Y.Z-suffix)
        assert re.match(r'\d+\.\d+\.\d+(-\d+)?', version), \
            "Image version should follow semantic versioning"


class TestDirectoryStructure:
    """Test directory creation and permissions."""

    def test_required_directories_created(self, dockerfile_content):
        """Verify required directories are created."""
        required_dirs = [
            '/etc/certs',
            '/etc/jans/conf',
            '/app/db',
        ]
        
        for directory in required_dirs:
            assert directory in dockerfile_content, f"Required directory '{directory}' must be created"

    def test_permissions_set_correctly(self, dockerfile_content):
        """Verify file and directory permissions are set."""
        # Should have chmod or chown commands
        assert 'chmod' in dockerfile_content or 'chown' in dockerfile_content, \
            "Permissions should be explicitly set"

    def test_group_permissions_for_openshift(self, dockerfile_content):
        """Verify group permissions are set for OpenShift compatibility."""
        # OpenShift runs containers with random UIDs in root group
        assert 'chmod -R g=u' in dockerfile_content or 'chmod g+rwx' in dockerfile_content, \
            "Group permissions should be set for OpenShift compatibility"


class TestBuildOptimization:
    """Test build optimization and layer caching."""

    def test_layer_count_reasonable(self, dockerfile_lines):
        """Verify layer count is reasonable (not excessive)."""
        instruction_count = sum(
            1 for line in dockerfile_lines 
            if any(line.startswith(cmd) for cmd in ['RUN', 'COPY', 'ADD'])
        )
        assert instruction_count < 30, \
            f"Too many layers ({instruction_count}). Consider combining RUN commands"

    def test_run_commands_use_continuation(self, dockerfile_content):
        """Verify multi-line RUN commands use proper continuation."""
        # Multi-line RUN commands should use && and \
        multiline_runs = re.findall(r'RUN[^R]*?(?=\nRUN|\nFROM|\Z)', dockerfile_content, re.DOTALL)
        for run_cmd in multiline_runs:
            if '\n' in run_cmd and 'apk' in run_cmd:
                assert '&&' in run_cmd or '\\' in run_cmd, \
                    "Multi-line RUN commands should use && for proper error propagation"

    def test_copy_before_run_when_possible(self, dockerfile_lines):
        """Verify COPY instructions come before RUN when possible for better caching."""
        # Find requirements.txt COPY
        requirements_copy_idx = None
        pip_install_idx = None
        
        for idx, line in enumerate(dockerfile_lines):
            if 'COPY requirements.txt' in line:
                requirements_copy_idx = idx
            if 'pip' in line and 'install' in line and line.startswith('RUN'):
                pip_install_idx = idx
                break
        
        if requirements_copy_idx is not None and pip_install_idx is not None:
            assert requirements_copy_idx < pip_install_idx, \
                "COPY requirements.txt should come before pip install for better caching"


class TestEntrypoint:
    """Test ENTRYPOINT and CMD configuration."""

    def test_entrypoint_defined(self, dockerfile_content):
        """Verify ENTRYPOINT is defined."""
        assert 'ENTRYPOINT' in dockerfile_content, "ENTRYPOINT must be defined"

    def test_entrypoint_uses_exec_form(self, dockerfile_content):
        """Verify ENTRYPOINT uses exec form (JSON array)."""
        entrypoint_match = re.search(r'ENTRYPOINT\s+\[(.*?)\]', dockerfile_content, re.DOTALL)
        assert entrypoint_match is not None, \
            "ENTRYPOINT should use exec form (JSON array) for proper signal handling"

    def test_cmd_provides_default_args(self, dockerfile_content):
        """Verify CMD provides default arguments."""
        assert 'CMD' in dockerfile_content, "CMD should provide default arguments"

    def test_entrypoint_script_executable(self, dockerfile_content):
        """Verify entrypoint script is made executable."""
        if 'entrypoint.sh' in dockerfile_content:
            assert 'chmod +x' in dockerfile_content and 'entrypoint.sh' in dockerfile_content, \
                "Entrypoint script must be made executable"


class TestJavaConfiguration:
    """Test Java-specific configuration."""

    def test_java_home_or_symlink(self, dockerfile_content):
        """Verify Java is accessible via standard path."""
        # Should have symlink or JAVA_HOME
        assert '/opt/java' in dockerfile_content or 'JAVA_HOME' in dockerfile_content, \
            "Java should be accessible via standard path"

    def test_jre_not_jdk(self, dockerfile_lines):
        """Verify using JRE (not full JDK) for smaller image size."""
        from_line = next(
            (line for line in dockerfile_lines if line.startswith('FROM')),
            None
        )
        assert 'jre' in from_line.lower() or 'openjre' in from_line.lower(), \
            "Should use JRE (not full JDK) for smaller image size"

    def test_cacerts_permissions(self, dockerfile_content):
        """Verify cacerts file has correct permissions for updates."""
        if 'cacerts' in dockerfile_content:
            assert 'chmod' in dockerfile_content and '664' in dockerfile_content, \
                "cacerts should have 664 permissions to allow updates"


class TestDockerignore:
    """Test .dockerignore file."""

    def test_dockerignore_exists(self):
        """Verify .dockerignore file exists."""
        dockerignore_path = Path(__file__).parent.parent / '.dockerignore'
        assert dockerignore_path.exists(), ".dockerignore file should exist"

    def test_dockerignore_not_empty(self):
        """Verify .dockerignore is not empty."""
        dockerignore_path = Path(__file__).parent.parent / '.dockerignore'
        if dockerignore_path.exists():
            content = dockerignore_path.read_text()
            assert len(content.strip()) > 0, ".dockerignore should not be empty"


class TestGitCloneOptimization:
    """Test git clone optimization."""

    def test_git_sparse_checkout_used(self, dockerfile_content):
        """Verify git sparse-checkout is used to minimize clone size."""
        if 'git clone' in dockerfile_content:
            assert 'sparse-checkout' in dockerfile_content, \
                "Should use git sparse-checkout to minimize clone size"

    def test_git_clone_depth_limited(self, dockerfile_content):
        """Verify git clone depth is limited."""
        if 'git clone' in dockerfile_content:
            assert '--depth' in dockerfile_content or 'GIT_CLONE_DEPTH' in dockerfile_content, \
                "Should use shallow clone (--depth) to minimize clone size"

    def test_git_filter_blob_none(self, dockerfile_content):
        """Verify git clone uses blob filtering."""
        if 'git clone' in dockerfile_content:
            assert '--filter blob:none' in dockerfile_content, \
                "Should use --filter blob:none for blobless clone"