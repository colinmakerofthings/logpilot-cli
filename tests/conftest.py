"""Shared fixtures for tests."""

from pathlib import Path
from typing import List

import pytest

from logpilot.log_parser import LogEntry


@pytest.fixture
def sample_log_entries() -> List[LogEntry]:
    """Provides a list of sample LogEntry objects for testing."""
    return [
        LogEntry(
            timestamp="2024-01-01T10:00:00Z",
            level="INFO",
            source="app.main",
            message="Application started",
            raw=(
                '{"timestamp":"2024-01-01T10:00:00Z",'
                '"level":"INFO","source":"app.main",'
                '"message":"Application started"}'
            ),
        ),
        LogEntry(
            timestamp="2024-01-01T10:00:01Z",
            level="WARNING",
            source="app.auth",
            message="Failed login attempt",
            raw=(
                '{"timestamp":"2024-01-01T10:00:01Z",'
                '"level":"WARNING","source":"app.auth",'
                '"message":"Failed login attempt"}'
            ),
        ),
        LogEntry(
            timestamp="2024-01-01T10:00:02Z",
            level="ERROR",
            source="app.db",
            message="Connection timeout",
            raw=(
                '{"timestamp":"2024-01-01T10:00:02Z",'
                '"level":"ERROR","source":"app.db",'
                '"message":"Connection timeout"}'
            ),
        ),
        LogEntry(
            timestamp="2024-01-01T10:00:03Z",
            level="DEBUG",
            source="app.cache",
            message="Cache miss for key: user_123",
            raw=(
                '{"timestamp":"2024-01-01T10:00:03Z",'
                '"level":"DEBUG","source":"app.cache",'
                '"message":"Cache miss for key: user_123"}'
            ),
        ),
    ]


@pytest.fixture
def sample_json_logs() -> List[str]:
    """Provides sample JSON-formatted log strings."""
    return [
        (
            '{"timestamp":"2024-01-01T10:00:00Z","level":"INFO",'
            '"source":"app.main","message":"Application started"}'
        ),
        (
            '{"timestamp":"2024-01-01T10:00:01Z","level":"WARNING",'
            '"source":"app.auth","message":"Failed login attempt"}'
        ),
        (
            '{"timestamp":"2024-01-01T10:00:02Z","level":"ERROR",'
            '"source":"app.db","message":"Connection timeout"}'
        ),
        (
            '{"timestamp":"2024-01-01T10:00:03Z","level":"DEBUG",'
            '"source":"app.cache","message":"Cache miss"}'
        ),
    ]


@pytest.fixture
def sample_text_logs() -> List[str]:
    """Provides sample CSV-style text log strings."""
    return [
        "2024-01-01T10:00:00Z,INFO,app.main,Application started",
        "2024-01-01T10:00:01Z,WARNING,app.auth,Failed login attempt",
        "2024-01-01T10:00:02Z,ERROR,app.db,Connection timeout",
        "2024-01-01T10:00:03Z,DEBUG,app.cache,Cache miss",
    ]


@pytest.fixture
def malformed_logs() -> dict:
    """Provides various malformed log strings for edge case testing."""
    return {
        "empty": "",
        "whitespace_only": "   \t\n  ",
        "malformed_json": '{"timestamp":"2024-01-01","level":',
        "json_missing_message": '{"timestamp":"2024-01-01","level":"INFO"}',
        "text_no_commas": "This is just plain text without commas",
        "text_one_comma": "2024-01-01,INFO only two fields",
        # Missing message (needs 3+ commas)
        "text_two_commas": "2024-01-01,INFO,app.main",
        "json_array": '[{"message":"test"}]',
        "unicode": "2024-01-01,INFO,app,Message with unicode: 你好世界",
        "very_long": "2024-01-01,INFO,app," + "A" * 10000,
    }


@pytest.fixture
def temp_log_files(tmp_path: Path):
    """Factory fixture to create temporary log files with given content."""

    def _create_log_file(filename: str, content: str, subdirectory: str = None) -> Path:
        """
        Create a temporary log file with the given content.

        Args:
            filename: Name of the file to create
            content: Content to write to the file
            subdirectory: Optional subdirectory within tmp_path

        Returns:
            Path to the created file
        """
        if subdirectory:
            dir_path = tmp_path / subdirectory
            dir_path.mkdir(parents=True, exist_ok=True)
            file_path = dir_path / filename
        else:
            file_path = tmp_path / filename

        file_path.write_text(content, encoding="utf-8")
        return file_path

    return _create_log_file


@pytest.fixture
def sample_log_file_structure(tmp_path: Path) -> dict:
    """
    Creates a sample directory structure with various log files.

    Returns a dict with paths to different files and directories for testing.
    """
    # Create directory structure
    # tmp_path/
    #   ├── app.log
    #   ├── error.log
    #   ├── logs/
    #   │   ├── access.log
    #   │   ├── debug.log
    #   │   └── nested/
    #   │       └── deep.log
    #   └── data.txt (non-log file)

    # Root level files
    app_log = tmp_path / "app.log"
    app_log.write_text(
        "2024-01-01,INFO,app,Test log 1\n2024-01-01,INFO,app,Test log 2\n"
    )

    error_log = tmp_path / "error.log"
    error_log.write_text("2024-01-01,ERROR,app,Error occurred\n")

    data_txt = tmp_path / "data.txt"
    data_txt.write_text("This is not a log file\n")

    # Subdirectory
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()

    access_log = logs_dir / "access.log"
    access_log.write_text("2024-01-01,INFO,web,GET /api/users\n")

    debug_log = logs_dir / "debug.log"
    debug_log.write_text("2024-01-01,DEBUG,app,Debug info\n")

    # Nested subdirectory
    nested_dir = logs_dir / "nested"
    nested_dir.mkdir()

    deep_log = nested_dir / "deep.log"
    deep_log.write_text("2024-01-01,INFO,deep,Deep nested log\n")

    return {
        "root": tmp_path,
        "app_log": app_log,
        "error_log": error_log,
        "data_txt": data_txt,
        "logs_dir": logs_dir,
        "access_log": access_log,
        "debug_log": debug_log,
        "nested_dir": nested_dir,
        "deep_log": deep_log,
    }
