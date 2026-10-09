"""
Unit tests for the AetherGrid CLI entry point.
"""

import pytest

from aethergrid.main import main
from aethergrid.security import hash_password


# ---------------------------------------------------------------------------
# Test 1 — No arguments prints usage
# ---------------------------------------------------------------------------

def test_no_arguments_prints_usage(capsys):
    code = main([])
    captured = capsys.readouterr()

    assert code == 0
    assert "usage" in captured.out.lower()


# ---------------------------------------------------------------------------
# Test 2 — help command prints usage
# ---------------------------------------------------------------------------

def test_help_command_prints_usage(capsys):
    code = main(["help"])
    captured = capsys.readouterr()

    assert code == 0
    assert "usage" in captured.out.lower()


# ---------------------------------------------------------------------------
# Test 3 — Unknown command returns 1
# ---------------------------------------------------------------------------

def test_unknown_command_returns_error(capsys):
    code = main(["not_a_command"])
    captured = capsys.readouterr()

    assert code == 1
    assert "unknown" in captured.out.lower()


# ---------------------------------------------------------------------------
# Test 4 — load-config with valid file
# ---------------------------------------------------------------------------

def test_load_config_command(tmp_path, capsys):
    config_file = tmp_path / "config.txt"
    config_file.write_text(
        "log_level=INFO\n"
        "max_cycles=100\n",
        encoding="utf-8",
    )

    code = main(["load-config", str(config_file)])
    captured = capsys.readouterr()

    assert code == 0
    assert "INFO" in captured.out
    assert "100" in captured.out


# ---------------------------------------------------------------------------
# Test 5 — load-config with missing file returns 1
# ---------------------------------------------------------------------------

def test_load_config_missing_file_returns_error(capsys):
    code = main(["load-config", "no_such_file.txt"])
    captured = capsys.readouterr()

    assert code == 1
    assert "error" in captured.out.lower()


# ---------------------------------------------------------------------------
# Test 6 — telemetry with valid file
# ---------------------------------------------------------------------------

def test_telemetry_command(tmp_path, capsys):
    telemetry_file = tmp_path / "telemetry.txt"
    telemetry_file.write_text(
        "N1|100|50|0.9|40\n"
        "N2|200|100|0.8|50\n",
        encoding="utf-8",
    )

    code = main(["telemetry", str(telemetry_file)])
    captured = capsys.readouterr()

    assert code == 0
    assert "total_load" in captured.out
    assert "150" in captured.out


# ---------------------------------------------------------------------------
# Test 7 — telemetry with missing file returns 1
# ---------------------------------------------------------------------------

def test_telemetry_missing_file_returns_error(capsys):
    code = main(["telemetry", "no_such_telemetry.txt"])
    captured = capsys.readouterr()

    assert code == 1
    assert "error" in captured.out.lower()


# ---------------------------------------------------------------------------
# Test 8 — authenticate with correct credentials
# ---------------------------------------------------------------------------

def test_authenticate_success(tmp_path, capsys):
    creds_file = tmp_path / "credentials.txt"
    creds_file.write_text(
        "alice=" + hash_password("wonderland") + "\n",
        encoding="utf-8",
    )

    code = main(["authenticate", str(creds_file), "alice", "wonderland"])
    captured = capsys.readouterr()

    assert code == 0
    assert "authenticated" in captured.out.lower()


# ---------------------------------------------------------------------------
# Test 9 — authenticate with wrong password returns 1
# ---------------------------------------------------------------------------

def test_authenticate_wrong_password_returns_error(tmp_path, capsys):
    creds_file = tmp_path / "credentials.txt"
    creds_file.write_text(
        "alice=" + hash_password("wonderland") + "\n",
        encoding="utf-8",
    )

    code = main(["authenticate", str(creds_file), "alice", "wrong"])
    captured = capsys.readouterr()

    assert code == 1
    assert "error" in captured.out.lower()


# ---------------------------------------------------------------------------
# Test 10 — authenticate with unknown user returns 1
# ---------------------------------------------------------------------------

def test_authenticate_unknown_user_returns_error(tmp_path, capsys):
    creds_file = tmp_path / "credentials.txt"
    creds_file.write_text(
        "alice=" + hash_password("wonderland") + "\n",
        encoding="utf-8",
    )

    code = main(["authenticate", str(creds_file), "bob", "wonderland"])
    captured = capsys.readouterr()

    assert code == 1
    assert "error" in captured.out.lower()


# ---------------------------------------------------------------------------
# Test 11 — decay with valid inputs
# ---------------------------------------------------------------------------

def test_decay_command(capsys):
    code = main(["decay", "100.0", "0.5", "3", "EXPONENTIAL"])
    captured = capsys.readouterr()

    assert code == 0
    assert "12.5" in captured.out


# ---------------------------------------------------------------------------
# Test 12 — decay accepts lowercase mode
# ---------------------------------------------------------------------------

def test_decay_lowercase_mode(capsys):
    code = main(["decay", "100.0", "0.5", "3", "exponential"])
    captured = capsys.readouterr()

    assert code == 0
    assert "12.5" in captured.out


# ---------------------------------------------------------------------------
# Test 13 — decay with bad numeric input returns 1
# ---------------------------------------------------------------------------

def test_decay_bad_numeric_returns_error(capsys):
    code = main(["decay", "abc", "0.5", "3", "EXPONENTIAL"])
    captured = capsys.readouterr()

    assert code == 1
    assert "error" in captured.out.lower()


# ---------------------------------------------------------------------------
# Test 14 — decay with bad mode returns 1
# ---------------------------------------------------------------------------

def test_decay_bad_mode_returns_error(capsys):
    code = main(["decay", "100", "0.5", "3", "SINE"])
    captured = capsys.readouterr()

    assert code == 1
    assert "mode" in captured.out.lower()


# ---------------------------------------------------------------------------
# Test 15 — funds with valid amounts
# ---------------------------------------------------------------------------

def test_funds_command(capsys):
    code = main(["funds", "100", "50", "25"])
    captured = capsys.readouterr()

    assert code == 0
    assert "125" in captured.out


# ---------------------------------------------------------------------------
# Test 16 — funds with overdraft returns 1
# ---------------------------------------------------------------------------

def test_funds_overdraft_returns_error(capsys):
    code = main(["funds", "100", "0", "500"])
    captured = capsys.readouterr()

    assert code == 1
    assert "error" in captured.out.lower()


# ---------------------------------------------------------------------------
# Test 17 — funds with bad numeric input returns 1
# ---------------------------------------------------------------------------

def test_funds_bad_numeric_returns_error(capsys):
    code = main(["funds", "abc", "50", "25"])
    captured = capsys.readouterr()

    assert code == 1
    assert "error" in captured.out.lower()


# ---------------------------------------------------------------------------
# Test 18 — Commands with wrong argument count return 1
# ---------------------------------------------------------------------------

def test_commands_with_wrong_arg_count(capsys):
    assert main(["load-config"]) == 1
    assert main(["telemetry"]) == 1
    assert main(["authenticate", "only_one"]) == 1
    assert main(["authenticate", "a", "b"]) == 1
    assert main(["funds", "100"]) == 1
    assert main(["funds", "100", "50"]) == 1
    assert main(["decay", "100"]) == 1
    assert main(["decay", "100", "0.5", "3"]) == 1

    