# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-02-26

### Added

- Initial release of `logpilot`
- `analyze` command to analyze log files and directories using the GitHub Copilot SDK
- Support for plain-text and JSON log formats with `--format auto|json|text`
- Auto-detection of log format when `--format auto` (default)
- Accurate token counting via [tiktoken](https://github.com/openai/tiktoken) (cl100k_base / GPT-4 compatible)
- Character-based token count fallback when tiktoken is unavailable
- Automatic chunking of large logs to stay within the model context window (`--max-tokens`)
- Directory mode: analyze all log files in a directory (with optional `--recursive`)
- Glob filters for directory mode (`--include`, `--exclude`)
- Output to stdout or a file (`--out-file`)
- Output format selection: human-readable text or JSON (`--output text|json`)
- Model selection via `--model` (default: `gpt-4`)
- `--version` flag to display the installed version
- Cross-platform support: Windows, macOS, Linux
- Python 3.9–3.13 compatibility

[Unreleased]: https://github.com/colinmakerofthings/logpilot-cli/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/colinmakerofthings/logpilot-cli/releases/tag/v0.1.0
