import os
from typing import Any, Dict

from aethergrid.exceptions import ConfigError


def load_config(path: str) -> Dict[str, Any]:
    """
    Read and parse a configuration file.

    """
    if not isinstance(path, str) or not path:
        raise ConfigError("path must be a non-empty string")

    expanded = os.path.expanduser(path)

    try:
        with open(expanded, "r", encoding="utf-8") as handle:
            raw = handle.read()
    except FileNotFoundError:
        raise ConfigError(f"config file not found: {expanded}")
    except PermissionError:
        raise ConfigError(f"permission denied: {expanded}")
    except OSError as exc:
        raise ConfigError(f"could not read config: {exc}")

    return _parse_config(raw)


def _parse_config(raw: str) -> Dict[str, Any]:
    """
    Parse raw configuration text into a dictionary.

    """
    result: Dict[str, Any] = {}

    lines = [
        line.strip()
        for line in raw.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    for line in lines:
        if "=" not in line:
            raise ConfigError(f"invalid config line: {line}")

        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()

        if not key:
            raise ConfigError(f"empty key in config line: {line}")

        result[key] = _coerce_value(value)

    return result


def _coerce_value(value: str) -> Any:
    """
    Convert a string value to ``int``, ``float``, ``bool``, or ``str``.

    """
    lowered = value.lower()

    if lowered == "true":
        return True
    if lowered == "false":
        return False

    try:
        return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        pass

    return value