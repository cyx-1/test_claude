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
from ai_integration import AIClient
from batch_operations import BatchOperator


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


async def run_commit_push(config_path: Optional[Path] = None, use_ai: bool = True):
    """
    Commit and push all repositories with uncommitted changes.

    Args:
        config_path: Path to config.yaml (defaults to ./config.yaml)
        use_ai: Whether to use AI for commit messages
    """
    print("💾 Git Repository Control - Commit & Push")
    print("=" * 60)

    # Load configuration
    print("\n📋 Loading configuration...")
    config_manager = ConfigManager(config_path=config_path)
    try:
        config = config_manager.load()
        repos = config_manager.get_repositories()
        settings = config_manager.get_settings()
        ai_config = config_manager.get_ai_config()
        print(f"✅ Loaded {len(repos)} repositories")
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return 1

    # Initialize AI client if enabled
    ai_client = None
    if use_ai and ai_config.get("enabled", False):
        print("🤖 Initializing AI client...")
        ai_client = AIClient(ai_config)
        if ai_client.enabled:
            print("  ✅ AI enabled (using OpenAI API)")
        else:
            print("  ⚠️  AI unavailable, using simple messages")
    else:
        print("📝 Using simple commit messages (AI disabled)")

    # Initialize batch operator
    operator = BatchOperator(
        ai_client=ai_client,
        max_concurrent=settings.get("parallel_limit", 5)
    )

    # Commit and push all repositories
    print(f"\n💾 Committing and pushing repositories...")
    results = await operator.commit_and_push_all(repos)

    # Display results
    print("\n" + "=" * 60)
    print("Results")
    print("=" * 60)

    success_count = 0
    skipped_count = 0
    error_count = 0

    for result in results:
        name = result["name"]
        status = result["status"]

        if status == "success":
            success_count += 1
            branch = result.get("branch", "unknown")
            msg = result.get("commit_message", "")
            msg_preview = msg[:50] + "..." if len(msg) > 50 else msg
            print(f"✅ {name}: Committed and pushed to {branch}")
            print(f"   └─ {msg_preview}")
        elif status == "skipped":
            skipped_count += 1
            print(f"⏭️  {name}: {result.get('message', 'Skipped')}")
        else:
            error_count += 1
            print(f"❌ {name}: {result.get('message', 'Error')}")

    print("\n" + "=" * 60)
    print(f"Total: {len(results)} | Success: {success_count} | Skipped: {skipped_count} | Failed: {error_count}")
    print("=" * 60)

    return 0 if error_count == 0 else 1


async def run_pull(config_path: Optional[Path] = None):
    """
    Pull from all repositories.

    Args:
        config_path: Path to config.yaml (defaults to ./config.yaml)
    """
    print("⬇️  Git Repository Control - Pull")
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

    # Initialize batch operator
    operator = BatchOperator(max_concurrent=settings.get("parallel_limit", 5))

    # Pull from all repositories
    print(f"\n⬇️  Pulling from repositories...")
    results = await operator.pull_all(repos)

    # Display results
    print("\n" + "=" * 60)
    print("Results")
    print("=" * 60)

    success_count = 0
    error_count = 0

    for result in results:
        name = result["name"]
        status = result["status"]

        if status == "success":
            success_count += 1
            message = result.get("message", "")
            branch = result.get("branch", "unknown")
            commits_pulled = result.get("commits_pulled", 0)

            if commits_pulled > 0:
                print(f"✅ {name}: Pulled {commits_pulled} commit(s) on {branch}")
                commits = result.get("commits", [])
                for commit in commits[:3]:  # Show first 3 commits
                    msg = commit["message"][:60]
                    print(f"   └─ {commit['hash']} - {msg}")
                if len(commits) > 3:
                    print(f"   └─ ... and {len(commits) - 3} more")
            else:
                print(f"✅ {name}: {message}")
        else:
            error_count += 1
            print(f"❌ {name}: {result.get('message', 'Error')}")

    print("\n" + "=" * 60)
    print(f"Total: {len(results)} | Success: {success_count} | Failed: {error_count}")
    print("=" * 60)

    return 0 if error_count == 0 else 1


def main():
    """Main entry point."""
    # Parse simple command-line arguments
    args = sys.argv[1:]

    command = "status"  # Default command
    config_path = None
    use_ai = True

    # Simple argument parsing
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ["status", "commit-push", "pull", "help", "--help", "-h"]:
            if arg in ["--help", "-h"]:
                command = "help"
            else:
                command = arg
        elif arg in ["--config", "-c"]:
            if i + 1 < len(args):
                config_path = Path(args[i + 1])
                i += 1
        elif arg == "--no-ai":
            use_ai = False
        i += 1

    if command == "help":
        print("Git Repository Control")
        print("=" * 60)
        print()
        print("Usage:")
        print("  uv run python main.py [COMMAND] [OPTIONS]")
        print()
        print("Commands:")
        print("  status              Check status of all repositories (default)")
        print("  commit-push         Commit and push all repos with changes")
        print("  pull                Pull from all repositories")
        print()
        print("Options:")
        print("  --config, -c PATH   Path to config.yaml (default: ./config.yaml)")
        print("  --no-ai             Disable AI for commit messages")
        print("  --help, -h          Show this help message")
        print()
        print("Examples:")
        print("  uv run python main.py")
        print("  uv run python main.py status")
        print("  uv run python main.py commit-push")
        print("  uv run python main.py commit-push --no-ai")
        print("  uv run python main.py pull")
        print("  uv run python main.py --config ~/repos/config.yaml")
        return 0

    # Run appropriate command
    try:
        if command == "commit-push":
            exit_code = asyncio.run(run_commit_push(config_path, use_ai))
        elif command == "pull":
            exit_code = asyncio.run(run_pull(config_path))
        else:  # default to status
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
