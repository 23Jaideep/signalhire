import os
import sqlite3
import json
from fastapi import FastAPI
from core.storage.db import load_session, load_events, load_sessions
import uuid
import time
from core.storage.db import save_session
from pathlib import Path
import yaml
from fastapi import UploadFile, File
import zipfile
import shutil
app = FastAPI()
from core.storage.db import init_db
init_db()
from core.execution.test_executor import run_session
from fastapi.middleware.cors import CORSMiddleware
from core.telementry.analytics import compute_session_analytics
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

    return {
        "session_id": session_id
    }

@app.post("/run_tests")
def run_tests(data: dict):

    result = run_session(
        session_id=data["session_id"],
        task_id=data["task_id"],
        candidate_id="test_user",
        files=data["files"],
        phase=data["phase"]
    )

    return result
    

@app.get("/session/{session_id}")
def get_session(session_id: str):

    session = load_session(session_id)

    if session is None:
        return {"error": "Session not found"}

    events = load_events(session_id)

    analytics = compute_session_analytics(events)

    return {
        "summary": analytics,
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

@app.get("/uploaded_task/{task_id}")
def load_uploaded_task(task_id: str):
    task_dir = Path(f"uploaded_tasks/{task_id}")
    task_yaml_path = task_dir / "task.yaml"

    with open(task_yaml_path, "r") as f:

        task_config = yaml.safe_load(f) or {}

    visible_paths = task_config.get("visible", [])
    print("TASK CONFIG:", task_config)
    print("VISIBLE PATHS:", visible_paths)
    files = {}

    for file in task_dir.rglob("*"):

         # skip folders
        if not file.is_file():
            continue

    # skip pycache
        if "__pycache__" in str(file):
            continue

    # skip binary / irrelevant files
        allowed_extensions = {
        ".py",
        ".txt",
       ".yaml",
       ".yml",
       ".json",
       ".md"
       }

        if file.suffix.lower() not in allowed_extensions:
            continue

        relative_path = file.relative_to(task_dir)
        relative_str = str(relative_path).replace("\\", "/")
        print("CHECKING FILE:", relative_str)

        allowed = False

        for visible in visible_paths:
            visible = visible.replace("\\", "/").rstrip("/")

            print("VISIBLE:", visible)
            if relative_str.startswith(visible):
                allowed = True
                break
        print("ALLOWED:", allowed)
        if not allowed:
            continue

        try:

            with open(file, "r", encoding="utf-8") as f:

                files[str(relative_path)] = f.read()

        except Exception as e:

            print("FAILED TO READ:", file, e)

    print("FILES:", files.keys())

    return {
        "task_id": task_id,
        "files": files
    }

@app.post("/upload_task")
async def upload_task(file: UploadFile = File(...)):

    # ---- create unique task id ----
    task_id = str(uuid.uuid4())

    # ---- temp zip path ----
    zip_path = f"uploaded_tasks/{task_id}.zip"

    # ---- final extraction dir ----
    extract_dir = Path(f"uploaded_tasks/{task_id}")

    # ---- save uploaded zip ----
    with open(zip_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # ---- extract zip ----
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    # ---- validation ----
    required = ["src", "tests", "task.yaml"]

    missing = []

    for item in required:

        if not (extract_dir / item).exists():
            missing.append(item)

    # ---- invalid task ----
    if missing:

        shutil.rmtree(extract_dir)

        os.remove(zip_path)

        return {
            "status": "failed",
            "missing": missing
        }

    # ---- success ----
    return {
        "status": "uploaded",
        "task_id": task_id
    }