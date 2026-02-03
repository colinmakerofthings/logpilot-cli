import fnmatch
import os
from typing import Iterable, Iterator, Optional, Sequence


def read_logs(path: str) -> Iterator[str]:
    """Yield log lines from a single file."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"No such file: {path}")
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            yield line.rstrip("\n")


def iter_log_files(
    path: str,
    recursive: bool = False,
    include: Optional[Sequence[str]] = None,
    exclude: Optional[Sequence[str]] = None,
) -> Iterator[str]:
    """Yield log file paths from a file or directory."""
    include = include or ["*"]
    exclude = exclude or []

    def matches(patterns: Sequence[str], rel_path: str, name: str) -> bool:
        for pattern in patterns:
            if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(name, pattern):
                return True
        return False

    if os.path.isfile(path):
        rel_path = os.path.basename(path)
        if matches(include, rel_path, rel_path) and not matches(
            exclude, rel_path, rel_path
        ):
            yield path
        return

    if not os.path.isdir(path):
        raise FileNotFoundError(f"No such file or directory: {path}")

    files: list[str] = []
    if recursive:
        for root, _, filenames in os.walk(path):
            for name in filenames:
                full_path = os.path.join(root, name)
                rel_path = os.path.relpath(full_path, path)
                if matches(include, rel_path, name) and not matches(
                    exclude, rel_path, name
                ):
                    files.append(full_path)
    else:
        for name in os.listdir(path):
            full_path = os.path.join(path, name)
            if not os.path.isfile(full_path):
                continue
            rel_path = os.path.relpath(full_path, path)
            if matches(include, rel_path, name) and not matches(
                exclude, rel_path, name
            ):
                files.append(full_path)

    files.sort()
    for file_path in files:
        yield file_path


def read_logs_from_paths(paths: Iterable[str]) -> Iterator[str]:
    """Yield log lines from multiple files in order."""
    for path in paths:
        yield from read_logs(path)
