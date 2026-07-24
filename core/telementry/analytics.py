from core.telementry.analyzer import (
    compute_time_between_runs,
    compute_recovery,
    compute_scope_violations,
)

def compute_session_analytics(events):
    core_runs = 0
    mutation_runs = 0

    core_passed = False
    mutation_passed = False

    for e in events:
        if e["event_type"] != "test_run":
            continue

        if e["phase"] == "core":
            core_runs += 1
            if e["passed"]:
                core_passed = True

        elif e["phase"] == "mutation":
            mutation_runs += 1
            if e["passed"]:
                mutation_passed = True

    return {
        "core_runs": core_runs,
        "mutation_runs": mutation_runs,
        "core_passed": core_passed,
        "mutation_passed": mutation_passed,
        "time_between_runs": compute_time_between_runs(events),
        "recovery": compute_recovery(events),
        "scope": compute_scope_violations(events),
    }