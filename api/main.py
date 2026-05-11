import subprocess
import tempfile
import os
import sqlite3
import json
from fastapi import FastAPI
from core.storage.db import load_session, load_events, load_sessions
import uuid
import time
from core.storage.db import save_session
from core.storage.db import save_events
import time
from pathlib import Path
import yaml

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/session/start")
def start_session(data: dict):
    session_id = str(uuid.uuid4())

    session = {
        "session_id": session_id,
        "candidate_id": data["candidate_id"],
        "task_name": data["task_name"],
        "start_time": time.time(),
        "end_time": None,
        "summary": {}
    }

    save_session(session)

    return {"session_id": session_id}

@app.post("/run_tests")
def run_tests(data: dict):
    code = data["code"]
    session_id = data["session_id"]

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "solution.py")

        with open(file_path, "w") as f:
            f.write(code)

        test_code = """
from solution import add

def test_add():
    assert add(2, 3) == 5
    assert add(1, 1) == 2
"""
        test_path = os.path.join(tmpdir, "test_solution.py")
        with open(test_path, "w") as f:
            f.write(test_code)

        result = subprocess.run(
            ["pytest", test_path],
            capture_output=True,
            text=True
        )

        passed = result.returncode == 0

        # ✅ LOG EVENT HERE
        event = {
            "session_id": session_id,
            "timestamp": time.time(),
            "event_type": "test_run",
            "phase": "core",
            "passed": passed,
            "tests_passed": 2 if passed else 1,
            "diff": None
        }

        save_events([event])

        return {
            "passed": passed,
            "output": result.stdout + result.stderr
        }
    

@app.get("/session/{session_id}")
def get_session(session_id: str):
    session = load_session(session_id)
    events = load_events(session_id)

    return {
        "summary": session["summary"],
        "events": events
    }

@app.get("/candidate/{candidate_id}")
def get_candidate(candidate_id: str):
    sessions = load_sessions(candidate_id)

    return {
        "sessions": sessions
    }

@app.post("/session/end")
def end_session(data: dict):
    session_id = data["session_id"]

    # you already have tracker logic, but for now keep simple
    summary = {
        "note": "basic session complete"
    }

    conn = sqlite3.connect("signalhire.db")
    cur = conn.cursor()

    cur.execute(
        "UPDATE sessions SET end_time = ?, summary = ? WHERE session_id = ?",
        (time.time(), json.dumps(summary), session_id)
    )

    conn.commit()
    conn.close()

    return {"status": "ended"}

@app.get("/task/{task_name}")
def load_task(task_name: str):

    task_dir = Path(f"tasks/{task_name}")

    print("TASK DIR:", task_dir)

    src_dir = task_dir / "src"

    print("SRC DIR:", src_dir)

    print("SRC EXISTS:", src_dir.exists())

    files = {}

    for file in src_dir.glob("*.py"):

        print("FOUND FILE:", file)

        with open(file, "r") as f:
            files[file.name] = f.read()

    print("FILES:", files.keys())

    return {
        "task_name": task_name,
        "files": files
    }