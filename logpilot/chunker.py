from typing import List

import tiktoken
from tqdm import tqdm

from logpilot.log_parser import LogEntry

# Global encoding instance for token estimation
_encoding = None


def _get_encoding():
    """Get or create the encoding instance for token estimation."""
    global _encoding
    if _encoding is None:
        try:
            # Use cl100k_base encoding which is used by GPT-4 and GPT-3.5-turbo
            _encoding = tiktoken.get_encoding("cl100k_base")
        except Exception:  # noqa: S110
            # Catch all exceptions (network errors, file system errors, etc.)
            # and fall back to simple estimation. Tiktoken may need to download
            # encoding files, which can fail in various ways.
            pass
    return _encoding


def estimate_tokens(text: str) -> int:
    """
    Estimate the number of tokens in the given text.

    Uses tiktoken with cl100k_base encoding (GPT-4 compatible) for accurate
    token counting. Falls back to simple character-based estimation if tiktoken
    is unavailable or fails.

    Args:
            text: The text to estimate tokens for

    Returns:
            The estimated number of tokens (minimum 1)
    """
    encoding = _get_encoding()

    if encoding is not None:
        try:
            # Use tiktoken for accurate token counting
            return max(1, len(encoding.encode(text)))
        except Exception:  # noqa: S110
            # Catch all encoding errors (invalid UTF-8, memory errors, etc.)
            # and fall back to simple estimation for robustness
            pass

    # Simple fallback: approximately 4 characters per token
    return max(1, len(text) // 4)


def chunk_logs(entries: List[LogEntry], max_tokens: int) -> List[List[LogEntry]]:
    chunks = []
    current = []
    tokens = 0
    for entry in tqdm(entries, desc="Chunking logs", unit="entry"):
        entry_tokens = estimate_tokens(entry.raw)
        if tokens + entry_tokens > max_tokens and current:
            chunks.append(current)
            current = []
            tokens = 0
        current.append(entry)
        tokens += entry_tokens
    if current:
        chunks.append(current)
    return chunks
