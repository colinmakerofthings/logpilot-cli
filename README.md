# logpilot

A Python CLI tool for analyzing logs using the GitHub Copilot SDK.

## Features

- Accepts logs from files, directories, or stdin
- Supports plain text and JSON log formats
- Batch processing (no real-time/streaming)
- Uses Copilot SDK for LLM-powered analysis
- Extensible, modular architecture

## Usage (MVP)

```sh
logpilot analyze <file|dir|-> [options]
```

## Project Structure

- `logpilot/` - Core modules
- `tests/` - Unit tests

## Requirements

- Python 3.9+
- Typer
- rich
- GitHub Copilot SDK


## Setup

1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. (Recommended) Install dev dependencies: `pip install -r requirements-dev.txt`
4. Authenticate with Copilot SDK as per GitHub's instructions

## Development

### Linting & Formatting

- Run `ruff .` to lint the codebase.
- Run `black .` to auto-format code (uses tabs).

### Pre-commit Hooks

To automatically lint and format code before each commit:

1. Install pre-commit: `pip install pre-commit`
2. Run `pre-commit install` to enable hooks.
3. Now, ruff and black will run on staged files before every commit.

## License

MIT
