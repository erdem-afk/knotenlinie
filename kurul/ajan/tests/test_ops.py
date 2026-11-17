"""Ops markers in KURUL_STATE_DIR read by deploy/ scripts: heartbeat and busy.json."""

import json
import time
import unittest

from ajan.worker import BUSY_FILE, HEARTBEAT_FILE

from .util import PROF_A, Harness


class Markers(Harness):
    def test_heartbeat_written_on_successful_poll(self):
        hb = self.worker.cfg.state_dir / HEARTBEAT_FILE
        self.assertFalse(hb.exists())
        before = time.time()
        self.worker.poll_once(0)
        self.assertTrue(hb.exists())
        self.assertGreaterEqual(int(hb.read_text().strip()), int(before) - 1)
        self.assertLessEqual(int(hb.read_text().strip()), int(time.time()) + 1)

    def test_no_heartbeat_when_poll_fails(self):
        hb = self.worker.cfg.state_dir / HEARTBEAT_FILE

        def boom(*a, **k):
            raise RuntimeError("site down")
        self.worker.client.events = boom
        with self.assertRaises(RuntimeError):
            self.worker.poll_once(0)
        self.assertFalse(hb.exists())

    def test_busy_marker_only_while_processing(self):
        busy = self.worker.cfg.state_dir / BUSY_FILE
        seen = []
        orig = self.worker.dispatch

        def spy(etype, p, eid):
            seen.append(json.loads(busy.read_text()))
            return orig(etype, p, eid)
        self.worker.dispatch = spy
        self.site.member_post(PROF_A, "Good morning everyone")
        self.pump()
        self.assertTrue(seen)
        self.assertEqual(seen[0]["type"], "message.created")
        self.assertIn("pid", seen[0])
        self.assertIn("event_id", seen[0])
        self.assertFalse(busy.exists())

    def test_busy_marker_removed_after_error(self):
        busy = self.worker.cfg.state_dir / BUSY_FILE

        def bad(*a):
            raise ValueError("bug")
        self.worker.dispatch = bad
        self.site.member_post(PROF_A, "hello")
        self.pump()
        self.assertFalse(busy.exists())


if __name__ == "__main__":
    unittest.main()
