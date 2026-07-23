from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from safetrace.source_engine.build_public_status import build
from safetrace.source_engine.engine import SourceDefinition, SnapshotStore, sha256_bytes


class SnapshotStoreTests(unittest.TestCase):
    def test_snapshot_writes_raw_payload_and_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = SourceDefinition(
                source_id="official-page",
                title="Official page",
                url="https://example.test/source",
                publisher="Example authority",
                source_type="official_status_page",
                parser="example_v1",
                expected_content_type="text/html",
            )
            store = SnapshotStore(directory)
            receipt = store.snapshot(
                source,
                fetcher=lambda _: (b"<html>official</html>", "text/html"),
                retrieved_at=datetime(2026, 7, 23, tzinfo=timezone.utc),
            )
            self.assertEqual(receipt.sha256, sha256_bytes(b"<html>official</html>"))
            self.assertFalse(receipt.changed)
            self.assertTrue((Path(directory) / receipt.raw_path).exists())

    def test_second_different_snapshot_is_marked_changed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = SourceDefinition(
                source_id="official-page",
                title="Official page",
                url="https://example.test/source",
                publisher="Example authority",
                source_type="official_status_page",
                parser="example_v1",
            )
            store = SnapshotStore(directory)
            store.snapshot(source, fetcher=lambda _: (b"v1", "text/plain"))
            second = store.snapshot(source, fetcher=lambda _: (b"v2", "text/plain"))
            self.assertTrue(second.changed)
            self.assertIsNotNone(second.previous_sha256)


class PublicStatusTests(unittest.TestCase):
    def test_seed_data_builds_expected_totals(self) -> None:
        data_dir = Path(__file__).parents[1] / "data"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "case-001.json"
            public = build(data_dir, output)
            summary = public["case"]["summary"]
            self.assertEqual(summary["implemented_satisfactorily"], 4)
            self.assertEqual(summary["partly_implemented"], 6)
            self.assertEqual(summary["not_implemented"], 4)
            self.assertEqual(len(public["case"]["recommendations"]), 14)
            self.assertTrue(output.exists())
            loaded = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(loaded["schema_version"], "safetrace.public-status/0.3")


if __name__ == "__main__":
    unittest.main()
