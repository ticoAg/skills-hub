import copy
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "poetry-poster/scripts/poster_history.py"
SPEC = importlib.util.spec_from_file_location("poster_history", SCRIPT)
history = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(history)


def plan():
    return {
        "poem": "千山鸟飞绝，万径人踪灭。孤舟蓑笠翁，独钓寒江雪。",
        "anchors": ["群山无人无鸟", "一舟一翁独钓", "寒江雪"],
        "axes": dict(zip(history.AXES, (
            "corner-anchor", "bird-eye", "isolated-in-vastness", "tiny-in-landscape",
            "restrained-illustration", "diffuse-day", "top-horizontal",
        ))),
        "locked_axes": [],
    }


class HistoryBehavior(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / "new-output/history.sqlite3"

    def test_readonly_first_use_does_not_create_output(self):
        self.assertEqual(history.read_history(self.db), [])
        self.assertTrue(history.check(self.db, plan())["accepted"])
        self.assertFalse(self.db.parent.exists())

    def test_duplicate_and_punctuation_variant_are_rejected_without_new_record(self):
        self.assertTrue(history.record(self.db, plan(), "accepted-image-1")["accepted"])
        duplicate = plan()
        duplicate["poem"] = " 千山鸟飞绝 万径人踪灭\n孤舟蓑笠翁 独钓寒江雪 "
        report = history.record(self.db, duplicate, "duplicate-image")
        self.assertFalse(report["accepted"])
        self.assertTrue(report["conflicts"][0]["same_poem"])
        self.assertEqual(len(history.read_history(self.db)), 1)

    def test_cosmetic_changes_cannot_pass_without_spatial_change(self):
        history.record(self.db, plan(), "image-1")
        candidate = plan()
        candidate["axes"].update(medium="paper-stage", lighting="soft-dusk",
                                 typography="side-vertical")
        self.assertFalse(history.check(self.db, candidate)["accepted"])

    def test_valid_variation_preserves_poem_and_semantic_anchors(self):
        base = plan()
        history.record(self.db, base, "image-1")
        candidate = copy.deepcopy(base)
        candidate["axes"].update(layout="horizontal-bands", viewpoint="water-level",
                                 typography="side-vertical")
        self.assertTrue(history.record(self.db, candidate, "image-2")["accepted"])
        saved = history.read_history(self.db)[0]["plan"]
        self.assertEqual(saved["poem"], base["poem"])
        self.assertEqual(saved["anchors"], base["anchors"])

    def test_locked_axes_cannot_be_counted_as_variation(self):
        history.record(self.db, plan(), "image-1")
        candidate = plan()
        candidate["locked_axes"] = ["layout", "viewpoint", "typography"]
        candidate["axes"].update(layout="horizontal-bands", viewpoint="water-level",
                                 typography="side-vertical")
        self.assertFalse(history.check(self.db, candidate)["accepted"])

    def test_cross_poem_template_is_also_rejected(self):
        history.record(self.db, plan(), "image-1")
        candidate = plan()
        candidate["poem"] = "明月松间照，清泉石上流。"
        candidate["anchors"] = ["松间月光", "石上流水"]
        report = history.check(self.db, candidate)
        self.assertFalse(report["accepted"])
        self.assertFalse(report["conflicts"][0]["same_poem"])

    def test_same_poem_outside_global_window_is_still_checked(self):
        history.record(self.db, plan(), "old-image")
        # Simulate an established project with more than 20 intervening records.
        conn = sqlite3.connect(self.db)
        for i in range(25):
            later = plan()
            later["poem"] = f"独立诗文{i}"
            conn.execute("INSERT INTO posters(poem_key,plan_json,artifact) VALUES (?,?,?)",
                         (history.poem_key(later["poem"]), json.dumps(later), f"later-{i}"))
        conn.commit()
        conn.close()
        report = history.check(self.db, plan())
        self.assertEqual(report["history_count"], 21)
        self.assertTrue(any(item["same_poem"] for item in report["conflicts"]))

    def test_concurrent_duplicate_records_are_serialized(self):
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(
                lambda i: history.record(self.db, plan(), f"accepted-{i}"), [1, 2]))
        self.assertEqual(sum(x["accepted"] for x in results), 1)
        self.assertEqual(len(history.read_history(self.db)), 1)

    def test_invalid_plan_and_unrelated_database_are_not_overwritten(self):
        bad = plan()
        del bad["axes"]["layout"]
        with self.assertRaises(ValueError):
            history.record(self.db, bad, "image")
        self.assertFalse(self.db.exists())
        self.db.parent.mkdir(parents=True)
        conn = sqlite3.connect(self.db)
        conn.execute("CREATE TABLE unrelated (value TEXT)")
        conn.commit()
        conn.close()
        with self.assertRaises(ValueError):
            history.record(self.db, plan(), "image")
        conn = sqlite3.connect(self.db)
        self.assertEqual(conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall(),
                         [("unrelated",)])
        conn.close()

    def test_cli_exit_codes_and_errors(self):
        filename = Path(self.tmp.name) / "plan.json"
        filename.write_text(json.dumps(plan(), ensure_ascii=False), encoding="utf-8")
        def run(command, *extra):
            return subprocess.run([sys.executable, str(SCRIPT), command, "--db", str(self.db),
                                   "--plan", str(filename), *extra],
                                  capture_output=True, text=True, timeout=10)
        self.assertEqual(run("check").returncode, 0)
        self.assertEqual(run("record", "--artifact", "image").returncode, 0)
        rejected = run("record", "--artifact", "duplicate")
        self.assertEqual(rejected.returncode, 2)
        self.assertFalse(json.loads(rejected.stdout)["accepted"])
        filename.write_text("not json", encoding="utf-8")
        invalid = run("check")
        self.assertEqual(invalid.returncode, 1)
        self.assertIn("error", json.loads(invalid.stderr))


if __name__ == "__main__":
    unittest.main()
