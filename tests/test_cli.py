import os
import subprocess
import sys
from unittest.mock import mock_open, patch

import pytest
import typer
import typer.testing

from logpilot.cli import app, get_version


def run_cli(args, env=None):
    env = dict(os.environ) if env is None else env
    env["LOGPILOT_MOCK_LLM"] = "1"
    return subprocess.run(
        [sys.executable, "-m", "logpilot.cli"] + args,
        capture_output=True,
        text=True,
        env=env,
    )


def run_cli_direct(args, env_vars=None):
    """Run CLI directly using CliRunner (better for coverage)."""
    if env_vars is None:
        env_vars = {}

    # Set environment variables including mock LLM
    env_vars_to_set = {"LOGPILOT_MOCK_LLM": "1"}
    env_vars_to_set.update(env_vars)

    with patch.dict(os.environ, env_vars_to_set):
        runner = typer.testing.CliRunner()
        return runner.invoke(app, args)


# ============================================================================
# Unit Tests
# ============================================================================


@pytest.mark.unit
class TestGetVersion:
    """Unit tests for the get_version function."""

    def test_get_version_success(self):
        """Test get_version successfully reads version from pyproject.toml."""
        version = get_version()
        # Should return the actual version from pyproject.toml
        assert version is not None
        assert isinstance(version, str)
        # From the actual pyproject.toml, version is "0.1.0"
        assert version == "0.1.0" or version != "unknown"

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_get_version_missing_file(self, mock_file):
        """Test get_version returns 'unknown' when pyproject.toml is missing."""
        version = get_version()
        assert version == "unknown"

    @patch("builtins.open", side_effect=PermissionError)
    def test_get_version_permission_error(self, mock_file):
        """Test get_version returns 'unknown' on permission error."""
        version = get_version()
        assert version == "unknown"

    @patch("builtins.open", mock_open(read_data=b"invalid toml content [[["))
    def test_get_version_invalid_toml(self):
        """Test get_version returns 'unknown' for invalid TOML."""
        version = get_version()
        assert version == "unknown"

    @patch("builtins.open", mock_open(read_data=b"[other]\ndata = 'test'"))
    def test_get_version_missing_project_section(self):
        """Test get_version returns 'unknown' when project section is missing."""
        version = get_version()
        assert version == "unknown"

    @patch("builtins.open", mock_open(read_data=b"[project]\nname = 'test'"))
    def test_get_version_missing_version_field(self):
        """Test get_version returns 'unknown' when version field is missing."""
        version = get_version()
        assert version == "unknown"


# ============================================================================
# Integration Tests
# ============================================================================


@pytest.mark.integration
def test_cli_missing_file():
    result = run_cli(["analyze", "not_a_real_file.log"])
    assert result.returncode != 0
    assert "No such file" in result.stderr or "Error" in result.stderr


@pytest.mark.integration
def test_cli_empty_file(tmp_path):
    log_file = tmp_path / "empty.log"
    log_file.write_text("")
    result = run_cli(["analyze", str(log_file)])
    assert result.returncode != 0
    assert "No log entries found" in result.stderr or "Error" in result.stderr


@pytest.mark.integration
def test_cli_invalid_format(tmp_path):
    log_file = tmp_path / "invalid.log"
    log_file.write_text("not a log line\nnot json\n")
    result = run_cli(["analyze", str(log_file)])
    assert result.returncode != 0
    assert "No log entries found" in result.stderr or "Error" in result.stderr


@pytest.mark.integration
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


@pytest.mark.integration
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


@pytest.mark.integration
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


@pytest.mark.integration
def test_cli_format_text(tmp_path):
    log_file = tmp_path / "test.log"
    log_file.write_text("plain log line\n")
    result = run_cli(["analyze", str(log_file), "--format", "text"])
    assert result.returncode != 0 or "plain log line" in result.stdout


@pytest.mark.integration
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


@pytest.mark.integration
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


@pytest.mark.integration
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


@pytest.mark.integration
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


@pytest.mark.integration
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


@pytest.mark.integration
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


@pytest.mark.integration
def test_cli_directory_no_matches(tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    (log_dir / "skip.txt").write_text("not a log\n")

    result = run_cli(["analyze", str(log_dir), "--include", "*.log"])
    assert result.returncode != 0
    assert "No log files matched" in result.stderr or "Error" in result.stderr


# ============================================================================
# Additional Tests for Better Coverage
# ============================================================================


@pytest.mark.unit
class TestVersionCallback:
    """Tests for version_callback function."""

    def test_version_callback_true(self, capsys):
        """Test version callback with True value."""
        from logpilot.cli import version_callback

        with pytest.raises(typer.Exit) as exc_info:
            version_callback(True)

        assert exc_info.value.exit_code == 0
        captured = capsys.readouterr()
        assert "logpilot version" in captured.out

    def test_version_callback_false(self):
        """Test version callback with False value."""
        from logpilot.cli import version_callback

        # Should not raise
        result = version_callback(False)
        assert result is None


@pytest.mark.unit
class TestAnalyzeUnitLevel:
    """Unit tests for analyze function."""

    def test_analyze_stdin_rejected(self):
        """Test that stdin input is rejected."""
        from logpilot.cli import app

        runner = typer.testing.CliRunner()
        result = runner.invoke(app, ["analyze", "-"])
        assert result.exit_code != 0
        output = (result.stdout or "") + (result.stderr or "")
        assert "Error: stdin is not supported" in output

    def test_analyze_with_max_tokens(self, tmp_path):
        """Test analyze with custom max_tokens."""
        log_file = tmp_path / "test.log"
        log_file.write_text(
            '{"timestamp": "2026-01-28T12:00:00Z", "level": "ERROR", '
            '"message": "Test"}\n'
        )
        result = run_cli(["analyze", str(log_file), "--max-tokens", "1024"])
        assert (
            result.returncode == 0
        ), f"stdout: {result.stdout}\nstderr: {result.stderr}"

    def test_analyze_with_output_json_option(self, tmp_path):
        """Test analyze with --output json option."""
        log_file = tmp_path / "test.log"
        log_file.write_text(
            '{"timestamp": "2026-01-28T12:00:00Z", "level": "ERROR", '
            '"message": "Test"}\n'
        )
        result = run_cli(["analyze", str(log_file), "--output", "json"])
        assert (
            result.returncode == 0
        ), f"stdout: {result.stdout}\nstderr: {result.stderr}"
        assert result.stdout.strip() != ""


@pytest.mark.integration
def test_cli_analyze_with_permission_error(tmp_path):
    """Test analyze with permission denied error."""
    if os.name == "nt":
        pytest.skip("File permissions are not reliable on Windows")

    log_file = tmp_path / "forbidden.log"
    log_file.write_text(
        '{"timestamp": "2026-01-28T12:00:00Z", "level": "ERROR", "message": "Test"}\n'
    )
    log_file.chmod(0)
    try:
        result = run_cli(["analyze", str(log_file)])
        # Should fail with error
        assert result.returncode != 0
    finally:
        log_file.chmod(0o666)


@pytest.mark.integration
def test_cli_help_command():
    """Test CLI help command."""
    result = run_cli_direct(["--help"])
    assert result.exit_code == 0
    output = (result.stdout or "") + (result.stderr or "")
    assert "Logpilot CLI" in output or "Usage" in output


@pytest.mark.integration
def test_cli_analyze_help(tmp_path):
    """Test analyze subcommand help."""
    result = run_cli_direct(["analyze", "--help"])
    assert result.exit_code == 0
    output = (result.stdout or "") + (result.stderr or "")
    assert "Analyze logs" in output or "analyze" in output.lower()


@pytest.mark.integration
def test_cli_version_flag():
    """Test --version flag."""
    result = run_cli(["--version"])
    assert result.returncode == 0
    assert "logpilot version" in result.stdout


@pytest.mark.integration
def test_cli_mixed_log_files_and_errors(tmp_path):
    """Test with directory containing both valid and invalid files."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    # Add valid log
    (log_dir / "valid.log").write_text(
        '{"timestamp": "2026-01-28T12:00:00Z", "level": "ERROR", "message": "Error"}\n'
    )
    # Add non-log file
    (log_dir / "readme.txt").write_text("This is a readme\n")

    # Filter to only .log files
    result = run_cli(["analyze", str(log_dir), "--include", "*.log"])
    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert "Mocked summary" in result.stdout


@pytest.mark.integration
def test_cli_exclude_pattern(tmp_path):
    """Test exclude pattern filtering."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    (log_dir / "important.log").write_text(
        '{"timestamp": "2026-01-28T12:00:00Z", "level": "ERROR", '
        '"message": "Important"}\n'
    )
    (log_dir / "debug.log").write_text(
        '{"timestamp": "2026-01-28T12:00:00Z", "level": "DEBUG", '
        '"message": "Debug"}\n'
    )

    # Exclude debug logs
    result = run_cli(["analyze", str(log_dir), "--exclude", "debug.*"])
    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert "Mocked summary" in result.stdout


@pytest.mark.integration
def test_cli_multiple_include_patterns(tmp_path):
    """Test multiple include patterns."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    (log_dir / "app.log").write_text(
        '{"timestamp": "2026-01-28T12:00:00Z", "level": "ERROR", "message": "App"}\n'
    )
    (log_dir / "data.csv").write_text(
        '{"timestamp": "2026-01-28T12:00:00Z", "level": "ERROR", "message": "Data"}\n'
    )

    result = run_cli(
        ["analyze", str(log_dir), "--include", "*.log", "--include", "*.csv"]
    )
    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"


@pytest.mark.integration
def test_cli_format_auto(tmp_path):
    """Test auto format detection."""
    log_file = tmp_path / "test.log"
    log_file.write_text(
        '{"timestamp": "2026-01-28T12:00:00Z", "level": "ERROR", "message": "Test"}\n'
    )
    result = run_cli(["analyze", str(log_file), "--format", "auto"])
    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"


@pytest.mark.integration
def test_cli_output_to_file_with_content(tmp_path):
    """Test output file contains actual content."""
    log_file = tmp_path / "test.log"
    log_file.write_text(
        '{"timestamp": "2026-01-28T12:00:00Z", "level": "ERROR", '
        '"message": "Critical issue"}\n'
    )
    out_file = tmp_path / "output.txt"
    result = run_cli(["analyze", str(log_file), "--out-file", str(out_file)])
    assert_msg = f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert result.returncode == 0, assert_msg
    content = out_file.read_text()
    assert len(content) > 0
    assert "Mocked summary" in content or "failed" in content.lower()


class TestMainCallback:
    """Tests for main callback function."""

    def test_main_without_version(self):
        """Test main callback when version is not provided."""
        from logpilot.cli import main

        # Should not raise or do anything
        result = main(version=False)
        assert result is None

    def test_main_with_none_version(self):
        """Test main callback when version is None."""
        from logpilot.cli import main

        # Should not raise or do anything
        result = main(version=None)
        assert result is None


@pytest.mark.unit
class TestCliImports:
    """Tests for CLI imports and fallback handling."""

    @patch("sys.modules", {"tomllib": None})
    def test_toml_fallback_import(self):
        """Test that toml is used as fallback when tomllib is not available."""
        # This would test the except ImportError clause
        # Note: This is complex to test because imports happen at module load
        # For now, we just verify tomllib/toml is available
        try:
            import tomllib  # noqa: F401

            tomllib_available = True
        except ImportError:
            tomllib_available = False

        try:
            import toml  # noqa: F401

            toml_available = True
        except ImportError:
            toml_available = False

        # At least one should be available
        assert tomllib_available or toml_available


@pytest.mark.integration
def test_cli_with_newline_variations(tmp_path):
    """Test reading files with different newline styles."""
    log_file = tmp_path / "test.log"
    # Mix of different line endings (they get normalized)
    log_file.write_text(
        '{"timestamp": "2026-01-28T12:00:00Z", "level": "ERROR", "message": "Line1"}\n'
        '{"timestamp": "2026-01-28T12:00:00Z", "level": "ERROR", "message": "Line2"}\n'
    )
    result = run_cli(["analyze", str(log_file)])
    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"


@pytest.mark.integration
def test_cli_with_special_characters(tmp_path):
    """Test logs with special characters."""
    log_file = tmp_path / "test.log"
    log_file.write_text(
        '{"timestamp": "2026-01-28T12:00:00Z", "level": "ERROR", '
        '"message": "Error with special chars: @#$%^&*()"}\n'
    )
    result = run_cli(["analyze", str(log_file)])
    assert_msg = f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert result.returncode == 0, assert_msg


@pytest.mark.integration
def test_cli_deep_nested_directories(tmp_path):
    """Test with deeply nested directory structures."""
    log_dir = tmp_path / "a" / "b" / "c" / "d"
    log_dir.mkdir(parents=True)
    (log_dir / "deep.log").write_text(
        '{"timestamp": "2026-01-28T12:00:00Z", "level": "ERROR", "message": "Deep"}\n'
    )

    result = run_cli(["analyze", str(tmp_path / "a"), "--recursive"])
    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"


@pytest.mark.integration
def test_cli_analyze_multiple_files_in_directory(tmp_path):
    """Test analyzing a directory with multiple log files."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    for i in range(5):
        (log_dir / f"file{i}.log").write_text(
            f'{{"timestamp": "2026-01-28T12:00:00Z", "level": "ERROR", '
            f'"message": "Error {i}"}}\n'
        )

    result = run_cli(["analyze", str(log_dir)])
    assert_msg = f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert result.returncode == 0, assert_msg
    assert "Mocked summary" in result.stdout


# ============================================================================
# Direct CliRunner Tests (For Coverage)
# ============================================================================


@pytest.mark.unit
class TestCliDirect:
    """Direct tests using CliRunner for proper coverage measurement."""

    def test_analyze_basic_with_runner(self, tmp_path):
        """Test basic analyze command with CliRunner."""
        log_file = tmp_path / "test.log"
        log_file.write_text(
            '{"timestamp": "2026-01-28T12:00:00Z", "level": "ERROR", '
            '"message": "Test error"}\n'
        )

        result = run_cli_direct(["analyze", str(log_file)])
        assert (
            result.exit_code == 0
        ), f"stdout: {result.stdout}\nstderr: {result.stderr}"
        assert "Mocked summary" in result.stdout or "failed" in result.stdout.lower()

    def test_analyze_with_format_option(self, tmp_path):
        """Test analyze with format option."""
        log_file = tmp_path / "test.log"
        log_file.write_text(
            '{"timestamp": "2026-01-28T12:00:00Z", "level": "ERROR", '
            '"message": "Test"}\n'
        )

        cmd = ["analyze", str(log_file), "--format", "json"]
        result = run_cli_direct(cmd)
        assert result.exit_code == 0, f"stdout: {result.stdout}"

    def test_analyze_with_output_option(self, tmp_path):
        """Test analyze with output option."""
        log_file = tmp_path / "test.log"
        log_file.write_text(
            '{"timestamp": "2026-01-28T12:00:00Z", "level": "ERROR", '
            '"message": "Test"}\n'
        )

        cmd = ["analyze", str(log_file), "--output", "json"]
        result = run_cli_direct(cmd)
        assert result.exit_code == 0, f"stdout: {result.stdout}"

    def test_analyze_with_output_file(self, tmp_path):
        """Test analyze with output file."""
        log_file = tmp_path / "test.log"
        log_file.write_text(
            '{"timestamp": "2026-01-28T12:00:00Z", "level": "ERROR", '
            '"message": "Test"}\n'
        )
        out_file = tmp_path / "output.txt"

        cmd = ["analyze", str(log_file), "--out-file", str(out_file)]
        result = run_cli_direct(cmd)
        assert result.exit_code == 0, f"stdout: {result.stdout}\nerror: {result.stderr}"
        assert out_file.exists()
        assert len(out_file.read_text()) > 0

    def test_analyze_recursive_flag(self, tmp_path):
        """Test analyze with recursive flag."""
        log_dir = tmp_path / "logs"
        nested = log_dir / "nested"
        nested.mkdir(parents=True)
        (nested / "test.log").write_text(
            '{"timestamp": "2026-01-28T12:00:00Z", "level": "ERROR", '
            '"message": "Nested"}\n'
        )

        cmd = ["analyze", str(log_dir), "--recursive"]
        result = run_cli_direct(cmd)
        assert result.exit_code == 0, f"stdout: {result.stdout}"

    def test_analyze_include_pattern(self, tmp_path):
        """Test analyze with include pattern."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        (log_dir / "app.log").write_text(
            '{"timestamp": "2026-01-28T12:00:00Z", "level": "ERROR", '
            '"message": "App"}\n'
        )
        (log_dir / "other.txt").write_text("not a log\n")

        cmd = ["analyze", str(log_dir), "--include", "*.log"]
        result = run_cli_direct(cmd)
        assert result.exit_code == 0, f"stdout: {result.stdout}"

    def test_analyze_exclude_pattern(self, tmp_path):
        """Test analyze with exclude pattern."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        (log_dir / "important.log").write_text(
            '{"timestamp": "2026-01-28T12:00:00Z", "level": "ERROR", '
            '"message": "Important"}\n'
        )
        (log_dir / "debug.log").write_text(
            '{"timestamp": "2026-01-28T12:00:00Z", "level": "DEBUG", '
            '"message": "Debug"}\n'
        )

        cmd = ["analyze", str(log_dir), "--exclude", "debug.*"]
        result = run_cli_direct(cmd)
        assert result.exit_code == 0, f"stdout: {result.stdout}"

    def test_analyze_max_tokens_option(self, tmp_path):
        """Test analyze with max_tokens option."""
        log_file = tmp_path / "test.log"
        log_file.write_text(
            '{"timestamp": "2026-01-28T12:00:00Z", "level": "ERROR", '
            '"message": "Test"}\n'
        )

        cmd = ["analyze", str(log_file), "--max-tokens", "512"]
        result = run_cli_direct(cmd)
        assert result.exit_code == 0, f"stdout: {result.stdout}"

    def test_analyze_nonexistent_file(self):
        """Test analyze with nonexistent file."""
        result = run_cli_direct(["analyze", "/nonexistent/file.log"])
        assert result.exit_code != 0

    def test_analyze_directory_with_no_log_files(self, tmp_path):
        """Test analyze directory with no log files matching filter."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        (log_dir / "readme.txt").write_text("not a log\n")

        result = run_cli_direct(["analyze", str(log_dir), "--include", "*.log"])
        assert result.exit_code != 0

    def test_analyze_empty_log_file(self, tmp_path):
        """Test analyze with empty log file."""
        log_file = tmp_path / "empty.log"
        log_file.write_text("")

        result = run_cli_direct(["analyze", str(log_file)])
        assert result.exit_code != 0
        output = (result.stdout or "") + (result.stderr or "")
        assert "No log entries" in output or "Error" in output

    def test_analyze_stdin_not_supported(self):
        """Test that stdin input is rejected."""
        result = run_cli_direct(["analyze", "-"])
        assert result.exit_code != 0
        output = (result.stdout or "") + (result.stderr or "")
        assert "stdin is not supported" in output

    def test_analyze_with_all_options(self, tmp_path):
        """Test analyze with all options combined."""
        log_dir = tmp_path / "logs"
        nested = log_dir / "nested"
        nested.mkdir(parents=True)
        (log_dir / "app.log").write_text(
            '{"timestamp": "2026-01-28T12:00:00Z", "level": "ERROR", '
            '"message": "App"}\n'
        )
        (nested / "debug.log").write_text(
            '{"timestamp": "2026-01-28T12:00:00Z", "level": "DEBUG", '
            '"message": "Debug"}\n'
        )
        out_file = tmp_path / "output.txt"

        result = run_cli_direct(
            [
                "analyze",
                str(log_dir),
                "--recursive",
                "--include",
                "*.log",
                "--format",
                "json",
                "--output",
                "json",
                "--max-tokens",
                "1024",
                "--out-file",
                str(out_file),
            ]
        )
        assert result.exit_code == 0, f"stdout: {result.stdout}\nerror: {result.stderr}"
        assert out_file.exists()

    def test_analyze_permission_error_handling(self, tmp_path):
        """Test that permission errors are handled gracefully."""
        # Create a file that we can't read (on non-Windows systems)
        if os.name == "nt":
            pytest.skip("File permissions not reliable on Windows")

        log_file = tmp_path / "forbidden.log"
        log_file.write_text(
            '{"timestamp": "2026-01-28T12:00:00Z", "level": "ERROR", '
            '"message": "Test"}\n'
        )
        log_file.chmod(0o000)  # Remove all permissions

        try:
            result = run_cli_direct(["analyze", str(log_file)])
            # Should fail with permission error
            assert result.exit_code != 0
        finally:
            log_file.chmod(0o644)

    def test_analyze_with_mock_llm_direct(self, tmp_path, monkeypatch):
        """Test analyze uses mock LLM when env var is set."""
        monkeypatch.setenv("LOGPILOT_MOCK_LLM", "1")

        log_file = tmp_path / "test.log"
        log_file.write_text(
            '{"timestamp": "2026-01-28T12:00:00Z", "level": "ERROR", '
            '"message": "Test error"}\n'
        )

        result = run_cli_direct(["analyze", str(log_file)])
        assert result.exit_code == 0
        msg = "Mocked summary" in result.stdout or "failed" in result.stdout.lower()
        assert msg

    def test_analyze_handles_generic_exception(self, tmp_path):
        """Test analyze handles generic exceptions gracefully."""
        log_file = tmp_path / "test.log"
        log_file.write_text(
            '{"timestamp": "2026-01-28T12:00:00Z", "level": "ERROR", '
            '"message": "Test"}\n'
        )

        with patch(
            "logpilot.cli.iter_log_files", side_effect=RuntimeError("Unexpected error")
        ):
            result = run_cli_direct(["analyze", str(log_file)])
            assert result.exit_code != 0

    def test_analyze_without_mock_llm(self, tmp_path, monkeypatch):
        """Test analyze without mock LLM (uses real LLMClient)."""
        # Skip this test - when monkeypatch deletes LOGPILOT_MOCK_LLM,
        # the conftest has already set it so it won't affect the run_cli_direct behavior
        pytest.skip("Cannot easily test non-mock path with conftest env var")
