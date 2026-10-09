import pytest

from aethergrid.node import BaseNode, QuantumNode
from aethergrid.enums import NodeStatus
from aethergrid.exceptions import InvalidError


"""Unit test for BaseNode"""


# Fixtures
@pytest.fixture
def base_node():
    return BaseNode("B1", capacity=100.0, load=50.0, efficiency=0.9, temperature=40.0)


# Construction(VALID)

def test_valid_construction():
    node = BaseNode("B1", 100.0, 50.0, 0.9, 40.0)
    assert node.node_id == "B1"
    assert node.capacity == 100.0
    assert node.load == 50.0
    assert node.efficiency == 0.9
    assert node.temperature == 40.0
    assert node.status is NodeStatus.online
    assert node.max_temperature == 100.0
    assert node.min_efficiency == 0.1

def test_valid_construction_custom_status():
    node = BaseNode("B1", 100.0, 50.0, 0.9, 40.0, status=NodeStatus.maintenance)
    assert node.status is NodeStatus.maintenance


# Construction(INVALID)

def test_empty_node_id_raises():
    with pytest.raises(InvalidError):
        BaseNode("", 100.0, 50.0, 0.9, 40.0)

def test_non_string_node_id_raises():
    with pytest.raises(InvalidError):
        BaseNode(123, 100.0, 50.0, 0.9, 40.0)

def test_zero_capacity_raises():
    with pytest.raises(InvalidError):
        BaseNode("B1", 0.0, 0.0, 0.9, 40.0)

def test_negative_capacity_raises():
    with pytest.raises(InvalidError):
        BaseNode("B1", -100.0, 0.0, 0.9, 40.0)

def test_negative_load_raises():
    with pytest.raises(InvalidError):
        BaseNode("B1", 100.0, -1.0, 0.9, 40.0)

def test_load_exceeds_capacity_raises():
    with pytest.raises(InvalidError):
        BaseNode("B1", 100.0, 150.0, 0.9, 40.0)

def test_efficiency_above_one_raises():
    with pytest.raises(InvalidError):
        BaseNode("B1", 100.0, 50.0, 1.5, 40.0)

def test_efficiency_below_zero_raises():
    with pytest.raises(InvalidError):
        BaseNode("B1", 100.0, 50.0, -0.1, 40.0)

def test_negative_temperature_raises():
    with pytest.raises(InvalidError):
        BaseNode("B1", 100.0, 50.0, 0.9, -5.0)

def test_temperature_above_max_raises():
    with pytest.raises (InvalidError):
        BaseNode("B1", 100.0, 50.0, 0.9, 200.0)

def test_invalid_status_string_raises():
    with pytest.raises(InvalidError):
        BaseNode("B1", 100.0, 50.0, 0.9, 40.0, status="ONLINE")


# PROPERTIES

def test_current_power(base_node):
    assert base_node.current_power == 50.0 * 0.9

def test_available_capacity(base_node):
    assert base_node.available_capacity == 100.0 - 50.0

def test_load_factor(base_node):
    assert base_node.load_factor == 50.0 / 100.0


# Check is_healthy

def test_is_healthy_true_for_online_node(base_node):
    assert base_node.is_healthy is True

def test_is_healthy_false_for_offline_node():
    node = BaseNode("B1", 100.0, 50.0, 0.9, 40.0,
                    status=NodeStatus.offline)
    assert node.is_healthy is False

def test_is_healthy_false_for_maintenance_node():
    node = BaseNode("B1", 100.0, 50.0, 0.9, 40.0, status=NodeStatus.maintenance)
    assert node.is_healthy is False

def test_is_healthy_false_for_hot_node():
    node = BaseNode("B1", 100.0, 50.0, 0.9, 95.0)
    assert node.is_healthy is False


def test_is_healthy_false_for_low_efficiency():
    node = BaseNode("B1", 100.0, 50.0, 0.05, 40.0)
    assert node.is_healthy is False


def test_is_healthy_false_for_overloaded_node():
    node = BaseNode("B1", 100.0, 98.0, 0.9, 40.0)
    assert node.is_healthy is False    


# Check health_score

def test_health_score_in_range(base_node):
    assert 0.0 <= base_node.health_score <= 100.0


def test_health_score_full_for_healthy_node(base_node):
    assert base_node.health_score == 100.0


def test_health_score_penalized_for_hot_node():
    node = BaseNode("B1", 100.0, 50.0, 0.9, 95.0)
    assert node.health_score < 100.0


def test_health_score_penalized_for_low_efficiency():
    node = BaseNode("B1", 100.0, 50.0, 0.05, 40.0)
    assert node.health_score < 100.0


def test_health_score_penalized_for_overload():
    node = BaseNode("B1", 100.0, 98.0, 0.9, 40.0)
    assert node.health_score < 100.0


def test_health_score_penalized_for_non_online_status():
    node = BaseNode("B1", 100.0, 50.0, 0.9, 40.0, status=NodeStatus.offline)
    assert node.health_score < 100.0


def test_health_score_never_below_zero():
    node = BaseNode("B1", 100.0, 98.0, 0.05, 95.0, status=NodeStatus.offline)
    assert node.health_score >= 0.0


# Check to_dict

def test_to_dict_contains_all_base_keys(base_node):
    d = base_node.to_dict()
    expected_keys = {
        "node_id",
        "capacity",
        "load",
        "efficiency",
        "temperature",
        "status",
        "current_power",
        "available_capacity",
        "load_factor",
        "is_healthy",
        "health_score",
    }
    assert expected_keys.issubset(d.keys())


def test_to_dict_status_is_string(base_node):
    d = base_node.to_dict()
    assert isinstance(d["status"], str)


def test_to_dict_values_match_attributes(base_node):
    d = base_node.to_dict()
    assert d["node_id"] == base_node.node_id
    assert d["capacity"] == base_node.capacity
    assert d["load"] == base_node.load
    assert d["efficiency"] == base_node.efficiency
    assert d["temperature"] == base_node.temperature
    assert d["status"] == base_node.status.value
    assert d["current_power"] == base_node.current_power
    assert d["available_capacity"] == base_node.available_capacity
    assert d["load_factor"] == base_node.load_factor
    assert d["is_healthy"] == base_node.is_healthy
    assert d["health_score"] == base_node.health_score


# Scale

def test_scale_returns_new_node(base_node):
    scaled = base_node.scale(2.0)
    assert scaled is not base_node
    assert isinstance(scaled, BaseNode)


def test_scale_multiplies_capacity_and_load(base_node):
    scaled = base_node.scale(2.0)
    assert scaled.capacity == base_node.capacity * 2.0
    assert scaled.load == base_node.load * 2.0


def test_scale_preserves_efficiency_and_temperature(base_node):
    scaled = base_node.scale(2.0)
    assert scaled.efficiency == base_node.efficiency
    assert scaled.temperature == base_node.temperature


def test_scale_zero_raises(base_node):
    with pytest.raises(InvalidError):
        base_node.scale(0)


def test_scale_negative_raises(base_node):
    with pytest.raises(InvalidError):
        base_node.scale(-1.0)


def test_scale_does_not_mutate_original(base_node):
    snapshot = base_node.to_dict()
    base_node.scale(2.0)
    assert base_node.to_dict() == snapshot




# Check update_load

def test_update_load_valid(base_node):
    updated = base_node.update_load(75.0)
    assert updated.load == 75.0
    assert updated is not base_node


def test_update_load_does_not_mutate_original(base_node):
    snapshot = base_node.to_dict()
    base_node.update_load(75.0)
    assert base_node.to_dict() == snapshot


def test_update_load_negative_raises(base_node):
    with pytest.raises(InvalidError):
        base_node.update_load(-1.0)


def test_update_load_exceeds_capacity_raises(base_node):
    with pytest.raises(InvalidError):
        base_node.update_load(200.0)



# Check update_efficiency

def test_update_efficiency_valid(base_node):
    updated = base_node.update_efficiency(0.95)
    assert updated.efficiency == 0.95
    assert updated is not base_node


def test_update_efficiency_does_not_mutate_original(base_node):
    snapshot = base_node.to_dict()
    base_node.update_efficiency(0.95)
    assert base_node.to_dict() == snapshot


def test_update_efficiency_above_one_raises(base_node):
    with pytest.raises(InvalidError):
        base_node.update_efficiency(1.5)


def test_update_efficiency_below_zero_raises(base_node):
    with pytest.raises(InvalidError):
        base_node.update_efficiency(-0.1)


# Check generate_health_report

def test_generate_health_report_returns_string(base_node):
    report = base_node.generate_health_report()
    assert isinstance(report, str)


def test_generate_health_report_contains_node_id(base_node):
    report = base_node.generate_health_report()
    assert "B1" in report


def test_generate_health_report_contains_status(base_node):
    report = base_node.generate_health_report()
    assert "ONLINE" in report


# Dunder Functions check

def test_repr_returns_string(base_node):
    assert isinstance(repr(base_node), str)


def test_repr_contains_node_id(base_node):
    assert "B1" in repr(base_node)


def test_str_returns_string(base_node):
    assert isinstance(str(base_node), str)


def test_str_contains_node_id(base_node):
    assert "B1" in str(base_node)


def test_eq_true_for_same_id():
    a = BaseNode("X", 100.0, 50.0, 0.9, 40.0)
    b = BaseNode("X", 200.0, 100.0, 0.8, 45.0)
    assert a == b


def test_eq_false_for_different_ids():
    a = BaseNode("X", 100.0, 50.0, 0.9, 40.0)
    b = BaseNode("Y", 100.0, 50.0, 0.9, 40.0)
    assert a != b


def test_eq_false_for_non_node():
    a = BaseNode("X", 100.0, 50.0, 0.9, 40.0)
    assert a != 42
    assert a != "X"







# Quantum Node Class Test

@pytest.fixture
def quantum_node():
    return QuantumNode(
        "Q1",
        capacity=200.0,
        load=80.0,
        efficiency=0.95,
        temperature=35.0,
        coherence=0.85,
        entanglement_pairs=16,
        qubit_stability=0.9,
        decoherence_rate=0.02,
    )

def test_quantum_valid_construction():
    node = QuantumNode("Q1", 200.0, 80.0, 0.95, 35.0, coherence=0.85, entanglement_pairs=16, qubit_stability=0.9, decoherence_rate=0.02)
    assert node.node_id == "Q1"
    assert node.capacity == 200.0
    assert node.load == 80.0
    assert node.efficiency == 0.95
    assert node.temperature == 35.0
    assert node.coherence == 0.85
    assert node.entanglement_pairs == 16
    assert node.qubit_stability == 0.9
    assert node.decoherence_rate == 0.02
    assert node.status is NodeStatus.online


def test_quantum_inherits_base_attributes(quantum_node):
    assert isinstance(quantum_node, BaseNode)
    assert quantum_node.node_id == "Q1"
    assert quantum_node.capacity == 200.0
    assert quantum_node.load == 80.0
    assert quantum_node.efficiency == 0.95
    assert quantum_node.temperature == 35.0


# Invalid Construction

def test_quantum_empty_node_id_raises():
    with pytest.raises(InvalidError):
        QuantumNode(
            "",
            200.0,
            80.0,
            0.95,
            35.0,
            coherence=0.85,
            entanglement_pairs=16,
            qubit_stability=0.9,
            decoherence_rate=0.02,
        )


def test_quantum_zero_capacity_raises():
    with pytest.raises(InvalidError):
        QuantumNode(
            "Q1",
            0.0,
            0.0,
            0.95,
            35.0,
            coherence=0.85,
            entanglement_pairs=16,
            qubit_stability=0.9,
            decoherence_rate=0.02,
        )


def test_quantum_negative_load_raises():
    with pytest.raises(InvalidError):
        QuantumNode(
            "Q1",
            200.0,
            -1.0,
            0.95,
            35.0,
            coherence=0.85,
            entanglement_pairs=16,
            qubit_stability=0.9,
            decoherence_rate=0.02,
        )


def test_quantum_load_exceeds_capacity_raises():
    with pytest.raises(InvalidError):
        QuantumNode(
            "Q1",
            200.0,
            250.0,
            0.95,
            35.0,
            coherence=0.85,
            entanglement_pairs=16,
            qubit_stability=0.9,
            decoherence_rate=0.02,
        )


def test_quantum_efficiency_above_one_raises():
    with pytest.raises(InvalidError):
        QuantumNode(
            "Q1",
            200.0,
            80.0,
            1.5,
            35.0,
            coherence=0.85,
            entanglement_pairs=16,
            qubit_stability=0.9,
            decoherence_rate=0.02,
        )


def test_quantum_efficiency_below_zero_raises():
    with pytest.raises(InvalidError):
        QuantumNode(
            "Q1",
            200.0,
            80.0,
            -0.1,
            35.0,
            coherence=0.85,
            entanglement_pairs=16,
            qubit_stability=0.9,
            decoherence_rate=0.02,
        )


def test_quantum_negative_temperature_raises():
    with pytest.raises(InvalidError):
        QuantumNode(
            "Q1",
            200.0,
            80.0,
            0.95,
            -5.0,
            coherence=0.85,
            entanglement_pairs=16,
            qubit_stability=0.9,
            decoherence_rate=0.02,
        )


def test_quantum_temperature_above_max_raises():
    with pytest.raises(InvalidError):
        QuantumNode(
            "Q1",
            200.0,
            80.0,
            0.95,
            200.0,
            coherence=0.85,
            entanglement_pairs=16,
            qubit_stability=0.9,
            decoherence_rate=0.02,
        )


def test_quantum_invalid_status_raises():
    with pytest.raises(InvalidError):
        QuantumNode(
            "Q1",
            200.0,
            80.0,
            0.95,
            35.0,
            coherence=0.85,
            entanglement_pairs=16,
            qubit_stability=0.9,
            decoherence_rate=0.02,
            status="ONLINE",
        )


def test_quantum_coherence_above_one_raises():
    with pytest.raises(InvalidError):
        QuantumNode(
            "Q1",
            200.0,
            80.0,
            0.95,
            35.0,
            coherence=1.5,
            entanglement_pairs=16,
            qubit_stability=0.9,
            decoherence_rate=0.02,
        )


def test_quantum_coherence_below_zero_raises():
    with pytest.raises(InvalidError):
        QuantumNode(
            "Q1",
            200.0,
            80.0,
            0.95,
            35.0,
            coherence=-0.1,
            entanglement_pairs=16,
            qubit_stability=0.9,
            decoherence_rate=0.02,
        )


def test_quantum_negative_entanglement_pairs_raises():
    with pytest.raises(InvalidError):
        QuantumNode(
            "Q1",
            200.0,
            80.0,
            0.95,
            35.0,
            coherence=0.85,
            entanglement_pairs=-1,
            qubit_stability=0.9,
            decoherence_rate=0.02,
        )


def test_quantum_non_integer_entanglement_pairs_raises():
    with pytest.raises(InvalidError):
        QuantumNode(
            "Q1",
            200.0,
            80.0,
            0.95,
            35.0,
            coherence=0.85,
            entanglement_pairs=1.5,
            qubit_stability=0.9,
            decoherence_rate=0.02,
        )


def test_quantum_stability_above_one_raises():
    with pytest.raises(InvalidError):
        QuantumNode(
            "Q1",
            200.0,
            80.0,
            0.95,
            35.0,
            coherence=0.85,
            entanglement_pairs=16,
            qubit_stability=1.5,
            decoherence_rate=0.02,
        )


def test_quantum_stability_below_zero_raises():
    with pytest.raises(InvalidError):
        QuantumNode(
            "Q1",
            200.0,
            80.0,
            0.95,
            35.0,
            coherence=0.85,
            entanglement_pairs=16,
            qubit_stability=-0.1,
            decoherence_rate=0.02,
        )


def test_quantum_negative_decoherence_raises():
    with pytest.raises(InvalidError):
        QuantumNode(
            "Q1",
            200.0,
            80.0,
            0.95,
            35.0,
            coherence=0.85,
            entanglement_pairs=16,
            qubit_stability=0.9,
            decoherence_rate=-0.01,
        )


# Inherited Properties

def test_quantum_current_power(quantum_node):
    assert quantum_node.current_power == 80.0 * 0.95


def test_quantum_available_capacity(quantum_node):
    assert quantum_node.available_capacity == 200.0 - 80.0


def test_quantum_load_factor(quantum_node):
    assert quantum_node.load_factor == 80.0 / 200.0


# is_healty Check

def test_quantum_is_healthy_true_for_all_good_metrics(quantum_node):
    assert quantum_node.is_healthy is True


def test_quantum_is_healthy_false_for_low_coherence():
    node = QuantumNode(
        "Q1",
        200.0,
        80.0,
        0.95,
        35.0,
        coherence=0.2,
        entanglement_pairs=16,
        qubit_stability=0.9,
        decoherence_rate=0.02,
    )
    assert node.is_healthy is False


def test_quantum_is_healthy_false_for_low_stability():
    node = QuantumNode(
        "Q1",
        200.0,
        80.0,
        0.95,
        35.0,
        coherence=0.85,
        entanglement_pairs=16,
        qubit_stability=0.2,
        decoherence_rate=0.02,
    )
    assert node.is_healthy is False


def test_quantum_is_healthy_false_for_high_decoherence():
    node = QuantumNode(
        "Q1",
        200.0,
        80.0,
        0.95,
        35.0,
        coherence=0.85,
        entanglement_pairs=16,
        qubit_stability=0.9,
        decoherence_rate=0.5,
    )
    assert node.is_healthy is False


def test_quantum_is_healthy_false_for_offline_status():
    node = QuantumNode(
        "Q1",
        200.0,
        80.0,
        0.95,
        35.0,
        coherence=0.85,
        entanglement_pairs=16,
        qubit_stability=0.9,
        decoherence_rate=0.02,
        status=NodeStatus.offline,
    )
    assert node.is_healthy is False


def test_quantum_is_healthy_false_for_hot_node():
    node = QuantumNode(
        "Q1",
        200.0,
        80.0,
        0.95,
        95.0,
        coherence=0.85,
        entanglement_pairs=16,
        qubit_stability=0.9,
        decoherence_rate=0.02,
    )
    assert node.is_healthy is False


def test_quantum_is_healthy_false_for_overloaded_node():
    node = QuantumNode(
        "Q1",
        200.0,
        195.0,
        0.95,
        35.0,
        coherence=0.85,
        entanglement_pairs=16,
        qubit_stability=0.9,
        decoherence_rate=0.02,
    )
    assert node.is_healthy is False




# health_score

def test_quantum_health_score_in_range(quantum_node):
    assert 0.0 <= quantum_node.health_score <= 100.0


def test_quantum_health_score_penalized_for_low_coherence(quantum_node):
    bad = QuantumNode(
        "Q2",
        200.0,
        80.0,
        0.95,
        35.0,
        coherence=0.2,
        entanglement_pairs=16,
        qubit_stability=0.9,
        decoherence_rate=0.02,
    )
    assert bad.health_score < quantum_node.health_score


def test_quantum_health_score_penalized_for_low_stability(quantum_node):
    bad = QuantumNode(
        "Q2",
        200.0,
        80.0,
        0.95,
        35.0,
        coherence=0.85,
        entanglement_pairs=16,
        qubit_stability=0.2,
        decoherence_rate=0.02,
    )
    assert bad.health_score < quantum_node.health_score


def test_quantum_health_score_penalized_for_high_decoherence(quantum_node):
    bad = QuantumNode(
        "Q2",
        200.0,
        80.0,
        0.95,
        35.0,
        coherence=0.85,
        entanglement_pairs=16,
        qubit_stability=0.9,
        decoherence_rate=0.5,
    )
    assert bad.health_score < quantum_node.health_score


def test_quantum_health_score_never_below_zero():
    worst = QuantumNode(
        "Q1",
        200.0,
        195.0,
        0.05,
        95.0,
        coherence=0.0,
        entanglement_pairs=0,
        qubit_stability=0.0,
        decoherence_rate=1.0,
        status=NodeStatus.offline,
    )
    assert worst.health_score >= 0.0


# to_dict

def test_quantum_to_dict_has_base_keys(quantum_node):
    data = quantum_node.to_dict()
    assert "node_id" in data
    assert "capacity" in data
    assert "load" in data
    assert "efficiency" in data
    assert "temperature" in data
    assert "status" in data
    assert "current_power" in data
    assert "is_healthy" in data
    assert "health_score" in data


def test_quantum_to_dict_has_quantum_keys(quantum_node):
    data = quantum_node.to_dict()
    assert "coherence" in data
    assert "entanglement_pairs" in data
    assert "qubit_stability" in data
    assert "decoherence_rate" in data


def test_quantum_to_dict_values_match_attributes(quantum_node):
    data = quantum_node.to_dict()
    assert data["node_id"] == quantum_node.node_id
    assert data["capacity"] == quantum_node.capacity
    assert data["coherence"] == quantum_node.coherence
    assert data["entanglement_pairs"] == quantum_node.entanglement_pairs
    assert data["qubit_stability"] == quantum_node.qubit_stability
    assert data["decoherence_rate"] == quantum_node.decoherence_rate


# Scale

def test_quantum_scale_returns_new_quantum_node(quantum_node):
    scaled = quantum_node.scale(2.0)
    assert scaled is not quantum_node
    assert isinstance(scaled, QuantumNode)


def test_quantum_scale_multiplies_capacity_and_load(quantum_node):
    scaled = quantum_node.scale(2.0)
    assert scaled.capacity == quantum_node.capacity * 2.0
    assert scaled.load == quantum_node.load * 2.0


def test_quantum_scale_multiplies_entanglement_pairs(quantum_node):
    scaled = quantum_node.scale(2.0)
    assert scaled.entanglement_pairs == int(quantum_node.entanglement_pairs * 2)


def test_quantum_scale_preserves_coherence(quantum_node):
    scaled = quantum_node.scale(2.0)
    assert scaled.coherence == quantum_node.coherence


def test_quantum_scale_preserves_stability(quantum_node):
    scaled = quantum_node.scale(2.0)
    assert scaled.qubit_stability == quantum_node.qubit_stability


def test_quantum_scale_zero_raises(quantum_node):
    with pytest.raises(InvalidError):
        quantum_node.scale(0)


def test_quantum_scale_negative_raises(quantum_node):
    with pytest.raises(InvalidError):
        quantum_node.scale(-1.0)


def test_quantum_scale_does_not_mutate_original(quantum_node):
    snapshot = quantum_node.to_dict()
    quantum_node.scale(2.0)
    assert quantum_node.to_dict() == snapshot



# generate_health_report

def test_quantum_health_report_returns_string(quantum_node):
    report = quantum_node.generate_health_report()
    assert isinstance(report, str)


def test_quantum_health_report_contains_node_id(quantum_node):
    report = quantum_node.generate_health_report()
    assert "Q1" in report


def test_quantum_health_report_contains_status(quantum_node):
    report = quantum_node.generate_health_report()
    assert "ONLINE" in report


def test_quantum_health_report_contains_quantum_metrics(quantum_node):
    report = quantum_node.generate_health_report()
    assert "Coherence" in report
    assert "Entanglement" in report
    assert "Stability" in report
    assert "Decoherence" in report



# Dunder Methods

def test_quantum_repr_returns_string(quantum_node):
    assert isinstance(repr(quantum_node), str)


def test_quantum_repr_contains_node_id(quantum_node):
    assert "Q1" in repr(quantum_node)


def test_quantum_str_returns_string(quantum_node):
    assert isinstance(str(quantum_node), str)


def test_quantum_str_contains_node_id(quantum_node):
    assert "Q1" in str(quantum_node)


def test_quantum_eq_true_for_same_id():
    a = QuantumNode(
        "X", 200.0, 80.0, 0.95, 35.0,
        coherence=0.85, entanglement_pairs=16,
        qubit_stability=0.9, decoherence_rate=0.02,
    )
    b = QuantumNode(
        "X", 300.0, 100.0, 0.9, 40.0,
        coherence=0.75, entanglement_pairs=24,
        qubit_stability=0.8, decoherence_rate=0.05,
    )
    assert a == b


def test_quantum_eq_false_for_different_ids(quantum_node):
    other = QuantumNode(
        "Q2", 200.0, 80.0, 0.95, 35.0,
        coherence=0.85, entanglement_pairs=16,
        qubit_stability=0.9, decoherence_rate=0.02,
    )
    assert quantum_node != other


def test_quantum_eq_false_for_non_node(quantum_node):
    assert quantum_node != 42
    assert quantum_node != "Q1"







