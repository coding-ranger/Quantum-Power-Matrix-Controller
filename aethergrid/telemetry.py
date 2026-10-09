from functools import reduce
from typing import List, Dict, Any, Tuple, Optional

from aethergrid.exceptions import TelemetryError
from aethergrid.diagnostics import log_matrix_calculation

"""Functional telemetry pipeline for AetherGrid."""

FIELD_COUNT = 5
FIELD_SEPARATOR = "|"


@log_matrix_calculation
def process_telemetry(raw_records: List[str]) -> Dict[str, Any]:
    """Process raw telemetry strings into a structured summary."""

    if not isinstance(raw_records, list):
        raise TelemetryError("raw_records must be a list")

    parsed = map(parse_record, raw_records)
    valid = filter(record_is_valid, parsed)
    cleaned = list(map(clean_record, valid))

    total_load = reduce(sum_load, cleaned, 0.0)

    efficiency_total, efficiency_count = reduce(
        average_efficiency, cleaned, (0.0, 0)
    )
    avg_efficiency = (
        efficiency_total / efficiency_count if efficiency_count else 0.0
    )

    max_temp = reduce(max_temperature, cleaned, 0.0)

    rejected_count = len(raw_records) - len(cleaned)

    return {
        "records": cleaned,
        "total_load": total_load,
        "average_efficiency": avg_efficiency,
        "max_temperature": max_temp,
        "valid_count": len(cleaned),
        "rejected_count": rejected_count,
    }


def parse_record(raw: str) -> Optional[Tuple[str, ...]]:
    """Split a raw telemetry string into a tuple of stripped field strings."""
    if not isinstance(raw, str):
        return None
    if not raw:
        return None

    parts = raw.split(FIELD_SEPARATOR)
    if len(parts) != FIELD_COUNT:
        return None

    return tuple(part.strip() for part in parts)


def record_is_valid(parsed: Optional[Tuple[str, ...]]) -> bool:
    """Return ``True`` if a parsed telemetry record is valid."""
    if parsed is None:
        return False

    node_id, capacity, load, efficiency, temperature = parsed

    if not node_id:
        return False

    try:
        float(capacity)
        float(load)
        float(efficiency)
        float(temperature)
    except ValueError:
        return False

    return True


def clean_record(parsed: Tuple[str, ...]) -> Dict[str, Any]:
    """Convert a parsed telemetry record into a typed dictionary."""
    node_id, capacity, load, efficiency, temperature = parsed
    return {
        "node_id": node_id,
        "capacity": float(capacity),
        "load": float(load),
        "efficiency": float(efficiency),
        "temperature": float(temperature),
    }


def sum_load(accumulator: float, record: Dict[str, Any]) -> float:
    """Add a record's load to the accumulator."""
    return accumulator + record["load"]


def average_efficiency(
    accumulator: Tuple[float, int],
    record: Dict[str, Any],
) -> Tuple[float, int]:
    """Accumulate running total and count of efficiency values."""
    total, count = accumulator
    return (total + record["efficiency"], count + 1)


def max_temperature(accumulator: float, record: Dict[str, Any]) -> float:
    """Track the highest temperature seen across cleaned records."""
    return max(accumulator, record["temperature"])


extract_load = lambda record: record["load"]
extract_temperature = lambda record: record["temperature"]
is_high_load = lambda record: record["load"] > 50.0


def extract_node_ids(records: List[Dict[str, Any]]) -> List[str]:
    """Return the list of ``node_id`` values from cleaned telemetry records."""
    return [record["node_id"] for record in records]


def filter_healthy_ids(records: List[Dict[str, Any]]) -> List[str]:
    """Return node IDs whose efficiency is at least 0.5."""
    return [
        record["node_id"]
        for record in records
        if record["efficiency"] >= 0.5
    ]