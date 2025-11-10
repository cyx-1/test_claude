# Git Repository Control Program - Implementation Plan

## Overview
A Python program to monitor and manage multiple git repositories on your desktop, tracking synchronization status between local and remote branches.

## Core Features

### 1. Repository Discovery
- Recursively scan desktop directory to find all git repositories
- Identify valid `.git` directories
- Build a list of repository paths

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
- Display repository-by-repository status
- Highlight repositories that need attention
- Show branch-level details for sync status

## Technical Implementation Steps

### Step 1: Environment Setup
- Use `uv` for dependency management
- Required libraries: GitPython (for git operations)
- Add dependencies: `uv add gitpython`

### Step 2: Repository Scanner
- Implement directory traversal function
- Filter for valid git repositories
- Handle permission errors and edge cases

### Step 3: Git Operations Module
- Fetch latest remote information (without pulling)
- Parse branch information (local and remote)
- Compare commits between local and remote branches

### Step 4: Commit Comparison Logic
- Use `git rev-list` or GitPython equivalents
- Identify commit differences (ahead/behind)
- Extract commit metadata

### Step 5: Summary Generator
- Parse commit messages
- Format output in readable structure
- Group by repository and branch

### Step 6: Main Controller
- Orchestrate scanning, analysis, and reporting
- Handle errors gracefully
- Provide progress feedback for large numbers of repositories

### Step 7: CLI Interface
- Accept root directory as input (default to desktop)
- Provide options for filtering/verbosity
- Output formatted results

## Project Structure
```
git_repo_control/
├── main.py                 # Entry point
├── scanner.py             # Repository discovery
├── analyzer.py            # Git operations and status analysis
├── summarizer.py          # Commit summary generation
├── reporter.py            # Output formatting
├── README.md              # Documentation
└── pyproject.toml         # Dependencies
```

## Questions to Clarify

Before proceeding with implementation, please answer the following:

1. **Repository Discovery**:
   - Should the program scan your entire desktop recursively, or would you prefer to provide a specific list of directories?
   - Should it ignore certain directories (e.g., node_modules, venv, hidden folders)?
   - Maximum depth for recursive scanning?

2. **Remote Configuration**:
   - Should the program check all remotes (origin, upstream, etc.) or just `origin`?
   - How should it handle repositories with no remotes configured?

3. **Output Format**:
   - Do you want a CLI text output, or would you prefer JSON/CSV for further processing?
   - Should results be saved to a file, or just displayed?
   - Do you want color-coded output for better readability?

4. **Authentication & Network**:
   - Should the program handle authentication for private repositories?
   - How should network failures be handled (retry, skip, error out)?
   - Should it perform `git fetch` automatically, or assume repos are already fetched?

5. **Performance**:
   - Do you expect to scan many repositories (>50)? Should operations be parallelized?
   - Should there be a progress indicator?

6. **Actions vs Reporting**:
   - Is this purely a reporting tool, or should it offer actions like "pull all" or "push all"?
   - Should it have an interactive mode to select repositories for action?

7. **Edge Cases**:
   - How should it handle:
     - Detached HEAD states?
     - Repositories with merge conflicts?
     - Submodules?
     - Bare repositories?

8. **Commit Summary Detail**:
   - For the commit summaries, what level of detail do you want?
     - Just count and first line of commit message?
     - Full commit message?
     - Include author and date?
   - Should summaries be grouped by date, author, or just listed chronologically?

Please review these questions and let me know your preferences so I can refine the plan accordingly.
