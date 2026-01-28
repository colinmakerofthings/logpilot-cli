import os
from typing import Iterator


def read_logs(path: str) -> Iterator[str]:
    """Yield log lines from a single file."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"No such file: {path}")
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            yield line.rstrip("\n")
