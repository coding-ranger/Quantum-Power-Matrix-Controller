
"""Domain model for hardware nodes in Aethergrid"""

from typing import Union, Optional, Dict, Any
from aethergrid.enums import NodeStatus
from aethergrid.exceptions import InvalidError


# Helper functions

# 1) weighted_average

def weighted_average(value_a, value_b, weight_a, weight_b):
    """Return capacity-weighted average of two values."""

    total_weight = weight_a + weight_b

    if total_weight == 0:
        return 0.0
    return (value_a * weight_a + value_b * weight_b) / total_weight

# 2) clamp

def clamp(value, minimum, maximum):
    """Restrict value to the range [minimum, maximum]."""

    return max(minimum, min(value, maximum)) 

# BaseNode Class

class BaseNode:
    """Standard hardware node with power, load, efficiency, temperature.
        Standard hardware node with power, load, efficiency, and temperature.

        A ``BaseNode`` is immutable in the sense that its methods never mutate
        the instance. Instead, ``scale``, ``update_load``, ``update_efficiency``,
        and ``__add__`` all return new ``BaseNode`` instances.

        Attributes
        ----------
        node_id : str
            Unique identifier for the node.
        capacity : float
            Maximum power output.
        load : float
            Current power output.
        efficiency : float
            Efficiency between 0.0 and 1.0.
        temperature : float
            Current temperature.
        status : NodeStatus
            Operational status.
        max_temperature : float
            Temperature threshold used for health checks.
        min_efficiency : float
            Minimum acceptable efficiency for health checks."""


    # Constructor Fucntion
    def __init__(self, node_id: str, capacity: float, load: float, efficiency: float, temperature: float, status=NodeStatus.online, max_temperature=100.0, min_efficiency=0.1) -> None:
        
        if not isinstance(node_id, str) or not node_id.strip():
            raise InvalidError("node_id must be a non-empty string")
        
        if not isinstance(capacity, (int, float)) or capacity <= 0:
            raise InvalidError("capacity must be greater than 0")
        
        if not isinstance(load, (int, float)) or not (0 <= load <= capacity):
            raise InvalidError("load must satisfy 0 <= load <= capacity")
        
        if not isinstance(efficiency, (int, float)) or not (0.0 <= efficiency <= 1.0):
            raise InvalidError("efficiency must be between 0.0 and 1.0")
        
        if not isinstance(temperature, (int, float)) or not (0 <= temperature <= max_temperature):
            raise InvalidError("temperature must be between 0 and max_temperature")
        
        if not isinstance(status, NodeStatus):
            raise InvalidError("status must be a NodeStatus member")
        

        self.node_id = node_id
        self.capacity = float(capacity)
        self.load = float(load)
        self.efficiency = float(efficiency)
        self.temperature = float(temperature)
        self.status = status
        self.max_temperature = float(max_temperature)
        self.min_efficiency = float(min_efficiency)


    #Property Functions

    @property
    def current_power(self) -> float:
        """Return the current effective power output (``load * efficiency``)."""
        return self.load * self.efficiency
    
    @property
    def available_capacity(self) -> float:
        """Return the unused capacity (``capacity - load``)."""
        return self.capacity - self.load
    
    @property
    def load_factor(self) -> float:
        """Return the ratio of ``load`` to ``capacity``."""
        return self.load / self.capacity
    
    @property
    def is_healthy(self) -> bool:
        """Return ``True`` if the node is healthy under normal operating rules."""
        return (
            self.status is NodeStatus.online
            and self.temperature < self.max_temperature * 0.9
            and self.efficiency >= self.min_efficiency
            and self.load_factor <= 0.95
        )
    
    @property
    def health_score(self) -> float:
        """Return a health score between 0.0 and 100.0."""
        score = 100.0
        if self.temperature > self.max_temperature * 0.8:
            score -= 20.0
        if self.efficiency < self.min_efficiency:
            score -= 20.0
        if self.load_factor > 0.9:
            score -= 15.0
        if self.status is not NodeStatus.online:
            score -= 30.0
        return clamp(score, 0.0, 100.0)
    

    
    def to_dict(self) -> Dict[str, Any]:
        """Return a dictionary representation of the node."""
        return {
            "node_id": self.node_id,
            "capacity": self.capacity,
            "load": self.load,
            "efficiency": self.efficiency,
            "temperature": self.temperature,
            "status": self.status.value,
            "current_power": self.current_power,
            "available_capacity": self.available_capacity,
            "load_factor": self.load_factor,
            "is_healthy": self.is_healthy,
            "health_score": self.health_score,
        }
    



    # Instance Methods

    def scale(self, factor: float) -> "BaseNode":
        """
        Return a new node with capacity and load scaled by ``factor``.

        Parameters
        ----------
        factor : float
            Positive scaling factor.

        Returns
        -------
        BaseNode
            A new node with scaled values.

            
        Raises
        ------
        InvalidError
            If ``factor`` is not positive.
        """     

        if factor <= 0:
            raise InvalidError("factor must be positive")
        
        return BaseNode (
            node_id=self.node_id + "scaled",
            capacity=self.capacity * factor,
            load=self.load * factor,
            efficiency=self.efficiency,
            temperature= self.temperature,
            status=self.status,
            max_temperature=self.max_temperature,
            min_efficiency=self.min_efficiency,
        )
    
    def update_load(self, new_load: float) -> "BaseNode":
        """
        Return a new node with an updated load.

        Parameters
        ----------
        new_load : float
            Must satisfy ``0 <= new_load <= capacity``.

        Returns
        -------
        BaseNode
            A new node with the updated load.

        Raises
        ------
        InvalidError
            If ``new_load`` is out of range.
        """

        if new_load < 0 or new_load > self.capacity:
            raise InvalidError("new_load must be between 0 and capacity")
        
        return BaseNode(
            node_id=self.node_id,
            capacity=self.capacity,
            load=new_load,
            efficiency=self.efficiency,
            temperature=self.temperature,
            status=self.status,
            max_temperature=self.max_temperature,
            min_efficiency=self.min_efficiency,)
    

    def update_efficiency(self, new_efficiency: float) -> "BaseNode":
        """
        Return a new node with updated efficiency.

        Parameters
        ----------
        new_efficiency : float
            Must satisfy ``0.0 <= new_efficiency <= 1.0``.

        Returns
        -------
        BaseNode
            A new node with the updated efficiency.

        Raises
        ------
        InvalidError
            If ``new_efficiency`` is out of range.
        """ 
        
        if new_efficiency < 0.0 or new_efficiency > 1.0:
            raise InvalidError("efficiency must be between 0 and 1")
        
        return BaseNode(
            node_id=self.node_id,
            capacity=self.capacity,
            load=self.load,
            efficiency=new_efficiency,
            temperature=self.temperature,
            status=self.status,
            max_temperature=self.max_temperature,
            min_efficiency=self.min_efficiency,
        )
    

    def generate_health_report(self) -> str:
        """Return a human-readable multi-line health report."""
        return (
            f"Node: {self.node_id}\n"
            f"Status: {self.status.value}\n"
            f"Current Power: {self.current_power: .2f}\n"
            f"Load factor: {self.load_factor: .2f}\n"
            f"Health score: {self.health_score: .2f}\n"
            f"Healthy: {self.is_healthy}\n"
        )
    

    # Operator Overloading

    def __add__(self, other: object) -> Union["BaseNode", "QuantumNode"]:

        """
        Combine two nodes into a new node.

        The result is a ``BaseNode`` unless either operand is a
        ``QuantumNode``, in which case the result is a ``QuantumNode``.

        Parameters
        ----------
        other : object
            The right-hand operand.

        Returns
        -------
        BaseNode or QuantumNode
            A new combined node, or ``NotImplemented`` if ``other`` is not
            a ``BaseNode``.
        """

        if not isinstance(other,BaseNode):
            return NotImplemented
        
        combined_capacity = self.capacity + other.capacity
        combined_load = self.load + other.load
        combined_efficiency = weighted_average(
            self.efficiency,
            other.efficiency,
            self.capacity,
            other.capacity,
        )

        combined_temperature = max(self.temperature, other.temperature)
        combined_id = f"{self.node_id}+{other.node_id}"


        if isinstance (other, QuantumNode):
            return QuantumNode(
                node_id = combined_id,
                capacity =combined_capacity,
                load = combined_load,
                efficiency = combined_efficiency,
                coherence = other.coherence,
                entanglement_pairs=other.entanglement_pairs,
                qubit_stability=other.qubit_stability,
                decoherence_rate=other.decoherence_rate,
                status = NodeStatus.combined
            )
        return BaseNode(
            node_id=combined_id,
            capacity=combined_capacity,
            load=combined_load,
            efficiency=combined_efficiency,
            temperature=combined_temperature,
            status=NodeStatus.combined,
        )
    
    # Dunder Functions

    def __repr__(self) -> str:
        """Return a debug-friendly representation."""
        return (
            f"<BaseNode id={self.node_id!r} "
            f"capacity={self.capacity} "
            f"load={self.load}>"
        )
    
    def __str__(self) -> str:
        """Return a human-readable summary."""
        return (
            f"Node {self.node_id} | "
            f"Status: {self.status.value} | "
            f"Load: {self.load}/{self.capacity}"
        )
    
    def __eq__(self, other: object) -> bool:
        """Compare nodes by ``node_id``."""
        if not isinstance(other, BaseNode):
            return False
        return self.node_id == other.node_id
        
        


    

# QuantumNode Class

class QuantumNode(BaseNode):
    """
    Advanced node with quantum coherence and entanglement properties.

    Inherits all behaviour from :class:`BaseNode` and extends it with
    quantum-specific metrics: ``coherence``, ``entanglement_pairs``,
    ``qubit_stability``, and ``decoherence_rate``.

    Health checks and health scores account for both classical and
    quantum metrics. Operator overloading is extended so that adding
    any node to a ``QuantumNode`` produces a new ``QuantumNode``.

    Attributes
    ----------
    coherence : float
        Quantum coherence between 0.0 and 1.0.
    entanglement_pairs : int
        Number of entangled qubit pairs (non-negative integer).
    qubit_stability : float
        Qubit stability between 0.0 and 1.0.
    decoherence_rate : float
        Rate of coherence loss (non-negative).
    """

    def __init__(
        self,
        node_id: str,
        capacity: float,
        load: float,
        efficiency: float,
        temperature: float,
        coherence: float,
        entanglement_pairs: int,
        qubit_stability: float,
        decoherence_rate: float,
        status: NodeStatus = NodeStatus.online,
        max_temperature: float = 100.0,
        min_efficiency: float = 0.1,
    ) -> None:
        """
        Construct a ``QuantumNode``.

        Parameters
        ----------
        node_id : str
            Non-empty string identifier.
        capacity : float
            Must be positive.
        load : float
            Must satisfy ``0 <= load <= capacity``.
        efficiency : float
            Must satisfy ``0.0 <= efficiency <= 1.0``.
        temperature : float
            Must satisfy ``0 <= temperature <= max_temperature``.
        coherence : float
            Must satisfy ``0.0 <= coherence <= 1.0``.
        entanglement_pairs : int
            Non-negative integer.
        qubit_stability : float
            Must satisfy ``0.0 <= qubit_stability <= 1.0``.
        decoherence_rate : float
            Non-negative.
        status : NodeStatus, optional
            Operational status. Defaults to ``NodeStatus.ONLINE``.
        max_temperature : float, optional
            Upper bound for ``temperature``. Defaults to ``100.0``.
        min_efficiency : float, optional
            Minimum efficiency for health checks. Defaults to ``0.1``.

        Raises
        ------
        InvalidError
            If any argument fails validation.
        """
        super().__init__(
            node_id=node_id,
            capacity=capacity,
            load=load,
            efficiency=efficiency,
            temperature=temperature,
            status=status,
            max_temperature=max_temperature,
            min_efficiency=min_efficiency,
        )

        if coherence < 0.0 or coherence > 1.0:
            raise InvalidError("coherence must be between 0 and 1")

        if not isinstance(entanglement_pairs, int) or entanglement_pairs < 0:
            raise InvalidError(
                "entanglement_pairs must be a non-negative integer"
            )

        if qubit_stability < 0.0 or qubit_stability > 1.0:
            raise InvalidError("qubit_stability must be between 0 and 1")

        if decoherence_rate < 0.0:
            raise InvalidError("decoherence_rate must be non-negative")

        self.coherence: float = coherence
        self.entanglement_pairs: int = entanglement_pairs
        self.qubit_stability: float = qubit_stability
        self.decoherence_rate: float = decoherence_rate

    
    # Overridden properties

    @property
    def is_healthy(self) -> bool:
        """Return ``True`` if both classical and quantum health checks pass."""
        base_healthy = super().is_healthy
        quantum_healthy = (
            self.coherence >= 0.5
            and self.qubit_stability >= 0.5
            and self.decoherence_rate <= 0.1
        )
        return base_healthy and quantum_healthy

    @property
    def health_score(self) -> float:
        """Return a health score between 0.0 and 100.0 including quantum penalties."""
        base_score = super().health_score
        penalty = 0.0
        if self.coherence < 0.5:
            penalty += 15.0
        if self.qubit_stability < 0.5:
            penalty += 15.0
        if self.decoherence_rate > 0.1:
            penalty += 10.0
        return clamp(base_score - penalty, 0.0, 100.0)

    
    def to_dict(self) -> Dict[str, Any]:
        """Return a dictionary representation including quantum metrics."""
        base_dict = super().to_dict()
        base_dict["coherence"] = self.coherence
        base_dict["entanglement_pairs"] = self.entanglement_pairs
        base_dict["qubit_stability"] = self.qubit_stability
        base_dict["decoherence_rate"] = self.decoherence_rate
        return base_dict

    # Overridden methods

    def scale(self, factor: float) -> "QuantumNode":
        """
        Return a new ``QuantumNode`` with scaled capacity, load, and
        entanglement pairs.

        Parameters
        ----------
        factor : float
            Positive scaling factor.

        Returns
        -------
        QuantumNode
            A new node with scaled values.

        Raises
        ------
        InvalidError
            If ``factor`` is not positive.
        """
        if factor <= 0:
            raise InvalidError("factor must be positive")
        return QuantumNode(
            node_id=self.node_id + "_scaled",
            capacity=self.capacity * factor,
            load=self.load * factor,
            efficiency=self.efficiency,
            temperature=self.temperature,
            coherence=self.coherence,
            entanglement_pairs=int(self.entanglement_pairs * factor),
            qubit_stability=self.qubit_stability,
            decoherence_rate=self.decoherence_rate,
            status=self.status,
            max_temperature=self.max_temperature,
            min_efficiency=self.min_efficiency,
        )

    def generate_health_report(self) -> str:
        """Return a health report including classical and quantum metrics."""
        base_report = super().generate_health_report()
        quantum_section = (
            f"Coherence: {self.coherence:.2f}\n"
            f"Entanglement Pairs: {self.entanglement_pairs}\n"
            f"Qubit Stability: {self.qubit_stability:.2f}\n"
            f"Decoherence Rate: {self.decoherence_rate:.2f}\n"
        )
        return base_report + quantum_section

    # Operator overloading

    def __add__(self, other: object) -> Union["BaseNode", "QuantumNode"]:
        """
        Combine this ``QuantumNode`` with another node.

        The result is always a ``QuantumNode`` because at least one
        operand (``self``) is quantum.

        Parameters
        ----------
        other : object
            The right-hand operand.

        Returns
        -------
        QuantumNode
            A new combined node, or ``NotImplemented`` if ``other`` is
            not a ``BaseNode``.
        """
        if not isinstance(other, BaseNode):
            return NotImplemented

        combined_capacity = self.capacity + other.capacity
        combined_load = self.load + other.load
        combined_efficiency = weighted_average(
            self.efficiency,
            other.efficiency,
            self.capacity,
            other.capacity,
        )
        combined_temperature = max(self.temperature, other.temperature)
        combined_id = f"{self.node_id}+{other.node_id}"

        if isinstance(other, QuantumNode):
            combined_coherence = weighted_average(
                self.coherence,
                other.coherence,
                self.capacity,
                other.capacity,
            )
            combined_pairs = self.entanglement_pairs + other.entanglement_pairs
            combined_stability = weighted_average(
                self.qubit_stability,
                other.qubit_stability,
                self.capacity,
                other.capacity,
            )
            combined_decoherence = weighted_average(
                self.decoherence_rate,
                other.decoherence_rate,
                self.capacity,
                other.capacity,
            )
        else:
            combined_coherence = self.coherence
            combined_pairs = self.entanglement_pairs
            combined_stability = self.qubit_stability
            combined_decoherence = self.decoherence_rate

        return QuantumNode(
            node_id=combined_id,
            capacity=combined_capacity,
            load=combined_load,
            efficiency=combined_efficiency,
            temperature=combined_temperature,
            coherence=combined_coherence,
            entanglement_pairs=combined_pairs,
            qubit_stability=combined_stability,
            decoherence_rate=combined_decoherence,
            status=NodeStatus.combined,
        )

    def __radd__(self, other: object) -> Union["BaseNode", "QuantumNode"]:
        """
        Handle ``BaseNode + QuantumNode`` when ``BaseNode.__add__``
        returns ``NotImplemented``.

        Delegates to :meth:`__add__` because addition is commutative.
        """
        return self.__add__(other)

