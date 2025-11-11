# Git Repository Control - MVP

A Python tool to monitor and manage multiple git repositories from a single configuration file.

## Features (MVP)

✅ **Config-driven repository management** - Define all repos in `config.yaml`  
✅ **Auto-clone missing repositories** - Automatically clones repos that don't exist locally  
✅ **Parallel operations** - Uses asyncio for fast concurrent processing  
✅ **Branch analysis** - Shows ahead/behind status for all branches  
✅ **Remote branch detection** - Identifies remote branches without local equivalents  
✅ **YAML output** - Structured results in `result.yaml` for programmatic use  
✅ **Clean CLI** - Simple command-line interface with progress indicators  

## Quick Start

### 1. Install dependencies

```bash
uv add gitpython pyyaml
```

### 2. Create config.yaml

```yaml
repositories:
  - name: my-project
    local_path: /home/user/projects/my-project
    remote_url: https://github.com/user/my-project.git
```

### 3. Run status check

```bash
uv run python main.py
```

## Usage

```bash
# Check status (default)
uv run python main.py

# Use custom config
uv run python main.py --config /path/to/config.yaml

# Show help
uv run python main.py --help
```

## Development

Tests: 49 passing, 90%+ coverage  
Run: `uv run pytest`

## License

MIT
