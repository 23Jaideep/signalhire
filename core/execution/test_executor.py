import subprocess
import time
from core.telementry import tracker
from core.telementry.tracker import SessionTracker
import re
from core.telementry.snapshot import create_snapshot
from core.telementry.diff_analyzer import compute_diff
import os
import yaml
import uuid
from core.storage.db import (
    init_db,
    save_candidate,
    save_events,
    update_session,
    load_events,
)
from core.telementry.analytics import compute_session_analytics

def run_tests(file):
    result = subprocess.run(
        ["pytest", file, "-q"],
        capture_output=True,
        text=True
    )
    output = result.stdout

    lines = output.splitlines()

    lines = [
        line for line in lines
        if not re.match(r"^\.+\s*\[\d+%\]\s*$", line)
    ]

    output = "\n".join(lines)
    print(output)   # <-- add this line
    print(result.stderr)
    return result.returncode, output

import re

def extract_passed_tests(output):
    match = re.search(r"(\d+) passed", output)
    if match:
        return int(match.group(1))
    return 0

def load_task_config(task_path):
        with open(f"{task_path}/task.yaml", "r") as f:
            return yaml.safe_load(f)

def run_session(
    session_id,
    task_id,
    candidate_id,
    files,
    phase
):
    init_db()  
    tracker = SessionTracker()
    task_path = f"uploaded_tasks/{task_id}"
    import sys

    if task_path not in sys.path:
        sys.path.insert(0, task_path)
    for relative_path, content in files.items():
        full_path = os.path.join(task_path, relative_path)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
    config = load_task_config(task_path)

    core_test = config["entry_tests"]
    mutation_test = config["mutation_tests"]
    snapshot_base = "snapshots"
    os.makedirs(snapshot_base, exist_ok=True)

    snap_id = 1
    prev_snapshot = f"{snapshot_base}/snap_{snap_id}"
    create_snapshot(task_path, prev_snapshot)
    start = time.time()

    # -------- Phase 1: Core --------
    if phase == "core":
        code, output = run_tests(f"{task_path}/{core_test}")

        snap_id += 1
        new_snapshot = f"{snapshot_base}/snap_{snap_id}"

        create_snapshot(task_path, new_snapshot)

        tracker.log_event({
        "session_id": session_id,
        "timestamp": time.time(),
        "event_type": "edit_snapshot",
        "snapshot_id": snap_id
        }) 

        diff = compute_diff(prev_snapshot, new_snapshot)

        print("Telemetry diff:", diff)

        prev_snapshot = new_snapshot

        passed_tests = extract_passed_tests(output)
        tracker.record_progress(passed_tests)

        passed = (code == 0)
        tracker.record_core_run(passed)

        tracker.log_event({
        "session_id": session_id,
        "timestamp": time.time(),
        "event_type": "test_run",
        "phase": "core",
        "passed": passed,
        "tests_passed": passed_tests,
        "diff": diff
        })

        end = time.time()

        save_candidate(candidate_id)

        print("EVENTS:", tracker.events)

        save_events(tracker.events)

        events = load_events(session_id)

        summary = compute_session_analytics(events)

        update_session(session_id, summary)

        print("SUMMARY SAVED:", summary)

        return {
            "phase": "core",
            "passed": passed,
            "output": output,
            "summary": summary
        }

    # -------- Phase 2: Mutation --------
    if phase == "mutation":
        mutation_code, mutation_output = run_tests(f"{task_path}/{mutation_test}")

        snap_id += 1
        new_snapshot = f"{snapshot_base}/snap_{snap_id}"

        create_snapshot(task_path, new_snapshot)

        tracker.log_event({
            "session_id": session_id,
            "timestamp": time.time(),
            "event_type": "edit_snapshot",
            "snapshot_id": snap_id
        })

        diff = compute_diff(prev_snapshot, new_snapshot)

        prev_snapshot = new_snapshot

        passed_mutation_tests = extract_passed_tests(mutation_output)

        tracker.record_progress(passed_mutation_tests)

        passed = (mutation_code == 0)

        tracker.record_mutation_run(passed)

        tracker.log_event({
            "session_id": session_id,
            "timestamp": time.time(),
            "event_type": "test_run",
            "phase": "mutation",
            "passed": passed,
            "tests_passed": passed_mutation_tests,
            "diff": diff
        })
        end = time.time()
        save_candidate(candidate_id)

        print("EVENTS:", tracker.events)

        save_events(tracker.events)

        events = load_events(session_id)

        summary = compute_session_analytics(events)

        update_session(session_id, summary)

        print("SUMMARY SAVED:", summary)

        return {
            "phase": "mutation",
            "passed": passed,
            "output": mutation_output,
            "summary": summary
        }

#     end = time.time()

#     print("\nTotal session time:", end - start)
#     summary = tracker.summary()

#     session = {
#         "session_id": session_id,
#         "candidate_id": candidate_id,
#         "task_name": task_path,
#         "start_time": start,
#         "end_time": end,
#         "summary": summary
#     }

#     save_candidate(candidate_id)
#     save_session(session)
#     save_events(tracker.events)

#     print(summary)
#     final_passed = (
#     tracker.core_pass_time is not None and
#     tracker.mutation_pass_time is not None
# )
#     return {
#     "phase": "mutation",
#     "passed": passed,
#     "output": mutation_output,
#     "summary": summary
# }


