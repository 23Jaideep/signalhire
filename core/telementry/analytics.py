from core.telementry.analyzer import (
    compute_time_between_runs,
    compute_recovery,
    compute_scope_violations,
    compute_composite,
    interpret_iteration,
    interpret_adaptability,
    interpret_recovery,
)


def compute_session_analytics(events):

    core_runs = 0
    mutation_runs = 0

    core_passed = False
    mutation_passed = False

    core_start = None
    mutation_start = None

    time_to_core_pass = None
    time_to_mutation_pass = None

    # -----------------------------
    # Scan all test runs
    # -----------------------------
    for e in events:

        if e["event_type"] != "test_run":
            continue

        if e["phase"] == "core":

            core_runs += 1

            if core_start is None:
                core_start = e["timestamp"]

            if e["passed"]:
                core_passed = True

                if time_to_core_pass is None:
                    time_to_core_pass = (
                        e["timestamp"] - core_start
                    )

        elif e["phase"] == "mutation":

            mutation_runs += 1

            if mutation_start is None:
                mutation_start = e["timestamp"]

            if e["passed"]:
                mutation_passed = True

                if time_to_mutation_pass is None:
                    time_to_mutation_pass = (
                        e["timestamp"] - mutation_start
                    )

    # -----------------------------
    # Analytics
    # -----------------------------
    time_between_runs = compute_time_between_runs(events)

    recoveries = compute_recovery(events)

    scope = compute_scope_violations(events)

    summary = {
        "core_runs": core_runs,
        "mutation_runs": mutation_runs,
        "time_to_core_pass": time_to_core_pass,
        "time_to_mutation_pass": time_to_mutation_pass,
        "recovery": recoveries,
    }

    # -----------------------------
    # Behavioral Scores
    # -----------------------------
    scores = compute_composite(events, summary)

    # Overall Iteration Efficiency
    valid_scores = [
        s
        for s in [
            scores["iteration_core"],
            scores["iteration_mutation"],
        ]
        if s is not None
    ]

    overall_iteration = (
        sum(valid_scores) / len(valid_scores)
        if valid_scores
        else None
    )

    scores["iteration"] = overall_iteration

    # -----------------------------
    # Behavioral Interpretation
    # -----------------------------
    interpretation = {
        "iteration": interpret_iteration(overall_iteration),
        "adaptability": interpret_adaptability(
            scores["adaptability"]
        ),
        "recovery": interpret_recovery(
            scores["recovery"]
        ),
    }

    # -----------------------------
    # Final Response
    # -----------------------------
    return {
        "core_runs": core_runs,
        "mutation_runs": mutation_runs,
        "core_passed": core_passed,
        "mutation_passed": mutation_passed,
        "time_between_runs": time_between_runs,
        "recovery": recoveries,
        "scope": scope,
        "scores": scores,
        "interpretation": interpretation,
    }