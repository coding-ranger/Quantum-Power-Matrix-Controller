import pytest

from aethergrid.enums import DecayMode
from aethergrid.exceptions import RecursionLimitError
from aethergrid.recursion import harmonic_decay


def test_zero_cycles_returns_initial_amplitude():
    result = harmonic_decay(100.0, 0.9, 0, DecayMode.exponential)
    assert result == 100.0


def test_exponential_decay_over_cycles():
    result = harmonic_decay(100.0, 0.5, 3, DecayMode.exponential)
    assert result == pytest.approx(12.5)


def test_linear_decay_over_cycles():
    result = harmonic_decay(100.0, 10.0, 3, DecayMode.linear)
    assert result == pytest.approx(70.0)


def test_quadratic_decay_over_cycles():
    result = harmonic_decay(100.0, 5.0, 3, DecayMode.quadratic)
    assert result == pytest.approx(70.0)


def test_amplitude_never_goes_negative():
    result = harmonic_decay(10.0, 100.0, 5, DecayMode.linear)
    assert result == 0.0


def test_cycles_above_max_raises():
    with pytest.raises(RecursionLimitError):
        harmonic_decay(100.0, 0.9, 2000, DecayMode.exponential)


def test_negative_amplitude_raises():
    with pytest.raises(RecursionLimitError):
        harmonic_decay(-1.0, 0.9, 3, DecayMode.exponential)


def test_negative_cycles_raises():
    with pytest.raises(RecursionLimitError):
        harmonic_decay(100.0, 0.9, -1, DecayMode.exponential)


def test_zero_damping_factor_raises():
    with pytest.raises(RecursionLimitError):
        harmonic_decay(100.0, 0.0, 3, DecayMode.exponential)


def test_negative_damping_factor_raises():
    with pytest.raises(RecursionLimitError):
        harmonic_decay(100.0, -0.5, 3, DecayMode.exponential)


def test_invalid_mode_raises():
    with pytest.raises(RecursionLimitError):
        harmonic_decay(100.0, 0.9, 3, "exponential")