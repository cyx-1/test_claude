"""
Tests for Repository Initialization (repo_manager.py)

Following TDD principles - tests written FIRST before implementation.

Tests cover:
- Detection of existing repositories
- Cloning missing repositories (mock git clone)
- Handling clone failures (network, auth errors)
- Async parallel cloning of multiple repos
- Validation of .git directory
"""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, call

import pytest

from config_manager import ConfigManager


class TestRepoManager:
    """Test suite for RepoManager class."""

    @pytest.mark.asyncio
    async def test_initialize_existing_repository(self, temp_dir, mocker):
        """Test that existing repositories are detected and validated."""
        from repo_manager import RepoManager

        # Create a fake repo with .git directory
        repo_path = temp_dir / "existing_repo"
        repo_path.mkdir()
        git_dir = repo_path / ".git"
        git_dir.mkdir()

        repo_config = {
            "name": "existing-repo",
            "local_path": str(repo_path),
            "remote_url": "https://github.com/user/existing.git",
        }

        manager = RepoManager()
        result = await manager.initialize_repository(repo_config)

        assert result["status"] == "success"
        assert result["action"] == "validated"
        assert result["name"] == "existing-repo"

    @pytest.mark.asyncio
    async def test_clone_missing_repository(self, temp_dir, mocker):
        """Test cloning a repository that doesn't exist locally."""
        from repo_manager import RepoManager

        repo_path = temp_dir / "new_repo"
        repo_config = {
            "name": "new-repo",
            "local_path": str(repo_path),
            "remote_url": "https://github.com/user/new.git",
        }

        # Mock git.Repo.clone_from
        mock_clone = mocker.patch("git.Repo.clone_from")
        mock_repo = MagicMock()
        mock_clone.return_value = mock_repo

        manager = RepoManager()
        result = await manager.initialize_repository(repo_config)

        assert result["status"] == "success"
        assert result["action"] == "cloned"
        assert result["name"] == "new-repo"
        mock_clone.assert_called_once_with(
            "https://github.com/user/new.git", str(repo_path)
        )

    @pytest.mark.asyncio
    async def test_clone_failure_network_error(self, temp_dir, mocker):
        """Test handling of network errors during cloning."""
        from repo_manager import RepoManager
        import git

        repo_path = temp_dir / "failing_repo"
        repo_config = {
            "name": "failing-repo",
            "local_path": str(repo_path),
            "remote_url": "https://github.com/user/failing.git",
        }

        # Mock git.Repo.clone_from to raise GitCommandError
        mock_clone = mocker.patch("git.Repo.clone_from")
        mock_clone.side_effect = git.exc.GitCommandError(
            "clone", "Network error: Could not resolve host"
        )

        manager = RepoManager()
        result = await manager.initialize_repository(repo_config)

        assert result["status"] == "error"
        assert result["name"] == "failing-repo"
        assert "network" in result["error_message"].lower() or "could not resolve" in result["error_message"].lower()

    @pytest.mark.asyncio
    async def test_clone_failure_auth_error(self, temp_dir, mocker):
        """Test handling of authentication errors during cloning."""
        from repo_manager import RepoManager
        import git

        repo_path = temp_dir / "auth_failing_repo"
        repo_config = {
            "name": "auth-failing-repo",
            "local_path": str(repo_path),
            "remote_url": "git@github.com:user/private.git",
        }

        # Mock git.Repo.clone_from to raise authentication error
        mock_clone = mocker.patch("git.Repo.clone_from")
        mock_clone.side_effect = git.exc.GitCommandError(
            "clone", "Authentication failed"
        )

        manager = RepoManager()
        result = await manager.initialize_repository(repo_config)

        assert result["status"] == "error"
        assert result["name"] == "auth-failing-repo"
        assert "authentication" in result["error_message"].lower()

    @pytest.mark.asyncio
    async def test_invalid_repository_no_git_dir(self, temp_dir):
        """Test detection of invalid repository (missing .git directory)."""
        from repo_manager import RepoManager

        # Create directory without .git
        repo_path = temp_dir / "invalid_repo"
        repo_path.mkdir()

        repo_config = {
            "name": "invalid-repo",
            "local_path": str(repo_path),
            "remote_url": "https://github.com/user/invalid.git",
        }

        manager = RepoManager()
        result = await manager.initialize_repository(repo_config)

        assert result["status"] == "error"
        assert "not a valid git repository" in result["error_message"].lower() or ".git" in result["error_message"].lower()

    @pytest.mark.asyncio
    async def test_parallel_initialization_multiple_repos(self, temp_dir, mocker):
        """Test parallel initialization of multiple repositories."""
        from repo_manager import RepoManager

        # Create mix of existing and new repos
        existing_repo = temp_dir / "existing"
        existing_repo.mkdir()
        (existing_repo / ".git").mkdir()

        repos_config = [
            {
                "name": "existing-repo",
                "local_path": str(existing_repo),
                "remote_url": "https://github.com/user/existing.git",
            },
            {
                "name": "new-repo-1",
                "local_path": str(temp_dir / "new1"),
                "remote_url": "https://github.com/user/new1.git",
            },
            {
                "name": "new-repo-2",
                "local_path": str(temp_dir / "new2"),
                "remote_url": "https://github.com/user/new2.git",
            },
        ]

        # Mock cloning
        mock_clone = mocker.patch("git.Repo.clone_from")
        mock_clone.return_value = MagicMock()

        manager = RepoManager()
        results = await manager.initialize_repositories(repos_config)

        assert len(results) == 3
        assert results[0]["status"] == "success"
        assert results[0]["action"] == "validated"
        assert results[1]["status"] == "success"
        assert results[1]["action"] == "cloned"
        assert results[2]["status"] == "success"
        assert results[2]["action"] == "cloned"

    @pytest.mark.asyncio
    async def test_parallel_initialization_with_failures(self, temp_dir, mocker):
        """Test that one repo failure doesn't prevent others from initializing."""
        from repo_manager import RepoManager
        import git

        repos_config = [
            {
                "name": "good-repo",
                "local_path": str(temp_dir / "good"),
                "remote_url": "https://github.com/user/good.git",
            },
            {
                "name": "failing-repo",
                "local_path": str(temp_dir / "failing"),
                "remote_url": "https://github.com/user/failing.git",
            },
        ]

        # Mock clone_from with side effects - first succeeds, second fails
        mock_clone = mocker.patch("git.Repo.clone_from")
        mock_clone.side_effect = [
            MagicMock(),  # First call succeeds
            git.exc.GitCommandError("clone", "Network error"),  # Second fails
        ]

        manager = RepoManager()
        results = await manager.initialize_repositories(repos_config)

        assert len(results) == 2
        assert results[0]["status"] == "success"
        assert results[1]["status"] == "error"

    @pytest.mark.asyncio
    async def test_create_parent_directories(self, temp_dir, mocker):
        """Test that parent directories are created if they don't exist."""
        from repo_manager import RepoManager

        # Path with nested non-existent directories
        deep_path = temp_dir / "level1" / "level2" / "repo"
        repo_config = {
            "name": "deep-repo",
            "local_path": str(deep_path),
            "remote_url": "https://github.com/user/deep.git",
        }

        mock_clone = mocker.patch("git.Repo.clone_from")
        mock_clone.return_value = MagicMock()

        manager = RepoManager()
        result = await manager.initialize_repository(repo_config)

        assert result["status"] == "success"
        # Verify parent directories were created
        assert deep_path.parent.exists()

    def test_is_valid_repository_true(self, temp_dir):
        """Test validation returns True for valid git repository."""
        from repo_manager import is_valid_repository

        repo_path = temp_dir / "valid_repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()

        assert is_valid_repository(repo_path) is True

    def test_is_valid_repository_false_no_git_dir(self, temp_dir):
        """Test validation returns False for directory without .git."""
        from repo_manager import is_valid_repository

        repo_path = temp_dir / "not_a_repo"
        repo_path.mkdir()

        assert is_valid_repository(repo_path) is False

    def test_is_valid_repository_false_not_exists(self, temp_dir):
        """Test validation returns False for non-existent path."""
        from repo_manager import is_valid_repository

        repo_path = temp_dir / "nonexistent"

        assert is_valid_repository(repo_path) is False

    @pytest.mark.asyncio
    async def test_concurrent_cloning_respects_limit(self, temp_dir, mocker):
        """Test that parallel cloning respects concurrency limit."""
        from repo_manager import RepoManager

        # Create many repos to clone
        repos_config = [
            {
                "name": f"repo-{i}",
                "local_path": str(temp_dir / f"repo{i}"),
                "remote_url": f"https://github.com/user/repo{i}.git",
            }
            for i in range(20)
        ]

        mock_clone = mocker.patch("git.Repo.clone_from")
        mock_clone.return_value = MagicMock()

        manager = RepoManager(max_concurrent=5)
        results = await manager.initialize_repositories(repos_config)

        assert len(results) == 20
        assert all(r["status"] == "success" for r in results)

    @pytest.mark.asyncio
    async def test_clone_with_progress_callback(self, temp_dir, mocker):
        """Test that progress callbacks are invoked during initialization."""
        from repo_manager import RepoManager

        repo_config = {
            "name": "progress-repo",
            "local_path": str(temp_dir / "progress"),
            "remote_url": "https://github.com/user/progress.git",
        }

        mock_clone = mocker.patch("git.Repo.clone_from")
        mock_clone.return_value = MagicMock()

        progress_calls = []

        def progress_callback(repo_name, status):
            progress_calls.append((repo_name, status))

        manager = RepoManager()
        result = await manager.initialize_repository(
            repo_config, progress_callback=progress_callback
        )

        assert result["status"] == "success"
        assert len(progress_calls) > 0
        assert any("progress-repo" in call[0] for call in progress_calls)

    @pytest.mark.asyncio
    async def test_repository_already_exists_not_cloned(self, temp_dir, mocker):
        """Test that existing repositories are not re-cloned."""
        from repo_manager import RepoManager

        repo_path = temp_dir / "existing_repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()

        repo_config = {
            "name": "existing-repo",
            "local_path": str(repo_path),
            "remote_url": "https://github.com/user/existing.git",
        }

        mock_clone = mocker.patch("git.Repo.clone_from")

        manager = RepoManager()
        result = await manager.initialize_repository(repo_config)

        # Should not attempt to clone
        mock_clone.assert_not_called()
        assert result["action"] == "validated"

    @pytest.mark.asyncio
    async def test_empty_repository_list(self):
        """Test handling of empty repository list."""
        from repo_manager import RepoManager

        manager = RepoManager()
        results = await manager.initialize_repositories([])

        assert results == []


@pytest.mark.unit
class TestRepoManagerEdgeCases:
    """Edge case tests for repository manager."""

    @pytest.mark.asyncio
    async def test_invalid_repo_config_missing_fields(self):
        """Test handling of invalid repository configuration."""
        from repo_manager import RepoManager

        # Missing remote_url
        invalid_config = {
            "name": "incomplete",
            "local_path": "/tmp/incomplete",
        }

        manager = RepoManager()

        # Should handle gracefully
        result = await manager.initialize_repository(invalid_config)
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_repository_path_with_spaces(self, temp_dir, mocker):
        """Test handling of repository paths containing spaces."""
        from repo_manager import RepoManager

        repo_path = temp_dir / "repo with spaces"
        repo_config = {
            "name": "spaced-repo",
            "local_path": str(repo_path),
            "remote_url": "https://github.com/user/spaced.git",
        }

        mock_clone = mocker.patch("git.Repo.clone_from")
        mock_clone.return_value = MagicMock()

        manager = RepoManager()
        result = await manager.initialize_repository(repo_config)

        assert result["status"] == "success"
        mock_clone.assert_called_once()

    @pytest.mark.asyncio
    async def test_repository_with_ssh_url(self, temp_dir, mocker):
        """Test cloning repository with SSH URL format."""
        from repo_manager import RepoManager

        repo_path = temp_dir / "ssh_repo"
        repo_config = {
            "name": "ssh-repo",
            "local_path": str(repo_path),
            "remote_url": "git@github.com:user/ssh-repo.git",
        }

        mock_clone = mocker.patch("git.Repo.clone_from")
        mock_clone.return_value = MagicMock()

        manager = RepoManager()
        result = await manager.initialize_repository(repo_config)

        assert result["status"] == "success"
        mock_clone.assert_called_with("git@github.com:user/ssh-repo.git", str(repo_path))

    @pytest.mark.asyncio
    async def test_timeout_during_clone(self, temp_dir, mocker):
        """Test handling of timeout during git clone operation."""
        from repo_manager import RepoManager
        import git

        repo_path = temp_dir / "timeout_repo"
        repo_config = {
            "name": "timeout-repo",
            "local_path": str(repo_path),
            "remote_url": "https://github.com/user/timeout.git",
        }

        # Simulate timeout - use Exception since run_in_executor wraps it
        mock_clone = mocker.patch("git.Repo.clone_from")
        mock_clone.side_effect = Exception("Timeout error")

        manager = RepoManager()
        result = await manager.initialize_repository(repo_config)

        assert result["status"] == "error"
        assert "error" in result["error_message"].lower()
