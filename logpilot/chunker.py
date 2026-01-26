from typing import List

from logpilot.log_parser import LogEntry


# Dummy token estimation (replace with real logic if needed)
def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def chunk_logs(entries: List[LogEntry], max_tokens: int) -> List[List[LogEntry]]:
    chunks = []
    current = []
    tokens = 0
    for entry in entries:
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
