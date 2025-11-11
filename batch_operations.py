"""
Batch Operations Module

Handles batch commit/push and pull operations across multiple repositories.
"""

import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

import git
from git.exc import GitCommandError

from ai_integration import AIClient


class BatchOperator:
    """
    Executes batch operations across multiple repositories.
    """

    def __init__(self, ai_client: Optional[AIClient] = None, max_concurrent: int = 5):
        """
        Initialize batch operator.

        Args:
            ai_client: AI client for generating commit messages
            max_concurrent: Maximum concurrent operations
        """
        self.ai_client = ai_client
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def commit_and_push_all(
        self,
        repos: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """
        Commit and push all repositories with uncommitted changes.

        Args:
            repos: List of repository configurations

        Returns:
            List of operation results
        """
        async def process_repo(repo_config):
            async with self._semaphore:
                return await self._commit_and_push_single(repo_config)

        tasks = [process_repo(repo) for repo in repos]
        results = await asyncio.gather(*tasks, return_exceptions=False)

        return list(results)

    async def _commit_and_push_single(
        self,
        repo_config: Dict[str, str],
    ) -> Dict[str, Any]:
        """
        Commit and push a single repository.

        Args:
            repo_config: Repository configuration

        Returns:
            Operation result
        """
        repo_name = repo_config["name"]
        local_path = Path(repo_config["local_path"])

        try:
            # Open repository
            repo = git.Repo(local_path)

            # Check if there are uncommitted changes
            if not repo.is_dirty(untracked_files=True):
                return {
                    "name": repo_name,
                    "status": "skipped",
                    "message": "No uncommitted changes",
                }

            # Get current branch
            try:
                current_branch = repo.active_branch.name
            except TypeError:
                return {
                    "name": repo_name,
                    "status": "error",
                    "message": "Repository in detached HEAD state",
                }

            # Get diff and status for AI
            diff_output = await asyncio.get_event_loop().run_in_executor(
                None, lambda: repo.git.diff(cached=False)
            )

            status_output = await asyncio.get_event_loop().run_in_executor(
                None, lambda: repo.git.status(short=True)
            )

            # Generate commit message
            if self.ai_client:
                commit_message = await self.ai_client.generate_commit_message(
                    diff_output, status_output
                )
            else:
                # Simple fallback message
                commit_message = "Update repository"

            # Stage all changes
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: repo.git.add(A=True)
            )

            # Commit
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: repo.git.commit(m=commit_message)
            )

            # Push to remote
            try:
                origin = repo.remote("origin")
                await asyncio.get_event_loop().run_in_executor(
                    None, lambda: origin.push(current_branch)
                )

                return {
                    "name": repo_name,
                    "status": "success",
                    "branch": current_branch,
                    "commit_message": commit_message,
                }

            except GitCommandError as e:
                error_msg = str(e)
                if "rejected" in error_msg.lower():
                    return {
                        "name": repo_name,
                        "status": "error",
                        "message": "Push rejected (pull required)",
                    }
                elif "authentication" in error_msg.lower():
                    return {
                        "name": repo_name,
                        "status": "error",
                        "message": "Authentication failed",
                    }
                else:
                    return {
                        "name": repo_name,
                        "status": "error",
                        "message": f"Push failed: {error_msg[:100]}",
                    }

        except GitCommandError as e:
            return {
                "name": repo_name,
                "status": "error",
                "message": f"Git error: {str(e)[:100]}",
            }

        except Exception as e:
            return {
                "name": repo_name,
                "status": "error",
                "message": f"Unexpected error: {str(e)[:100]}",
            }

    async def pull_all(
        self,
        repos: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """
        Pull from all repositories.

        Args:
            repos: List of repository configurations

        Returns:
            List of operation results
        """
        async def process_repo(repo_config):
            async with self._semaphore:
                return await self._pull_single(repo_config)

        tasks = [process_repo(repo) for repo in repos]
        results = await asyncio.gather(*tasks, return_exceptions=False)

        return list(results)

    async def _pull_single(
        self,
        repo_config: Dict[str, str],
    ) -> Dict[str, Any]:
        """
        Pull from a single repository.

        Args:
            repo_config: Repository configuration

        Returns:
            Operation result
        """
        repo_name = repo_config["name"]
        local_path = Path(repo_config["local_path"])

        try:
            # Open repository
            repo = git.Repo(local_path)

            # Get current branch
            try:
                current_branch = repo.active_branch.name
            except TypeError:
                return {
                    "name": repo_name,
                    "status": "error",
                    "message": "Repository in detached HEAD state",
                }

            # Check if clean
            if repo.is_dirty(untracked_files=True):
                return {
                    "name": repo_name,
                    "status": "error",
                    "message": "Uncommitted changes present (stash or commit first)",
                }

            # Get current commit hash
            before_hash = repo.head.commit.hexsha

            # Pull from remote
            try:
                origin = repo.remote("origin")
                pull_info = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: origin.pull(current_branch)
                )

                # Get new commit hash
                after_hash = repo.head.commit.hexsha

                # Check if anything changed
                if before_hash == after_hash:
                    return {
                        "name": repo_name,
                        "status": "success",
                        "message": "Already up to date",
                        "branch": current_branch,
                        "commits_pulled": 0,
                    }

                # Count commits pulled
                commits = list(repo.iter_commits(f"{before_hash}..{after_hash}"))

                return {
                    "name": repo_name,
                    "status": "success",
                    "message": f"Pulled {len(commits)} commit(s)",
                    "branch": current_branch,
                    "commits_pulled": len(commits),
                    "commits": [
                        {
                            "hash": c.hexsha[:7],
                            "author": c.author.name,
                            "message": c.message.split('\n')[0],
                        }
                        for c in commits
                    ],
                }

            except GitCommandError as e:
                error_msg = str(e)
                if "conflict" in error_msg.lower():
                    return {
                        "name": repo_name,
                        "status": "error",
                        "message": "Merge conflict occurred",
                    }
                elif "authentication" in error_msg.lower():
                    return {
                        "name": repo_name,
                        "status": "error",
                        "message": "Authentication failed",
                    }
                else:
                    return {
                        "name": repo_name,
                        "status": "error",
                        "message": f"Pull failed: {error_msg[:100]}",
                    }

        except Exception as e:
            return {
                "name": repo_name,
                "status": "error",
                "message": f"Unexpected error: {str(e)[:100]}",
            }
