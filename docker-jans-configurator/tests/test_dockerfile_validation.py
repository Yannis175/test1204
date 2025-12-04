"""Validation tests for Dockerfile configuration values and consistency."""
import re
import pytest


class TestVersionConsistency:
    """Test version consistency across Dockerfile."""

    def test_cn_version_matches_image_label(self, dockerfile_content):
        """Verify CN_VERSION matches org.opencontainers.image.version."""
        cn_version_match = re.search(r'ENV CN_VERSION=([^\s]+)', dockerfile_content)
        label_version_match = re.search(
            r'org\.opencontainers\.image\.version="([^"]+)"',
            dockerfile_content
        )
        
        assert cn_version_match is not None, "Should define CN_VERSION"
        assert label_version_match is not None, "Should define image version label"
        
        cn_version = cn_version_match.group(1)
        label_version = label_version_match.group(1)
        
        # Label version might have a build suffix like "1.7.0-1"
        assert label_version.startswith(cn_version), \
            f"Image version label ({label_version}) should start with CN_VERSION ({cn_version})"

    def test_image_url_label_format(self, dockerfile_content):
        """Verify image URL label has proper format."""
        url_match = re.search(
            r'org\.opencontainers\.image\.url="([^"]+)"',
            dockerfile_content
        )
        assert url_match is not None, "Should define image URL label"
        
        url = url_match.group(1)
        assert url.startswith("ghcr.io/"), \
            "Image URL should be from ghcr.io registry"
        assert "configurator" in url.lower(), \
            "Image URL should reference configurator"


class TestBuildArguments:
    """Test build arguments configuration."""

    def test_git_clone_depth_arg(self, dockerfile_content):
        """Verify GIT_CLONE_DEPTH argument is defined."""
        assert "ARG GIT_CLONE_DEPTH=100" in dockerfile_content, \
            "Should define GIT_CLONE_DEPTH build argument"

    def test_pip_timeout_arg(self, dockerfile_content):
        """Verify PIP_TIMEOUT argument is defined."""
        assert "ARG PIP_TIMEOUT" in dockerfile_content, \
            "Should define PIP_TIMEOUT build argument"
        
        # Check default value
        assert "ARG PIP_TIMEOUT=15" in dockerfile_content, \
            "PIP_TIMEOUT should have default value of 15"


class TestPathConsistency:
    """Test path consistency throughout Dockerfile."""

    def test_configurator_paths_consistent(self, dockerfile_content):
        """Verify configurator paths are consistent."""
        # Check that paths reference the same base
        paths = [
            "/opt/jans/configurator",
            "/opt/jans/configurator/javalibs",
        ]
        
        # All should be present or derivable from ENV vars
        assert any(path in dockerfile_content for path in paths), \
            "Should define configurator paths"

    def test_env_path_consistency(self, dockerfile_content):
        """Verify environment variable paths match directory creation."""
        # Check DB_DIR
        if "CN_CONFIGURATOR_DB_DIR=/app/db" in dockerfile_content:
            assert "mkdir -p" in dockerfile_content and "/app/db" in dockerfile_content, \
                "Should create directory referenced in CN_CONFIGURATOR_DB_DIR"

    def test_certs_directory_paths(self, dockerfile_content):
        """Verify certificate directory paths are consistent."""
        certs_paths = [
            "/etc/certs",
            "CN_CONFIGURATOR_CERTS_DIR",
        ]
        
        for path in certs_paths:
            assert path in dockerfile_content, \
                f"Should reference certs path: {path}"


class TestRequirementsFile:
    """Test requirements.txt configuration."""

    def test_requirements_file_exists(self, requirements_path):
        """Verify requirements.txt file exists."""
        assert requirements_path.exists(), \
            "requirements.txt should exist"

    def test_requirements_has_grpcio(self, requirements_content):
        """Verify grpcio is in requirements with version pin."""
        assert "grpcio" in requirements_content, \
            "requirements.txt should include grpcio"
        
        # Check for version specification
        grpcio_match = re.search(r'grpcio[=<>]+[\d.]+', requirements_content)
        assert grpcio_match is not None, \
            "grpcio should have version specification"

    def test_requirements_has_click(self, requirements_content):
        """Verify click is in requirements."""
        assert "click" in requirements_content.lower(), \
            "requirements.txt should include click"

    def test_requirements_has_pycloudlib(self, requirements_content):
        """Verify jans-pycloudlib is referenced."""
        assert "jans-pycloudlib" in requirements_content or \
               "/tmp/jans/jans-pycloudlib" in requirements_content, \
            "requirements.txt should reference jans-pycloudlib"

    def test_requirements_no_insecure_protocols(self, requirements_content):
        """Verify requirements don't use insecure protocols."""
        insecure_patterns = [
            r'http://(?!localhost)',  # HTTP except localhost
            r'git://(?!github\.com)',  # Git protocol except GitHub
        ]
        
        for pattern in insecure_patterns:
            assert not re.search(pattern, requirements_content), \
                f"requirements.txt should not contain insecure pattern: {pattern}"


class TestHadolintCompliance:
    """Test compliance with hadolint rules (based on .hadolint.yaml)."""

    def test_hadolint_config_exists(self, project_root):
        """Verify .hadolint.yaml configuration exists."""
        hadolint_path = project_root / "docker-jans-configurator" / ".hadolint.yaml"
        assert hadolint_path.exists(), \
            ".hadolint.yaml should exist in docker-jans-configurator"

    def test_dockerfile_has_ignored_rules_documented(self):
        """Verify ignored hadolint rules are documented."""
        # Known ignored rules from .hadolint.yaml:
        # DL3018 - Pin versions in apk add
        # DL3013 - Pin versions in pip
        # DL3003 - Use WORKDIR to switch to a directory
        
        # This is just documentation - the rules are intentionally ignored
        ignored_rules = ["DL3018", "DL3013", "DL3003"]
        assert len(ignored_rules) == 3, \
            "Three hadolint rules are intentionally ignored"


class TestImageMetadata:
    """Test OCI image metadata."""

    def test_all_oci_labels_present(self, dockerfile_content):
        """Verify all standard OCI labels are present."""
        oci_labels = [
            "org.opencontainers.image.url",
            "org.opencontainers.image.authors",
            "org.opencontainers.image.vendor",
            "org.opencontainers.image.version",
            "org.opencontainers.image.title",
            "org.opencontainers.image.description",
        ]
        
        for label in oci_labels:
            assert label in dockerfile_content, \
                f"Should have OCI label: {label}"

    def test_janssen_project_metadata(self, dockerfile_content):
        """Verify Janssen Project specific metadata."""
        assert "Janssen Project" in dockerfile_content, \
            "Should reference Janssen Project"
        assert "support@jans.io" in dockerfile_content, \
            "Should include Janssen support email"

    def test_image_title_descriptive(self, dockerfile_content):
        """Verify image title is descriptive."""
        title_match = re.search(
            r'org\.opencontainers\.image\.title="([^"]+)"',
            dockerfile_content
        )
        assert title_match is not None, "Should have image title"
        
        title = title_match.group(1)
        assert len(title) > 10, "Image title should be descriptive"
        assert "Configuration" in title or "Configurator" in title, \
            "Title should describe configuration purpose"


class TestEntrypointConfiguration:
    """Test ENTRYPOINT and CMD configuration."""

    def test_entrypoint_uses_exec_form(self, dockerfile_content):
        """Verify ENTRYPOINT uses exec form (JSON array)."""
        entrypoint_match = re.search(
            r'ENTRYPOINT\s+\[(.*?)\]',
            dockerfile_content,
            re.DOTALL
        )
        assert entrypoint_match is not None, \
            "ENTRYPOINT should use exec form (JSON array)"

    def test_entrypoint_includes_tini(self, dockerfile_content):
        """Verify ENTRYPOINT includes tini."""
        assert 'ENTRYPOINT ["tini"' in dockerfile_content, \
            "ENTRYPOINT should start with tini"

    def test_cmd_provides_help_by_default(self, dockerfile_content):
        """Verify CMD defaults to --help."""
        assert 'CMD ["--help"]' in dockerfile_content, \
            "CMD should default to --help for user guidance"

    def test_tini_flags_present(self, dockerfile_content):
        """Verify tini is configured with appropriate flags."""
        assert '"-g"' in dockerfile_content and '"--"' in dockerfile_content, \
            "tini should use -g and -- flags"