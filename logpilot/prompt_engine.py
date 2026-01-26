from typing import List

from logpilot.log_parser import LogEntry

PROMPT_TEMPLATE = (
    "You are analyzing application logs.\n"
    "Logs:\n{chunk}\n"
    "Tasks:\n"
    "1. Identify critical issues\n"
    "2. Explain likely causes\n"
    "3. Suggest next debugging steps\n"
)


def format_prompt(chunk: List[LogEntry]) -> str:
    chunk_text = "\n".join(entry.raw for entry in chunk)
    return PROMPT_TEMPLATE.format(chunk=chunk_text)
