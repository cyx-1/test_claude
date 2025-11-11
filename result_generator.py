"""
Result Generator Module - MVP Version

Generates YAML output from repository analysis results.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

import yaml


class ResultGenerator:
    """Generates result.yaml from analysis data."""

    def __init__(self):
        """Initialize result generator."""
        self.results = []

    def add_repository_result(
        self,
        repo_name: str,
        local_path: str,
        analysis: Dict[str, Any],
    ):
        """
        Add a repository analysis result.

        Args:
            repo_name: Repository name
            local_path: Local path to repository
            analysis: Analysis results from GitAnalyzer
        """
        result = {
            "name": repo_name,
            "local_path": local_path,
        }

        if analysis.get("status") == "success":
            result["status"] = "success"
            result["current_branch"] = analysis.get("current_branch", "unknown")
            result["dirty_working_tree"] = analysis.get("dirty_working_tree", False)
            result["branches"] = analysis.get("branches", [])
        else:
            result["status"] = "error"
            result["error_message"] = analysis.get("error_message", "Unknown error")

        self.results.append(result)

    def generate_yaml(self, output_path: Path) -> None:
        """
        Generate result.yaml file.

        Args:
            output_path: Path where to write result.yaml
        """
        # Calculate summary statistics
        total = len(self.results)
        successful = sum(1 for r in self.results if r.get("status") == "success")
        failed = total - successful

        # Build output structure
        output = {
            "metadata": {
                "analysis_timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "total_repositories": total,
                "successful": successful,
                "failed": failed,
            },
            "repositories": self.results,
        }

        # Write to file
        with open(output_path, "w") as f:
            yaml.dump(output, f, default_flow_style=False, sort_keys=False)

    def get_summary(self) -> str:
        """
        Get a text summary of results.

        Returns:
            Formatted summary string
        """
        total = len(self.results)
        successful = sum(1 for r in self.results if r.get("status") == "success")
        failed = total - successful

        summary = f"\n{'='*60}\n"
        summary += f"Analysis Complete\n"
        summary += f"{'='*60}\n"
        summary += f"Total Repositories: {total}\n"
        summary += f"Successful: {successful}\n"
        summary += f"Failed: {failed}\n"
        summary += f"{'='*60}\n\n"

        # Add per-repository summary
        for result in self.results:
            name = result["name"]
            status = result["status"]

            summary += f"📁 {name}: "

            if status == "success":
                branch = result.get("current_branch", "unknown")
                dirty = result.get("dirty_working_tree", False)
                branches = result.get("branches", [])

                # Count branches with changes
                ahead_count = sum(1 for b in branches if b.get("ahead", 0) > 0)
                behind_count = sum(1 for b in branches if b.get("behind", 0) > 0)

                summary += f"✅ OK (on {branch}"
                if dirty:
                    summary += ", uncommitted changes"
                if ahead_count > 0:
                    summary += f", {ahead_count} branch(es) ahead"
                if behind_count > 0:
                    summary += f", {behind_count} branch(es) behind"
                summary += ")\n"
            else:
                error = result.get("error_message", "Unknown error")
                summary += f"❌ ERROR: {error}\n"

        return summary
