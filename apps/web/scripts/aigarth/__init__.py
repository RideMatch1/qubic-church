"""
AIGARTH - LOCAL NEURAL COMPUTER

The world's first publicly demonstrable ternary neural network for AGI development.
This implementation uses the REAL tick-loop algorithm from Qubic Core.

Usage:
    from aigarth import AigarthEngine

    engine = AigarthEngine()
    result = engine.process("Hello World")
    print(result.energy, result.ticks, result.convergence_reason)
"""

from .core.engine import AigarthEngine
from .core.neuron import TernaryNeuron
from .core.circle import NeuronCircle
from .core.encoding import (
    to_ternary_bits,
    from_ternary_bits,
    ternary_clamp,
    TernaryState,
)

__version__ = "1.0.0"
__author__ = "Qubic Academic Research"

__all__ = [
    "AigarthEngine",
    "TernaryNeuron",
    "NeuronCircle",
    "to_ternary_bits",
    "from_ternary_bits",
    "ternary_clamp",
    "TernaryState",
]
