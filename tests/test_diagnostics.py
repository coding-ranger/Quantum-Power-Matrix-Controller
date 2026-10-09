import pytest
import logging
from aethergrid.diagnostics import log_matrix_calculation

"""Tests for diagnostic decorators."""


def test_wrapped_function_returns_result():
    @log_matrix_calculation
    def simple_function():
        return "expected_value"
        
    assert simple_function() == "expected_value"


# METADATA PRESERVED

def test_wraps_preserves_name_and_docstring():
    @log_matrix_calculation
    def compute():
        """Compute something."""
        return 42

    assert compute.__name__ == "compute"
    assert compute.__doc__ == "Compute something."



# SUCCESS IS LOGGED

def test_success_is_logged(caplog):
    caplog.set_level(logging.INFO, logger="aethergrid.diagnostics")
    
    @log_matrix_calculation
    def compute():
        return 42
        
    compute()
    
    assert "Entering" in caplog.text
    assert "Exiting" in caplog.text
    assert "42" in caplog.text


# EXCEPTION IS LOGGED AND RE-RAISED

def test_exception_is_logged_and_reraised(caplog):
    caplog.set_level(logging.ERROR, logger="aethergrid.diagnostics")
    
    @log_matrix_calculation
    def explode():
        raise ValueError("bad input")
        
    with pytest.raises(ValueError):
        explode()
        
    assert "Exception" in caplog.text
    assert "ValueError" in caplog.text
    assert "bad input" in caplog.text


# ARGUMENTS ARE LOGGED

def test_arguments_are_logged(caplog):
    caplog.set_level(logging.INFO, logger="aethergrid.diagnostics")
    
    @log_matrix_calculation
    def add(a, b):
        return a + b
        
    add(1, 2)
    
    assert "1" in caplog.text
    assert "2" in caplog.text


# TIMING IS LOGGED

def test_timing_is_logged(caplog):
    caplog.set_level(logging.INFO, logger="aethergrid.diagnostics")
    
    @log_matrix_calculation
    def compute():
        return 42
        
    compute()
    
    assert "elapsed_ms" in caplog.text

    




