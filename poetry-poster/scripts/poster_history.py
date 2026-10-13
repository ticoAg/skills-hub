#!/usr/bin/env python3
"""Track accepted poster compositions; stdlib only, no image/API calls."""

import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import unicodedata

AXES = (
    "layout", "viewpoint", "subject_relation", "scale",
    "medium", "lighting", "typography",
)
SPATIAL = AXES[:4]
SCHEMA_VERSION = 1


def validate_plan(plan):
    if not isinstance(plan, dict):
        raise ValueError("plan must be a JSON object")
    if not isinstance(plan.get("poem"), str) or not plan["poem"].strip():
        raise ValueError("poem must be nonempty text")
    if not normalized_poem(plan["poem"]):
        raise ValueError("poem must contain more than whitespace or punctuation")
    anchors = plan.get("anchors")
    if not isinstance(anchors, list) or not 2 <= len(anchors) <= 4:
        raise ValueError("anchors must contain 2–4 semantic anchors")
    if any(not isinstance(x, str) or not x.strip() for x in anchors):
        raise ValueError("anchors must be nonempty strings")
    axes = plan.get("axes")
    if not isinstance(axes, dict) or set(axes) != set(AXES):
        raise ValueError("axes must contain exactly: " + ", ".join(AXES))
    if any(not isinstance(x, str) or not x.strip() or x != x.strip()
           for x in axes.values()):
        raise ValueError("axis values must be nonempty, trimmed stable labels")
    locked = plan.get("locked_axes", [])
    if not isinstance(locked, list) or any(x not in AXES for x in locked):
        raise ValueError("locked_axes must be a list of known axis names")
    if len(locked) != len(set(locked)):
        raise ValueError("locked_axes must not contain duplicates")
    return plan


def normalized_poem(poem):
    return "".join(
        c for c in unicodedata.normalize("NFKC", poem)
        if not c.isspace() and not unicodedata.category(c).startswith("P")
    )


def poem_key(poem):
    return hashlib.sha256(normalized_poem(poem).encode("utf-8")).hexdigest()


def load_plan(path):
    return validate_plan(json.loads(Path(path).read_text(encoding="utf-8")))


def verify_schema(conn):
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    if version != SCHEMA_VERSION:
        raise ValueError(f"unsupported history schema version {version}; expected 1")


def initialize(conn):
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    if version == 0:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        if tables:
            raise ValueError("refusing to initialize an unrelated SQLite database")
        conn.execute("""CREATE TABLE posters (
            id INTEGER PRIMARY KEY,
            created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
            poem_key TEXT NOT NULL,
            plan_json TEXT NOT NULL,
            artifact TEXT NOT NULL
        )""")
        conn.execute("CREATE INDEX posters_poem ON posters(poem_key, id)")
        conn.execute("PRAGMA user_version = 1")
    else:
        verify_schema(conn)


def decode_rows(rows):
    result = []
    for row in rows:
        plan = validate_plan(json.loads(row[2]))
        result.append({"id": row[0], "created_at": row[1],
                       "plan": plan, "artifact": row[3]})
    return result


def selected_history(conn, key=None, limit=20):
    rows = conn.execute(
        "SELECT id, created_at, plan_json, artifact FROM posters ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    if key is not None:
        same = conn.execute(
            "SELECT id, created_at, plan_json, artifact FROM posters "
            "WHERE poem_key=? ORDER BY id DESC LIMIT 3", (key,),
        ).fetchall()
        rows = sorted({row[0]: row for row in rows + same}.values(),
                      key=lambda row: row[0], reverse=True)
    return decode_rows(rows)


def read_history(db, key=None, limit=20):
    path = Path(db).resolve()
    if not path.exists():
        return []
    conn = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    try:
        verify_schema(conn)
        return selected_history(conn, key, limit)
    finally:
        conn.close()


def analyze(plan, history):
    validate_plan(plan)
    unlocked = [axis for axis in AXES if axis not in plan.get("locked_axes", [])]
    conflicts = []
    for previous in history:
        changed = [axis for axis in unlocked
                   if plan["axes"][axis] != previous["plan"]["axes"][axis]]
        spatial_changed = [axis for axis in changed if axis in SPATIAL]
        if len(changed) < 3 or not spatial_changed:
            conflicts.append({
                "history_id": previous["id"],
                "same_poem": poem_key(plan["poem"]) == poem_key(previous["plan"]["poem"]),
                "changed_axes": changed,
                "spatial_changed_axes": spatial_changed,
                "reason": "require >=3 unlocked changes including >=1 spatial change",
            })
    return {
        "accepted": not conflicts,
        "history_count": len(history),
        "unlocked_axes": unlocked,
        "conflicts": conflicts,
        "note": "composition heuristic only; inspect poetry fidelity, typography and actual images",
    }


def check(db, plan):
    validate_plan(plan)
    return analyze(plan, read_history(db, poem_key(plan["poem"])))


def record(db, plan, artifact):
    validate_plan(plan)
    if not isinstance(artifact, str) or not artifact.strip():
        raise ValueError("artifact must identify an actually generated and accepted image")
    path = Path(db).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=30, isolation_level=None)
    try:
        conn.execute("BEGIN IMMEDIATE")
        initialize(conn)
        report = analyze(plan, selected_history(conn, poem_key(plan["poem"])))
        if not report["accepted"]:
            conn.rollback()
            return report
        cursor = conn.execute(
            "INSERT INTO posters(poem_key, plan_json, artifact) VALUES (?,?,?)",
            (poem_key(plan["poem"]), json.dumps(plan, ensure_ascii=False), artifact.strip()),
        )
        conn.commit()
        report["record_id"] = cursor.lastrowid
        return report
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("list", "check", "record"):
        command = commands.add_parser(name)
        command.add_argument("--db", required=True)
        if name == "list":
            command.add_argument("--limit", type=int, default=20)
        else:
            command.add_argument("--plan", required=True)
        if name == "record":
            command.add_argument("--artifact", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "list":
            if not 1 <= args.limit <= 200:
                raise ValueError("limit must be between 1 and 200")
            result = {"records": read_history(args.db, limit=args.limit)}
        else:
            plan = load_plan(args.plan)
            result = (check(args.db, plan) if args.command == "check"
                      else record(args.db, plan, args.artifact))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("accepted", True) else 2
    except (OSError, ValueError, TypeError, sqlite3.Error) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
