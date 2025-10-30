# test_claude

A demonstration project combining Python development best practices with a Three.js 3D visualization.

## Project Overview

**Version:** 1.0.0.0

This project contains two main components:

1. **Python Application** (`main.py`)
   - Simple command-line application with structured logging
   - Demonstrates logging configuration with custom formatting
   - Includes version tracking via `__init__.py`
   - Entry point that prints "hello" and logs program startup

2. **Three.js 3D Planet Visualization** (`planet.html`, `planet.js`)
   - Interactive 3D rotating planet with realistic features:
     - Procedurally generated continents and oceans
     - Polar ice caps with gradient effects
     - Atmospheric glow effect around the planet
     - Starfield background with 10,000+ stars
     - Dynamic lighting with ambient, directional, and rim lights
   - Responsive canvas that adapts to window resizing
   - Open `planet.html` in a browser to view the visualization

## Project Structure

```
test_claude/
├── main.py              # Main Python application with logging
├── planet.html          # HTML page for 3D planet visualization
├── planet.js            # Three.js implementation of rotating planet
├── test_1.py            # Pytest test suite
├── __init__.py          # Package initialization with version info
├── pyproject.toml       # Project configuration and dependencies
├── uv.lock              # Locked dependency versions
└── README.md            # This file
```

## Dependencies

### Python Dependencies
- **pytest** - Testing framework
- **pytest-xdist** - Parallel test execution

### JavaScript Dependencies
- **Three.js r128** - 3D graphics library (loaded via CDN)

## Development Environment Setup

- this project uses [uv](https://cyx-1.github.io/notes_technology/uv.html) extensively to manage tools, libraries, and python version
- the following tools should be already installed via ```uv tool install``` with versions greater or equal to:
    - [pre-commit v4.3.0](https://cyx-1.github.io/notes_technology/pre-commit.html)
    - [cookiecutter v2.6.0](https://cyx-1.github.io/notes_technology/cookiecutter.html)
    - [ruff v0.12.11](https://cyx-1.github.io/notes_technology/ruff.html)
- python should be already installed via ```uv python install 3.10, 3.11, 3.12, 3.13```
- this project's [pre-commit](https://cyx-1.github.io/notes_technology/pre-commit.html) uses: ruff, json, yaml, trailing-white-spaces
    - pre-commit has pre and post hook logic to validate and activate git, uv, pre-commit and so on
- this project uses python version: 3.12

## Running the Project

### Python Application
```bash
# Run the main Python application
uv run python main.py
```

### Three.js Visualization
Simply open `planet.html` in your web browser to view the 3D planet animation.

### Running Tests
```bash
# Run all tests
uv run pytest

# Run tests with file watching (auto-rerun on changes)
uv run pytest -f
```

## Useful Commands

### Code Quality
- To run pre-commit explicitly: ```pre-commit run --all-files```
- To run ruff explicitly: ```uv run ruff check``` and ```uv run ruff format```

### Dependency Management
- To use uv to add library dependencies: ```uv add <pkg>```
- To update pre-commit packages: ```pre-commit autoupdate```

### Version Management
- To update project version, modify ```__init__.py```
- To switch to a different python version, update ```.python-version``` then run ```uv run python --version```

# TODO
- add ability to turn into a package and deal with version information via setup.cfg