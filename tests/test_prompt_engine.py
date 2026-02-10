"""Unit tests for prompt_engine module."""

import pytest

from logpilot.log_parser import LogEntry
from logpilot.prompt_engine import PROMPT_TEMPLATE, format_prompt


@pytest.mark.unit
class TestFormatPrompt:
    """Tests for the format_prompt function."""

    def test_format_prompt_with_sample_entries(self, sample_log_entries):
        """Test formatting prompt with sample log entries."""
        prompt = format_prompt(sample_log_entries)

        # Verify template structure is present
        assert "You are analyzing application logs." in prompt
        assert "Logs:" in prompt
        assert "Tasks:" in prompt
        assert "Identify critical issues" in prompt

        # Verify all log raw data is included
        for entry in sample_log_entries:
            assert entry.raw in prompt

    def test_format_prompt_single_entry(self):
        """Test formatting prompt with a single entry."""
        entry = LogEntry(
            timestamp="2024-01-01",
            level="ERROR",
            source="test",
            message="Error occurred",
            raw='{"timestamp":"2024-01-01","level":"ERROR","message":"Error occurred"}',
        )

        prompt = format_prompt([entry])

        assert entry.raw in prompt
        assert "You are analyzing application logs." in prompt

    def test_format_prompt_empty_chunk(self):
        """Test formatting prompt with empty chunk."""
        prompt = format_prompt([])

        # Should still have the template structure
        assert "You are analyzing application logs." in prompt
        assert "Logs:" in prompt
        # The chunk section should be empty
        assert prompt.count("\n\n") >= 1

    def test_format_prompt_preserves_order(self):
        """Test that format_prompt preserves the order of entries."""
        entries = [
            LogEntry(None, None, None, "First", "First log"),
            LogEntry(None, None, None, "Second", "Second log"),
            LogEntry(None, None, None, "Third", "Third log"),
        ]

        prompt = format_prompt(entries)

        # Find positions of each log in the prompt
        first_pos = prompt.find("First log")
        second_pos = prompt.find("Second log")
        third_pos = prompt.find("Third log")

        assert first_pos < second_pos < third_pos

    def test_format_prompt_with_special_characters(self):
        """Test formatting prompt with special characters in logs."""
        entry = LogEntry(
            None,
            None,
            None,
            "Special chars",
            "Log with special chars: !@#$%^&*(){}[]|\\",
        )

        prompt = format_prompt([entry])

        assert entry.raw in prompt
        assert "!@#$%^&*()" in prompt

    def test_format_prompt_with_unicode(self):
        """Test formatting prompt with unicode characters."""
        entry = LogEntry(None, None, None, "Unicode", "Unicode log: 你好世界 🚀")

        prompt = format_prompt([entry])

        assert "你好世界" in prompt
        assert "🚀" in prompt

    def test_format_prompt_with_multiline_raw(self):
        """Test formatting prompt with entries containing newlines."""
        entry = LogEntry(None, None, None, "Multiline", "Line 1\nLine 2\nLine 3")

        prompt = format_prompt([entry])

        assert "Line 1" in prompt
        assert "Line 2" in prompt
        assert "Line 3" in prompt

    def test_format_prompt_uses_template(self):
        """Test that format_prompt uses the PROMPT_TEMPLATE constant."""
        entry = LogEntry(None, None, None, "Test", "Test log")

        prompt = format_prompt([entry])

        # Verify all parts of the template are present
        assert "You are analyzing application logs." in prompt
        assert "1. Identify critical issues" in prompt
        assert "2. Explain likely causes" in prompt
        assert "3. Suggest next debugging steps" in prompt

    def test_format_prompt_entries_separated_by_newlines(self):
        """Test that entries are separated by newlines in the prompt."""
        entries = [
            LogEntry(None, None, None, "Log 1", "Raw 1"),
            LogEntry(None, None, None, "Log 2", "Raw 2"),
            LogEntry(None, None, None, "Log 3", "Raw 3"),
        ]

        prompt = format_prompt(entries)

        # The chunk should have entries joined by newlines
        assert "Raw 1\nRaw 2\nRaw 3" in prompt

    def test_format_prompt_with_very_long_entries(self):
        """Test formatting prompt with very long log entries."""
        long_raw = "x" * 10000
        entry = LogEntry(None, None, None, "Long", long_raw)

        prompt = format_prompt([entry])

        assert long_raw in prompt
        assert len(prompt) > 10000

    def test_prompt_template_constant(self):
        """Test that PROMPT_TEMPLATE is properly defined."""
        assert isinstance(PROMPT_TEMPLATE, str)
        assert "{chunk}" in PROMPT_TEMPLATE
        assert "analyzing" in PROMPT_TEMPLATE.lower()
        assert "logs" in PROMPT_TEMPLATE.lower()
