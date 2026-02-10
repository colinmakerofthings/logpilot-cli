"""Unit tests for postprocessor module."""

import pytest

from logpilot.postprocessor import aggregate_responses


@pytest.mark.unit
class TestAggregateResponses:
    """Tests for the aggregate_responses function."""

    def test_aggregate_single_response(self):
        """Test aggregating a single response."""
        responses = ["Response 1"]
        result = aggregate_responses(responses)

        assert result == "Response 1"

    def test_aggregate_multiple_responses(self):
        """Test aggregating multiple responses."""
        responses = ["Response 1", "Response 2", "Response 3"]
        result = aggregate_responses(responses)

        expected = "Response 1\n---\n" + "Response 2\n---\n" + "Response 3"
        assert result == expected

    def test_aggregate_two_responses(self):
        """Test aggregating exactly two responses."""
        responses = ["First", "Second"]
        result = aggregate_responses(responses)

        assert result == "First\n---\nSecond"
        assert result.count("---") == 1

    def test_aggregate_empty_list(self):
        """Test aggregating an empty list of responses."""
        responses = []
        result = aggregate_responses(responses)

        assert result == ""

    def test_aggregate_responses_with_newlines(self):
        """Test aggregating responses that contain newlines."""
        responses = [
            "Response 1\nLine 2",
            "Response 2\nLine 2\nLine 3",
            "Response 3",
        ]
        result = aggregate_responses(responses)

        # Verify all responses are included
        assert "Response 1\nLine 2" in result
        assert "Response 2\nLine 2\nLine 3" in result
        assert "Response 3" in result
        # Verify separator is present
        assert result.count("\n---\n") == 2

    def test_aggregate_responses_with_empty_strings(self):
        """Test aggregating responses with empty strings."""
        responses = ["Response 1", "", "Response 3"]
        result = aggregate_responses(responses)

        assert result == "Response 1\n---\n\n---\nResponse 3"
        # Empty response should still create a section

    def test_aggregate_responses_all_empty(self):
        """Test aggregating all empty responses."""
        responses = ["", "", ""]
        result = aggregate_responses(responses)

        assert result == "\n---\n\n---\n"

    def test_aggregate_responses_with_separator_in_content(self):
        """Test aggregating when responses already contain '---'."""
        responses = ["Response with --- in it", "Normal response"]
        result = aggregate_responses(responses)

        # The function should still add separators
        # Count total occurrences of '---'
        assert result.count("---") == 2  # One in content, one as separator

    def test_aggregate_responses_preserves_order(self):
        """Test that aggregation preserves the order of responses."""
        responses = ["First", "Second", "Third", "Fourth"]
        result = aggregate_responses(responses)

        # Find positions to verify order
        first_pos = result.find("First")
        second_pos = result.find("Second")
        third_pos = result.find("Third")
        fourth_pos = result.find("Fourth")

        assert first_pos < second_pos < third_pos < fourth_pos

    def test_aggregate_responses_with_unicode(self):
        """Test aggregating responses with unicode characters."""
        responses = ["Response with 你好", "Response with 🚀"]
        result = aggregate_responses(responses)

        assert "你好" in result
        assert "🚀" in result
        assert "\n---\n" in result

    def test_aggregate_responses_with_special_characters(self):
        """Test aggregating responses with special characters."""
        responses = [
            "Response with !@#$%",
            "Response with ^&*()",
            "Response with {}[]|\\",
        ]
        result = aggregate_responses(responses)

        assert "!@#$%" in result
        assert "^&*()" in result
        assert "{}[]|\\" in result

    def test_aggregate_large_number_of_responses(self):
        """Test aggregating a large number of responses."""
        responses = [f"Response {i}" for i in range(100)]
        result = aggregate_responses(responses)

        # Verify all responses are present
        for i in range(100):
            assert f"Response {i}" in result

        # Verify separator count (should be 99 separators for 100 responses)
        assert result.count("\n---\n") == 99

    def test_aggregate_responses_with_very_long_responses(self):
        """Test aggregating very long responses."""
        long_response = "x" * 10000
        responses = [long_response, "Short", long_response]
        result = aggregate_responses(responses)

        assert len(result) > 20000
        assert result.count("\n---\n") == 2

    def test_aggregate_responses_separator_format(self):
        """Test that the separator format is exactly '\\n---\\n'."""
        responses = ["A", "B"]
        result = aggregate_responses(responses)

        # Verify the exact separator format
        assert result == "A\n---\nB"
        # Verify no extra spaces or characters
        assert "A\n---\nB" == result
