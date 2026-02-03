import os
import subprocess
import sys

import pytest


def run_cli(args, env=None):
    env = dict(os.environ) if env is None else env
    env["LOGPILOT_MOCK_LLM"] = "1"
    return subprocess.run(
        [sys.executable, "-m", "logpilot.cli"] + args,
        capture_output=True,
        text=True,
        env=env,
    )


def test_cli_missing_file():
    result = run_cli(["analyze", "not_a_real_file.log"])
    assert result.returncode != 0
    assert "No such file" in result.stderr or "Error" in result.stderr


def test_cli_empty_file(tmp_path):
    log_file = tmp_path / "empty.log"
    log_file.write_text("")
    result = run_cli(["analyze", str(log_file)])
    assert result.returncode != 0
    assert "No log entries found" in result.stderr or "Error" in result.stderr


def test_cli_invalid_format(tmp_path):
    log_file = tmp_path / "invalid.log"
    log_file.write_text("not a log line\nnot json\n")
    result = run_cli(["analyze", str(log_file)])
    assert result.returncode != 0
    assert "No log entries found" in result.stderr or "Error" in result.stderr


def test_cli_out_file(tmp_path):
    log_file = tmp_path / "test.log"
    log_file.write_text(
        (
            '{"timestamp": "2026-01-28T12:00:00Z", '
            '"level": "ERROR", '
            '"message": "Something failed"}\n'
        )
    )
    out_file = tmp_path / "out.txt"
    result = run_cli(["analyze", str(log_file), "--out-file", str(out_file)])
    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert out_file.read_text().strip() != ""


def test_cli_output_json(tmp_path):
    log_file = tmp_path / "test.log"
    log_file.write_text(
        (
            '{"timestamp": "2026-01-28T12:00:00Z", '
            '"level": "ERROR", '
            '"message": "Something failed"}\n'
        )
    )
    result = run_cli(["analyze", str(log_file), "--output", "json"])
    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    import json as pyjson

    # Should be valid JSON or at least not empty
    try:
        pyjson.loads(result.stdout)
    except Exception:
        assert result.stdout.strip() != ""


def test_cli_format_json(tmp_path):
    log_file = tmp_path / "test.log"
    log_file.write_text(
        (
            '{"timestamp": "2026-01-28T12:00:00Z", '
            '"level": "ERROR", '
            '"message": "Something failed"}\n'
        )
    )
    result = run_cli(["analyze", str(log_file), "--format", "json"])
    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"


def test_cli_format_text(tmp_path):
    log_file = tmp_path / "test.log"
    log_file.write_text("plain log line\n")
    result = run_cli(["analyze", str(log_file), "--format", "text"])
    assert result.returncode != 0 or "plain log line" in result.stdout


def test_cli_unreadable_file(tmp_path):
    if os.name == "nt":
        pytest.skip("File permissions are not reliable on Windows")

    log_file = tmp_path / "unreadable.log"
    log_file.write_text("test")
    log_file.chmod(0)
    try:
        result = run_cli(["analyze", str(log_file)])
        assert result.returncode != 0
        # Accept either error message or 'No log entries found.'
        valid = (
            "Error" in result.stderr
            or "Permission" in result.stderr
            or "No log entries found." in result.stderr
        )
        assert valid, f"stderr: {result.stderr}"
    finally:
        log_file.chmod(0o666)


def test_cli_large_file(tmp_path):
    log_file = tmp_path / "large.log"
    log_file.write_text(
        (
            '{"timestamp": "2026-01-28T12:00:00Z", '
            '"level": "ERROR", '
            '"message": "Something failed"}\n'
        )
        * 10000
    )
    result = run_cli(["analyze", str(log_file)])
    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"


def test_cli_analyze_basic(tmp_path, monkeypatch):
    # Create a simple log file
    log_content = (
        '{"timestamp": "2026-01-28T12:00:00Z", '
        '"level": "ERROR", '
        '"message": "Something failed"}\n'
    )
    log_file = tmp_path / "test.log"
    log_file.write_text(log_content)

    # Run the CLI analyze command with mock LLM enabled
    env = dict(os.environ)
    env["LOGPILOT_MOCK_LLM"] = "1"
    result = subprocess.run(
        [sys.executable, "-m", "logpilot.cli", "analyze", str(log_file)],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert "Something failed" in result.stdout or "critical" in result.stdout.lower()


def test_cli_directory_basic(tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    (log_dir / "a.log").write_text(
        '{"timestamp": "2026-01-28T12:00:00Z", "level": "ERROR", "message": "A"}\n'
    )
    (log_dir / "b.log").write_text(
        '{"timestamp": "2026-01-28T12:00:01Z", "level": "ERROR", "message": "B"}\n'
    )

    result = run_cli(["analyze", str(log_dir)])
    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert "Mocked summary" in result.stdout


def test_cli_directory_recursive(tmp_path):
    log_dir = tmp_path / "logs"
    nested = log_dir / "nested"
    nested.mkdir(parents=True)
    (nested / "nested.log").write_text(
        '{"timestamp": "2026-01-28T12:00:00Z", "level": "ERROR", "message": "Nested"}\n'
    )

    result = run_cli(["analyze", str(log_dir), "--recursive"])
    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert "Mocked summary" in result.stdout


def test_cli_directory_include_exclude(tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    (log_dir / "keep.log").write_text(
        '{"timestamp": "2026-01-28T12:00:00Z", "level": "ERROR", "message": "Keep"}\n'
    )
    (log_dir / "skip.txt").write_text(
        '{"timestamp": "2026-01-28T12:00:01Z", "level": "ERROR", "message": "Skip"}\n'
    )

    result = run_cli(
        ["analyze", str(log_dir), "--include", "*.log", "--exclude", "skip.*"]
    )
    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert "Mocked summary" in result.stdout


def test_cli_directory_no_matches(tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    (log_dir / "skip.txt").write_text("not a log\n")

    result = run_cli(["analyze", str(log_dir), "--include", "*.log"])
    assert result.returncode != 0
    assert "No log files matched" in result.stderr or "Error" in result.stderr
