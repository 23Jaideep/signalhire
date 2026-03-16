import shutil
import os
from pathlib import Path


def handle_remove_error(func, path, exc_info):
    os.chmod(path, 0o777)
    func(path)


def create_snapshot(src_dir: str, snapshot_dir: str):
    src = Path(src_dir)
    dest = Path(snapshot_dir)

    if dest.exists():
        shutil.rmtree(dest, onerror=handle_remove_error)

    shutil.copytree(
        src,
        dest,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
    )