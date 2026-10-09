import pytest

from aethergrid.enums import NodeStatus, NodeType, DecayMode, SecurityLevel, LogLevel 

"""Unit tests for Aethergrid enums"""

# Member count tests
def test_node_status_member_count():
    assert len(NodeStatus) == 5

def test_node_type_member_count():
    assert len(NodeType) == 2

def test_decay_mode_member_count():
    assert len(DecayMode) == 3

def test_security_level_member_count():
    assert len(SecurityLevel) == 4

def test_log_level_member_count():
    assert len(LogLevel) == 5



#Value Lookup tests

def test_node_status_lookup_online():
    assert NodeStatus("ONLINE") is NodeStatus.online

def test_node_status_lookup_degraded():
    assert NodeStatus("DEGRADED") is NodeStatus.degraded

def test_node_type_lookup_quantum():
    assert NodeType("QUANTUM") is NodeType.quantum

def test_node_security_level_lookup_admin():
    assert SecurityLevel(2) is SecurityLevel.admin

def test_node_log_level_lookup_error():
    assert LogLevel(40) is LogLevel.error


# Invalid Value Test

def test_node_status_invalid_value_raises():
    with pytest.raises(ValueError):
        NodeStatus("BROKEN")

def test_node_type_invalid_value_raises():
    with pytest.raises(ValueError):
        NodeType("HYBRID")

def test_node_decay_mode_invalid_value_raises():
    with pytest.raises(ValueError):
        DecayMode("SINE")

def test_node_security_level_invalid_value_raises():
    with pytest.raises(ValueError):
        SecurityLevel(99)

def test_node_log_level_invalid_value_raises():
    with pytest.raises(ValueError):
        LogLevel(0)

# Ordering

def test_security_level_ordering():
    assert SecurityLevel.admin.value > SecurityLevel.user.value

# Checking if is_operational

def test_is_operational_true_for_online():
    assert NodeStatus.online.is_operational() is True   

def test_is_operational_false_for_offline():
    assert NodeStatus.offline.is_operational() is False

def test_is_operational_false_for_maintenance():
    assert NodeStatus.maintenance.is_operational() is False



