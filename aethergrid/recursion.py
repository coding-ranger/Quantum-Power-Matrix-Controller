from aethergrid.enums import DecayMode
from aethergrid.exceptions import RecursionLimitError

MAX_CYCLES = 1000
AMPLITUDE_FLOOR = 0.0

def harmonic_decay(amplitude: float,
    damping_factor: float,
    cycles: int,
    mode: DecayMode,) -> float:
    """Compute the final amplitude after recursive decay."""
    if amplitude < 0:
        raise RecursionLimitError("amplitude must be non-negative")
    
    if damping_factor <= 0:
        raise RecursionLimitError("damping_factor must be positive")
    
    if cycles < 0:
        raise RecursionLimitError("cycles must be non-negative")
    
    if cycles > MAX_CYCLES:
        raise RecursionLimitError("cycles exceeds safe limit")
    
    if not isinstance(mode, DecayMode):
        raise RecursionLimitError("mode must be a DecayMode member")
    
    return _decay_step(amplitude, damping_factor, cycles, mode)


def _decay_step(
    amplitude: float,
    damping_factor: float,
    cycles: int,
    mode: DecayMode,
) -> float:
    
    """Internal recursive step for harmonic decay."""

    if  cycles == 0:
        return amplitude
    
    if amplitude <= AMPLITUDE_FLOOR:
        return AMPLITUDE_FLOOR
    
    if mode is DecayMode.linear:
        next_amplitude = amplitude - damping_factor

    elif mode is DecayMode.exponential:
        next_amplitude = amplitude * damping_factor

    elif mode is DecayMode.quadratic:
        next_amplitude = amplitude - (damping_factor * cycles)

    else:
        next_amplitude = amplitude

    if next_amplitude < AMPLITUDE_FLOOR:
        next_amplitude = AMPLITUDE_FLOOR

    return _decay_step(next_amplitude, damping_factor, cycles - 1, mode)




