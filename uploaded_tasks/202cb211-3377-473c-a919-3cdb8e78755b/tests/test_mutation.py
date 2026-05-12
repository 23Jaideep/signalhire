from tasks.log_parser_v1.src.parser import parse_log_line
from tasks.log_parser_v1.src.aggregator import LogAggregator


def test_parser_supports_optional_region():
    line = "2026-02-15T12:00:00 | user_1 | 200 | 100 | EU"
    result = parse_log_line(line)

    assert result["timestamp"] == "2026-02-15T12:00:00"
    assert result["user_id"] == "user_1"
    assert result["status_code"] == 200
    assert result["response_time"] == 100.0


def test_aggregation_still_works_with_optional_region():
    logs = [
        parse_log_line("2026-02-15T12:00:00 | user_1 | 200 | 100 | EU"),
        parse_log_line("2026-02-15T12:00:01 | user_2 | 500 | 200 | US"),
    ]

    agg = LogAggregator(logs)

    assert agg.error_rate() == 0.5
    assert agg.unique_users() == 2
