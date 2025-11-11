# Git Repository Control

A Python tool to monitor and manage multiple git repositories from a single configuration file.

## Features

✅ **Config-driven repository management** - Define all repos in `config.yaml`
✅ **Auto-clone missing repositories** - Automatically clones repos that don't exist locally
✅ **Parallel operations** - Uses asyncio for fast concurrent processing
✅ **Branch analysis** - Shows ahead/behind status for all branches
✅ **Remote branch detection** - Identifies remote branches without local equivalents
✅ **YAML output** - Structured results in `result.yaml` for programmatic use
✅ **Batch commit & push** - Commit and push all repos with one command
✅ **Batch pull** - Pull from all repos simultaneously
✅ **AI-powered commit messages** - Optional OpenAI integration for smart commits
✅ **Clean CLI** - Simple command-line interface with progress indicators

## Quick Start

### 1. Install dependencies

```bash
uv add gitpython pyyaml openai
```

### 2. Create config.yaml

```yaml
repositories:
  - name: my-project
    local_path: /home/user/projects/my-project
    remote_url: https://github.com/user/my-project.git

  - name: another-repo
    local_path: /home/user/projects/another
    remote_url: git@github.com:user/another.git

settings:
  auto_fetch: true
  parallel_limit: 10
  clone_on_missing: true

ai:
  enabled: false  # Set to true to enable AI commit messages
  api_key: ${OPENAI_API_KEY}
  model: gpt-4o-mini
```

### 3. Run commands

```bash
# Check status
uv run python main.py status

# Commit and push all repos with changes
uv run python main.py commit-push

# Pull from all repos
uv run python main.py pull
```

## Commands

### Status Check

Check the status of all configured repositories:

```bash
uv run python main.py status
```

Features:
- Shows current branch
- Detects uncommitted changes
- Lists ahead/behind status for all branches
- Identifies remote branches without local equivalents
- Generates `result.yaml` with detailed analysis

### Commit and Push

Commit and push all repositories with uncommitted changes:

```bash
# With AI-generated commit messages (requires OpenAI API key)
uv run python main.py commit-push

# With simple commit messages (no API required)
uv run python main.py commit-push --no-ai
```

Features:
- Automatically detects repos with uncommitted changes
- Stages all changes (`git add .`)
- Generates commit message (AI or simple)
- Commits and pushes to current branch
- Processes repos in parallel
- Skips repos without changes
- Reports success/failure for each repo

### Pull

Pull from all repositories:

```bash
uv run python main.py pull
```

Features:
- Pulls latest changes from remote
- Only pulls current branch
- Shows commits that were pulled
- Handles conflicts gracefully
- Skips repos with uncommitted changes

## AI Integration

Enable AI-powered commit messages by setting up OpenAI API:

1. Get API key from https://platform.openai.com/
2. Set environment variable: `export OPENAI_API_KEY=sk-...`
3. Enable in config.yaml:

```yaml
ai:
  enabled: true
  api_type: openai
  api_key: ${OPENAI_API_KEY}
  model: gpt-4o-mini
  max_tokens: 500
  temperature: 0.7
```

AI features:
- Analyzes `git diff` and `git status`
- Generates conventional commit messages
- Falls back to simple messages if API unavailable

## Usage Examples

```bash
# Check status
uv run python main.py
uv run python main.py status

# Commit and push with AI
export OPENAI_API_KEY=sk-...
uv run python main.py commit-push

# Commit and push without AI
uv run python main.py commit-push --no-ai

# Pull from all repos
uv run python main.py pull

# Use custom config
uv run python main.py --config ~/repos/config.yaml status

# Show help
uv run python main.py --help
```

## Development

Tests: 49 passing, 90%+ coverage
Run: `uv run pytest`

## Project Structure

```
git_repo_control/
├── main.py                 # CLI entry point
├── config.yaml             # Repository configuration
├── result.yaml             # Generated analysis output
├── config_manager.py       # Config parsing (92% coverage)
├── repo_manager.py         # Repo initialization (88% coverage)
├── git_analyzer.py         # Git operations
├── result_generator.py     # YAML output generation
├── ai_integration.py       # OpenAI integration
├── batch_operations.py     # Batch commit/push/pull
├── tests/                  # Test suite (TDD)
└── README.md
```

## License

MIT
