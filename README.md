# logpilot 🪵

<!-- badges: start -->
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-d7ff64.svg)
![Security: ruff](https://img.shields.io/badge/security-ruff%20S-orange)
<!-- badges: end -->

A Python CLI tool for analyzing logs using the GitHub Copilot SDK.

## Features

- Accepts logs from a single file or a directory (combined analysis)
- Supports plain text and JSON log formats
- Uses Copilot SDK for LLM-powered analysis

## Usage (MVP)

```sh
python -m logpilot.cli analyze <path> [OPTIONS]
```

### Arguments

- `<path>`: Path to a log file or directory (any extension)

### Options

- `--version` : Show the current logpilot version and exit
- `--format [auto|json|text]` : Log format (default: auto)
- `--output [text|json]` : Output type (default: text)
- `--max-tokens <int>` : Max tokens per chunk (default: 2048)
- `--out-file <path>` : Write output to file (default: stdout)
- `--recursive` : Recurse into subdirectories (directory mode)
- `--include <glob>` : Glob pattern(s) to include (repeatable)
- `--exclude <glob>` : Glob pattern(s) to exclude (repeatable)

### Example

Summarize a log file and print to terminal:

```sh
python -m logpilot.cli analyze mylog.txt
```

Summarize all logs in a directory (combined analysis):

```sh
python -m logpilot.cli analyze ./logs
```

Summarize logs in a directory recursively with filters:

```sh
python -m logpilot.cli analyze ./logs --recursive --include "*.log" --exclude "archive/*"
```

Summarize a log file and write to a file:

```sh
python -m logpilot.cli analyze mylog.txt --out-file summary.txt
```

## Project Structure

- `logpilot/` - Core modules
- `tests/` - Unit tests

## Requirements

- Python 3.9+
- Typer
- rich
- GitHub Copilot SDK

## Supported Platforms

logpilot works on Windows, macOS, and Linux platforms where Python 3.9+ is available.

## Setup

1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. (Recommended) Install dev dependencies: `pip install -r requirements-dev.txt`
4. Authenticate with Copilot SDK as per GitHub's instructions

## License

MIT
