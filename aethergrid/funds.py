from typing import Any, Callable, Dict, List

from aethergrid.diagnostics import log_matrix_calculation
from aethergrid.exceptions import InsufficientFundsError


def create_fund_manager(
    initial_balance: float = 0.0,
) -> Dict[str, Callable]:
    """Create a fund manager with private balance and history."""

    if not isinstance(initial_balance, (int, float)):
        raise InsufficientFundsError("initial_balance must be a number")
    if initial_balance < 0:
        raise InsufficientFundsError("initial_balance must be non-negative")

    _balance: float = float(initial_balance)
    _history: List[Dict[str, Any]] = []

    @log_matrix_calculation
    def deposit(amount: float) -> float:

        """Add funds to the balance."""

        nonlocal _balance
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise InsufficientFundsError("deposit amount must be positive")
        _balance += amount
        _history.append({
            "operation": "deposit",
            "amount": float(amount),
            "balance": _balance,
        })
        return _balance

    @log_matrix_calculation
    def withdraw(amount: float) -> float:
        
        """Remove funds from the balance.
        """
        nonlocal _balance
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise InsufficientFundsError("withdraw amount must be positive")
        if amount > _balance:
            raise InsufficientFundsError("insufficient funds for withdrawal")
        _balance -= amount
        _history.append({
            "operation": "withdraw",
            "amount": float(amount),
            "balance": _balance,
        })
        return _balance

    def get_balance() -> float:
        """Return the current balance."""
        return _balance

    def get_history() -> List[Dict[str, Any]]:
        """Return a shallow copy of the transaction history."""
        return [dict(entry) for entry in _history]

    return {
        "deposit": deposit,
        "withdraw": withdraw,
        "get_balance": get_balance,
        "get_history": get_history,
    }