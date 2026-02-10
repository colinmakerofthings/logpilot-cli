"""Unit tests for chunker module."""

from unittest.mock import patch

import pytest

from logpilot.chunker import chunk_logs, estimate_tokens
from logpilot.log_parser import LogEntry

# ============================================================================
# estimate_tokens Tests
# ============================================================================


@pytest.mark.unit
class TestEstimateTokens:
    """Tests for the estimate_tokens function."""

    def test_estimate_tokens_empty_string(self):
        """Test token estimation for empty string returns at least 1."""
        tokens = estimate_tokens("")
        assert tokens == 1  # max(1, 0 // 4)

    def test_estimate_tokens_short_string(self):
        """Test token estimation for short strings."""
        # "test" = 4 chars, 4 // 4 = 1
        tokens = estimate_tokens("test")
        assert tokens == 1

    def test_estimate_tokens_medium_string(self):
        """Test token estimation for medium-length strings."""
        # 100 chars = 100 // 4 = 25 tokens
        text = "x" * 100
        tokens = estimate_tokens(text)
        assert tokens == 25

    def test_estimate_tokens_large_string(self):
        """Test token estimation for large strings."""
        # 10000 chars = 10000 // 4 = 2500 tokens
        text = "x" * 10000
        tokens = estimate_tokens(text)
        assert tokens == 2500

    def test_estimate_tokens_unicode(self):
        """Test token estimation with unicode characters."""
        # Each unicode char still counts as 1 character in Python
        text = "你好世界🚀"  # 5 characters
        tokens = estimate_tokens(text)
        assert tokens == 1  # 5 // 4 = 1

    def test_estimate_tokens_single_char(self):
        """Test token estimation for single character."""
        tokens = estimate_tokens("a")
        assert tokens == 1  # max(1, 1 // 4)

    def test_estimate_tokens_three_chars(self):
        """Test token estimation for strings less than 4 chars."""
        tokens = estimate_tokens("abc")
        assert tokens == 1  # max(1, 3 // 4)

    def test_estimate_tokens_realistic_log_line(self):
        """Test token estimation for a realistic log line."""
        log_line = (
            '{"timestamp":"2024-01-01T10:00:00Z","level":"INFO",'
            '"source":"app.main","message":"Application started"}'
        )
        tokens = estimate_tokens(log_line)
        # Length is ~107 chars, so ~26-27 tokens
        assert tokens > 20
        assert tokens < 30


# ============================================================================
# chunk_logs Tests - Normal Scenarios
# ============================================================================


@pytest.mark.unit
class TestChunkLogsNormal:
    """Tests for chunk_logs with normal scenarios."""

    @patch("logpilot.chunker.tqdm", side_effect=lambda x, **kwargs: x)
    def test_chunk_logs_single_chunk(self, mock_tqdm, sample_log_entries):
        """Test chunking when all entries fit in a single chunk."""
        # With high max_tokens, everything should fit in one chunk
        chunks = chunk_logs(sample_log_entries, max_tokens=10000)

        assert len(chunks) == 1
        assert len(chunks[0]) == len(sample_log_entries)
        assert chunks[0] == sample_log_entries

    @patch("logpilot.chunker.tqdm", side_effect=lambda x, **kwargs: x)
    def test_chunk_logs_multiple_chunks(self, mock_tqdm, sample_log_entries):
        """Test chunking when entries need to be split into multiple chunks."""
        # With low max_tokens, should create multiple chunks
        chunks = chunk_logs(sample_log_entries, max_tokens=50)

        assert len(chunks) > 1
        # Verify all entries are preserved
        total_entries = sum(len(chunk) for chunk in chunks)
        assert total_entries == len(sample_log_entries)

    @patch("logpilot.chunker.tqdm", side_effect=lambda x, **kwargs: x)
    def test_chunk_logs_preserves_order(self, mock_tqdm, sample_log_entries):
        """Test that chunking preserves the order of entries."""
        chunks = chunk_logs(sample_log_entries, max_tokens=100)

        # Flatten chunks and verify order is preserved
        flattened = []
        for chunk in chunks:
            flattened.extend(chunk)

        assert flattened == sample_log_entries

    @patch("logpilot.chunker.tqdm", side_effect=lambda x, **kwargs: x)
    def test_chunk_logs_no_entries_lost(self, mock_tqdm, sample_log_entries):
        """Test that no entries are lost during chunking."""
        chunks = chunk_logs(sample_log_entries, max_tokens=75)

        # Count total entries across all chunks
        total = sum(len(chunk) for chunk in chunks)
        assert total == len(sample_log_entries)

        # Verify each original entry appears exactly once
        flattened = []
        for chunk in chunks:
            flattened.extend(chunk)

        for entry in sample_log_entries:
            assert entry in flattened

    @patch("logpilot.chunker.tqdm", side_effect=lambda x, **kwargs: x)
    def test_chunk_logs_respects_token_limit(self, mock_tqdm, sample_log_entries):
        """Test that chunks approximately respect the token limit."""
        max_tokens = 100
        chunks = chunk_logs(sample_log_entries, max_tokens=max_tokens)

        for chunk in chunks:
            # Calculate actual tokens in chunk
            chunk_tokens = sum(estimate_tokens(entry.raw) for entry in chunk)
            # Should not significantly exceed the limit
            # Note: Last entry might push it slightly over, that's acceptable
            assert chunk_tokens <= max_tokens * 2  # Generous bound for edge cases


# ============================================================================
# chunk_logs Tests - Boundary Conditions
# ============================================================================


@pytest.mark.unit
class TestChunkLogsBoundary:
    """Tests for boundary conditions in chunk_logs."""

    @patch("logpilot.chunker.tqdm", side_effect=lambda x, **kwargs: x)
    def test_chunk_logs_empty_list(self, mock_tqdm):
        """Test chunking an empty list of entries."""
        chunks = chunk_logs([], max_tokens=1000)
        assert len(chunks) == 0

    @patch("logpilot.chunker.tqdm", side_effect=lambda x, **kwargs: x)
    def test_chunk_logs_single_entry(self, mock_tqdm):
        """Test chunking a single entry."""
        entry = LogEntry(
            timestamp="2024-01-01",
            level="INFO",
            source="test",
            message="Test",
            raw="Test message",
        )
        chunks = chunk_logs([entry], max_tokens=1000)

        assert len(chunks) == 1
        assert len(chunks[0]) == 1
        assert chunks[0][0] == entry

    @patch("logpilot.chunker.tqdm", side_effect=lambda x, **kwargs: x)
    def test_chunk_logs_single_entry_exceeds_limit(self, mock_tqdm):
        """Test chunking when a single entry exceeds max_tokens."""
        # Create an entry with a very long raw string
        long_text = "x" * 1000  # This will estimate to 250 tokens
        entry = LogEntry(
            timestamp="2024-01-01",
            level="INFO",
            source="test",
            message="Long message",
            raw=long_text,
        )

        # Set max_tokens lower than the entry's token count
        chunks = chunk_logs([entry], max_tokens=50)

        # Should still create a chunk with that entry
        assert len(chunks) == 1
        assert len(chunks[0]) == 1
        assert chunks[0][0] == entry

    @patch("logpilot.chunker.tqdm", side_effect=lambda x, **kwargs: x)
    def test_chunk_logs_all_entries_exceed_limit(self, mock_tqdm):
        """Test when all entries individually exceed the token limit."""
        # Create entries that each exceed the limit
        entries = [
            LogEntry(
                timestamp=f"2024-01-0{i}",
                level="INFO",
                source="test",
                message=f"Entry {i}",
                raw="x" * 1000,  # 250 tokens each
            )
            for i in range(3)
        ]

        chunks = chunk_logs(entries, max_tokens=50)

        # Each entry should be in its own chunk
        assert len(chunks) == 3
        for chunk in chunks:
            assert len(chunk) == 1

    @patch("logpilot.chunker.tqdm", side_effect=lambda x, **kwargs: x)
    def test_chunk_logs_exact_boundary(self, mock_tqdm):
        """Test chunking when entries exactly hit the token boundary."""
        # Create entries that exactly fit the limit
        entries = [
            LogEntry(
                timestamp=f"2024-01-0{i}",
                level="INFO",
                source="test",
                message=f"Entry {i}",
                raw="x" * 40,  # 10 tokens each
            )
            for i in range(10)
        ]

        # With 50 token limit, should get 5 entries per chunk (50 tokens)
        chunks = chunk_logs(entries, max_tokens=50)

        # Should create 2 chunks
        assert len(chunks) == 2
        assert len(chunks[0]) == 5
        assert len(chunks[1]) == 5

    @patch("logpilot.chunker.tqdm", side_effect=lambda x, **kwargs: x)
    def test_chunk_logs_very_low_token_limit(self, mock_tqdm, sample_log_entries):
        """Test chunking with a very low token limit."""
        chunks = chunk_logs(sample_log_entries, max_tokens=10)

        # Should create many chunks
        assert len(chunks) > 0
        # All entries should still be preserved
        total = sum(len(chunk) for chunk in chunks)
        assert total == len(sample_log_entries)

    @patch("logpilot.chunker.tqdm", side_effect=lambda x, **kwargs: x)
    def test_chunk_logs_max_tokens_zero(self, mock_tqdm, sample_log_entries):
        """Test chunking with max_tokens of zero."""
        # With max_tokens=0, should still create chunks (one entry per chunk)
        chunks = chunk_logs(sample_log_entries, max_tokens=0)

        # Each entry should be in its own chunk
        assert len(chunks) == len(sample_log_entries)
        for chunk in chunks:
            assert len(chunk) == 1


# ============================================================================
# chunk_logs Tests - Integration and Edge Cases
# ============================================================================


@pytest.mark.unit
class TestChunkLogsEdgeCases:
    """Tests for edge cases in chunk_logs."""

    @patch("logpilot.chunker.tqdm", side_effect=lambda x, **kwargs: x)
    def test_chunk_logs_mixed_entry_sizes(self, mock_tqdm):
        """Test chunking with entries of varying sizes."""
        entries = [
            LogEntry(
                timestamp=None, level=None, source=None, message="Small", raw="x" * 10
            ),
            LogEntry(
                timestamp=None, level=None, source=None, message="Medium", raw="x" * 100
            ),
            LogEntry(
                timestamp=None, level=None, source=None, message="Large", raw="x" * 500
            ),
            LogEntry(
                timestamp=None, level=None, source=None, message="Small2", raw="x" * 10
            ),
        ]

        chunks = chunk_logs(entries, max_tokens=50)

        # Verify all entries are preserved
        total = sum(len(chunk) for chunk in chunks)
        assert total == 4

    @patch("logpilot.chunker.tqdm", side_effect=lambda x, **kwargs: x)
    def test_chunk_logs_with_empty_raw_fields(self, mock_tqdm):
        """Test chunking with entries that have empty raw fields."""
        entries = [
            LogEntry(timestamp=None, level=None, source=None, message="Test", raw=""),
            LogEntry(timestamp=None, level=None, source=None, message="Test2", raw=""),
        ]

        # Empty strings estimate to 1 token (minimum)
        chunks = chunk_logs(entries, max_tokens=10)

        assert len(chunks) >= 1
        total = sum(len(chunk) for chunk in chunks)
        assert total == 2

    @patch("logpilot.chunker.tqdm")
    def test_chunk_logs_calls_tqdm(self, mock_tqdm):
        """Test that chunk_logs calls tqdm for progress display."""
        mock_tqdm.return_value = iter([])

        entries = []
        chunk_logs(entries, max_tokens=1000)

        # Verify tqdm was called
        mock_tqdm.assert_called_once()
        call_args = mock_tqdm.call_args
        assert call_args[1]["desc"] == "Chunking logs"
        assert call_args[1]["unit"] == "entry"

    @patch("logpilot.chunker.tqdm", side_effect=lambda x, **kwargs: x)
    def test_chunk_logs_many_entries(self, mock_tqdm):
        """Test chunking with a large number of entries."""
        # Create 1000 entries
        entries = [
            LogEntry(
                timestamp=f"2024-01-01T00:00:{i:02d}",
                level="INFO",
                source="test",
                message=f"Entry {i}",
                raw=f"Entry {i}",
            )
            for i in range(1000)
        ]

        chunks = chunk_logs(entries, max_tokens=100)

        # Verify all 1000 entries are preserved
        total = sum(len(chunk) for chunk in chunks)
        assert total == 1000

        # Should have created multiple chunks
        assert len(chunks) > 1


# ============================================================================
# Integration Tests
# ============================================================================


@pytest.mark.unit
class TestChunkerIntegration:
    """Integration tests combining estimate_tokens and chunk_logs."""

    @patch("logpilot.chunker.tqdm", side_effect=lambda x, **kwargs: x)
    def test_chunking_preserves_all_data(self, mock_tqdm, sample_log_entries):
        """Test that chunking preserves all log entry data."""
        chunks = chunk_logs(sample_log_entries, max_tokens=75)

        # Flatten chunks
        flattened = []
        for chunk in chunks:
            flattened.extend(chunk)

        # Verify all attributes are preserved
        for orig, reconstructed in zip(sample_log_entries, flattened):
            assert orig.timestamp == reconstructed.timestamp
            assert orig.level == reconstructed.level
            assert orig.source == reconstructed.source
            assert orig.message == reconstructed.message
            assert orig.raw == reconstructed.raw

    @patch("logpilot.chunker.tqdm", side_effect=lambda x, **kwargs: x)
    def test_estimate_tokens_consistency(self, mock_tqdm):
        """Test that estimate_tokens gives consistent results."""
        text = "This is a test message"

        # Call multiple times
        tokens1 = estimate_tokens(text)
        tokens2 = estimate_tokens(text)
        tokens3 = estimate_tokens(text)

        assert tokens1 == tokens2 == tokens3
