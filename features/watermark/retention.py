"""Remove expired task folders, confined to the watermark outputs directory."""
from pathlib import Path
import logging
import re
import shutil
import time

RETENTION_SECONDS = 7 * 24 * 60 * 60
TASK_FOLDER = re.compile(r"(?:[0-9a-f]{32}|\d{8}-\d{6})")
logger = logging.getLogger(__name__)


def cleanup_outputs(output_root, active_ids=(), now=None):
    root = Path(output_root).absolute()
    if root.resolve() != root:
        return []
    if not root.exists():
        return []
    cutoff = (time.time() if now is None else now) - RETENTION_SECONDS
    removed = []
    for folder in root.iterdir():
        if folder.name in active_ids or not TASK_FOLDER.fullmatch(folder.name):
            continue
        try:
            # Never follow a task-folder link or delete outside the intended root.
            if folder.is_symlink() or not folder.is_dir() or folder.resolve().parent != root:
                continue
            modified = folder.stat().st_mtime
            # Generated task files are flat. Leave unexpected nested folders or
            # links untouched rather than traversing user-added content.
            items = list(folder.iterdir())
            if any(item.is_symlink() or item.is_dir() for item in items):
                continue
            for item in items:
                modified = max(modified, item.stat().st_mtime)
            if modified > cutoff:
                continue
            shutil.rmtree(folder)
            removed.append(folder.name)
        except OSError:
            logger.exception("Could not clean expired watermark task %s; will retry", folder.name)
    return removed
