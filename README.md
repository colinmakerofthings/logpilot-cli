# logpilot 🪵

A Python CLI tool for analyzing logs using the GitHub Copilot SDK.

## Features

- Accepts logs from a single file
- Supports plain text and JSON log formats
- Uses Copilot SDK for LLM-powered analysis

## Usage (MVP)

```sh
python -m logpilot.cli analyze <file> [OPTIONS]
```

### Arguments

- `<file>`: Path to a log file (any extension)

### Options

- `--version` : Show the current logpilot version and exit
- `--format [auto|json|text]` : Log format (default: auto)
- `--output [text|json]` : Output type (default: text)
- `--max-tokens <int>` : Max tokens per chunk (default: 2048)
- `--out-file <path>` : Write output to file (default: stdout)

### Example

Summarize a log file and print to terminal:

```sh
python -m logpilot.cli analyze mylog.txt
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

## Setup

1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. (Recommended) Install dev dependencies: `pip install -r requirements-dev.txt`
4. Authenticate with Copilot SDK as per GitHub's instructions

## License

MIT
