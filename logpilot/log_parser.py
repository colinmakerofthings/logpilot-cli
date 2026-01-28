import json
from typing import Iterator, Optional


class LogEntry:
    def __init__(
        self,
        timestamp: Optional[str],
        level: Optional[str],
        source: Optional[str],
        message: str,
        raw: str,
    ):
        self.timestamp = timestamp
        self.level = level
        self.source = source
        self.message = message
        self.raw = raw


def parse_log_line(line: str, fmt: str = "auto") -> Optional[LogEntry]:
    """
    Parse a log line into a LogEntry. Supports 'json' and 'text'.
    Returns None if not valid.
    """
    stripped = line.strip()
    if not stripped:
        return None
    if fmt == "json" or (fmt == "auto" and stripped.startswith("{")):
        try:
            data = json.loads(line)
            return LogEntry(
                timestamp=data.get("timestamp"),
                level=data.get("level"),
                source=data.get("source"),
                message=data.get("message", str(data)),
                raw=line,
            )
        except Exception:
            return None
    # Fallback: treat as plain text only if it looks like a log
    # (very basic: must have at least 2 commas)
    if "," in stripped and stripped.count(",") >= 2:
        return LogEntry(timestamp=None, level=None, source=None, message=line, raw=line)
    return None


def parse_logs(lines: Iterator[str], fmt: str = "auto") -> Iterator[LogEntry]:
    for line in lines:
        entry = parse_log_line(line, fmt)
        if entry is not None:
            yield entry
