"""
NEURON CIRCLE MODULE

Implements the Circle topology for the Aigarth neural network.
Based on Qubic Core architecture.

The circle arranges neurons in a ring where each neuron
connects to its N nearest neighbors on both sides.

Circle topology:
    ... ←→ N₀ ←→ N₁ ←→ N₂ ←→ ... ←→ Nₙ₋₁ ←→ N₀ ←→ ...

Input neurons are at positions 0..num_inputs-1
Output neurons are at positions num_inputs..population-1
"""

from typing import List, Optional, Tuple
from dataclasses import dataclass
import numpy as np

from .neuron import TernaryNeuron, NeuronType
from .encoding import ternary_clamp, compute_energy, compute_distribution


@dataclass
class InferenceResult:
    """Result of running inference on the network."""
    outputs: List[int]           # Output neuron states
    all_states: List[int]        # All neuron states
    ticks: int                   # Number of ticks executed
    end_reason: str              # "converged", "all_nonzero", or "max_ticks"
    energy: int                  # Total energy (sum of all states)
    distribution: dict           # State distribution
    history: Optional[List[List[int]]] = None  # State history per tick


class NeuronCircle:
    """
    A circle of ternary neurons.

    The fundamental structure of Aigarth:
    - Neurons arranged in a ring
    - Each neuron connects to neighbors on both sides
    - Input and Output neurons are at fixed positions

    Attributes:
        neurons: List of TernaryNeuron instances
        num_inputs: Number of input neurons
        num_outputs: Number of output neurons
        num_neighbors: Number of neighbors per neuron
        max_ticks: Maximum ticks before stopping
    """

    def __init__(
        self,
        num_inputs: int = 64,
        num_outputs: int = 64,
        num_neighbors: int = 8,
        max_ticks: int = 1000
    ):
        """
        Initialize a neuron circle.

        Args:
            num_inputs: Number of input neurons
            num_outputs: Number of output neurons
            num_neighbors: Number of neighbors each neuron connects to
            max_ticks: Maximum number of ticks per inference
        """
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self.num_neighbors = num_neighbors
        self.max_ticks = max_ticks

        self.population = num_inputs + num_outputs
        self.neurons: List[TernaryNeuron] = []

        self._init_neurons()

    def _init_neurons(self) -> None:
        """Initialize neurons in the circle."""
        # Input neurons at positions 0..num_inputs-1
        for i in range(self.num_inputs):
            neuron = TernaryNeuron(
                neuron_type=NeuronType.INPUT,
                weights=[],  # Input neurons don't have weights
                index=i
            )
            self.neurons.append(neuron)

        # Output neurons at positions num_inputs..population-1
        for i in range(self.num_outputs):
            neuron = TernaryNeuron(
                neuron_type=NeuronType.OUTPUT,
                weights=[0] * self.num_neighbors,  # Will be set from matrix
                index=self.num_inputs + i
            )
            self.neurons.append(neuron)

    def get_neighbor_indices(self, neuron_idx: int) -> List[int]:
        """
        Get indices of neighbors for a neuron.

        Neighbors are arranged symmetrically around the neuron:
        - Left neighbors: offset -1, -2, ..., -left_count
        - Right neighbors: offset +1, +2, ..., +right_count

        Args:
            neuron_idx: Index of the neuron

        Returns:
            List of neighbor indices (circular)
        """
        left_count = self.num_neighbors // 2
        right_count = self.num_neighbors - left_count

        indices = []

        # Left neighbors
        for offset in range(1, left_count + 1):
            idx = (neuron_idx - offset) % self.population
            indices.append(idx)

        # Right neighbors
        for offset in range(1, right_count + 1):
            idx = (neuron_idx + offset) % self.population
            indices.append(idx)

        return indices

    def get_neighbor_states(self, neuron_idx: int) -> List[int]:
        """
        Get current states of a neuron's neighbors.

        Args:
            neuron_idx: Index of the neuron

        Returns:
            List of neighbor states
        """
        indices = self.get_neighbor_indices(neuron_idx)
        return [self.neurons[i].state for i in indices]

    def set_inputs(self, values: List[int]) -> None:
        """
        Set input neuron values.

        Args:
            values: List of input values (will be clamped to ternary)
        """
        for i, value in enumerate(values):
            if i >= self.num_inputs:
                break
            self.neurons[i].set_input(value)

    def get_outputs(self) -> List[int]:
        """
        Get output neuron states.

        Returns:
            List of output neuron states
        """
        return [n.state for n in self.neurons[self.num_inputs:]]

    def get_all_states(self) -> List[int]:
        """
        Get all neuron states.

        Returns:
            List of all neuron states
        """
        return [n.state for n in self.neurons]

    def all_outputs_nonzero(self) -> bool:
        """
        Check if all output neurons have non-zero states.

        Returns:
            True if all outputs are non-zero
        """
        for neuron in self.neurons[self.num_inputs:]:
            if neuron.state == 0:
                return False
        return True

    def run_tick(self) -> bool:
        """
        Run one tick of the network.

        1. Compute next states for all output neurons
        2. Commit all states atomically

        Returns:
            True if any state changed
        """
        # Phase 1: Compute next states
        for i in range(self.num_inputs, self.population):
            neuron = self.neurons[i]
            neighbor_states = self.get_neighbor_states(i)
            neuron.feedforward(neighbor_states)

        # Phase 2: Commit all states atomically
        any_changed = False
        for neuron in self.neurons:
            if neuron.commit():
                any_changed = True

        return any_changed

    def reset(self) -> None:
        """Reset all neurons to initial state."""
        for neuron in self.neurons:
            neuron.reset(0)

    def run_inference(
        self,
        inputs: List[int],
        record_history: bool = False
    ) -> InferenceResult:
        """
        Run full inference on the network.

        THE CORE AIGARTH ALGORITHM:
        1. Set input neuron values
        2. Clear output neurons
        3. Run tick-loop until:
           - All outputs non-zero (solution found)
           - No state changes (converged)
           - Max ticks reached

        Args:
            inputs: Input values (will be clamped to ternary)
            record_history: Whether to record state history

        Returns:
            InferenceResult with outputs, ticks, and convergence info
        """
        # Step 1: Set input neurons
        self.set_inputs(inputs)

        # Step 2: Clear output neurons
        for i in range(self.num_inputs, self.population):
            self.neurons[i].reset(0)

        # Optional: Record history
        history = [] if record_history else None
        if record_history:
            history.append(self.get_all_states())

        # Step 3: Tick-Loop
        end_reason = "max_ticks"

        for tick in range(self.max_ticks):
            # Check termination: all outputs non-zero
            if self.all_outputs_nonzero():
                end_reason = "all_nonzero"
                break

            # Run one tick
            state_changed = self.run_tick()

            # Record history
            if record_history:
                history.append(self.get_all_states())

            # Check termination: no state changes (converged)
            if not state_changed:
                end_reason = "converged"
                break

        # Collect results
        outputs = self.get_outputs()
        all_states = self.get_all_states()
        energy = compute_energy(all_states)
        distribution = compute_distribution(all_states)

        return InferenceResult(
            outputs=outputs,
            all_states=all_states,
            ticks=tick + 1 if tick < self.max_ticks else self.max_ticks,
            end_reason=end_reason,
            energy=energy,
            distribution=distribution,
            history=history
        )

    def load_weights_from_matrix(
        self,
        matrix: np.ndarray,
        use_sign_only: bool = True
    ) -> None:
        """
        Load neuron weights from the Anna Matrix.

        Each output neuron gets weights from a row of the matrix.

        Args:
            matrix: The Anna Matrix (128x128)
            use_sign_only: If True, convert to ternary weights (-1, 0, +1)
        """
        for i in range(self.num_outputs):
            neuron_idx = self.num_inputs + i
            neuron = self.neurons[neuron_idx]

            if i < len(matrix):
                row = matrix[i]
                # Take num_neighbors weights from the row
                weights = row[:self.num_neighbors].tolist()
                neuron.set_weights_from_matrix_row(weights, use_sign_only)

    def load_weights_from_matrix_circular(
        self,
        matrix: np.ndarray,
        use_sign_only: bool = True
    ) -> None:
        """
        Load weights using circular indexing from the matrix.

        Uses the full matrix row for each neuron, wrapping around
        to get neighbor-specific weights.

        Args:
            matrix: The Anna Matrix (128x128)
            use_sign_only: If True, convert to ternary weights
        """
        for i in range(self.num_outputs):
            neuron_idx = self.num_inputs + i
            neuron = self.neurons[neuron_idx]

            if i < len(matrix):
                row = matrix[i]
                neighbor_indices = self.get_neighbor_indices(neuron_idx)

                # Get weights corresponding to neighbor positions
                weights = []
                for neighbor_idx in neighbor_indices:
                    # Use matrix column corresponding to neighbor
                    col = neighbor_idx % len(row)
                    weights.append(int(row[col]))

                neuron.set_weights_from_matrix_row(weights, use_sign_only)

    def __repr__(self) -> str:
        return (
            f"NeuronCircle(inputs={self.num_inputs}, "
            f"outputs={self.num_outputs}, "
            f"neighbors={self.num_neighbors})"
        )
