import sqlite3
import json
import time

DB_PATH = "signalhire.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        candidate_id TEXT PRIMARY KEY,
        created_at REAL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        candidate_id TEXT,
        task_name TEXT,
        start_time REAL,
        end_time REAL,
        summary TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        timestamp REAL,
        event_type TEXT,
        phase TEXT,
        passed INTEGER,
        tests_passed INTEGER,
        diff TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_candidate(candidate_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "INSERT OR IGNORE INTO candidates VALUES (?, ?)",
        (candidate_id, time.time())
    )

    conn.commit()
    conn.close()
    
def update_session(session_id, summary):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE sessions
        SET end_time = ?, summary = ?
        WHERE session_id = ?
        """,
        (
            time.time(),
            json.dumps(summary),
            session_id
        )
    )

    conn.commit()
    conn.close()

def save_session(session):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO sessions VALUES (?, ?, ?, ?, ?, ?)",
        (
            session["session_id"],
            session["candidate_id"],
            session["task_name"],
            session["start_time"],
            session["end_time"],
            json.dumps(session["summary"])
        )
    )

    conn.commit()
    conn.close()


def save_events(events):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for e in events:
        cur.execute(
            "INSERT INTO events (session_id, timestamp, event_type, phase, passed, tests_passed, diff) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                e.get("session_id"),
                e.get("timestamp"),
                e.get("event_type"),
                e.get("phase"),
                int(e.get("passed")) if e.get("passed") is not None else None,
                e.get("tests_passed"),
                json.dumps(e.get("diff"))
            )
        )

    conn.commit()
    conn.close()


def load_session(session_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
    row = cur.fetchone()

    conn.close()

    if not row:
        return None

    return {
        "session_id": row[0],
        "candidate_id": row[1],
        "task_name": row[2],
        "start_time": row[3],
        "end_time": row[4],
        "summary": json.loads(row[5])
    }


def load_events(session_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT * FROM events WHERE session_id = ?", (session_id,))
    rows = cur.fetchall()

    conn.close()

    events = []
    for r in rows:
        events.append({
            "timestamp": r[2],
            "event_type": r[3],
            "phase": r[4],
            "passed": r[5],
            "tests_passed": r[6],
            "diff": json.loads(r[7]) if r[7] else None
        })

    return events


def load_sessions(candidate_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM sessions WHERE candidate_id = ? ORDER BY start_time",
        (candidate_id,)
    )
    rows = cur.fetchall()

    conn.close()

    sessions = []
    for r in rows:
        sessions.append({
            "session_id": r[0],
            "task_name": r[2],
            "start_time": r[3],
            "end_time": r[4],
            "summary": json.loads(r[5])
        })

    return sessions