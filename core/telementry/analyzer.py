# ---- Time Between Runs ----
def compute_time_between_runs(events):
    times = [
        e["timestamp"]
        for e in events
        if e["event_type"] == "test_run"
    ]

    if len(times) < 2:
        return None

    intervals = [
        times[i] - times[i-1]
        for i in range(1, len(times))
    ]

    return {
        "avg": sum(intervals) / len(intervals),
        "min": min(intervals),
        "max": max(intervals)
    }


# ---- Recovery ----
def compute_recovery(events):
    recoveries = []
    last_pass_time = None
    in_regression = False

    for e in events:
        if e["event_type"] != "test_run":
            continue

        if e["passed"]:
            if in_regression:
                recoveries.append(e["timestamp"] - last_pass_time)
                in_regression = False
            last_pass_time = e["timestamp"]

        else:
            if last_pass_time is not None:
                in_regression = True

    return recoveries


# ---- Progress ----
def compute_progress(events):
    progress = [
        e["tests_passed"]
        for e in events
        if e["event_type"] == "test_run"
    ]

    if len(progress) < 2:
        return None

    improvements = sum(
        1 for i in range(1, len(progress))
        if progress[i] > progress[i-1]
    )

    return {
        "improvements": improvements,
        "final": progress[-1],
        "max": max(progress)
    }


# ---- Scope Discipline ----
ALLOWED_FILES = {"parser.py", "aggregator.py"}

def compute_scope_violations(events):
    violations = []

    for e in events:
        if e["event_type"] != "test_run":
            continue

        for f in e["diff"]["files_changed"]:
            if f not in ALLOWED_FILES:
                violations.append(f)

    return {
        "count": len(violations),
        "files": list(set(violations))
    }

def compute_iteration_efficiency(events, phase="core"):
    test_runs = [
        e for e in events
        if e["event_type"] == "test_run" and e["phase"] == phase
    ]

    if len(test_runs) < 2:
        return None

    improvements = 0

    for i in range(1, len(test_runs)):
        if test_runs[i]["tests_passed"] > test_runs[i-1]["tests_passed"]:
            improvements += 1

    return improvements / (len(test_runs) - 1)

def compute_adaptability(summary):
    core_time = summary.get("time_to_core_pass")
    mutation_time = summary.get("time_to_mutation_pass")

    if not core_time or not mutation_time:
        return None

    return core_time / mutation_time

def compute_recovery_score(recoveries):
    if not recoveries:
        return None

    avg_recovery = sum(recoveries) / len(recoveries)

    return 1 / (1 + avg_recovery)

def compute_composite(events, summary):
    return {
        "iteration_core": compute_iteration_efficiency(events, "core"),
        "iteration_mutation": compute_iteration_efficiency(events, "mutation"),
        "adaptability": compute_adaptability(summary),
        "recovery": compute_recovery_score(summary.get("recovery")),
    }