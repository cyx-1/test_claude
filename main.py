#!/usr/bin/env python3
"""
Git Repository Control - Main Entry Point (MVP)

A tool to manage and monitor multiple git repositories.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

from config_manager import ConfigManager
from repo_manager import RepoManager
from git_analyzer import GitAnalyzer
from result_generator import ResultGenerator


async def run_status(config_path: Optional[Path] = None):
    """
    Run status check on all configured repositories.

    Args:
        config_path: Path to config.yaml (defaults to ./config.yaml)
    """
    print("🔍 Git Repository Control - Status Check")
    print("=" * 60)

    # Load configuration
    print("\n📋 Loading configuration...")
    config_manager = ConfigManager(config_path=config_path)
    try:
        config = config_manager.load()
        repos = config_manager.get_repositories()
        settings = config_manager.get_settings()
        print(f"✅ Loaded {len(repos)} repositories")
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return 1

    # Initialize repositories (clone missing ones)
    print(f"\n🔧 Initializing repositories...")
    repo_manager = RepoManager(max_concurrent=settings.get("parallel_limit", 10))

    init_results = await repo_manager.initialize_repositories(repos)

    # Show initialization summary
    cloned = sum(1 for r in init_results if r.get("action") == "cloned")
    validated = sum(1 for r in init_results if r.get("action") == "validated")
    failed = sum(1 for r in init_results if r.get("status") == "error")

    if cloned > 0:
        print(f"  📥 Cloned: {cloned}")
    if validated > 0:
        print(f"  ✓ Validated: {validated}")
    if failed > 0:
        print(f"  ❌ Failed: {failed}")

    # Analyze repositories
    print(f"\n🔍 Analyzing repositories...")
    result_gen = ResultGenerator()

    for repo_config, init_result in zip(repos, init_results):
        repo_name = repo_config["name"]
        local_path = repo_config["local_path"]

        if init_result["status"] == "error":
            # Skip failed initializations
            result_gen.add_repository_result(
                repo_name,
                local_path,
                {"status": "error", "error_message": init_result["error_message"]},
            )
            continue

        # Analyze repository
        print(f"  📁 {repo_name}...", end=" ", flush=True)
        analyzer = GitAnalyzer(Path(local_path))
        analysis = await analyzer.analyze()

        if analysis["status"] == "success":
            print("✅")
        else:
            print(f"❌ {analysis.get('error_message', 'Error')}")

        result_gen.add_repository_result(repo_name, local_path, analysis)

    # Generate result.yaml
    output_path = Path("result.yaml")
    result_gen.generate_yaml(output_path)
    print(f"\n💾 Results saved to: {output_path}")

    # Print summary
    print(result_gen.get_summary())

    return 0


def main():
    """Main entry point."""
    # Parse simple command-line arguments
    args = sys.argv[1:]

    command = "status"  # Default command
    config_path = None

    # Simple argument parsing
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ["status", "help", "--help", "-h"]:
            command = "status" if arg == "status" else "help"
        elif arg in ["--config", "-c"]:
            if i + 1 < len(args):
                config_path = Path(args[i + 1])
                i += 1
        i += 1

    if command == "help":
        print("Git Repository Control - MVP")
        print("=" * 60)
        print()
        print("Usage:")
        print("  python main.py [status] [--config PATH]")
        print()
        print("Commands:")
        print("  status              Check status of all repositories (default)")
        print()
        print("Options:")
        print("  --config, -c PATH   Path to config.yaml (default: ./config.yaml)")
        print("  --help, -h          Show this help message")
        print()
        print("Examples:")
        print("  python main.py")
        print("  python main.py status")
        print("  python main.py --config ~/repos/config.yaml")
        return 0

    # Run status command
    try:
        exit_code = asyncio.run(run_status(config_path))
        return exit_code
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
