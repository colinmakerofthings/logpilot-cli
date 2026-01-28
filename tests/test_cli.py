import subprocess
import sys


def test_cli_shows_help():
    # Run the CLI with '--help' and check output
    result = subprocess.run(
        [sys.executable, "-m", "logpilot.cli", "--help"], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "Usage:" in result.stdout or "usage:" in result.stdout


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
    import os

    env = dict(os.environ)
    env["LOGPILOT_MOCK_LLM"] = "1"
    result = subprocess.run(
        [sys.executable, "-m", "logpilot.cli", str(log_file)],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert "Something failed" in result.stdout or "critical" in result.stdout.lower()
