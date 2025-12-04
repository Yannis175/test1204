"""Tests for Dockerfile structure, best practices, and configuration."""
import re
import pytest


class TestDockerfileStructure:
    """Test Dockerfile structure and organization."""

    def test_dockerfile_has_maintainer_labels(self, dockerfile_content):
        """Verify Dockerfile has proper OCI labels."""
        required_labels = [
            "org.opencontainers.image.url",
            "org.opencontainers.image.authors",
            "org.opencontainers.image.vendor",
            "org.opencontainers.image.version",
            "org.opencontainers.image.title",
            "org.opencontainers.image.description",
        ]
        
        for label in required_labels:
            assert label in dockerfile_content, \
                f"Dockerfile should contain label: {label}"

    def test_dockerfile_has_license(self, dockerfile_content):
        """Verify LICENSE file is copied into image."""
        assert "COPY LICENSE /licenses/LICENSE" in dockerfile_content, \
            "Should copy LICENSE file to /licenses/"

    def test_uses_tini_as_init_system(self, dockerfile_content):
        """Verify tini is used as init system."""
        assert 'apk add --no-cache' in dockerfile_content, \
            "Should install packages using apk"
        assert 'tini' in dockerfile_content, \
            "Should install tini init system"
        assert 'ENTRYPOINT ["tini"' in dockerfile_content, \
            "Should use tini in ENTRYPOINT"

    def test_runs_as_non_root_user(self, dockerfile_content):
        """Verify container runs as non-root user."""
        assert "adduser" in dockerfile_content, \
            "Should create a non-root user"
        assert "USER 1000" in dockerfile_content, \
            "Should switch to non-root user (UID 1000)"

    def test_entrypoint_and_cmd_defined(self, dockerfile_content):
        """Verify ENTRYPOINT and CMD are properly defined."""
        assert "ENTRYPOINT" in dockerfile_content, \
            "Should have ENTRYPOINT instruction"
        assert "CMD" in dockerfile_content, \
            "Should have CMD instruction"

    def test_environment_variables_documented(self, dockerfile_content):
        """Verify environment variables are set."""
        env_vars = [
            "CN_CONFIG_ADAPTER",
            "CN_SECRET_ADAPTER",
            "CN_VERSION",
            "CN_BUILD_DATE",
            "CN_WAIT_MAX_TIME",
        ]
        
        for var in env_vars:
            assert f"{var}=" in dockerfile_content, \
                f"Should define environment variable: {var}"

    def test_workdir_or_directory_creation(self, dockerfile_content):
        """Verify necessary directories are created."""
        required_dirs = [
            "/etc/certs",
            "/etc/jans/conf",
            "/app/db",
        ]
        
        for directory in required_dirs:
            assert directory in dockerfile_content, \
                f"Should create or reference directory: {directory}"

    def test_cleanup_after_build(self, dockerfile_content):
        """Verify cleanup commands remove build dependencies."""
        assert "apk del .build-deps" in dockerfile_content, \
            "Should remove build dependencies"
        assert "rm -rf /var/cache/apk/*" in dockerfile_content, \
            "Should clean apk cache"


class TestDockerfileBestPractices:
    """Test adherence to Docker best practices."""

    def test_uses_alpine_for_small_size(self, dockerfile_lines):
        """Verify Alpine Linux is used for minimal image size."""
        from_line = dockerfile_lines[0]
        assert "alpine" in from_line.lower(), \
            "Should use Alpine for smaller image size"

    def test_combines_run_commands(self, dockerfile_content):
        """Verify RUN commands are combined to reduce layers."""
        # Check that apk commands are combined with && and \
        apk_pattern = r'RUN apk update\s+&&\s+apk upgrade'
        assert re.search(apk_pattern, dockerfile_content, re.MULTILINE), \
            "Should combine apk update and upgrade"

    def test_no_cache_for_apk(self, dockerfile_content):
        """Verify apk uses --no-cache flag."""
        apk_adds = re.findall(r'apk add[^\n]*', dockerfile_content)
        for apk_add in apk_adds:
            if "apk add" in apk_add:
                assert "--no-cache" in apk_add, \
                    "apk add should use --no-cache flag"

    def test_uses_specific_package_versions_where_important(self, dockerfile_content):
        """Verify critical components specify versions."""
        assert "CN_VERSION=" in dockerfile_content, \
            "Should specify CN_VERSION"
        assert "JANS_SOURCE_VERSION=" in dockerfile_content, \
            "Should specify JANS_SOURCE_VERSION"

    def test_virtual_build_deps_pattern(self, dockerfile_content):
        """Verify virtual build dependencies are used and cleaned up."""
        assert "--virtual .build-deps" in dockerfile_content, \
            "Should use virtual build dependencies"
        assert "apk del .build-deps" in dockerfile_content, \
            "Should remove virtual build dependencies"

    def test_pip_no_cache_dir(self, dockerfile_content):
        """Verify pip uses --no-cache-dir flag."""
        pip_installs = re.findall(r'pip3? install[^\n]*', dockerfile_content)
        for pip_install in pip_installs:
            assert "--no-cache-dir" in pip_install, \
                "pip install should use --no-cache-dir"


class TestAlpinePackages:
    """Test Alpine package installation."""

    def test_required_alpine_packages(self, dockerfile_content):
        """Verify required Alpine packages are installed."""
        required_packages = [
            "openssl",
            "python3",
            "curl",
            "tini",
        ]
        
        for package in required_packages:
            assert package in dockerfile_content, \
                f"Should install package: {package}"

    def test_python_cryptography_packages(self, dockerfile_content):
        """Verify Python cryptography packages are installed."""
        crypto_packages = [
            "py3-cryptography",
            "py3-psycopg2",
            "py3-grpcio",
        ]
        
        for package in crypto_packages:
            assert package in dockerfile_content, \
                f"Should install package: {package}"

    def test_build_tools_installed_temporarily(self, dockerfile_content):
        """Verify build tools are installed and removed."""
        assert "wget" in dockerfile_content or "git" in dockerfile_content, \
            "Should install wget or git for downloads"
        assert "apk del .build-deps" in dockerfile_content, \
            "Should remove build tools after use"


class TestJavaConfiguration:
    """Test Java-specific configuration."""

    def test_jans_auth_client_jar_downloaded(self, dockerfile_content):
        """Verify jans-auth-client JAR is downloaded."""
        assert "jans-auth-client" in dockerfile_content, \
            "Should download jans-auth-client JAR"
        assert "CN_SOURCE_URL" in dockerfile_content, \
            "Should define CN_SOURCE_URL for JAR download"
        assert "/opt/jans/configurator/javalibs" in dockerfile_content, \
            "Should download JAR to javalibs directory"

    def test_jar_download_uses_wget(self, dockerfile_content):
        """Verify JAR download uses wget with quiet flag."""
        assert "wget -q ${CN_SOURCE_URL}" in dockerfile_content, \
            "Should use wget -q to download JAR"


class TestPythonConfiguration:
    """Test Python environment configuration."""

    def test_python_externally_managed_disabled(self, dockerfile_content):
        """Verify EXTERNALLY-MANAGED file is disabled."""
        assert "EXTERNALLY-MANAGED" in dockerfile_content, \
            "Should handle EXTERNALLY-MANAGED file"
        assert ".disabled" in dockerfile_content, \
            "Should rename EXTERNALLY-MANAGED to disable it"

    def test_pip_upgraded(self, dockerfile_content):
        """Verify pip, wheel, and setuptools are upgraded."""
        assert "pip3 install --no-cache-dir -U pip wheel setuptools" in dockerfile_content, \
            "Should upgrade pip, wheel, and setuptools"

    def test_requirements_installed(self, dockerfile_content):
        """Verify requirements.txt is copied and installed."""
        assert "COPY requirements.txt /app/requirements.txt" in dockerfile_content, \
            "Should copy requirements.txt"
        assert "pip3 install --no-cache-dir -r /app/requirements.txt" in dockerfile_content, \
            "Should install requirements"

    def test_pip_uninstalled_after_use(self, dockerfile_content):
        """Verify pip and wheel are uninstalled after requirements installation."""
        assert "pip3 uninstall -y pip wheel" in dockerfile_content, \
            "Should uninstall pip and wheel after use to reduce image size"

    def test_pip_timeout_configurable(self, dockerfile_content):
        """Verify pip timeout is configurable via ARG."""
        assert "ARG PIP_TIMEOUT" in dockerfile_content, \
            "Should define PIP_TIMEOUT as build arg"
        assert "--timeout ${PIP_TIMEOUT}" in dockerfile_content or \
               "--timeout=$PIP_TIMEOUT" in dockerfile_content, \
            "Should use PIP_TIMEOUT in pip install commands"


class TestGitConfiguration:
    """Test Git sparse checkout configuration."""

    def test_git_sparse_checkout_for_pycloudlib(self, dockerfile_content):
        """Verify git sparse-checkout is used for jans-pycloudlib."""
        assert "git clone --depth" in dockerfile_content, \
            "Should use shallow clone for efficiency"
        assert "git sparse-checkout" in dockerfile_content, \
            "Should use sparse-checkout"
        assert "jans-pycloudlib" in dockerfile_content, \
            "Should checkout jans-pycloudlib"

    def test_git_repo_cleaned_up(self, dockerfile_content):
        """Verify git repository is cleaned up after use."""
        assert "rm -rf" in dockerfile_content and "/tmp/jans" in dockerfile_content, \
            "Should clean up git repository after use"

    def test_jans_source_version_pinned(self, dockerfile_content):
        """Verify JANS_SOURCE_VERSION is pinned to specific commit."""
        assert "JANS_SOURCE_VERSION=" in dockerfile_content, \
            "Should define JANS_SOURCE_VERSION"
        
        # Extract the version and verify it's a commit hash
        version_match = re.search(r'JANS_SOURCE_VERSION=([a-f0-9]{40})', dockerfile_content)
        assert version_match is not None, \
            "JANS_SOURCE_VERSION should be a 40-character commit hash"


class TestSecurityConfiguration:
    """Test security-related configurations."""

    def test_file_permissions_set(self, dockerfile_content):
        """Verify proper file permissions are set."""
        assert "chmod -R g=u" in dockerfile_content, \
            "Should set group permissions equal to user"
        assert "chmod 664" in dockerfile_content, \
            "Should set specific permissions for cacerts"

    def test_entrypoint_script_executable(self, dockerfile_content):
        """Verify entrypoint script is made executable."""
        assert "chmod +x /app/scripts/entrypoint.sh" in dockerfile_content, \
            "Should make entrypoint script executable"

    def test_user_added_to_root_group(self, dockerfile_content):
        """Verify non-root user is added to root group for OpenShift compatibility."""
        assert "adduser" in dockerfile_content and "-G root" in dockerfile_content, \
            "Should add user to root group for OpenShift"

    def test_home_directory_created(self, dockerfile_content):
        """Verify home directory is created for non-root user."""
        assert "-h /home/1000" in dockerfile_content or \
               "mkdir -p $HOME" in dockerfile_content, \
            "Should create home directory for user"


class TestEnvironmentVariableGroups:
    """Test environment variable configuration groups."""

    def test_config_adapter_env_vars(self, dockerfile_content):
        """Verify config adapter environment variables are defined."""
        config_vars = [
            "CN_CONFIG_ADAPTER=consul",
            "CN_CONFIG_CONSUL_HOST",
            "CN_CONFIG_KUBERNETES_NAMESPACE",
        ]
        
        for var in config_vars:
            assert var in dockerfile_content, \
                f"Should define config variable: {var}"

    def test_secret_adapter_env_vars(self, dockerfile_content):
        """Verify secret adapter environment variables are defined."""
        secret_vars = [
            "CN_SECRET_ADAPTER=vault",
            "CN_SECRET_VAULT_ADDR",
            "CN_SECRET_KUBERNETES_SECRET",
        ]
        
        for var in secret_vars:
            assert var in dockerfile_content, \
                f"Should define secret variable: {var}"

    def test_generic_env_vars(self, dockerfile_content):
        """Verify generic environment variables are defined."""
        generic_vars = [
            "CN_WAIT_MAX_TIME",
            "CN_WAIT_SLEEP_DURATION",
            "CN_CONFIGURATOR_DB_DIR",
            "CN_CONFIGURATOR_CERTS_DIR",
        ]
        
        for var in generic_vars:
            assert var in dockerfile_content, \
                f"Should define generic variable: {var}"


class TestScriptsConfiguration:
    """Test scripts directory configuration."""

    def test_scripts_copied(self, dockerfile_content):
        """Verify scripts directory is copied."""
        assert "COPY scripts /app/scripts" in dockerfile_content, \
            "Should copy scripts directory"

    def test_entrypoint_uses_scripts(self, dockerfile_content):
        """Verify entrypoint uses script from scripts directory."""
        assert "/app/scripts/entrypoint.sh" in dockerfile_content, \
            "Should use entrypoint.sh from scripts directory"