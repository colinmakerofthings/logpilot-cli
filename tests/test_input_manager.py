"""Unit tests for input_manager module."""

import os

import pytest

from logpilot.input_manager import iter_log_files, read_logs, read_logs_from_paths

# ============================================================================
# read_logs Tests
# ============================================================================


@pytest.mark.unit
class TestReadLogs:
    """Tests for the read_logs function."""

    def test_read_logs_single_file(self, temp_log_files):
        """Test reading a single log file."""
        content = "Line 1\nLine 2\nLine 3\n"
        log_file = temp_log_files("test.log", content)

        lines = list(read_logs(str(log_file)))
        assert len(lines) == 3
        assert lines[0] == "Line 1"
        assert lines[1] == "Line 2"
        assert lines[2] == "Line 3"

    def test_read_logs_strips_newlines(self, temp_log_files):
        """Test that read_logs strips trailing newlines."""
        content = "Line with newline\n"
        log_file = temp_log_files("test.log", content)

        lines = list(read_logs(str(log_file)))
        assert lines[0] == "Line with newline"
        assert "\n" not in lines[0]

    def test_read_logs_empty_file(self, temp_log_files):
        """Test reading an empty file."""
        log_file = temp_log_files("empty.log", "")

        lines = list(read_logs(str(log_file)))
        assert len(lines) == 0

    def test_read_logs_file_with_empty_lines(self, temp_log_files):
        """Test reading file with empty lines."""
        content = "Line 1\n\nLine 3\n\n"
        log_file = temp_log_files("test.log", content)

        lines = list(read_logs(str(log_file)))
        assert len(lines) == 4
        assert lines[0] == "Line 1"
        assert lines[1] == ""
        assert lines[2] == "Line 3"
        assert lines[3] == ""

    def test_read_logs_unicode_content(self, temp_log_files):
        """Test reading file with unicode characters."""
        content = "Unicode: 你好世界 🚀\nEmoji: 🎉\n"
        log_file = temp_log_files("unicode.log", content)

        lines = list(read_logs(str(log_file)))
        assert len(lines) == 2
        assert "你好世界" in lines[0]
        assert "🚀" in lines[0]
        assert "🎉" in lines[1]

    def test_read_logs_large_file(self, temp_log_files):
        """Test reading a large file with many lines."""
        content = "\n".join([f"Line {i}" for i in range(1000)])
        log_file = temp_log_files("large.log", content)

        lines = list(read_logs(str(log_file)))
        assert len(lines) == 1000
        assert lines[0] == "Line 0"
        assert lines[999] == "Line 999"

    def test_read_logs_is_iterator(self, temp_log_files):
        """Test that read_logs returns a lazy iterator."""
        content = "Line 1\nLine 2\nLine 3\n"
        log_file = temp_log_files("test.log", content)

        lines_iter = read_logs(str(log_file))
        assert next(lines_iter) == "Line 1"
        assert next(lines_iter) == "Line 2"
        assert next(lines_iter) == "Line 3"

        with pytest.raises(StopIteration):
            next(lines_iter)

    def test_read_logs_nonexistent_file(self):
        """Test reading a nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="No such file"):
            list(read_logs("/nonexistent/path/to/file.log"))

    def test_read_logs_directory_path(self, tmp_path):
        """Test reading a directory path raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="No such file"):
            list(read_logs(str(tmp_path)))

    def test_read_logs_windows_line_endings(self, temp_log_files):
        """Test reading file with Windows line endings (CRLF)."""
        # Note: write_text automatically handles this, but we can test the behavior
        content = "Line 1\r\nLine 2\r\n"
        log_file = temp_log_files("windows.log", content)

        lines = list(read_logs(str(log_file)))
        # The result depends on how the OS handles line endings when written
        # Just verify we can read it without errors
        assert len(lines) >= 2


@pytest.mark.unit
class TestIterLogFilesSingleFile:
    """Tests for iter_log_files with a single file path."""

    def test_iter_single_file(self, temp_log_files):
        """Test iterating over a single file path."""
        log_file = temp_log_files("test.log", "content")

        files = list(iter_log_files(str(log_file)))
        assert len(files) == 1
        assert files[0] == str(log_file)

    def test_iter_single_file_with_include_match(self, temp_log_files):
        """Test single file with matching include pattern."""
        log_file = temp_log_files("test.log", "content")

        files = list(iter_log_files(str(log_file), include=["*.log"]))
        assert len(files) == 1

    def test_iter_single_file_with_include_no_match(self, temp_log_files):
        """Test single file with non-matching include pattern."""
        log_file = temp_log_files("test.log", "content")

        files = list(iter_log_files(str(log_file), include=["*.txt"]))
        assert len(files) == 0

    def test_iter_single_file_with_exclude(self, temp_log_files):
        """Test single file with exclude pattern."""
        log_file = temp_log_files("test.log", "content")

        files = list(iter_log_files(str(log_file), exclude=["*.log"]))
        assert len(files) == 0

    def test_iter_single_file_include_and_exclude(self, temp_log_files):
        """Test single file with both include and exclude patterns."""
        log_file = temp_log_files("test.log", "content")

        # Include matches but exclude also matches - should be excluded
        files = list(
            iter_log_files(str(log_file), include=["*.log"], exclude=["test.*"])
        )
        assert len(files) == 0


# ============================================================================
# iter_log_files Tests - Directory Non-Recursive
# ============================================================================


@pytest.mark.unit
class TestIterLogFilesDirectoryNonRecursive:
    """Tests for iter_log_files with directory (non-recursive mode)."""

    def test_iter_directory_non_recursive(self, sample_log_file_structure):
        """Test iterating over directory without recursion."""
        root = sample_log_file_structure["root"]

        files = list(iter_log_files(str(root), recursive=False))
        filenames = [os.path.basename(f) for f in files]

        # Should include root-level files only
        assert "app.log" in filenames
        assert "error.log" in filenames
        assert "data.txt" in filenames
        # Should NOT include subdirectory files
        assert "access.log" not in filenames
        assert "deep.log" not in filenames

    def test_iter_directory_with_log_filter(self, sample_log_file_structure):
        """Test iterating directory with .log filter."""
        root = sample_log_file_structure["root"]

        files = list(iter_log_files(str(root), recursive=False, include=["*.log"]))
        filenames = [os.path.basename(f) for f in files]

        assert "app.log" in filenames
        assert "error.log" in filenames
        assert "data.txt" not in filenames  # Excluded by include pattern

    def test_iter_directory_with_exclude(self, sample_log_file_structure):
        """Test iterating directory with exclude pattern."""
        root = sample_log_file_structure["root"]

        files = list(iter_log_files(str(root), recursive=False, exclude=["error.*"]))
        filenames = [os.path.basename(f) for f in files]

        assert "app.log" in filenames
        assert "data.txt" in filenames
        assert "error.log" not in filenames

    def test_iter_directory_multiple_include_patterns(self, sample_log_file_structure):
        """Test iterating directory with multiple include patterns."""
        root = sample_log_file_structure["root"]

        files = list(
            iter_log_files(str(root), recursive=False, include=["*.log", "*.txt"])
        )
        filenames = [os.path.basename(f) for f in files]

        assert len(filenames) == 3
        assert "app.log" in filenames
        assert "error.log" in filenames
        assert "data.txt" in filenames

    def test_iter_directory_files_sorted(self, sample_log_file_structure):
        """Test that files are returned in sorted order."""
        root = sample_log_file_structure["root"]

        files = list(iter_log_files(str(root), recursive=False))
        filenames = [os.path.basename(f) for f in files]

        # Check if sorted (app.log, data.txt, error.log alphabetically)
        assert filenames == sorted(filenames)

    def test_iter_empty_directory(self, tmp_path):
        """Test iterating over an empty directory."""
        files = list(iter_log_files(str(tmp_path), recursive=False))
        assert len(files) == 0


# ============================================================================
# iter_log_files Tests - Directory Recursive
# ============================================================================


@pytest.mark.unit
class TestIterLogFilesDirectoryRecursive:
    """Tests for iter_log_files with directory (recursive mode)."""

    def test_iter_directory_recursive(self, sample_log_file_structure):
        """Test iterating over directory with recursion."""
        root = sample_log_file_structure["root"]

        files = list(iter_log_files(str(root), recursive=True))

        # Get basenames for easier assertion
        filenames = [os.path.basename(f) for f in files]

        # Should include all files
        assert "app.log" in filenames
        assert "error.log" in filenames
        assert "data.txt" in filenames
        assert "access.log" in filenames
        assert "debug.log" in filenames
        assert "deep.log" in filenames

    def test_iter_directory_recursive_with_filter(self, sample_log_file_structure):
        """Test recursive iteration with .log filter."""
        root = sample_log_file_structure["root"]

        files = list(iter_log_files(str(root), recursive=True, include=["*.log"]))
        filenames = [os.path.basename(f) for f in files]

        assert "app.log" in filenames
        assert "error.log" in filenames
        assert "access.log" in filenames
        assert "debug.log" in filenames
        assert "deep.log" in filenames
        assert "data.txt" not in filenames

    def test_iter_directory_recursive_with_path_pattern(
        self, sample_log_file_structure
    ):
        """Test recursive iteration with path-based pattern."""
        root = sample_log_file_structure["root"]

        # Match only files in the 'logs' subdirectory
        files = list(iter_log_files(str(root), recursive=True, include=["logs/*.log"]))
        filenames = [os.path.basename(f) for f in files]

        # Should include logs in the logs directory
        assert "access.log" in filenames
        assert "debug.log" in filenames
        # Should NOT include root level logs
        assert "app.log" not in filenames
        assert "error.log" not in filenames

    def test_iter_directory_recursive_exclude_nested(self, sample_log_file_structure):
        """Test recursive iteration excluding nested directory."""
        root = sample_log_file_structure["root"]

        files = list(iter_log_files(str(root), recursive=True, exclude=["*/nested/*"]))
        filenames = [os.path.basename(f) for f in files]

        assert "app.log" in filenames
        assert "access.log" in filenames
        assert "deep.log" not in filenames  # In nested directory

    def test_iter_directory_recursive_sorted(self, sample_log_file_structure):
        """Test that recursive files are returned in sorted order."""
        root = sample_log_file_structure["root"]

        files = list(iter_log_files(str(root), recursive=True))

        # Files should be sorted
        assert files == sorted(files)


# ============================================================================
# iter_log_files Tests - Edge Cases
# ============================================================================


@pytest.mark.unit
class TestIterLogFilesEdgeCases:
    """Tests for edge cases in iter_log_files."""

    def test_iter_nonexistent_path(self):
        """Test iterating nonexistent path raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="No such file or directory"):
            list(iter_log_files("/nonexistent/path"))

    def test_iter_with_wildcard_patterns(self, sample_log_file_structure):
        """Test with various wildcard patterns."""
        root = sample_log_file_structure["root"]

        # Match files starting with 'a'
        files = list(iter_log_files(str(root), recursive=True, include=["a*"]))
        filenames = [os.path.basename(f) for f in files]
        assert "app.log" in filenames
        assert "access.log" in filenames
        assert "error.log" not in filenames

    def test_iter_include_default_matches_all(self, sample_log_file_structure):
        """Test that default include pattern matches all files."""
        root = sample_log_file_structure["root"]

        # Default include should be ['*']
        files_default = list(iter_log_files(str(root), recursive=False))
        files_explicit = list(iter_log_files(str(root), recursive=False, include=["*"]))

        assert len(files_default) == len(files_explicit)

    def test_iter_exclude_takes_precedence(self, temp_log_files):
        """Test that exclude takes precedence over include."""
        log_file = temp_log_files("test.log", "content")

        # Include matches, but exclude also matches
        files = list(
            iter_log_files(str(log_file), include=["*.log"], exclude=["*.log"])
        )
        assert len(files) == 0

    def test_iter_pattern_matching_name_and_path(self, sample_log_file_structure):
        """Test that patterns match both filename and relative path."""
        root = sample_log_file_structure["root"]

        # Pattern should match the filename 'deep.log'
        files = list(iter_log_files(str(root), recursive=True, include=["deep.log"]))
        assert len(files) == 1
        assert os.path.basename(files[0]) == "deep.log"


# ============================================================================
# read_logs_from_paths Tests
# ============================================================================


@pytest.mark.unit
class TestReadLogsFromPaths:
    """Tests for the read_logs_from_paths function."""

    def test_read_logs_from_multiple_files(self, temp_log_files):
        """Test reading logs from multiple files."""
        file1 = temp_log_files("file1.log", "Line 1\nLine 2\n")
        file2 = temp_log_files("file2.log", "Line 3\nLine 4\n")

        lines = list(read_logs_from_paths([str(file1), str(file2)]))

        assert len(lines) == 4
        assert lines[0] == "Line 1"
        assert lines[1] == "Line 2"
        assert lines[2] == "Line 3"
        assert lines[3] == "Line 4"

    def test_read_logs_from_paths_preserves_order(self, temp_log_files):
        """Test that files are read in the order provided."""
        file1 = temp_log_files("a.log", "From A\n")
        file2 = temp_log_files("b.log", "From B\n")
        file3 = temp_log_files("c.log", "From C\n")

        # Read in specific order
        lines = list(read_logs_from_paths([str(file3), str(file1), str(file2)]))

        assert lines[0] == "From C"
        assert lines[1] == "From A"
        assert lines[2] == "From B"

    def test_read_logs_from_empty_paths_list(self):
        """Test reading from empty paths list."""
        lines = list(read_logs_from_paths([]))
        assert len(lines) == 0

    def test_read_logs_from_single_file(self, temp_log_files):
        """Test reading from a single file path."""
        log_file = temp_log_files("test.log", "Line 1\nLine 2\n")

        lines = list(read_logs_from_paths([str(log_file)]))

        assert len(lines) == 2
        assert lines[0] == "Line 1"
        assert lines[1] == "Line 2"

    def test_read_logs_from_paths_is_iterator(self, temp_log_files):
        """Test that read_logs_from_paths returns a lazy iterator."""
        file1 = temp_log_files("file1.log", "Line 1\n")
        file2 = temp_log_files("file2.log", "Line 2\n")

        lines_iter = read_logs_from_paths([str(file1), str(file2)])

        assert next(lines_iter) == "Line 1"
        assert next(lines_iter) == "Line 2"

        with pytest.raises(StopIteration):
            next(lines_iter)

    def test_read_logs_from_paths_with_empty_file(self, temp_log_files):
        """Test reading from paths including an empty file."""
        file1 = temp_log_files("file1.log", "Line 1\n")
        file2 = temp_log_files("empty.log", "")
        file3 = temp_log_files("file3.log", "Line 3\n")

        lines = list(read_logs_from_paths([str(file1), str(file2), str(file3)]))

        assert len(lines) == 2
        assert lines[0] == "Line 1"
        assert lines[1] == "Line 3"

    def test_read_logs_from_paths_integration_with_iter_log_files(
        self, sample_log_file_structure
    ):
        """Test integration: use iter_log_files output as input to
        read_logs_from_paths."""
        root = sample_log_file_structure["root"]

        # Get all .log files recursively
        file_paths = list(iter_log_files(str(root), recursive=True, include=["*.log"]))

        # Read all lines from those files
        lines = list(read_logs_from_paths(file_paths))

        # Should have lines from all log files
        assert len(lines) > 0
        # Verify some expected content
        assert any("Test log 1" in line for line in lines)
        assert any("Error occurred" in line for line in lines)
