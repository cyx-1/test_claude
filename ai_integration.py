"""
AI Integration Module

Provides AI-powered commit message generation and summaries.
Falls back to simple messages when API is not available or disabled.
"""

import os
from typing import Optional, Dict, Any

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class AIClient:
    """
    AI client for generating commit messages and summaries.

    Falls back to simple message generation if API is unavailable.
    """

    def __init__(self, ai_config: Dict[str, Any]):
        """
        Initialize AI client.

        Args:
            ai_config: AI configuration from config.yaml
        """
        self.enabled = ai_config.get("enabled", False) and OPENAI_AVAILABLE
        self.api_type = ai_config.get("api_type", "openai")
        self.model = ai_config.get("model", "gpt-4o-mini")
        self.max_tokens = ai_config.get("max_tokens", 500)
        self.temperature = ai_config.get("temperature", 0.7)

        self.client = None

        if self.enabled:
            api_key = ai_config.get("api_key")
            base_url = ai_config.get("base_url")

            if api_key:
                try:
                    self.client = AsyncOpenAI(
                        api_key=api_key,
                        base_url=base_url,
                    )
                except Exception as e:
                    print(f"⚠️  Warning: Failed to initialize AI client: {e}")
                    self.enabled = False

    async def generate_commit_message(
        self,
        diff: str,
        status: str,
        max_length: int = 72
    ) -> str:
        """
        Generate commit message from git diff and status.

        Args:
            diff: Output from git diff
            status: Output from git status
            max_length: Maximum length of first line

        Returns:
            Generated commit message
        """
        if not self.enabled or not self.client:
            return self._generate_simple_commit_message(diff, status)

        try:
            prompt = self._build_commit_prompt(diff, status, max_length)

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates clear, concise git commit messages following conventional commit format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )

            message = response.choices[0].message.content.strip()

            # Clean up the message (remove quotes if present)
            if message.startswith('"') and message.endswith('"'):
                message = message[1:-1]

            return message

        except Exception as e:
            print(f"⚠️  AI generation failed, using simple message: {e}")
            return self._generate_simple_commit_message(diff, status)

    def _build_commit_prompt(self, diff: str, status: str, max_length: int) -> str:
        """Build prompt for commit message generation."""
        # Truncate diff if too long
        max_diff_length = 2000
        if len(diff) > max_diff_length:
            diff = diff[:max_diff_length] + "\n... (truncated)"

        return f"""Generate a git commit message for the following changes.

Git Status:
{status}

Git Diff:
{diff}

Requirements:
- Use conventional commit format (e.g., feat:, fix:, docs:, refactor:, test:)
- First line should be max {max_length} characters
- Be concise and descriptive
- Focus on WHAT changed and WHY, not HOW
- Return only the commit message, no additional text

Commit message:"""

    def _generate_simple_commit_message(self, diff: str, status: str) -> str:
        """
        Generate simple commit message without AI.

        Analyzes the changes and creates a basic message.
        """
        lines = status.split('\n')

        # Count changes
        modified = sum(1 for line in lines if 'modified:' in line.lower())
        added = sum(1 for line in lines if 'new file:' in line.lower() or 'added:' in line.lower())
        deleted = sum(1 for line in lines if 'deleted:' in line.lower())

        # Build message
        parts = []
        if added > 0:
            parts.append(f"Add {added} file{'s' if added > 1 else ''}")
        if modified > 0:
            parts.append(f"Update {modified} file{'s' if modified > 1 else ''}")
        if deleted > 0:
            parts.append(f"Delete {deleted} file{'s' if deleted > 1 else ''}")

        if not parts:
            return "Update repository"

        return ", ".join(parts)

    async def generate_pull_summary(
        self,
        commits: list,
        repo_name: str
    ) -> str:
        """
        Generate summary of pulled commits.

        Args:
            commits: List of commit dictionaries
            repo_name: Repository name

        Returns:
            Generated summary
        """
        if not self.enabled or not self.client or not commits:
            return self._generate_simple_pull_summary(commits)

        try:
            commit_messages = "\n".join([
                f"- {c.get('message', 'No message')}" for c in commits
            ])

            prompt = f"""Summarize the following git commits for repository '{repo_name}' in 1-2 sentences.
Focus on the overall themes and key changes.

Commits:
{commit_messages}

Summary:"""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that summarizes git commits concisely."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=200,
                temperature=self.temperature,
            )

            return response.choices[0].message.content.strip()

        except Exception:
            return self._generate_simple_pull_summary(commits)

    def _generate_simple_pull_summary(self, commits: list) -> str:
        """Generate simple summary without AI."""
        if not commits:
            return "No changes"

        count = len(commits)
        authors = list(set(c.get('author', 'Unknown') for c in commits))

        summary = f"{count} commit{'s' if count > 1 else ''}"
        if authors:
            summary += f" by {', '.join(authors[:2])}"
            if len(authors) > 2:
                summary += f" and {len(authors) - 2} other{'s' if len(authors) - 2 > 1 else ''}"

        return summary
