"""
Repository Initialization Module

Handles cloning and validation of git repositories.

Features:
- Detect existing repositories
- Clone missing repositories
- Validate .git directories
- Async parallel operations
- Error handling for network/auth failures
"""

import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable

import git
from git.exc import GitCommandError


def is_valid_repository(repo_path: Path) -> bool:
    """
    Check if a path contains a valid git repository.

    Args:
        repo_path: Path to check

    Returns:
        True if path exists and contains .git directory, False otherwise
    """
    if not isinstance(repo_path, Path):
        repo_path = Path(repo_path)

    return repo_path.exists() and (repo_path / ".git").exists()


class RepoManager:
    """
    Manages git repository initialization and validation.

    Handles cloning missing repos, validating existing ones,
    and coordinating parallel operations with concurrency control.
    """

    def __init__(self, max_concurrent: int = 10):
        """
        Initialize RepoManager.

        Args:
            max_concurrent: Maximum number of concurrent operations
        """
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def initialize_repository(
        self,
        repo_config: Dict[str, str],
        progress_callback: Optional[Callable[[str, str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Initialize a single repository (clone if missing, validate if exists).

        Args:
            repo_config: Repository configuration dict with keys:
                - name: Repository name
                - local_path: Local filesystem path
                - remote_url: Git remote URL
            progress_callback: Optional callback for progress updates

        Returns:
            Result dictionary with keys:
                - status: "success" or "error"
                - name: Repository name
                - action: "cloned", "validated", or None
                - error_message: Error description (if status is "error")
        """
        async with self._semaphore:
            return await self._initialize_single_repo(repo_config, progress_callback)

    async def _initialize_single_repo(
        self,
        repo_config: Dict[str, str],
        progress_callback: Optional[Callable[[str, str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Internal method to initialize a repository without semaphore.

        Args:
            repo_config: Repository configuration
            progress_callback: Optional progress callback

        Returns:
            Result dictionary
        """
        # Validate config has required fields
        required_fields = ["name", "local_path", "remote_url"]
        for field in required_fields:
            if field not in repo_config:
                return {
                    "status": "error",
                    "name": repo_config.get("name", "unknown"),
                    "action": None,
                    "error_message": f"Missing required field: {field}",
                }

        repo_name = repo_config["name"]
        local_path = Path(repo_config["local_path"])
        remote_url = repo_config["remote_url"]

        try:
            # Check if repository already exists
            if local_path.exists():
                # Validate it's a proper git repository
                if is_valid_repository(local_path):
                    if progress_callback:
                        progress_callback(repo_name, "validated")

                    return {
                        "status": "success",
                        "name": repo_name,
                        "action": "validated",
                        "local_path": str(local_path),
                    }
                else:
                    return {
                        "status": "error",
                        "name": repo_name,
                        "action": None,
                        "error_message": f"Directory exists but is not a valid git repository (missing .git directory)",
                    }

            # Repository doesn't exist - clone it
            if progress_callback:
                progress_callback(repo_name, "cloning")

            # Create parent directories if needed
            local_path.parent.mkdir(parents=True, exist_ok=True)

            # Clone repository (run in executor for async)
            await asyncio.get_event_loop().run_in_executor(
                None, git.Repo.clone_from, remote_url, str(local_path)
            )

            if progress_callback:
                progress_callback(repo_name, "cloned")

            return {
                "status": "success",
                "name": repo_name,
                "action": "cloned",
                "local_path": str(local_path),
            }

        except GitCommandError as e:
            # Handle git-specific errors
            error_msg = str(e)

            # Classify error type
            if "authentication" in error_msg.lower() or "permission denied" in error_msg.lower():
                error_type = "Authentication failed"
            elif "could not resolve" in error_msg.lower() or "network" in error_msg.lower():
                error_type = "Network error: Could not resolve host"
            else:
                error_type = f"Git error: {error_msg}"

            return {
                "status": "error",
                "name": repo_name,
                "action": None,
                "error_message": error_type,
            }

        except asyncio.TimeoutError:
            return {
                "status": "error",
                "name": repo_name,
                "action": None,
                "error_message": "Clone operation timed out",
            }

        except Exception as e:
            # Handle any other unexpected errors
            return {
                "status": "error",
                "name": repo_name,
                "action": None,
                "error_message": f"Unexpected error: {str(e)}",
            }

    async def initialize_repositories(
        self,
        repos_config: List[Dict[str, str]],
        progress_callback: Optional[Callable[[str, str], None]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Initialize multiple repositories in parallel.

        Args:
            repos_config: List of repository configurations
            progress_callback: Optional callback for progress updates

        Returns:
            List of result dictionaries, one per repository
        """
        if not repos_config:
            return []

        # Create tasks for all repositories
        tasks = [
            self.initialize_repository(repo_config, progress_callback)
            for repo_config in repos_config
        ]

        # Run all tasks in parallel (respecting semaphore limit)
        results = await asyncio.gather(*tasks, return_exceptions=False)

        return list(results)


async def initialize_from_config(
    config_manager,
    max_concurrent: int = 10,
    progress_callback: Optional[Callable[[str, str], None]] = None,
) -> List[Dict[str, Any]]:
    """
    Initialize all repositories from a ConfigManager.

    Args:
        config_manager: ConfigManager instance with loaded config
        max_concurrent: Maximum concurrent operations
        progress_callback: Optional progress callback

    Returns:
        List of initialization results
    """
    repos = config_manager.get_repositories()
    manager = RepoManager(max_concurrent=max_concurrent)
    return await manager.initialize_repositories(repos, progress_callback)
