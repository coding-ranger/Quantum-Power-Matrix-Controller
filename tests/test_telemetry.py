"""Unit tests for the functional telemetry pipeline."""

import pytest

from aethergrid.exceptions import TelemetryError
from aethergrid.telemetry import (
    clean_record,
    parse_record,
    process_telemetry,
    record_is_valid,
)


# ---------------------------------------------------------------------------
# Test 1 — Full pipeline with valid records
# ---------------------------------------------------------------------------

def test_pipeline_with_valid_records():
    raw = [
        "N1|100|50|0.9|40",
        "N2|200|100|0.8|50",
    ]
    result = process_telemetry(raw)

    assert result["valid_count"] == 2
    assert result["rejected_count"] == 0
    assert result["total_load"] == pytest.approx(150.0)
    assert result["max_temperature"] == pytest.approx(50.0)
    assert result["average_efficiency"] == pytest.approx(0.85)
    assert len(result["records"]) == 2


# ---------------------------------------------------------------------------
# Test 2 — Malformed records are rejected
# ---------------------------------------------------------------------------

def test_pipeline_rejects_malformed_records():
    raw = [
        "N1|100|50|0.9|40",
        "bad_record",
        "N2|200|100|0.8|50",
        "",
        "N3|100|50",
    ]
    result = process_telemetry(raw)

    assert result["valid_count"] == 2
    assert result["rejected_count"] == 3


# ---------------------------------------------------------------------------
# Test 3 — Non-numeric fields are rejected
# ---------------------------------------------------------------------------

def test_pipeline_rejects_non_numeric_fields():
    raw = [
        "N1|abc|50|0.9|40",
        "N2|200|xyz|0.8|50",
    ]
    result = process_telemetry(raw)

    assert result["valid_count"] == 0
    assert result["rejected_count"] == 2


# ---------------------------------------------------------------------------
# Test 4 — Empty input returns zeroed summary
# ---------------------------------------------------------------------------

def test_pipeline_with_empty_input():
    result = process_telemetry([])

    assert result["valid_count"] == 0
    assert result["rejected_count"] == 0
    assert result["total_load"] == 0.0
    assert result["average_efficiency"] == 0.0
    assert result["max_temperature"] == 0.0
    assert result["records"] == []


# ---------------------------------------------------------------------------
# Test 5 — All rejected returns zeroed aggregates
# ---------------------------------------------------------------------------

def test_pipeline_all_rejected():
    raw = ["bad", "worse", "still bad"]
    result = process_telemetry(raw)

    assert result["valid_count"] == 0
    assert result["rejected_count"] == 3
    assert result["average_efficiency"] == 0.0
    assert result["total_load"] == 0.0
    assert result["max_temperature"] == 0.0


# ---------------------------------------------------------------------------
# Test 6 — parse_record on valid input
# ---------------------------------------------------------------------------

def test_parse_record_valid():
    result = parse_record("N1|100|50|0.9|40")

    assert result == ("N1", "100", "50", "0.9", "40")


# ---------------------------------------------------------------------------
# Test 7 — parse_record on invalid input
# ---------------------------------------------------------------------------

def test_parse_record_invalid():
    assert parse_record("") is None
    assert parse_record("only|three|fields") is None
    assert parse_record(42) is None
    assert parse_record(None) is None


# ---------------------------------------------------------------------------
# Test 8 — record_is_valid branches
# ---------------------------------------------------------------------------

def test_record_is_valid_branches():
    assert record_is_valid(None) is False
    assert record_is_valid(("", "100", "50", "0.9", "40")) is False
    assert record_is_valid(("N1", "abc", "50", "0.9", "40")) is False
    assert record_is_valid(("N1", "100", "50", "0.9", "40")) is True


# ---------------------------------------------------------------------------
# Test 9 — clean_record output shape
# ---------------------------------------------------------------------------

def test_clean_record_output_shape():
    cleaned = clean_record(("N1", "100", "50", "0.9", "40"))

    assert cleaned["node_id"] == "N1"
    assert cleaned["capacity"] == 100.0
    assert cleaned["load"] == 50.0
    assert cleaned["efficiency"] == 0.9
    assert cleaned["temperature"] == 40.0

    assert isinstance(cleaned["node_id"], str)
    assert isinstance(cleaned["capacity"], float)
    assert isinstance(cleaned["load"], float)
    assert isinstance(cleaned["efficiency"], float)
    assert isinstance(cleaned["temperature"], float)


# ---------------------------------------------------------------------------
# Test 10 — Invalid input type raises
# ---------------------------------------------------------------------------

def test_pipeline_non_list_input_raises():
    with pytest.raises(TelemetryError):
        process_telemetry("not a list")

    with pytest.raises(TelemetryError):
        process_telemetry(None)

    with pytest.raises(TelemetryError):
        process_telemetry(42)