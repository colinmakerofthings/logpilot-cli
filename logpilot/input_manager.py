import os
from typing import Iterator


def read_logs(path: str) -> Iterator[str]:
    """Yield log lines from a file, directory, or stdin."""
    if path == "-":
        import sys
        for line in sys.stdin:
            yield line.rstrip("\n")
    elif os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                yield line.rstrip("\n")
    elif os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        yield line.rstrip("\n")
    else:
        raise FileNotFoundError(f"No such file or directory: {path}")
