"""
TERNARY NEURON MODULE

A single neuron in the Aigarth neural network.
Based on the Qubic Core implementation.

The neuron has:
- A current state (-1, 0, +1)
- A next state (computed during feedforward)
- Weights for connections to neighbors
- A type (INPUT, OUTPUT, or EVOLUTION)

Key operation:
    weighted_sum = sum(neighbor_state * weight)
    next_state = ternary_clamp(weighted_sum)
"""

from typing import List, Optional
from enum import IntEnum
from .encoding import ternary_clamp


class NeuronType(IntEnum):
    """Types of neurons in the network."""
    INPUT = 0      # Holds input values, doesn't compute
    OUTPUT = 1     # Produces output, computes from neighbors
    EVOLUTION = 2  # Internal processing, can evolve weights


class TernaryNeuron:
    """
    A single ternary neuron.

    Attributes:
        neuron_type: The type of this neuron (INPUT, OUTPUT, EVOLUTION)
        weights: Synapse weights to neighbor neurons
        state: Current ternary state (-1, 0, +1)
        next_state: Next state (computed during feedforward)
        index: Position in the circle (for debugging)
    """

    __slots__ = ['neuron_type', 'weights', 'state', 'next_state', 'index']

    def __init__(
        self,
        neuron_type: NeuronType = NeuronType.OUTPUT,
        weights: Optional[List[int]] = None,
        index: int = 0
    ):
        """
        Initialize a ternary neuron.

        Args:
            neuron_type: Type of neuron (INPUT, OUTPUT, EVOLUTION)
            weights: List of ternary weights for neighbor connections
            index: Position in the circle
        """
        self.neuron_type = neuron_type
        self.weights = weights if weights is not None else []
        self.state = 0
        self.next_state = 0
        self.index = index

    def feedforward(self, inputs: List[int]) -> int:
        """
        Compute the next state from neighbor inputs.

        For INPUT neurons: Returns current state (doesn't compute)
        For other neurons: Computes weighted sum and clamps to ternary

        Args:
            inputs: States of neighbor neurons

        Returns:
            The computed next state (-1, 0, or +1)
        """
        if self.neuron_type == NeuronType.INPUT:
            # Input neurons hold their value, don't compute
            return self.state

        # Compute weighted sum
        total = 0
        weight_count = min(len(inputs), len(self.weights))

        for i in range(weight_count):
            total += inputs[i] * self.weights[i]

        # Clamp to ternary
        self.next_state = ternary_clamp(total)
        return self.next_state

    def commit(self) -> bool:
        """
        Commit the next state as the current state.

        This is called after ALL neurons have computed their next states,
        ensuring atomic state updates across the network.

        Returns:
            True if state changed, False otherwise
        """
        changed = self.next_state != self.state
        self.state = self.next_state
        return changed

    def reset(self, value: int = 0) -> None:
        """
        Reset the neuron state.

        Args:
            value: Initial state value (default 0)
        """
        self.state = ternary_clamp(value)
        self.next_state = self.state

    def set_input(self, value: int) -> None:
        """
        Set input value (for INPUT neurons).

        Args:
            value: The input value to set
        """
        clamped = ternary_clamp(value)
        self.state = clamped
        self.next_state = clamped

    def set_weights(self, weights: List[int]) -> None:
        """
        Set synapse weights.

        Args:
            weights: List of weights (will be clamped to ternary)
        """
        self.weights = [ternary_clamp(w) for w in weights]

    def set_weights_from_matrix_row(self, row: List[int], use_sign_only: bool = True) -> None:
        """
        Set weights from an Anna Matrix row.

        Args:
            row: A row from the Anna Matrix
            use_sign_only: If True, only use sign (-1, 0, +1). If False, use full values.
        """
        if use_sign_only:
            # Convert to ternary by sign
            self.weights = [ternary_clamp(v) for v in row]
        else:
            # Use raw values (for weighted connections)
            self.weights = list(row)

    @property
    def is_input(self) -> bool:
        """Check if this is an input neuron."""
        return self.neuron_type == NeuronType.INPUT

    @property
    def is_output(self) -> bool:
        """Check if this is an output neuron."""
        return self.neuron_type == NeuronType.OUTPUT

    @property
    def is_nonzero(self) -> bool:
        """Check if current state is non-zero."""
        return self.state != 0

    def __repr__(self) -> str:
        type_name = self.neuron_type.name
        state_symbol = '+' if self.state > 0 else ('-' if self.state < 0 else '0')
        return f"Neuron[{self.index}]({type_name}, state={state_symbol})"
