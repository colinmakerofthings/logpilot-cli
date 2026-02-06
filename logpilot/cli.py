import os
from typing import List, Optional

import typer

try:
    import tomllib
except ImportError:
    import toml as tomllib

from logpilot.chunker import chunk_logs
from logpilot.input_manager import iter_log_files, read_logs_from_paths
from logpilot.llm_client import LLMClient
from logpilot.log_parser import parse_logs
from logpilot.postprocessor import aggregate_responses
from logpilot.prompt_engine import format_prompt


def get_version() -> str:
    pyproject_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "pyproject.toml"
    )
    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        version = data.get("project", {}).get("version")
        if version:
            return version
    except Exception:
        pass
    return "unknown"


def version_callback(value: bool):
    if value:
        typer.echo(f"logpilot version {get_version()}")
        raise typer.Exit()


app = typer.Typer(no_args_is_help=True)


@app.command()
def analyze(
    path: str = typer.Argument(..., help="Path to log file or directory"),
    format: str = typer.Option("auto", help="Log format: auto, json, text"),
    output: str = typer.Option("text", help="Output type: text or json"),
    max_tokens: int = typer.Option(2048, help="Max tokens per chunk"),
    out_file: str = typer.Option(None, help="Output file path (default: stdout)"),
    recursive: bool = typer.Option(False, help="Recurse into directories"),
    include: Optional[List[str]] = typer.Option(
        None,
        "--include",
        help="Glob pattern(s) to include (repeatable).",
    ),
    exclude: Optional[List[str]] = typer.Option(
        None,
        "--exclude",
        help="Glob pattern(s) to exclude (repeatable).",
    ),
    model: str = typer.Option("gpt-4", help="LLM model to use (default: gpt-4)"),
):
    """Analyze logs using Copilot SDK."""
    import os

    if path == "-":
        typer.echo("Error: stdin is not supported.\n", err=True)
        typer.echo(analyze.get_help(typer.Context(analyze)))
        raise typer.Exit(1)

    # 1. Read log lines
    try:
        paths = list(
            iter_log_files(
                path,
                recursive=recursive,
                include=include,
                exclude=exclude,
            )
        )
        if not paths:
            typer.echo(f"No log files matched: {path}", err=True)
            raise typer.Exit(1)

        lines = [line for line in read_logs_from_paths(paths)]
    except PermissionError as e:
        typer.echo(f"Error: Permission denied reading log file: {e}", err=True)
        raise typer.Exit(1)
    except FileNotFoundError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error reading log file: {e}", err=True)
        raise typer.Exit(1)

    # 2. Parse log lines
    entries = list(parse_logs(iter(lines), fmt=format))
    if not entries:
        typer.echo("No log entries found.", err=True)
        raise typer.Exit(1)

    # 3. Chunk logs
    chunks = chunk_logs(entries, max_tokens)
    typer.echo("Analyzing logs...")

    # 4. Format prompts
    prompts = [format_prompt(chunk) for chunk in chunks]

    # 5. Query LLM (mock if env var set)
    if os.environ.get("LOGPILOT_MOCK_LLM") == "1":
        responses = ["Mocked summary: Something failed" for _ in prompts]
    else:
        llm = LLMClient(model=model)
        responses = [llm.analyze(prompt) for prompt in prompts]

    # 6. Aggregate responses
    summary = aggregate_responses(responses)

    # 7. Output
    if out_file:
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(summary)
    else:
        typer.echo(summary)


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        help="Show the version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
):
    """
    Logpilot CLI

    USAGE:
      python -m logpilot.cli analyze <file> [OPTIONS]

    Note: You must specify the 'analyze' subcommand before the log file path.
    """
    pass


if __name__ == "__main__":
    app()
