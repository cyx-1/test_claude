# Git Repository Control Program - Implementation Plan

## Overview
A Python program to monitor and manage multiple git repositories defined in a configuration file, tracking synchronization status between local and remote branches. Uses asyncio for parallel operations and outputs results in YAML format for flexible consumption.

## Core Features

### 1. Repository Management (Config-Driven)
- Read repository definitions from `config.yaml`
- Each repository specifies:
  - Name (identifier)
  - Local path (where repo should exist)
  - Remote URL (git clone URL)
- **Auto-clone**: If local repository doesn't exist, clone it from remote
- Validate repository configuration and accessibility

### 2. Branch Analysis (Per Repository)
- **Local branches**: List all local branches
- **Remote branches**: List all remote branches (including those without local tracking)
- **Tracking status**: Identify which local branches track which remote branches

### 3. Sync Status Detection

#### 3.1 Unpushed Changes
- For each local branch with a tracking remote:
  - Detect commits that exist locally but not on remote
  - Count unpushed commits
  - Extract commit messages and create summary

#### 3.2 Unpulled Changes
- For each remote branch:
  - Detect commits that exist on remote but not locally
  - Handle both:
    - Remote branches with local tracking branches
    - Remote branches without local equivalents
  - Count unpulled commits
  - Extract commit messages and create summary

#### 3.3 Uncommitted Changes
- Detect modified/staged/untracked files in working directory
- Flag repositories with dirty working trees

### 4. Commit Summary Generation
- For unpushed commits: group by branch, show commit hash (short), author, date, message
- For unpulled commits: group by branch, show commit hash (short), author, date, message
- Format in readable structure

### 5. Output/Reporting
- Generate structured YAML output file (`result.yaml`)
- Output includes:
  - Repository-by-repository status
  - Branch-level sync details
  - Commit summaries (unpushed/unpulled)
  - Timestamp of analysis
  - Error/warning messages for problematic repositories
- YAML format allows easy translation to:
  - Text/CLI output
  - Web UI dashboard
  - JSON for API consumption
  - Other formats as needed

## Technical Implementation Steps

### Step 1: Environment Setup
- Use `uv` for dependency management
- Required libraries:
  - **GitPython**: Git operations
  - **PyYAML**: Config and result file parsing/generation
  - **asyncio**: Built-in (Python 3.7+) for parallel operations
- Add dependencies: `uv add gitpython pyyaml`

### Step 2: Configuration Management
- Create `config.yaml` schema/structure
- Implement config parser and validator
- Validate repository entries (name, local_path, remote_url)
- Handle malformed or missing configuration gracefully

### Step 3: Repository Initialization
- **Clone missing repositories**: Check if local_path exists
  - If not, perform `git clone <remote_url> <local_path>`
  - Handle clone failures (auth issues, network errors)
- Validate existing repositories (verify .git directory)
- Use asyncio to clone multiple repositories in parallel

### Step 4: Git Operations Module (Async)
- Implement async wrappers for git operations
- Fetch latest remote information (without pulling) - use `git fetch --all`
- Parse branch information (local and remote)
- Compare commits between local and remote branches
- All git operations should be async to enable parallelization

### Step 5: Commit Comparison Logic
- Use `git rev-list` or GitPython equivalents
- Identify commit differences (ahead/behind)
- Extract commit metadata (hash, author, date, message)
- Handle all branches (including remote-only branches)

### Step 6: Summary Generator
- Parse commit messages
- Structure data for YAML output
- Group by repository and branch
- Include metadata (analysis timestamp, repository status)

### Step 7: YAML Result Generation
- Design result.yaml structure
- Convert analysis data to YAML format
- Write to `result.yaml` file
- Include error/warning sections for failed operations

### Step 8: Main Controller (Async Orchestration)
- Use `asyncio.gather()` to process multiple repositories in parallel
- Orchestrate: config loading → clone/validate → fetch → analyze → generate output
- Handle errors gracefully (don't let one repo failure stop entire process)
- Implement logging for progress tracking

### Step 9: CLI Interface (Optional)
- Simple entry point: `uv run python main.py`
- Optional: Accept custom config path as argument
- Display progress/summary to console
- Exit with appropriate status code

## Project Structure
```
git_repo_control/
├── main.py                 # Entry point (async orchestration)
├── config.yaml             # Repository configuration (user-defined)
├── result.yaml             # Generated output (analysis results)
├── config_manager.py       # Config parsing and validation
├── repo_manager.py         # Repository cloning and initialization (async)
├── git_analyzer.py         # Git operations and status analysis (async)
├── commit_analyzer.py      # Commit comparison logic
├── result_generator.py     # YAML output generation
├── README.md               # Documentation with source code and output examples
└── pyproject.toml          # Dependencies (gitpython, pyyaml)
```

## Configuration File Structure (config.yaml)

```yaml
repositories:
  - name: project-alpha
    local_path: /home/user/projects/alpha
    remote_url: https://github.com/user/alpha.git

  - name: project-beta
    local_path: /home/user/projects/beta
    remote_url: git@github.com:user/beta.git

  - name: personal-scripts
    local_path: /home/user/scripts
    remote_url: https://gitlab.com/user/scripts.git

# Optional settings
settings:
  auto_fetch: true           # Automatically fetch from remotes
  parallel_limit: 10         # Max concurrent operations
  clone_on_missing: true     # Auto-clone if local path doesn't exist
```

## Result File Structure (result.yaml)

```yaml
metadata:
  analysis_timestamp: "2025-11-10T14:30:00Z"
  total_repositories: 3
  successful: 2
  failed: 1

repositories:
  - name: project-alpha
    status: success
    local_path: /home/user/projects/alpha
    current_branch: main
    dirty_working_tree: false

    branches:
      - name: main
        tracking: origin/main
        ahead: 2
        behind: 0
        unpushed_commits:
          - hash: abc1234
            author: John Doe
            date: "2025-11-10"
            message: "Add new feature X"
          - hash: def5678
            author: John Doe
            date: "2025-11-09"
            message: "Fix bug in Y"

      - name: origin/feature-branch
        local_exists: false
        ahead: 0
        behind: 3
        unpulled_commits:
          - hash: ghi9012
            author: Jane Smith
            date: "2025-11-08"
            message: "Implement feature Z"

  - name: project-beta
    status: error
    error_message: "Failed to clone: Authentication required"
    local_path: /home/user/projects/beta
```

## Implementation Decisions Made

Based on your requirements, the following decisions have been made:

✅ **Repository Discovery**: Config-driven via `config.yaml` (not scanning)
✅ **Parallelization**: Using `asyncio` for concurrent operations
✅ **Output Format**: YAML file (`result.yaml`) for flexible consumption
✅ **Auto-clone**: Missing local repositories will be cloned automatically
✅ **Remote Tracking**: All remote branches will be analyzed, including those without local equivalents

## Remaining Questions (Optional Refinements)

Before proceeding with implementation, please clarify if needed:

1. **Remote Configuration**:
   - Should the program check all configured remotes (origin, upstream, etc.) or just `origin`?
   - Default: Check all remotes

2. **Authentication & Network**:
   - How should authentication failures be handled? (prompt, use SSH agent, fail gracefully)
   - Should network failures trigger retries? (e.g., 3 retries with exponential backoff)
   - Default: Fail gracefully, log error in result.yaml

3. **Edge Cases**:
   - How should the program handle:
     - Detached HEAD states? (report status, flag as warning)
     - Repositories with merge conflicts? (report dirty state, include conflict info)
     - Submodules? (ignore, analyze separately, include in parent report)
   - Default: Report status, flag as warnings in result.yaml

4. **Commit Summary Detail**:
   - Include full commit messages or just first line?
   - Default: First line of commit message + author + date

5. **Progress Feedback**:
   - Should progress be displayed to console during execution?
   - Default: Yes, show repository processing progress

**If these defaults are acceptable, please say "proceed" to begin implementation.**
