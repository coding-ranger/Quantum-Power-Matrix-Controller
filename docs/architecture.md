# Architecture

## Overview

AetherGrid is organized in three layers. Lower layers never import
from higher layers.



## Layer 1 — Domain Model

### enums.py

Type-safe constants. Replaces magic strings and numbers across the
project. Contains `NodeStatus`, `NodeType`, `DecayMode`,
`SecurityLevel`, and `LogLevel`. String values for statuses (readable
in logs), int values for ordered scales (comparable with `>`).

### exceptions.py

A single root `AetherGridError` with specific subclasses:
`NodeError`, `InvalidNodeError`, `IncompatibleNodeError`,
`RecursionLimitError`, `TelemetryError`, `ConfigError`,
`AuthenticationError`, `InsufficientFundsError`.

The CLI catches only `AetherGridError` at the top level. Every other
module raises the narrowest applicable subclass.

### nodes.py

`BaseNode` models a standard hardware node with `node_id`, `capacity`,
`load`, `efficiency`, `temperature`, `status`, and two thresholds.
It exposes six computed properties (`current_power`,
`available_capacity`, `load_factor`, `is_healthy`, `health_score`,
`to_dict`) and four methods (`scale`, `update_load`,
`update_efficiency`, `generate_health_report`).

`QuantumNode` inherits from `BaseNode` and adds `coherence`,
`entanglement_pairs`, `qubit_stability`, and `decoherence_rate`. It
overrides `is_healthy`, `health_score`, `to_dict`, `scale`,
`generate_health_report`, `__add__`, and `__radd__`.

## Polymorphism Contract

Any function accepting a `BaseNode` accepts a `QuantumNode`. The
result type of addition follows the more specific operand:




Addition is commutative and never mutates operands.

## Operator Overloading

`BaseNode.__add__` returns `NotImplemented` for non-node operands.
Python then tries `other.__radd__(self)`. `QuantumNode.__radd__`
delegates to `__add__`. This follows Python's standard operator
protocol and requires no special cases in caller code.

## Immutability

All node methods return new instances. `scale`, `update_load`,
`update_efficiency`, and `__add__` never mutate `self` or `other`.
This makes chained operations safe and testing trivial.

## Layer 2 — Logic

### diagnostics.py

`log_matrix_calculation` wraps a function and logs entry, exit,
arguments, result, elapsed milliseconds, and any exception. It uses
`functools.wraps` to preserve metadata and re-raises exceptions after
logging. The decorator is applied to pipeline entry points only, not
to trivial helpers.

### recursion.py

`harmonic_decay` computes final amplitude after a number of decay
cycles. It supports `LINEAR`, `EXPONENTIAL`, and `QUADRATIC` modes.
Two base cases: zero cycles and amplitude at the floor. One recursive
call per step, decrementing cycles. `MAX_CYCLES` guards against
Python's recursion limit.

### telemetry.py

`process_telemetry` parses, filters, cleans, and aggregates raw
telemetry strings using `map`, `filter`, and `reduce`. No `for` or
`while` loops for filtering, cleaning, or summing. The entry point is
decorated with `log_matrix_calculation`.

### funds.py

`create_fund_manager` returns a dictionary of closures that hold
balance and history in the enclosing scope. `deposit` and `withdraw`
mutate state via `nonlocal` and are decorated for logging.
`get_history` returns copies to prevent external mutation.

## Layer 3 — I/O and CLI

### config.py

`load_config` reads a `key=value` file using `with open(...)`,
expands `~`, and coerces values to `int`, `float`, `bool`, or `str`.
All I/O failures raise `ConfigError`.

### security.py

`hash_password` returns a `salt$digest` string using `os.urandom`
and SHA-256. `verify_credentials` uses `hmac.compare_digest` to
prevent timing attacks and raises a generic `AuthenticationError` for
both unknown users and wrong passwords. `load_credentials` parses a
credentials file with the same format as config.

### main.py

`main(argv=None)` reads `sys.argv[1:]` if `argv` is not provided,
dispatches on `argv[0]`, and calls the correct handler. Each handler
validates its argument count and returns an exit code. The top-level
`try` catches `AetherGridError` and generic `Exception`, prints a
single-line message, and returns `1`. No traceback ever reaches the
user.

## Error Strategy

- Validate at the boundary.
- Raise domain-specific exceptions, never bare `Exception`.
- Catch only what you can handle at each layer.
- Wrap OS-level errors (`OSError`, `FileNotFoundError`,
  `PermissionError`) in domain exceptions.
- Never log or print secrets.

## Testing Strategy

- One test file per source module.
- Separate file for operator overloading.
- Fixtures for reusable node construction.
- `tmp_path` for all file-based tests.
- `capsys` for all CLI tests.
- Coverage target: 90% overall, 95% on `nodes.py`,
  `telemetry.py`, and `security.py`.


