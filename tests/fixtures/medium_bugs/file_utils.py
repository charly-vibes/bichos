"""File system utility helpers.

Provides safe wrappers around common file operations: atomic writes,
recursive directory cleanup, file hashing, and temporary file management.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
from pathlib import Path


def atomic_write(path: Path, content: str, encoding: str = "utf-8") -> None:
    """Write content to path atomically via a temporary file.

    On POSIX systems this guarantees that readers never see a partially
    written file.
    """
    dir_path = path.parent
    dir_path.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=dir_path, prefix=".tmp-")
    try:
        with os.fdopen(fd, "w", encoding=encoding) as fh:
            fh.write(content)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def atomic_write_bytes(path: Path, data: bytes) -> None:
    """Byte-level atomic write."""
    dir_path = path.parent
    dir_path.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=dir_path, prefix=".tmp-")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def sha256_file(path: Path, chunk_size: int = 65536) -> str:
    """Return the hex SHA-256 digest of a file."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def ensure_dir(path: Path) -> Path:
    """Create path and all parents; return path unchanged."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def rm_tree(path: Path, ignore_errors: bool = False) -> None:
    """Recursively remove a directory tree."""
    shutil.rmtree(path, ignore_errors=ignore_errors)


def list_files(root: Path, pattern: str = "*") -> list[Path]:
    """Return all files matching pattern under root, sorted by path."""
    return sorted(p for p in root.rglob(pattern) if p.is_file())


def move_file(src: Path, dst: Path) -> Path:
    """Move src to dst, creating dst's parent directories as needed."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    return Path(shutil.move(str(src), str(dst)))


def copy_file(src: Path, dst: Path) -> Path:
    """Copy src to dst, creating dst's parent directories as needed."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    return Path(shutil.copy2(str(src), str(dst)))
