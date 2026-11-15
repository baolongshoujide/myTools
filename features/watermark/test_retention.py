"""Retention tests use temporary fixtures, never existing user outputs."""
import os
from pathlib import Path
import tempfile
import unittest
import asyncio
import importlib.util
import sys
from types import ModuleType
from unittest.mock import patch

from retention import RETENTION_SECONDS, cleanup_outputs


class RetentionTests(unittest.TestCase):
    def test_expiry_and_protected_folders(self):
        now = 2_000_000_000
        cutoff = now - RETENTION_SECONDS
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "outputs"
            root.mkdir()

            def task(name, folder_time, file_time=None):
                folder = root / name
                folder.mkdir()
                for filename in ("original.png", "result.png", "comparison.png", "mask.png", "report.json"):
                    file = folder / filename
                    file.write_text("fixture")
                    timestamp = folder_time if file_time is None else file_time
                    os.utime(file, (timestamp, timestamp))
                os.utime(folder, (folder_time, folder_time))
                return folder

            expired = task("a" * 32, cutoff - 1)
            boundary = task("20261101-123456", cutoff)
            fresh = task("b" * 32, cutoff + 1)
            active = task("c" * 32, cutoff - 100)
            updated = task("d" * 32, cutoff - 100, now - 1)
            unrelated = task("my-photos", cutoff - 100)
            nested = task("e" * 32, cutoff - 100)
            (nested / "user-added").mkdir()
            os.utime(nested, (cutoff - 100, cutoff - 100))
            outside = Path(temporary) / "models"
            outside.mkdir()
            (outside / "keep.txt").write_text("keep")

            removed = cleanup_outputs(root, {active.name}, now=now)
            self.assertEqual(set(removed), {expired.name, boundary.name})
            self.assertFalse(expired.exists())
            self.assertFalse(boundary.exists())
            for folder in (fresh, active, updated, unrelated, nested, outside):
                self.assertTrue(folder.exists(), folder.name)
            self.assertEqual(cleanup_outputs(root, {active.name}, now=now), [])

    def test_missing_output_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            self.assertEqual(cleanup_outputs(Path(temporary) / "missing"), [])

    def test_service_startup_and_periodic_cleanup(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            outputs = root / "outputs"
            outputs.mkdir()

            def expired_task(name):
                folder = outputs / name
                folder.mkdir()
                file = folder / "original.png"
                file.write_text("fixture")
                os.utime(file, (1, 1))
                os.utime(folder, (1, 1))
                return folder

            expired = expired_task("f" * 32)
            fake_pipeline = ModuleType("pipeline")
            fake_pipeline.ROOT = root
            fake_pipeline.WatermarkPipeline = lambda: None
            spec = importlib.util.spec_from_file_location("retention_test_server", Path(__file__).with_name("server.py"))
            server = importlib.util.module_from_spec(spec)
            with patch.dict(sys.modules, {"pipeline": fake_pipeline}):
                spec.loader.exec_module(server)
            server.CLEANUP_INTERVAL_SECONDS = 0.01

            async def exercise():
                async with server.lifespan(server.app):
                    self.assertFalse(expired.exists())
                    later = expired_task("1" * 32)
                    server.jobs[later.name] = {"status": "completed"}
                    for _ in range(100):
                        await asyncio.sleep(0.01)
                        if not later.exists():
                            break
                    self.assertFalse(later.exists())
                    self.assertNotIn(later.name, server.jobs)

            asyncio.run(exercise())


if __name__ == "__main__":
    unittest.main()
