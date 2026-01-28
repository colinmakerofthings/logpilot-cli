import subprocess
import sys


def test_cli_shows_help():
    # Run the CLI with '--help' and check output
    result = subprocess.run(
        [sys.executable, "-m", "logpilot.cli", "--help"], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "Usage:" in result.stdout or "usage:" in result.stdout
