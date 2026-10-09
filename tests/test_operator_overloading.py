import pytest
from aethergrid.node import BaseNode, QuantumNode
from aethergrid.enums import NodeStatus

"""Tests for __add__ and __radd__ on BaseNode and QuantumNode."""


# FIXTURES

@pytest.fixture
def base_a():
    return BaseNode("A", capacity=100.0, load=50.0,
                    efficiency=0.9, temperature=40.0)

@pytest.fixture
def base_b():
    return BaseNode("B", capacity=200.0, load=100.0,
                    efficiency=0.8, temperature=50.0)

@pytest.fixture
def quantum_a():
    return QuantumNode("QA", capacity=300.0, load=150.0,
                       efficiency=0.95, temperature=35.0,
                       coherence=0.85, entanglement_pairs=16,
                       qubit_stability=0.9, decoherence_rate=0.02)

@pytest.fixture
def quantum_b():
    return QuantumNode("QB", capacity=400.0, load=200.0,
                       efficiency=0.9, temperature=45.0,
                       coherence=0.75, entanglement_pairs=24,
                       qubit_stability=0.8, decoherence_rate=0.05)


# RESULT TYPE IN ALL FOUR COMBINATIONS

def test_base_plus_base_returns_base(base_a, base_b):
    result = base_a + base_b
    assert isinstance(result, BaseNode)
    assert not isinstance(result, QuantumNode)

def test_quantum_plus_quantum_returns_quantum(quantum_a, quantum_b):
    result = quantum_a + quantum_b
    assert isinstance(result, QuantumNode)

def test_base_plus_quantum_returns_quantum(base_a, quantum_a):
    result = base_a + quantum_a
    assert isinstance(result, QuantumNode)

def test_quantum_plus_base_returns_quantum(quantum_a, base_a):
    result = quantum_a + base_a
    assert isinstance(result, QuantumNode)




# COMBINED VALUES

def test_capacity_is_sum(base_a, base_b):
    result = base_a + base_b
    assert result.capacity == base_a.capacity + base_b.capacity

def test_load_is_sum(base_a, base_b):
    result = base_a + base_b
    assert result.load == base_a.load + base_b.load

def test_temperature_is_max(base_a, base_b):
    result = base_a + base_b
    assert result.temperature == max(base_a.temperature, base_b.temperature)

def test_efficiency_is_weighted_average(base_a, base_b):
    total = base_a.capacity + base_b.capacity
    expected = (base_a.efficiency * base_a.capacity + base_b.efficiency * base_b.capacity) / total
    result = base_a + base_b
    assert result.efficiency == pytest.approx(expected)

def test_entanglement_pairs_is_sum(quantum_a, quantum_b):
    result = quantum_a + quantum_b
    assert result.entanglement_pairs == (quantum_a.entanglement_pairs + quantum_b.entanglement_pairs)

def test_combined_status_is_combined(base_a, base_b):
    result = base_a + base_b
    assert result.status is NodeStatus.combined

def test_combined_node_id_concatenates(base_a, base_b):
    result = base_a + base_b
    assert result.node_id == "A+B"


# COMMUTATIVITY

def test_addition_commutative_base(base_a, base_b):
    ab = base_a + base_b
    ba = base_b + base_a
    assert ab.capacity == ba.capacity
    assert ab.load == ba.load
    assert ab.efficiency == ba.efficiency
    assert ab.temperature == ba.temperature

def test_addition_commutative_quantum(quantum_a, quantum_b):
    ab = quantum_a + quantum_b
    ba = quantum_b + quantum_a
    assert ab.capacity == ba.capacity
    assert ab.entanglement_pairs == ba.entanglement_pairs
    assert ab.coherence == ba.coherence
    assert ab.qubit_stability == ba.qubit_stability

def test_addition_commutative_mixed(base_a, quantum_a):
    ab = base_a + quantum_a
    ba = quantum_a + base_a
    assert isinstance(ab, QuantumNode)
    assert isinstance(ba, QuantumNode)
    assert ab.capacity == ba.capacity
    assert ab.load == ba.load
    assert ab.entanglement_pairs == ba.entanglement_pairs



# IMMUTABILITY


def test_add_does_not_mutate_left(base_a, base_b):
    snapshot = base_a.to_dict()
    base_a + base_b
    assert base_a.to_dict() == snapshot

def test_add_does_not_mutate_right(base_a, base_b):
    snapshot = base_b.to_dict()
    base_a + base_b
    assert base_b.to_dict() == snapshot

def test_add_quantum_does_not_mutate_operands(quantum_a, quantum_b):
    snap_a = quantum_a.to_dict()
    snap_b = quantum_b.to_dict()
    quantum_a + quantum_b
    assert quantum_a.to_dict() == snap_a
    assert quantum_b.to_dict() == snap_b



# NotImplemented AND TypeError

def test_base_add_int_returns_not_implemented(base_a):
    assert base_a.__add__(42) is NotImplemented

def test_quantum_add_int_returns_not_implemented(quantum_a):
    assert quantum_a.__add__(42) is NotImplemented

def test_base_add_string_raises_type_error(base_a):
    with pytest.raises(TypeError):
        base_a + "not a node"

def test_quantum_add_none_raises_type_error(quantum_a):
    with pytest.raises(TypeError):
        quantum_a + None

def test_base_add_list_raises_type_error(base_a):
    with pytest.raises(TypeError):
        base_a + [1, 2, 3]


# __radd__ BEHAVIOR

def test_radd_delegates_to_add(quantum_a, base_a):
    direct = quantum_a.__add__(base_a)
    radd = quantum_a.__radd__(base_a)
    assert direct.capacity == radd.capacity
    assert direct.load == radd.load
    assert direct.entanglement_pairs == radd.entanglement_pairs

def test_base_plus_quantum_uses_radd(base_a, quantum_a):
    result = base_a + quantum_a
    assert isinstance(result, QuantumNode)
    assert result.capacity == base_a.capacity + quantum_a.capacity
    assert result.entanglement_pairs == quantum_a.entanglement_pairs


# CHAINED ADDITION

def test_chained_base_addition(base_a, base_b):
    c = BaseNode("C", capacity=150.0, load=75.0,
                 efficiency=0.85, temperature=45.0)
    result = base_a + base_b + c
    assert isinstance(result, BaseNode)
    assert result.capacity == 450.0
    assert result.load == 225.0


def test_chained_with_quantum_promotes_result(base_a, base_b, quantum_a):
    result = base_a + base_b + quantum_a
    assert isinstance(result, QuantumNode)
    assert result.entanglement_pairs == quantum_a.entanglement_pairs

def test_base_added_to_itself(base_a):
    result = base_a + base_a
    assert result.capacity == 2 * base_a.capacity
    assert result.load == 2 * base_a.load
    assert result is not base_a


def test_quantum_added_to_itself(quantum_a):
    result = quantum_a + quantum_a
    assert result.entanglement_pairs == 2 * quantum_a.entanglement_pairs
    assert result.coherence == pytest.approx(quantum_a.coherence)
    assert result is not quantum_a






    