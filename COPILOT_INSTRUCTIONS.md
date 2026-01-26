# Copilot Instructions

## Coding Style

- Use tabs for indentation.
- Use snake_case for variables and functions, PascalCase for classes.
- Always include type hints.
- Prefer small, composable functions.
- Write concise comments for non-obvious logic.

## CLI & UX Principles

- CLI-first project: prioritize clear, human-readable output.
- Error messages must be actionable and never silent.
- Respect stdin/stdout conventions and Unix-style piping.
- Avoid printing debug information unless explicitly requested.

## Log Processing Rules

- Assume logs may be very large (GB-scale).
- Prefer batch processing (no real-time/streaming).
- Avoid loading entire files into memory.
- Parsing must be resilient to malformed or partial log lines.

## LLM / Copilot Usage

- Treat all LLM responses as untrusted input.
- Keep prompt templates separate from business logic.
- Prompts should be deterministic, structured, and explicit.
- Never hardcode credentials, tokens, or secrets.
- Use the official GitHub Copilot SDK for LLM access.
- Authentication must follow GitHub Copilot SDK’s official method (env vars or CLI login).

## Project Conventions

- Follow the existing folder and file structure.
- Use the approved libraries and frameworks only.
- Isolate Copilot/LLM calls behind a thin abstraction layer.

## Testing

- Core logic (parsing, chunking, aggregation) must be unit-tested.
- Mock all Copilot/LLM interactions in tests.
- Tests must not require network access.

## What to Avoid

- Do not use deprecated APIs or libraries.
- Avoid placeholder code unless explicitly requested.
- Do not introduce unnecessary abstractions.
