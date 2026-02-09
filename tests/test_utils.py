"""Unit tests for utils module."""

import pytest

from logpilot.utils import space_indent, tab_indent


@pytest.mark.unit
class TestSpaceIndent:
    """Tests for the space_indent function."""

    def test_space_indent_single_line(self):
        """Test indenting a single line."""
        text = "Single line"
        result = space_indent(text)

        assert result == "    Single line"

    def test_space_indent_multiple_lines(self):
        """Test indenting multiple lines."""
        text = "Line 1\nLine 2\nLine 3"
        result = space_indent(text)

        expected = "    Line 1\n    Line 2\n    Line 3"
        assert result == expected

    def test_space_indent_empty_string(self):
        """Test indenting an empty string."""
        text = ""
        result = space_indent(text)

        assert result == ""

    def test_space_indent_empty_lines(self):
        """Test indenting text with empty lines."""
        text = "Line 1\n\nLine 3"
        result = space_indent(text)

        # Empty lines should remain empty (no spaces added)
        expected = "    Line 1\n\n    Line 3"
        assert result == expected

    def test_space_indent_whitespace_only_lines(self):
        """Test indenting lines with only whitespace."""
        text = "Line 1\n   \nLine 3"
        result = space_indent(text)

        # Lines with only whitespace should remain empty after strip check
        lines = result.split("\n")
        assert lines[0] == "    Line 1"
        assert lines[1] == ""  # Whitespace-only line becomes empty
        assert lines[2] == "    Line 3"

    def test_space_indent_already_indented(self):
        """Test indenting text that is already indented."""
        text = "  Already indented\n  Second line"
        result = space_indent(text)

        # Should add 4 more spaces to already indented lines
        expected = "      Already indented\n      Second line"
        assert result == expected

    def test_space_indent_tabs(self):
        """Test indenting text with tabs."""
        text = "\tTabbed line"
        result = space_indent(text)

        # Should add 4 spaces before the tab
        assert result == "    \tTabbed line"

    def test_space_indent_mixed_content(self):
        """Test indenting text with mixed content."""
        text = "Normal\n  Indented\n\nEmpty above\n   \nWhitespace above"
        result = space_indent(text)

        lines = result.split("\n")
        assert lines[0] == "    Normal"
        assert lines[1] == "      Indented"
        assert lines[2] == ""  # Empty line
        assert lines[3] == "    Empty above"
        assert lines[4] == ""  # Whitespace-only becomes empty
        assert lines[5] == "    Whitespace above"

    def test_space_indent_with_trailing_newline(self):
        """Test indenting text with trailing newline."""
        text = "Line 1\nLine 2\n"
        result = space_indent(text)

        # splitlines() doesn't include the trailing newline's empty string
        # So the result won't have a trailing newline
        assert result == "    Line 1\n    Line 2"

    def test_space_indent_single_word(self):
        """Test indenting a single word."""
        text = "word"
        result = space_indent(text)

        assert result == "    word"

    def test_space_indent_with_unicode(self):
        """Test indenting text with unicode characters."""
        text = "Unicode: 你好\nEmoji: 🚀"
        result = space_indent(text)

        expected = "    Unicode: 你好\n    Emoji: 🚀"
        assert result == expected

    def test_space_indent_special_characters(self):
        """Test indenting text with special characters."""
        text = "Special: !@#$%\nMore: ^&*()"
        result = space_indent(text)

        expected = "    Special: !@#$%\n    More: ^&*()"
        assert result == expected

    def test_space_indent_uses_four_spaces(self):
        """Test that space_indent uses exactly 4 spaces."""
        text = "test"
        result = space_indent(text)

        # Verify it starts with exactly 4 spaces
        assert result.startswith("    ")
        assert len(result) == len("    test")
        # Check the spaces are at the beginning
        assert result == "    test"

    def test_space_indent_long_lines(self):
        """Test indenting very long lines."""
        text = "x" * 1000
        result = space_indent(text)

        assert result == "    " + ("x" * 1000)
        assert len(result) == 1004  # 4 spaces + 1000 x's

    def test_space_indent_many_lines(self):
        """Test indenting many lines."""
        lines = [f"Line {i}" for i in range(100)]
        text = "\n".join(lines)
        result = space_indent(text)

        result_lines = result.split("\n")
        assert len(result_lines) == 100
        for i, line in enumerate(result_lines):
            assert line == f"    Line {i}"


@pytest.mark.unit
class TestTabIndent:
    """Tests for the tab_indent function."""

    def test_tab_indent_not_implemented(self):
        """Test that tab_indent is not yet implemented."""
        # The function currently just has 'pass', so it returns None
        result = tab_indent("test")
        assert result is None

    @pytest.mark.skip(reason="tab_indent is not implemented yet")
    def test_tab_indent_future_implementation(self):
        """Placeholder test for when tab_indent is implemented."""
        # When implemented, this test should be updated
        text = "Line 1\nLine 2"
        result = tab_indent(text)

        # Expected behavior: indent with tabs
        expected = "\tLine 1\n\tLine 2"
        assert result == expected
