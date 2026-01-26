from typing import Iterator, Optional, Dict, Any
import json

class LogEntry:
	def __init__(self, timestamp: Optional[str], level: Optional[str], source: Optional[str], message: str, raw: str):
		self.timestamp = timestamp
		self.level = level
		self.source = source
		self.message = message
		self.raw = raw


def parse_log_line(line: str, fmt: str = 'auto') -> LogEntry:
	"""Parse a log line into a LogEntry. Supports 'json' and 'text'."""
	if fmt == 'json' or (fmt == 'auto' and line.strip().startswith('{')):
		try:
			data = json.loads(line)
			return LogEntry(
				timestamp=data.get('timestamp'),
				level=data.get('level'),
				source=data.get('source'),
				message=data.get('message', str(data)),
				raw=line
			)
		except Exception:
			pass
	# Fallback: treat as plain text
	return LogEntry(
		timestamp=None,
		level=None,
		source=None,
		message=line,
		raw=line
	)

def parse_logs(lines: Iterator[str], fmt: str = 'auto') -> Iterator[LogEntry]:
	for line in lines:
		yield parse_log_line(line, fmt)
