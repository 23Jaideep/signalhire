import time
from core.telementry.analyzer import (
    compute_time_between_runs,
    compute_recovery,
    compute_progress,
    compute_scope_violations,
    compute_iteration_efficiency,
    compute_adaptability,
    compute_recovery_score,
    compute_composite
)


class SessionTracker:
    def __init__(self):
        self.events = []
        self.start_time = time.time()

        self.core_runs = 0
        self.mutation_runs = 0

        self.core_pass_time = None
        self.mutation_pass_time = None

        self.last_passed_tests = 0
        self.regressions = 0

    def log_event(self, event: dict):
        self.events.append(event)
    
    def record_progress(self, passed_tests):
        if passed_tests < self.last_passed_tests:
         self.regressions += 1

        self.last_passed_tests = passed_tests

    def record_core_run(self, passed):
        self.core_runs += 1
        if passed and self.core_pass_time is None:
            self.core_pass_time = time.time()

    def record_mutation_run(self, passed):
        self.mutation_runs += 1
        if passed and self.mutation_pass_time is None:
            self.mutation_pass_time = time.time()

    
    def summary(self):
        base = {
            "core_runs": self.core_runs,
            "mutation_runs": self.mutation_runs,
            "regressions": self.regressions,
            "time_to_core_pass": (
                self.core_pass_time - self.start_time
                if self.core_pass_time else None
            ),
            "time_to_mutation_pass": (
                self.mutation_pass_time - self.start_time
                if self.mutation_pass_time else None
           ),
            "time_between_runs": compute_time_between_runs(self.events),
            "recovery": compute_recovery(self.events),
            "progress": compute_progress(self.events),
            "scope": compute_scope_violations(self.events),
        }

        evaluation = compute_composite(self.events, base)

        return {
            **base,
            "evaluation": evaluation
        }
