"""
Unit tests for the configuration loader.
"""

import pytest

from aethergrid.config import load_config
from aethergrid.exceptions import ConfigError


# ---------------------------------------------------------------------------
# Test 1 — Valid config file
# ---------------------------------------------------------------------------

def test_load_config_valid(tmp_path):
    config_file = tmp_path / "config.txt"
    config_file.write_text(
        "log_level=INFO\n"
        "max_cycles=100\n"
        "enabled=true\n"
        "ratio=0.5\n",
        encoding="utf-8",
    )

    result = load_config(str(config_file))

    assert result["log_level"] == "INFO"
    assert result["max_cycles"] == 100
    assert result["enabled"] is True
    assert result["ratio"] == 0.5


# ---------------------------------------------------------------------------
# Test 2 — Missing file raises ConfigError
# ---------------------------------------------------------------------------

def test_load_config_missing_file_raises():
    with pytest.raises(ConfigError):
        load_config("this_file_does_not_exist.txt")


# ---------------------------------------------------------------------------
# Test 3 — Invalid path raises ConfigError
# ---------------------------------------------------------------------------

def test_load_config_invalid_path_raises():
    with pytest.raises(ConfigError):
        load_config("")

    with pytest.raises(ConfigError):
        load_config(None)

    with pytest.raises(ConfigError):
        load_config(42)


# ---------------------------------------------------------------------------
# Test 4 — Malformed line raises ConfigError
# ---------------------------------------------------------------------------

def test_load_config_malformed_line_raises(tmp_path):
    config_file = tmp_path / "bad.txt"
    config_file.write_text(
        "valid_key=1\n"
        "this_line_has_no_equals_sign\n",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError):
        load_config(str(config_file))


# ---------------------------------------------------------------------------
# Test 5 — Comments and blank lines are ignored
# ---------------------------------------------------------------------------

def test_load_config_ignores_comments_and_blanks(tmp_path):
    config_file = tmp_path / "config.txt"
    config_file.write_text(
        "# AetherGrid config\n"
        "\n"
        "log_level=DEBUG\n"
        "   # indented comment\n"
        "\n"
        "max_cycles=50\n",
        encoding="utf-8",
    )

    result = load_config(str(config_file))

    assert result == {"log_level": "DEBUG", "max_cycles": 50}


# ---------------------------------------------------------------------------
# Test 6 — Value coercion branches
# ---------------------------------------------------------------------------

def test_load_config_value_coercion(tmp_path):
    config_file = tmp_path / "types.txt"
    config_file.write_text(
        "int_val=42\n"
        "float_val=3.14\n"
        "true_val=true\n"
        "false_val=False\n"
        "string_val=hello\n"
        "empty_val=\n",
        encoding="utf-8",
    )

    result = load_config(str(config_file))

    assert result["int_val"] == 42
    assert isinstance(result["int_val"], int)

    assert result["float_val"] == 3.14
    assert isinstance(result["float_val"], float)

    assert result["true_val"] is True
    assert result["false_val"] is False
    assert result["string_val"] == "hello"
    assert result["empty_val"] == ""


# ---------------------------------------------------------------------------
# Test 7 — Empty key raises ConfigError
# ---------------------------------------------------------------------------

def test_load_config_empty_key_raises(tmp_path):
    config_file = tmp_path / "bad.txt"
    config_file.write_text("=value_without_key\n", encoding="utf-8")

    with pytest.raises(ConfigError):
        load_config(str(config_file))