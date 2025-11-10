"""
Pytest fixtures and configuration for git_repo_control tests.

Provides common fixtures for:
- Sample config.yaml structures
- Mock git repository objects
- Temporary directories for file operations
- Mock API response objects
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any
from unittest.mock import MagicMock, AsyncMock

import pytest


@pytest.fixture
def sample_config() -> Dict[str, Any]:
    """Provide a sample valid configuration structure."""
    return {
        "repositories": [
            {
                "name": "test-repo-1",
                "local_path": "/tmp/repos/test-repo-1",
                "remote_url": "https://github.com/user/test-repo-1.git",
            },
            {
                "name": "test-repo-2",
                "local_path": "/tmp/repos/test-repo-2",
                "remote_url": "git@github.com:user/test-repo-2.git",
            },
        ],
        "settings": {
            "auto_fetch": True,
            "parallel_limit": 10,
            "clone_on_missing": True,
        },
        "ai": {
            "enabled": True,
            "api_type": "openai",
            "api_key": "sk-test-key-12345",
            "base_url": None,
            "model": "gpt-4o-mini",
            "max_tokens": 500,
            "temperature": 0.7,
        },
    }


@pytest.fixture
def minimal_config() -> Dict[str, Any]:
    """Provide a minimal valid configuration (only repositories)."""
    return {
        "repositories": [
            {
                "name": "minimal-repo",
                "local_path": "/tmp/repos/minimal",
                "remote_url": "https://github.com/user/minimal.git",
            }
        ]
    }


@pytest.fixture
def invalid_config_missing_fields() -> Dict[str, Any]:
    """Provide an invalid configuration missing required fields."""
    return {
        "repositories": [
            {
                "name": "incomplete-repo",
                "local_path": "/tmp/repos/incomplete",
                # Missing remote_url
            }
        ]
    }


@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for test operations."""
    test_dir = tmp_path / "git_repo_control_test"
    test_dir.mkdir(exist_ok=True)
    return test_dir


@pytest.fixture
def temp_config_file(temp_dir, sample_config):
    """Create a temporary config.yaml file."""
    import yaml

    config_path = temp_dir / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(sample_config, f)
    return config_path


@pytest.fixture
def mock_git_repo():
    """Provide a mock GitPython Repo object."""
    mock_repo = MagicMock()

    # Mock common repo properties
    mock_repo.working_dir = "/tmp/repos/test-repo"
    mock_repo.bare = False
    mock_repo.is_dirty.return_value = False

    # Mock remotes
    mock_remote = MagicMock()
    mock_remote.name = "origin"
    mock_remote.url = "https://github.com/user/test-repo.git"
    mock_repo.remotes = [mock_remote]

    # Mock branches
    mock_main_branch = MagicMock()
    mock_main_branch.name = "main"
    mock_repo.active_branch = mock_main_branch
    mock_repo.heads = [mock_main_branch]

    # Mock refs
    mock_repo.refs = []

    return mock_repo


@pytest.fixture
def mock_git_commit():
    """Provide a mock GitPython Commit object."""
    mock_commit = MagicMock()
    mock_commit.hexsha = "abc1234567890def"
    mock_commit.message = "Test commit message"
    mock_commit.author.name = "Test Author"
    mock_commit.author.email = "test@example.com"
    mock_commit.committed_date = 1699564800  # 2023-11-10
    return mock_commit


@pytest.fixture
def mock_openai_response():
    """Provide a mock OpenAI API response."""
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "feat: add new feature for testing"
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    return mock_response


@pytest.fixture
def mock_openai_client():
    """Provide a mock OpenAI client with async support."""
    mock_client = MagicMock()
    mock_client.chat = MagicMock()
    mock_client.chat.completions = MagicMock()

    # Create async mock for create method
    async_mock = AsyncMock()
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "feat: add new feature"
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    async_mock.return_value = mock_response

    mock_client.chat.completions.create = async_mock
    return mock_client


@pytest.fixture
def sample_commit_data():
    """Provide sample commit data for testing."""
    return [
        {
            "hash": "abc1234",
            "author": "John Doe",
            "date": "2025-11-10",
            "message": "Add authentication module",
        },
        {
            "hash": "def5678",
            "author": "Jane Smith",
            "date": "2025-11-09",
            "message": "Fix bug in session handling",
        },
    ]


@pytest.fixture
def sample_result_yaml_structure():
    """Provide sample result.yaml structure for testing."""
    return {
        "metadata": {
            "analysis_timestamp": "2025-11-10T14:30:00Z",
            "total_repositories": 2,
            "successful": 2,
            "failed": 0,
        },
        "repositories": [
            {
                "name": "test-repo-1",
                "status": "success",
                "local_path": "/tmp/repos/test-repo-1",
                "current_branch": "main",
                "dirty_working_tree": False,
                "branches": [
                    {
                        "name": "main",
                        "tracking": "origin/main",
                        "ahead": 2,
                        "behind": 0,
                        "unpushed_commits": [],
                    }
                ],
            }
        ],
    }


@pytest.fixture
def env_with_api_key(monkeypatch):
    """Set up environment with OpenAI API key."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-12345")


@pytest.fixture
def env_without_api_key(monkeypatch):
    """Set up environment without OpenAI API key."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


# Async test helper fixtures
@pytest.fixture
def event_loop():
    """Provide event loop for async tests."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
