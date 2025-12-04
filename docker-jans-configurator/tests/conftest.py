"""Pytest configuration for docker-jans-configurator tests."""
import os
import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def dockerfile_path():
    """Return the path to the Dockerfile."""
    return Path(__file__).parent.parent / "Dockerfile"


@pytest.fixture(scope="session")
def dockerfile_content(dockerfile_path):
    """Return the content of the Dockerfile."""
    with open(dockerfile_path, "r") as f:
        return f.read()


@pytest.fixture(scope="session")
def dockerfile_lines(dockerfile_content):
    """Return Dockerfile content as a list of lines."""
    return dockerfile_content.splitlines()


@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture
def requirements_path():
    """Return the path to requirements.txt."""
    return Path(__file__).parent.parent / "requirements.txt"


@pytest.fixture
def requirements_content(requirements_path):
    """Return the content of requirements.txt."""
    with open(requirements_path, "r") as f:
        return f.read()