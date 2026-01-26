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
3. Authenticate with Copilot SDK as per GitHub's instructions

## License

MIT
