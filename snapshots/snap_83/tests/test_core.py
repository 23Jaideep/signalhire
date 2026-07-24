import pytest
from tasks.log_parser_v1.src.parser import parse_log_line
from tasks.log_parser_v1.src.aggregator import LogAggregator


# -------- parse_log_line --------

def test_parse_valid_line():
    line = "2026-02-15T12:00:00 | user_1 | 200 | 100"
    result = parse_log_line(line)

    assert result["timestamp"] == "2026-02-15T12:00:00"
    assert result["user_id"] == "user_1"
    assert result["status_code"] == 200
    assert result["response_time"] == 100.0


def test_parse_invalid_format():
    with pytest.raises(ValueError):
        parse_log_line("invalid line")


def test_parse_non_string():
    with pytest.raises(TypeError):
        parse_log_line(123)


def test_parse_negative_response_time():
    with pytest.raises(ValueError):
        parse_log_line("2026-02-15T12:00:00 | user_1 | 200 | -10")


# -------- compute_error_rate --------

def test_error_rate():
    logs = [
        {"timestamp": "2026-02-15T12:00:00", "user_id": "u1", "status_code": 200, "response_time": 100},
        {"user_id": "u1", "status_code": 500, "response_time": 100}
    ]
    agg = LogAggregator(logs)
    assert agg.error_rate() == 0.5


def test_error_rate_empty():
    agg = LogAggregator([])
    assert agg.error_rate() == 0.0


# -------- compute_avg_response_time --------

def test_avg_response_time():
    logs = [
        {"timestamp": "2026-02-15T12:00:00", "user_id": "u1", "status_code": 200, "response_time": 100},
        {"user_id": "u1", "status_code": 200, "response_time": 300}
    ]
    agg = LogAggregator(logs)
    assert agg.avg_response_time() == 200.0


def test_avg_response_time_empty():
    agg = LogAggregator([])
    assert agg.avg_response_time() == 0.0


# -------- count_unique_users --------

def test_unique_users():
    logs = [
        {"timestamp": "2026-02-15T12:00:00", "user_id": "u1", "status_code": 200, "response_time": 100},
        {"timestamp": "2026-02-15T12:00:01", "user_id": "u2", "status_code": 200, "response_time": 100},
        {"timestamp": "2026-02-15T12:00:02", "user_id": "u1", "status_code": 200, "response_time": 100}
    ]
    agg = LogAggregator(logs)
    assert agg.unique_users() == 2


def test_unique_users_empty():
    logs =[]
    agg = LogAggregator(logs)
    assert agg.unique_users() == 0

def test_parse_non_numeric_status():
    with pytest.raises(ValueError):
        parse_log_line("2026 | user | abc | 100")

def test_parse_non_numeric_response():
    with pytest.raises(ValueError):
        parse_log_line("2026 | user | 200 | fast")

def test_parse_extra_delimiters():
    with pytest.raises(ValueError):
        parse_log_line("2026 | user | 200 | 100 | extra | extra")

def test_error_rate_all_errors():
    logs = [
        {"timestamp": "2026-02-15T12:00:00", "user_id": "u1", "status_code": 500, "response_time": 100},
        {"timestamp": "2026-02-15T12:00:01", "user_id": "u2", "status_code": 400, "response_time": 150},
    ]
    agg = LogAggregator(logs)
    assert agg.error_rate() == 1.0

def test_parse_zero_response_time():
    result = parse_log_line("2026-02-15T12:00:00 | user_1 | 200 | 0")
    assert result["response_time"] == 0.0

def test_state_leakage():
    a1 = LogAggregator()
    a2 = LogAggregator()

    a1.add_log({"status_code": 500, "response_time": 100, "user_id": "u1"})

    assert a2.error_rate() == 0.0


