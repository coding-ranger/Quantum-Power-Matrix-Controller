import json
import os
import sys
from typing import List, Optional

from aethergrid.config import load_config
from aethergrid.enums import DecayMode
from aethergrid.exceptions import AethergridError
from aethergrid.funds import create_fund_manager
from aethergrid.recursion import harmonic_decay
from aethergrid.security import load_credentials, verify_credentials
from aethergrid.telemetry import process_telemetry


USAGE = (
    "AetherGrid - Quantum Power Matrix Controller\n"
    "\n"
    "Usage: python -m aethergrid.main <command> [args]\n"
    "\n"
    "Commands:\n"
    "  load-config <path>                            Load and print a config file\n"
    "  telemetry <path>                              Process a telemetry file\n"
    "  authenticate <creds_path> <user> <password>   Verify credentials\n"
    "  funds <initial> <deposit> <withdraw>          Run fund operations\n"
    "  decay <amplitude> <damping> <cycles> <mode>   Compute harmonic decay\n"
    "  help                                          Show this message\n"
)


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def handle_load_config(args: List[str]) -> int:
    """Handle the ``load-config`` command."""
    if len(args) != 1:
        print("usage: load-config <path>")
        return 1

    config = load_config(args[0])
    print(json.dumps(config, indent=2))
    return 0


def handle_telemetry(args: List[str]) -> int:
    """Handle the ``telemetry`` command."""
    if len(args) != 1:
        print("usage: telemetry <path>")
        return 1

    expanded = os.path.expanduser(args[0])

    try:
        with open(expanded, "r", encoding="utf-8") as handle:
            raw = handle.read().splitlines()
    except FileNotFoundError:
        print(f"error: telemetry file not found: {expanded}")
        return 1
    except PermissionError:
        print(f"error: permission denied: {expanded}")
        return 1
    except OSError as exc:
        print(f"error: could not read telemetry: {exc}")
        return 1

    summary = process_telemetry(raw)
    print(json.dumps(summary, indent=2))
    return 0


def handle_authenticate(args: List[str]) -> int:
    """Handle the ``authenticate`` command."""
    if len(args) != 3:
        print("usage: authenticate <creds_path> <username> <password>")
        return 1

    creds_path, username, password = args

    stored = load_credentials(creds_path)
    verify_credentials(username, password, stored)

    print("authenticated")
    return 0


def handle_funds(args: List[str]) -> int:
    """Handle the ``funds`` command."""
    if len(args) != 3:
        print("usage: funds <initial> <deposit> <withdraw>")
        return 1

    try:
        initial = float(args[0])
        deposit_amount = float(args[1])
        withdraw_amount = float(args[2])
    except ValueError:
        print("error: amounts must be numeric")
        return 1

    manager = create_fund_manager(initial)
    manager["deposit"](deposit_amount)
    manager["withdraw"](withdraw_amount)

    print(f"balance: {manager['get_balance']()}")
    print("history:")
    for entry in manager["get_history"]():
        print(json.dumps(entry))
    return 0


def handle_decay(args: List[str]) -> int:
    """Handle the ``decay`` command."""
    if len(args) != 4:
        print("usage: decay <amplitude> <damping> <cycles> <mode>")
        return 1

    try:
        amplitude = float(args[0])
        damping = float(args[1])
        cycles = int(args[2])
    except ValueError:
        print("error: amplitude and damping must be numeric; cycles must be an integer")
        return 1

    try:
        mode = DecayMode(args[3].upper())
    except ValueError:
        print("error: mode must be one of: LINEAR, EXPONENTIAL, QUADRATIC")
        return 1

    result = harmonic_decay(amplitude, damping, cycles, mode)
    print(f"final amplitude: {result}")
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    """
    Run the AetherGrid CLI.

    Parameters
    ----------
    argv : Optional[List[str]]
        Argument list excluding the program name. If ``None``,
        ``sys.argv[1:]`` is used.

    Returns
    -------
    int
        Exit code: ``0`` on success, ``1`` on any failure.
    """
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) == 0:
        print(USAGE)
        return 0

    command = argv[0]
    rest = argv[1:]

    try:
        if command == "help":
            print(USAGE)
            return 0
        if command == "load-config":
            return handle_load_config(rest)
        if command == "telemetry":
            return handle_telemetry(rest)
        if command == "authenticate":
            return handle_authenticate(rest)
        if command == "funds":
            return handle_funds(rest)
        if command == "decay":
            return handle_decay(rest)

        print(f"error: unknown command: {command}")
        print(USAGE)
        return 1

    except AethergridError as exc:
        print(f"error: {exc}")
        return 1
    except Exception as exc:
        print(f"unexpected error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())