class LogAggregator:
    def __init__(self, logs=[]):
        self.logs = logs

    def add_log(self, log: dict):
        self.logs.append(log)

    def error_rate(self) -> float:
        if not self.logs:
            return 0.0
        errors = sum(1 for log in self.logs if log["status_code"]  > 400)
        return errors / len(self.logs)

    def avg_response_time(self) -> float:
        if not self.logs:
            return 0.0
        total = sum(log["response_time"] for log in self.logs)
        return total / len(self.logs)

    def unique_users(self) -> int:
        return len({log["user_id"] for log in self.logs})

