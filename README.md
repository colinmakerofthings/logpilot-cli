# logpilot 🪵

<!-- badges: start -->
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)
![Linter: ruff](https://img.shields.io/badge/linter-ruff-d7ff64.svg)
![Security: ruff](https://img.shields.io/badge/security-ruff%20S-orange)
<!-- badges: end -->

A Python CLI tool for analyzing logs using the GitHub Copilot SDK.

## Features

- Accepts logs from a single file or a directory (combined analysis)
- Supports plain text and JSON log formats
- Accurate token counting via [tiktoken](https://github.com/openai/tiktoken) (cl100k_base / GPT-4 compatible), with a character-based fallback
- Large logs chunked automatically to stay within the model's context window
- Uses Copilot SDK for LLM-powered analysis

## Usage (MVP)

```sh
python -m logpilot.cli [--version] analyze <path> [OPTIONS]
```

### Global Options

- `--version` : Show the current logpilot version and exit

### Arguments

- `<path>`: Path to a log file or directory (any extension)

### Options

- `--format [auto|json|text]` : Log format (default: auto)
- `--output [text|json]` : Output type (default: text)
- `--max-tokens <int>` : Max tokens per chunk (default: 2048). Token counts are measured using tiktoken (cl100k_base encoding). Increase this value for larger context windows or decrease it to stay within tighter model limits.
- `--out-file <path>` : Write output to file (default: stdout)
- `--recursive` : Recurse into subdirectories (directory mode)
- `--include <glob>` : Glob pattern(s) to include (repeatable)
- `--exclude <glob>` : Glob pattern(s) to exclude (repeatable)
- `--model <model>` : LLM model to use (default: gpt-4)

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

Analyze logs with a different model:

```sh
python -m logpilot.cli analyze mylog.txt --model gpt-3.5-turbo
```

## Project Structure

- `logpilot/` - Core modules
- `tests/` - Unit tests

## Requirements

- Python 3.9+
- [Typer](https://typer.tiangolo.com/) — CLI framework
- [rich](https://github.com/Textualize/rich) — terminal output formatting
- [tiktoken](https://github.com/openai/tiktoken) — accurate token counting (cl100k_base)
- [tqdm](https://github.com/tqdm/tqdm) — progress bars
- [orjson](https://github.com/ijl/orjson) — fast JSON parsing
- [toml](https://github.com/uiri/toml) — TOML config parsing (Python < 3.11 fallback)
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
