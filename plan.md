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

## Development Approach

This project follows **Test-Driven Development (TDD)** principles:
- Write tests FIRST before implementing functionality
- Tests define expected behavior and API contracts
- Implementation follows to satisfy tests
- Refactor with confidence knowing tests will catch regressions

## Technical Implementation Steps

### Step 0: Test Infrastructure Setup
- Set up pytest framework and testing dependencies
- Configure pytest with async support (pytest-asyncio)
- Set up test fixtures for mocking git operations
- Create test directory structure mirroring source code
- Configure coverage reporting (pytest-cov)
- Dependencies: `uv add --dev pytest pytest-asyncio pytest-cov pytest-mock`

### Step 1: Environment Setup
- Use `uv` for dependency management
- Required libraries:
  - **GitPython**: Git operations
  - **PyYAML**: Config and result file parsing/generation
  - **asyncio**: Built-in (Python 3.7+) for parallel operations
  - **openai**: OpenAI API client for AI-generated commit messages and summaries
- Add dependencies: `uv add gitpython pyyaml openai`
- Add dev dependencies: `uv add --dev pytest pytest-asyncio pytest-cov pytest-mock`

### Step 2: Configuration Management (TDD)
**Tests First (`tests/test_config_manager.py`):**
- Test loading valid config.yaml
- Test handling missing config file
- Test validation of repository entries (missing fields, invalid paths)
- Test environment variable substitution (${OPENAI_API_KEY})
- Test default settings when not specified

**Implementation (`config_manager.py`):**
- Create `config.yaml` schema/structure
- Implement config parser and validator
- Validate repository entries (name, local_path, remote_url)
- Handle malformed or missing configuration gracefully

### Step 3: Repository Initialization (TDD)
**Tests First (`tests/test_repo_manager.py`):**
- Test detection of existing repositories
- Test cloning missing repositories (mock git clone)
- Test handling clone failures (network, auth errors)
- Test async parallel cloning of multiple repos
- Test validation of .git directory

**Implementation (`repo_manager.py`):**
- Clone missing repositories: Check if local_path exists
- Perform `git clone <remote_url> <local_path>`
- Handle clone failures (auth issues, network errors)
- Validate existing repositories (verify .git directory)
- Use asyncio to clone multiple repositories in parallel

### Step 4: Git Operations Module (TDD)
**Tests First (`tests/test_git_analyzer.py`):**
- Test fetching remote information (mock git fetch)
- Test parsing local and remote branch lists
- Test identifying tracking relationships
- Test handling repositories with no remotes
- Test async execution of git operations

**Implementation (`git_analyzer.py`):**
- Implement async wrappers for git operations
- Fetch latest remote information - use `git fetch --all`
- Parse branch information (local and remote)
- Compare commits between local and remote branches
- All git operations should be async to enable parallelization

### Step 5: Commit Comparison Logic (TDD)
**Tests First (`tests/test_commit_analyzer.py`):**
- Test identifying commits ahead/behind
- Test extracting commit metadata (hash, author, date, message)
- Test handling branches with no tracking remote
- Test remote-only branches without local equivalents
- Test edge cases (empty repos, initial commits)

**Implementation (`commit_analyzer.py`):**
- Use `git rev-list` or GitPython equivalents
- Identify commit differences (ahead/behind)
- Extract commit metadata (hash, author, date, message)
- Handle all branches (including remote-only branches)

### Step 6: Summary Generator (TDD)
**Tests First (`tests/test_result_generator.py`):**
- Test structuring repository data for YAML
- Test grouping commits by branch
- Test including metadata (timestamp, status)
- Test handling error/warning cases
- Test YAML output format validity

**Implementation (`result_generator.py`):**
- Parse commit messages
- Structure data for YAML output
- Group by repository and branch
- Include metadata (analysis timestamp, repository status)

### Step 7: YAML Result Generation (TDD)
**Tests First (in `tests/test_result_generator.py`):**
- Test complete result.yaml structure
- Test YAML serialization and deserialization
- Test handling special characters in commit messages
- Test error sections for failed operations

**Implementation (in `result_generator.py`):**
- Design result.yaml structure
- Convert analysis data to YAML format
- Write to `result.yaml` file
- Include error/warning sections for failed operations

### Step 8: AI Integration Module (TDD)
**Tests First (`tests/test_ai_integration.py`):**
- Test commit message generation (mock OpenAI API)
- Test pull summary generation
- Test conventional commit format
- Test API error handling (fallback to simple messages)
- Test different API types (OpenAI, Azure, custom)
- Test rate limiting and retries

**Implementation (`ai_integration.py`):**
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

### Step 9: Batch Action Operations (TDD)
**Tests First (`tests/test_batch_operations.py`):**
- Test commit-and-push workflow (mock git operations)
- Test detecting uncommitted changes
- Test handling repositories with no changes
- Test pull operation and change tracking
- Test handling merge conflicts
- Test async parallel execution across repos
- Test per-repository error handling

**Implementation (`batch_operations.py`):**
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

### Step 10: Journal Generation (TDD)
**Tests First (`tests/test_journal_generator.py`):**
- Test journal.md format generation
- Test appending new entries with timestamps
- Test organizing by repository and branch
- Test AI summary integration
- Test handling repos with no changes
- Test markdown formatting correctness

**Implementation (`journal_generator.py`):**
- Format pulled changes per repository/branch
- Generate AI summaries for each pull
- Append to journal.md with timestamps
- Use markdown formatting for readability

### Step 11: Main Controller (TDD)
**Tests First (`tests/test_main_controller.py`):**
- Test async orchestration workflow
- Test error handling (one repo failure doesn't stop others)
- Test config loading → clone → fetch → analyze → output
- Test progress tracking and logging
- Test integration of all modules

**Implementation (in `main.py`):**
- Use `asyncio.gather()` to process multiple repositories in parallel
- Orchestrate: config loading → clone/validate → fetch → analyze → generate output
- Handle errors gracefully (don't let one repo failure stop entire process)
- Implement logging for progress tracking

### Step 12: CLI Interface (TDD)
**Tests First (`tests/test_cli.py`):**
- Test command parsing (status, commit-push, pull, sync)
- Test argument handling (--config, --no-ai)
- Test exit codes for success/failure
- Test console output formatting
- Test command execution flow

**Implementation (in `main.py`):**
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
├── main.py                      # Entry point (CLI commands and async orchestration)
├── config.yaml                  # Repository configuration (user-defined)
├── result.yaml                  # Generated output (analysis results)
├── journal.md                   # Generated pull history with AI summaries
├── config_manager.py            # Config parsing and validation
├── repo_manager.py              # Repository cloning and initialization (async)
├── git_analyzer.py              # Git operations and status analysis (async)
├── commit_analyzer.py           # Commit comparison logic
├── result_generator.py          # YAML output generation
├── ai_integration.py            # OpenAI API wrapper for commit messages and summaries
├── batch_operations.py          # Commit/push/pull operations across all repos (async)
├── journal_generator.py         # Journal.md generation with AI summaries
├── tests/                       # Test suite (TDD approach)
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures and configuration
│   ├── test_config_manager.py   # Tests for config parsing
│   ├── test_repo_manager.py     # Tests for repository initialization
│   ├── test_git_analyzer.py     # Tests for git operations
│   ├── test_commit_analyzer.py  # Tests for commit comparison
│   ├── test_result_generator.py # Tests for YAML generation
│   ├── test_ai_integration.py   # Tests for AI integration (mocked)
│   ├── test_batch_operations.py # Tests for batch commit/push/pull
│   ├── test_journal_generator.py# Tests for journal generation
│   ├── test_main_controller.py  # Tests for main orchestration
│   └── test_cli.py              # Tests for CLI interface
├── pytest.ini                   # Pytest configuration
├── .coveragerc                  # Coverage configuration
├── README.md                    # Documentation with source code and output examples
└── pyproject.toml               # Dependencies (gitpython, pyyaml, openai, pytest, etc.)
```

## TDD Workflow

For each module implementation, follow this cycle:

1. **RED**: Write failing tests first
   - Define the expected behavior
   - Write test cases covering normal and edge cases
   - Run tests - they should fail (no implementation yet)

2. **GREEN**: Write minimal code to pass tests
   - Implement just enough to make tests pass
   - Focus on functionality, not optimization
   - Run tests - they should pass

3. **REFACTOR**: Improve code quality
   - Clean up implementation
   - Remove duplication
   - Optimize performance
   - Run tests - they should still pass

4. **REPEAT**: Move to next feature

### Testing Strategy

**Unit Tests:**
- Test individual functions and classes in isolation
- Mock external dependencies (git operations, API calls, file I/O)
- Fast execution (entire suite should run in seconds)
- High coverage (aim for >90%)

**Integration Tests:**
- Test interactions between modules
- Use test fixtures with temporary directories
- Mock external services but test real file operations
- Verify end-to-end workflows

**Mocking Strategy:**
- Mock all git operations (clone, fetch, push, pull)
- Mock OpenAI API calls with predefined responses
- Mock file system operations where appropriate
- Use pytest-mock for easy mocking

**Fixtures (conftest.py):**
- Sample config.yaml structures
- Mock git repository objects
- Temporary directories for file operations
- Mock API response objects

**Coverage Goals:**
- Minimum 90% code coverage
- 100% coverage for critical paths (config parsing, git operations)
- Run coverage reports with: `uv run pytest --cov=. --cov-report=html`

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
