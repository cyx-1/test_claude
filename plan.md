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

### 6. Batch Operations (Actions)

#### 6.1 Commit and Push All Repositories
- **Auto-commit with AI-generated messages**:
  - Detect uncommitted changes in each repository
  - Use OpenAI-style API to generate commit messages based on `git diff` and `git status`
  - Stage all changes (`git add .`)
  - Commit with AI-generated message
  - Push to remote (current branch)
- Execute across all repositories in parallel using asyncio
- Report success/failure per repository

#### 6.2 Pull from All Repositories
- **Pull changes from all tracked branches**:
  - For each repository, pull latest changes for current branch
  - Handle merge conflicts gracefully (flag and skip)
  - Track which branches were updated and what changed
- Execute across all repositories in parallel using asyncio

#### 6.3 Pull Journal Generation
- **Generate `journal.md` when pulling changes**:
  - Create a section for each repository
  - Within each repository section:
    - List each branch that had changes pulled
    - Summarize the pulled commits (using AI or simple aggregation)
    - Include commit count, authors, date range, and high-level summary
  - Append to journal.md with timestamp
  - Format for easy reading and historical tracking

## Technical Implementation Steps

### Step 1: Environment Setup
- Use `uv` for dependency management
- Required libraries:
  - **GitPython**: Git operations
  - **PyYAML**: Config and result file parsing/generation
  - **asyncio**: Built-in (Python 3.7+) for parallel operations
  - **openai**: OpenAI API client for AI-generated commit messages and summaries
- Add dependencies: `uv add gitpython pyyaml openai`

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

### Step 9: AI Integration Module
- Implement OpenAI API client wrapper
- **Commit message generation**:
  - Accept git diff and status as input
  - Generate concise, descriptive commit message
  - Follow conventional commit format (optional)
- **Pull summary generation**:
  - Accept list of commit messages
  - Generate high-level summary of changes
  - Group by functionality/theme if possible
- Handle API errors gracefully (fallback to simple messages)

### Step 10: Batch Action Operations (Async)
- **Commit and Push All**:
  - Check for uncommitted changes
  - Generate AI commit messages
  - Stage, commit, and push
  - Handle per-repository errors
- **Pull All**:
  - Pull from remote for current branch
  - Track changes (before/after commit SHAs)
  - Extract pulled commit information
  - Handle conflicts and errors
- **Journal Generation**:
  - Format pulled changes per repository/branch
  - Generate AI summaries for each pull
  - Append to journal.md with timestamps
  - Use markdown formatting for readability

### Step 11: CLI Interface
- Entry point: `uv run python main.py [command]`
- Commands:
  - `status` (default): Generate result.yaml with current status
  - `commit-push`: Commit and push all repositories with AI messages
  - `pull`: Pull from all repositories and generate journal.md
  - `sync`: Pull, then commit-push (full synchronization)
- Optional arguments:
  - `--config <path>`: Custom config file path
  - `--no-ai`: Disable AI features (use simple commit messages)
- Display progress/summary to console
- Exit with appropriate status code

## Project Structure
```
git_repo_control/
├── main.py                 # Entry point (CLI commands and async orchestration)
├── config.yaml             # Repository configuration (user-defined)
├── result.yaml             # Generated output (analysis results)
├── journal.md              # Generated pull history with AI summaries
├── config_manager.py       # Config parsing and validation
├── repo_manager.py         # Repository cloning and initialization (async)
├── git_analyzer.py         # Git operations and status analysis (async)
├── commit_analyzer.py      # Commit comparison logic
├── result_generator.py     # YAML output generation
├── ai_integration.py       # OpenAI API wrapper for commit messages and summaries
├── batch_operations.py     # Commit/push/pull operations across all repos (async)
├── journal_generator.py    # Journal.md generation with AI summaries
├── README.md               # Documentation with source code and output examples
└── pyproject.toml          # Dependencies (gitpython, pyyaml, openai)
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

# AI integration settings
ai:
  enabled: true              # Enable/disable AI features
  api_type: openai           # API type: openai, azure, ollama, etc.
  api_key: ${OPENAI_API_KEY} # API key (use environment variable)
  base_url: null             # Optional: custom API base URL (for compatible APIs)
  model: gpt-4o-mini         # Model to use for generation
  max_tokens: 500            # Max tokens for responses
  temperature: 0.7           # Creativity level (0.0-1.0)
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

## Journal File Structure (journal.md)

Generated when pulling changes from all repositories. Appends new entries with timestamps.

```markdown
# Git Pull Journal

## 2025-11-10 14:30:00

### project-alpha

#### Branch: main
**Commits pulled**: 3
**Authors**: Jane Smith, Bob Johnson
**Date range**: 2025-11-08 to 2025-11-10

**Summary**:
Added new authentication module with OAuth2 support and JWT token handling. Fixed critical bug in user session management that caused intermittent logouts. Updated documentation to reflect new API endpoints.

**Commits**:
- `abc1234` - Jane Smith (2025-11-10): Add OAuth2 authentication module
- `def5678` - Jane Smith (2025-11-09): Implement JWT token handling
- `ghi9012` - Bob Johnson (2025-11-08): Fix session management bug

---

#### Branch: feature/ui-redesign
**Commits pulled**: 2
**Authors**: Alice Chen
**Date range**: 2025-11-09 to 2025-11-10

**Summary**:
Redesigned dashboard UI with new color scheme and improved navigation. Implemented responsive layout for mobile devices.

**Commits**:
- `jkl3456` - Alice Chen (2025-11-10): Redesign dashboard with new color scheme
- `mno7890` - Alice Chen (2025-11-09): Add responsive layout for mobile

---

### project-beta

No changes pulled (already up to date).

---

### personal-scripts

#### Branch: main
**Commits pulled**: 1
**Authors**: You
**Date range**: 2025-11-10

**Summary**:
Added new backup script for automated database dumps with compression and rotation.

**Commits**:
- `pqr1234` - You (2025-11-10): Add database backup script

---

## 2025-11-09 09:15:00

### project-alpha

#### Branch: main
**Commits pulled**: 1
**Authors**: Bob Johnson
**Date range**: 2025-11-09

**Summary**:
Minor documentation updates and typo fixes.

**Commits**:
- `stu5678` - Bob Johnson (2025-11-09): Fix typos in README

---
```

## Implementation Decisions Made

Based on your requirements, the following decisions have been made:

✅ **Repository Discovery**: Config-driven via `config.yaml` (not scanning)
✅ **Parallelization**: Using `asyncio` for concurrent operations
✅ **Output Format**: YAML file (`result.yaml`) for flexible consumption
✅ **Auto-clone**: Missing local repositories will be cloned automatically
✅ **Remote Tracking**: All remote branches will be analyzed, including those without local equivalents
✅ **AI Integration**: OpenAI-style API for commit message generation and pull summaries
✅ **Batch Operations**: Commit/push and pull commands across all repositories
✅ **Journal Generation**: Automatic `journal.md` creation when pulling changes with AI summaries

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

6. **AI Commit Messages**:
   - Should commit messages follow conventional commit format (feat:, fix:, docs:, etc.)?
   - Should there be a character limit for commit messages?
   - Default: Conventional commits with 72 character first line limit

7. **Pull Behavior**:
   - Should pull operation update ALL branches or just current branch?
   - Should it create local tracking branches for remote-only branches?
   - Default: Pull current branch only, report remote-only branches in journal

8. **Journal Retention**:
   - Should journal.md have a maximum size/age (archive old entries)?
   - Default: Unlimited, append indefinitely

**If these defaults are acceptable, please say "proceed" to begin implementation.**
