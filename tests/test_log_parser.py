"""Unit tests for log_parser module."""

import pytest

from logpilot.log_parser import LogEntry, parse_log_line, parse_logs

# ============================================================================
# LogEntry Class Tests
# ============================================================================


@pytest.mark.unit
class TestLogEntry:
    """Tests for the LogEntry class."""

    def test_log_entry_initialization(self):
        """Test LogEntry can be initialized with all fields."""
        entry = LogEntry(
            timestamp="2024-01-01T10:00:00Z",
            level="INFO",
            source="app.main",
            message="Test message",
            raw='{"timestamp":"2024-01-01T10:00:00Z"}',
        )
        assert entry.timestamp == "2024-01-01T10:00:00Z"
        assert entry.level == "INFO"
        assert entry.source == "app.main"
        assert entry.message == "Test message"
        assert entry.raw == '{"timestamp":"2024-01-01T10:00:00Z"}'

    def test_log_entry_with_none_values(self):
        """Test LogEntry can be initialized with None values for optional fields."""
        entry = LogEntry(
            timestamp=None, level=None, source=None, message="Message only", raw="raw"
        )
        assert entry.timestamp is None
        assert entry.level is None
        assert entry.source is None
        assert entry.message == "Message only"
        assert entry.raw == "raw"


# ============================================================================
# parse_log_line JSON Format Tests
# ============================================================================


@pytest.mark.unit
class TestParseLogLineJSON:
    """Tests for parse_log_line with JSON format."""

    def test_parse_valid_json_log(self, sample_json_logs):
        """Test parsing a valid JSON log line."""
        entry = parse_log_line(sample_json_logs[0], fmt="json")
        assert entry is not None
        assert entry.timestamp == "2024-01-01T10:00:00Z"
        assert entry.level == "INFO"
        assert entry.source == "app.main"
        assert entry.message == "Application started"
        assert entry.raw == sample_json_logs[0]

    def test_parse_json_with_all_fields(self):
        """Test parsing JSON with all expected fields."""
        json_line = (
            '{"timestamp":"2024-02-09","level":"ERROR",'
            '"source":"test","message":"Error occurred"}'
        )
        entry = parse_log_line(json_line, fmt="json")
        assert entry is not None
        assert entry.timestamp == "2024-02-09"
        assert entry.level == "ERROR"
        assert entry.source == "test"
        assert entry.message == "Error occurred"

    def test_parse_json_missing_optional_fields(self):
        """Test parsing JSON with missing optional fields (timestamp, level, source)."""
        json_line = '{"message":"Just a message"}'
        entry = parse_log_line(json_line, fmt="json")
        assert entry is not None
        assert entry.timestamp is None
        assert entry.level is None
        assert entry.source is None
        assert entry.message == "Just a message"

    def test_parse_json_missing_message_field(self):
        """Test parsing JSON without a message field uses str(data) as message."""
        json_line = '{"timestamp":"2024-01-01","level":"INFO"}'
        entry = parse_log_line(json_line, fmt="json")
        assert entry is not None
        assert "timestamp" in entry.message
        assert "level" in entry.message

    def test_parse_json_with_extra_fields(self):
        """Test parsing JSON with extra fields (they are ignored)."""
        json_line = (
            '{"timestamp":"2024-01-01","level":"INFO","source":"app",'
            '"message":"Test","extra":"field","another":123}'
        )
        entry = parse_log_line(json_line, fmt="json")
        assert entry is not None
        assert entry.message == "Test"

    def test_parse_malformed_json(self, malformed_logs):
        """Test parsing malformed JSON returns None."""
        entry = parse_log_line(malformed_logs["malformed_json"], fmt="json")
        assert entry is None

    def test_parse_json_array(self, malformed_logs):
        """Test parsing JSON array returns None."""
        entry = parse_log_line(malformed_logs["json_array"], fmt="json")
        assert entry is None

    def test_parse_empty_json_object(self):
        """Test parsing empty JSON object."""
        entry = parse_log_line("{}", fmt="json")
        assert entry is not None
        assert entry.message == "{}"  # Uses str(data) when message is missing

    def test_parse_json_with_unicode(self):
        """Test parsing JSON with unicode characters."""
        json_line = '{"message":"Unicode test: 你好世界 🚀"}'
        entry = parse_log_line(json_line, fmt="json")
        assert entry is not None
        assert "你好世界" in entry.message
        assert "🚀" in entry.message

    def test_parse_json_with_escaped_characters(self):
        """Test parsing JSON with escaped characters."""
        json_line = '{"message":"Line 1\\nLine 2\\tTabbed"}'
        entry = parse_log_line(json_line, fmt="json")
        assert entry is not None
        assert "Line 1" in entry.message


# ============================================================================
# parse_log_line Text Format Tests
# ============================================================================


@pytest.mark.unit
class TestParseLogLineText:
    """Tests for parse_log_line with text/CSV format."""

    def test_parse_valid_text_log(self, sample_text_logs):
        """Test parsing a valid CSV-style text log."""
        entry = parse_log_line(sample_text_logs[0], fmt="text")
        assert entry is not None
        assert entry.timestamp is None  # Text format doesn't parse fields
        assert entry.level is None
        assert entry.source is None
        assert entry.message == sample_text_logs[0]
        assert entry.raw == sample_text_logs[0]

    def test_parse_text_requires_two_commas(self):
        """Test text format requires at least 2 commas to be valid."""
        # 0 commas - invalid
        entry = parse_log_line("No commas here", fmt="text")
        assert entry is None

        # 1 comma - invalid
        entry = parse_log_line("One,comma", fmt="text")
        assert entry is None

        # 2 commas - valid
        entry = parse_log_line("Two,commas,here", fmt="text")
        assert entry is not None

        # 3+ commas - valid
        entry = parse_log_line("Many,commas,in,this,line", fmt="text")
        assert entry is not None

    def test_parse_text_with_many_fields(self):
        """Test parsing text log with many comma-separated fields."""
        text_line = "2024-01-01,INFO,app.main,User logged in,user_id=123,session=abc"
        entry = parse_log_line(text_line, fmt="text")
        assert entry is not None
        assert entry.message == text_line

    def test_parse_text_with_unicode(self, malformed_logs):
        """Test parsing text with unicode characters."""
        entry = parse_log_line(malformed_logs["unicode"], fmt="text")
        assert entry is not None
        assert "你好世界" in entry.message


# ============================================================================
# parse_log_line Auto Format Detection Tests
# ============================================================================


@pytest.mark.unit
class TestParseLogLineAuto:
    """Tests for parse_log_line with automatic format detection."""

    def test_auto_detects_json(self, sample_json_logs):
        """Test auto format detects and parses JSON."""
        entry = parse_log_line(sample_json_logs[0], fmt="auto")
        assert entry is not None
        assert entry.timestamp == "2024-01-01T10:00:00Z"
        assert entry.level == "INFO"

    def test_auto_detects_text(self, sample_text_logs):
        """Test auto format detects and parses text."""
        entry = parse_log_line(sample_text_logs[0], fmt="auto")
        assert entry is not None
        assert entry.message == sample_text_logs[0]

    def test_auto_with_json_whitespace(self):
        """Test auto detection works with leading whitespace before JSON."""
        json_line = "  \t  " + '{"message":"test"}'
        entry = parse_log_line(json_line, fmt="auto")
        assert entry is not None
        assert entry.message == "test"

    def test_auto_rejects_invalid_formats(self, malformed_logs):
        """Test auto format rejects logs that don't match either format."""
        # No commas and not JSON
        entry = parse_log_line(malformed_logs["text_no_commas"], fmt="auto")
        assert entry is None

        # Only one comma
        entry = parse_log_line(malformed_logs["text_one_comma"], fmt="auto")
        assert entry is None


# ============================================================================
# parse_log_line Edge Cases
# ============================================================================


@pytest.mark.unit
class TestParseLogLineEdgeCases:
    """Tests for edge cases in parse_log_line."""

    def test_parse_empty_string(self, malformed_logs):
        """Test parsing empty string returns None."""
        entry = parse_log_line(malformed_logs["empty"])
        assert entry is None

    def test_parse_whitespace_only(self, malformed_logs):
        """Test parsing whitespace-only string returns None."""
        entry = parse_log_line(malformed_logs["whitespace_only"])
        assert entry is None

    def test_parse_very_long_line(self, malformed_logs):
        """Test parsing very long line (10K+ chars)."""
        entry = parse_log_line(malformed_logs["very_long"], fmt="text")
        assert entry is not None
        assert len(entry.message) > 10000

    def test_parse_line_with_newline_characters(self):
        """Test parsing line with embedded newline characters."""
        # In JSON, newlines are escaped
        json_line = '{"message":"Line 1\\nLine 2"}'
        entry = parse_log_line(json_line, fmt="json")
        assert entry is not None

        # In text, actual newlines in the string
        text_line = "A,B,C,with,embedded,newline"
        entry = parse_log_line(text_line, fmt="text")
        assert entry is not None

    def test_parse_line_with_special_characters(self):
        """Test parsing line with various special characters."""
        special_chars = '{"message":"Special: !@#$%^&*()[]{}|\\\\/\'\\""}'
        entry = parse_log_line(special_chars, fmt="json")
        assert entry is not None

    def test_parse_with_trailing_whitespace(self):
        """Test parsing handles trailing whitespace."""
        json_line = '{"message":"test"}   \n\t  '
        entry = parse_log_line(json_line, fmt="json")
        assert entry is not None
        assert entry.message == "test"

    def test_parse_text_exactly_two_commas(self):
        """Test edge case: exactly 2 commas (minimum for text format)."""
        entry = parse_log_line("A,B,C", fmt="text")
        assert entry is not None
        assert entry.message == "A,B,C"


# ============================================================================
# parse_logs Iterator Tests
# ============================================================================


@pytest.mark.unit
class TestParseLogs:
    """Tests for the parse_logs iterator function."""

    def test_parse_logs_with_valid_json_lines(self, sample_json_logs):
        """Test parsing multiple valid JSON log lines."""
        entries = list(parse_logs(iter(sample_json_logs), fmt="json"))
        assert len(entries) == 4
        assert entries[0].level == "INFO"
        assert entries[1].level == "WARNING"
        assert entries[2].level == "ERROR"
        assert entries[3].level == "DEBUG"

    def test_parse_logs_with_valid_text_lines(self, sample_text_logs):
        """Test parsing multiple valid text log lines."""
        entries = list(parse_logs(iter(sample_text_logs), fmt="text"))
        assert len(entries) == 4
        assert all(entry.message is not None for entry in entries)

    def test_parse_logs_with_mixed_valid_invalid(self):
        """Test parsing mixed valid and invalid lines (invalid are skipped)."""
        lines = [
            '{"message":"valid json"}',
            "invalid line",
            '{"message":"another valid"}',
            "",
            '{"message":"third valid"}',
        ]
        entries = list(parse_logs(iter(lines), fmt="json"))
        assert len(entries) == 3
        assert entries[0].message == "valid json"
        assert entries[1].message == "another valid"
        assert entries[2].message == "third valid"

    def test_parse_logs_empty_iterator(self):
        """Test parsing empty iterator returns no entries."""
        entries = list(parse_logs(iter([]), fmt="json"))
        assert len(entries) == 0

    def test_parse_logs_all_invalid_lines(self):
        """Test parsing all invalid lines returns no entries."""
        lines = ["invalid", "no commas", "single,comma"]
        entries = list(parse_logs(iter(lines), fmt="text"))
        assert len(entries) == 0

    def test_parse_logs_is_lazy(self):
        """Test that parse_logs is a lazy iterator (doesn't consume all at once)."""
        lines = iter(['{"message":"test1"}', '{"message":"test2"}'])
        entries_iter = parse_logs(lines, fmt="json")

        # Get first entry
        first = next(entries_iter)
        assert first.message == "test1"

        # Get second entry
        second = next(entries_iter)
        assert second.message == "test2"

        # No more entries
        with pytest.raises(StopIteration):
            next(entries_iter)

    def test_parse_logs_auto_format(self, sample_json_logs, sample_text_logs):
        """Test parse_logs with auto format detection."""
        # Mix JSON and text logs
        mixed_lines = [
            sample_json_logs[0],
            sample_text_logs[0],
            sample_json_logs[1],
        ]
        entries = list(parse_logs(iter(mixed_lines), fmt="auto"))
        assert len(entries) == 3

    def test_parse_logs_preserves_order(self):
        """Test that parse_logs preserves the order of entries."""
        lines = [
            '{"message":"first"}',
            '{"message":"second"}',
            '{"message":"third"}',
        ]
        entries = list(parse_logs(iter(lines), fmt="json"))
        assert entries[0].message == "first"
        assert entries[1].message == "second"
        assert entries[2].message == "third"

    def test_parse_logs_with_whitespace_lines(self):
        """Test parsing logs with whitespace-only lines (should be skipped)."""
        lines = [
            '{"message":"test1"}',
            "   ",
            "\t\n",
            '{"message":"test2"}',
            "",
        ]
        entries = list(parse_logs(iter(lines), fmt="json"))
        assert len(entries) == 2
        assert entries[0].message == "test1"
        assert entries[1].message == "test2"
