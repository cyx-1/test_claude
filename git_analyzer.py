"""
Git Analysis Module - MVP Version

Provides basic git operations for repository status analysis.
Simplified version focusing on core functionality.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

import git
from git.exc import GitCommandError


class GitAnalyzer:
    """
    Analyzes git repository status.

    MVP version with essential features:
    - Fetch from remotes
    - Get branch information
    - Calculate ahead/behind status
    - Extract commit information
    """

    def __init__(self, repo_path: Path):
        """
        Initialize analyzer for a repository.

        Args:
            repo_path: Path to git repository
        """
        self.repo_path = Path(repo_path)
        self.repo = None

    async def analyze(self) -> Dict[str, Any]:
        """
        Analyze repository status.

        Returns:
            Dictionary with repository analysis results
        """
        try:
            # Load repository
            self.repo = git.Repo(self.repo_path)

            # Fetch from remotes
            await self._fetch_all()

            # Get current branch
            current_branch = self._get_current_branch()

            # Analyze all branches
            branches = await self._analyze_branches()

            # Check working tree status
            is_dirty = self.repo.is_dirty(untracked_files=True)

            return {
                "status": "success",
                "current_branch": current_branch,
                "dirty_working_tree": is_dirty,
                "branches": branches,
            }

        except Exception as e:
            return {
                "status": "error",
                "error_message": str(e),
            }

    async def _fetch_all(self):
        """Fetch from all remotes."""
        try:
            for remote in self.repo.remotes:
                await asyncio.get_event_loop().run_in_executor(
                    None, remote.fetch
                )
        except GitCommandError as e:
            # Non-fatal - continue with potentially stale data
            pass

    def _get_current_branch(self) -> str:
        """Get name of current branch."""
        try:
            return self.repo.active_branch.name
        except TypeError:
            # Detached HEAD
            return "HEAD (detached)"

    async def _analyze_branches(self) -> List[Dict[str, Any]]:
        """
        Analyze all local and remote branches.

        Returns:
            List of branch analysis results
        """
        branch_results = []

        # Analyze local branches
        for branch in self.repo.heads:
            branch_info = self._analyze_local_branch(branch)
            branch_results.append(branch_info)

        # Analyze remote-only branches
        remote_branches = self._get_remote_only_branches()
        for remote_ref in remote_branches:
            branch_info = self._analyze_remote_branch(remote_ref)
            branch_results.append(branch_info)

        return branch_results

    def _analyze_local_branch(self, branch) -> Dict[str, Any]:
        """Analyze a local branch."""
        result = {
            "name": branch.name,
            "type": "local",
            "tracking": None,
            "ahead": 0,
            "behind": 0,
            "unpushed_commits": [],
            "unpulled_commits": [],
        }

        # Check if tracking a remote branch
        try:
            tracking = branch.tracking_branch()
            if tracking:
                result["tracking"] = tracking.name

                # Calculate ahead/behind
                ahead, behind = self._calculate_ahead_behind(branch, tracking)
                result["ahead"] = ahead
                result["behind"] = behind

                # Get unpushed commits (if ahead)
                if ahead > 0:
                    result["unpushed_commits"] = self._get_commits_between(
                        tracking, branch, limit=ahead
                    )

                # Get unpulled commits (if behind)
                if behind > 0:
                    result["unpulled_commits"] = self._get_commits_between(
                        branch, tracking, limit=behind
                    )

        except (ValueError, GitCommandError):
            # No tracking branch or other error
            pass

        return result

    def _analyze_remote_branch(self, remote_ref) -> Dict[str, Any]:
        """Analyze a remote-only branch."""
        return {
            "name": remote_ref.name,
            "type": "remote",
            "local_exists": False,
            "ahead": 0,
            "behind": len(list(remote_ref.commit.iter_items(self.repo, remote_ref.commit))),
            "unpushed_commits": [],
            "unpulled_commits": self._get_commits_from_ref(remote_ref, limit=10),
        }

    def _get_remote_only_branches(self) -> List:
        """Get list of remote branches that don't have local equivalents."""
        local_branch_names = {head.name for head in self.repo.heads}
        remote_only = []

        for remote in self.repo.remotes:
            for ref in remote.refs:
                # Skip HEAD references
                if ref.name.endswith("/HEAD"):
                    continue

                # Extract branch name (remove remote/ prefix)
                branch_name = ref.name.split("/", 1)[1] if "/" in ref.name else ref.name

                # Check if no local branch exists
                if branch_name not in local_branch_names:
                    remote_only.append(ref)

        return remote_only

    def _calculate_ahead_behind(self, local_branch, remote_branch) -> tuple:
        """
        Calculate how many commits local is ahead/behind remote.

        Returns:
            Tuple of (ahead, behind)
        """
        try:
            # Count commits ahead
            ahead_commits = list(
                self.repo.iter_commits(f"{remote_branch.name}..{local_branch.name}")
            )
            ahead = len(ahead_commits)

            # Count commits behind
            behind_commits = list(
                self.repo.iter_commits(f"{local_branch.name}..{remote_branch.name}")
            )
            behind = len(behind_commits)

            return ahead, behind

        except GitCommandError:
            return 0, 0

    def _get_commits_between(self, base, head, limit=10) -> List[Dict[str, Any]]:
        """Get commits between base and head."""
        try:
            commits = list(
                self.repo.iter_commits(f"{base.name}..{head.name}", max_count=limit)
            )
            return [self._format_commit(c) for c in commits]
        except GitCommandError:
            return []

    def _get_commits_from_ref(self, ref, limit=10) -> List[Dict[str, Any]]:
        """Get commits from a reference."""
        try:
            commits = list(self.repo.iter_commits(ref, max_count=limit))
            return [self._format_commit(c) for c in commits]
        except GitCommandError:
            return []

    def _format_commit(self, commit) -> Dict[str, str]:
        """Format commit information."""
        return {
            "hash": commit.hexsha[:7],
            "author": commit.author.name,
            "date": datetime.fromtimestamp(commit.committed_date).strftime("%Y-%m-%d"),
            "message": commit.message.split("\n")[0],  # First line only
        }


async def analyze_repository(repo_path: Path) -> Dict[str, Any]:
    """
    Convenience function to analyze a single repository.

    Args:
        repo_path: Path to repository

    Returns:
        Analysis results
    """
    analyzer = GitAnalyzer(repo_path)
    return await analyzer.analyze()


async def analyze_repositories(repo_paths: List[Path], max_concurrent: int = 10) -> List[Dict[str, Any]]:
    """
    Analyze multiple repositories in parallel.

    Args:
        repo_paths: List of repository paths
        max_concurrent: Maximum concurrent operations

    Returns:
        List of analysis results
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def analyze_with_semaphore(path):
        async with semaphore:
            return await analyze_repository(path)

    tasks = [analyze_with_semaphore(path) for path in repo_paths]
    return await asyncio.gather(*tasks)
