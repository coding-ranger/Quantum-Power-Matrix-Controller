from enum import Enum

class NodeStatus(Enum):
    """Operational status of a hardware node"""
    online = "ONLINE"
    offline = "OFFLINE"
    maintenance = "MAINTENANCE"
    degraded = "DEGRADED" 
    combined ="COMBINED"

    def is_operational(self):
        return self == NodeStatus.online

class NodeType(Enum):
    """Type of hardware node"""
    base = "BASE"
    quantum = "QUANTUM"

class DecayMode(Enum):
    """Harmonic decay modes for recursion"""
    linear = "LINEAR"
    exponential = "EXPONENTIAL"
    quadratic = "QUADRATIC"

class SecurityLevel(Enum):
    """Security clearance level"""
    guest = 0
    user = 1
    admin = 2
    root = 3

class LogLevel(Enum):
    """Diagnostic log levels"""
    debug = 10
    info = 20
    warning = 30
    error = 40
    critical = 50




