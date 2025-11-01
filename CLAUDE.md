# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Package Management and Tooling

This project uses [uv](https://docs.astral.sh/uv/) for all Python tooling and dependency management:

- **Run Python code**: `uv run python <script.py>` (NOT `python` directly - this ensures the environment is set up correctly)
- **Add dependencies**: `uv add <pkg>` (NOT `pip install` - this updates pyproject.toml)
- **Run tests**: `uv run pytest` or `uv run pytest -f` (watch mode)
- **Linting/formatting**: `uv run ruff check` and `uv run ruff format`

The following tools should be installed via `uv tool install`:
- pre-commit (>= v4.3.0)
- cookiecutter (>= v2.6.0)
- ruff (>= v0.12.11)

Python versions 3.10, 3.11, 3.12, and 3.13 should be installed via `uv python install`. This project uses Python 3.12 (specified in `.python-version`).

## Development Commands

- **Run pre-commit**: `pre-commit run --all-files`
- **Update pre-commit hooks**: `pre-commit autoupdate`
- **Switch Python version**: Update `.python-version` then run `uv run python --version`
- **Update project version**: Modify `__init__.py` (currently uses `__version__` variable)

## Project Structure

- this project is going to illustrate many examples of code sample
- for example, the python/asyncio folder will be a standalone project that showcases the ability of asyncio
- each of these folder will contain the following:
    - a main.py that uv can easily run
    - a readme.md that displays the following:
        - important source code with line number
        - output of the program that correlates well with source code line number
        - annotation of output and source code with clear guiding comments referencing source code and output line number

## Pre-commit Hooks

This project uses pre-commit with the following hooks:
- ruff (linting and formatting)
- JSON validation
- YAML validation
- Trailing whitespace removal

The hooks have pre and post logic to validate and activate git, uv, and pre-commit.

## Ruff Configuration

Configuration in `pyproject.toml`:
- Line length: 130 characters
- Import sorting enabled (rule "I")
- Ignores: E203, E266
- Max complexity: 18
