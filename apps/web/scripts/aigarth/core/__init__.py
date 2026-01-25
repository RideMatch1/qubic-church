"""
AIGARTH CORE MODULE

Contains the fundamental building blocks:
- encoding: Ternary bit conversion (from Qubic Core)
- neuron: Single ternary neuron implementation
- circle: Circle topology network
- engine: Main processing engine
"""

from .encoding import to_ternary_bits, from_ternary_bits, ternary_clamp, TernaryState
from .neuron import TernaryNeuron, NeuronType
from .circle import NeuronCircle
from .engine import AigarthEngine

__all__ = [
    "to_ternary_bits",
    "from_ternary_bits",
    "ternary_clamp",
    "TernaryState",
    "TernaryNeuron",
    "NeuronType",
    "NeuronCircle",
    "AigarthEngine",
]
