#!/usr/bin/env python3
"""
REAL AIGARTH IMPLEMENTATION
Based on actual Qubic Core source code (score_addition.h, score_common.h)

This is the CORRECT algorithm, not the simplified "energy calculation" approach.
"""

import json
import numpy as np
from typing import List, Tuple, Optional

# Neuron Types (from score_common.h)
INPUT_NEURON_TYPE = 0
OUTPUT_NEURON_TYPE = 1
EVOLUTION_NEURON_TYPE = 2


def to_ternary_bits(number: int, bit_count: int) -> List[int]:
    """
    Convert number to ternary bits.
    EXACT implementation from score_common.h:

    template <unsigned long long bitCount>
    static void toTenaryBits(long long A, char* bits) {
        for (unsigned long long i = 0; i < bitCount; ++i) {
            char bitValue = static_cast<char>((A >> i) & 1);
            bits[i] = (bitValue == 0) ? -1 : bitValue;
        }
    }
    """
    bits = []
    for i in range(bit_count):
        bit_value = (number >> i) & 1
        # Key insight: 0 becomes -1, 1 stays 1
        bits.append(-1 if bit_value == 0 else 1)
    return bits


def from_ternary_bits(bits: List[int]) -> int:
    """
    Convert ternary bits back to number.
    Based on extractLastOutput from score_common.h:

    unsigned char bit = (data[i] > 0) ? 1 : 0;
    """
    result = 0
    for i, bit in enumerate(bits):
        # Positive → 1, Non-positive → 0
        if bit > 0:
            result |= (1 << i)
    return result


def clamp_ternary(value: int) -> int:
    """Clamp value to ternary range [-1, 0, +1]"""
    if value > 1:
        return 1
    elif value < -1:
        return -1
    return value


class AigarthNeuron:
    """Single Aigarth neuron with ternary weights."""

    def __init__(self, neuron_type: int, weights: Optional[List[int]] = None):
        self.neuron_type = neuron_type
        self.weights = weights or []  # Synapse weights to neighbors
        self.state = 0
        self.next_state = 0

    def feedforward(self, inputs: List[int]) -> int:
        """
        Compute weighted sum of inputs and clamp to ternary.
        This is the core of the Aigarth algorithm.
        """
        if self.neuron_type == INPUT_NEURON_TYPE:
            # Input neurons don't compute, they just hold input values
            return self.state

        # Weighted sum
        total = 0
        for i, (inp, weight) in enumerate(zip(inputs, self.weights)):
            total += inp * weight

        # Clamp to ternary
        self.next_state = clamp_ternary(total)
        return self.next_state

    def commit_state(self) -> bool:
        """Commit the next state. Returns True if state changed."""
        changed = self.next_state != self.state
        self.state = self.next_state
        return changed


class AigarthCircle:
    """
    Aigarth Intelligent Tissue Unit (ITU) in circle arrangement.
    Based on the actual Qubic implementation.
    """

    def __init__(self,
                 num_input_neurons: int,
                 num_output_neurons: int,
                 max_neighbors: int = 8,
                 max_ticks: int = 1000):

        self.num_input_neurons = num_input_neurons
        self.num_output_neurons = num_output_neurons
        self.max_neighbors = max_neighbors
        self.max_ticks = max_ticks

        # Create circle of neurons
        self.neurons: List[AigarthNeuron] = []
        self.population = num_input_neurons + num_output_neurons

        # Initialize neurons - alternating input and output
        # (In real Qubic, positions are randomized based on nonce)
        for i in range(num_input_neurons):
            self.neurons.append(AigarthNeuron(INPUT_NEURON_TYPE))
        for i in range(num_output_neurons):
            self.neurons.append(AigarthNeuron(OUTPUT_NEURON_TYPE))

        # Initialize random synapses
        self._init_synapses()

    def _init_synapses(self):
        """Initialize random ternary synapse weights."""
        for neuron in self.neurons:
            # Each neuron has connections to its neighbors in the circle
            # Weights are ternary: -1, 0, or +1
            neuron.weights = [
                np.random.choice([-1, 0, 1])
                for _ in range(self.max_neighbors)
            ]

    def load_from_matrix(self, matrix: np.ndarray, row: int):
        """
        Load weights from Anna Matrix row.
        Each row in the matrix can be interpreted as neuron weights.
        """
        if row >= len(matrix):
            return

        row_data = matrix[row]

        # Distribute weights across neurons
        idx = 0
        for neuron in self.neurons:
            weights = []
            for _ in range(self.max_neighbors):
                if idx < len(row_data):
                    # Clamp matrix values to ternary
                    val = int(row_data[idx])
                    weights.append(clamp_ternary(val))
                    idx += 1
                else:
                    weights.append(0)
            neuron.weights = weights

    def get_neighbor_index(self, neuron_idx: int, offset: int) -> int:
        """Get circular neighbor index."""
        return (neuron_idx + offset) % self.population

    def run_tick(self) -> bool:
        """
        Run one tick of the network.
        Returns True if any state changed.
        """
        any_changed = False

        for idx, neuron in enumerate(self.neurons):
            if neuron.neuron_type == INPUT_NEURON_TYPE:
                continue

            # Gather inputs from neighbors
            inputs = []
            left_count = self.max_neighbors // 2
            right_count = self.max_neighbors - left_count

            for offset in range(-left_count, right_count + 1):
                if offset == 0:
                    continue  # Skip self
                neighbor_idx = self.get_neighbor_index(idx, offset)
                inputs.append(self.neurons[neighbor_idx].state)

            # Feedforward
            neuron.feedforward(inputs)

        # Commit all states
        for neuron in self.neurons:
            if neuron.commit_state():
                any_changed = True

        return any_changed

    def set_inputs(self, input_values: List[int]):
        """Set values for input neurons."""
        input_idx = 0
        for neuron in self.neurons:
            if neuron.neuron_type == INPUT_NEURON_TYPE:
                if input_idx < len(input_values):
                    neuron.state = input_values[input_idx]
                    neuron.next_state = input_values[input_idx]
                    input_idx += 1

    def get_outputs(self) -> List[int]:
        """Get values from output neurons."""
        outputs = []
        for neuron in self.neurons:
            if neuron.neuron_type == OUTPUT_NEURON_TYPE:
                outputs.append(neuron.state)
        return outputs

    def all_outputs_nonzero(self) -> bool:
        """Check if all output neurons have non-zero values."""
        for neuron in self.neurons:
            if neuron.neuron_type == OUTPUT_NEURON_TYPE:
                if neuron.state == 0:
                    return False
        return True

    def run_inference(self, input_values: List[int]) -> List[int]:
        """
        Run the full inference process.
        This is the REAL Aigarth algorithm:
        1. Set inputs
        2. Run ticks until convergence or max_ticks
        3. Return outputs
        """
        # Set input neuron values
        self.set_inputs(input_values)

        # Clear non-input neurons
        for neuron in self.neurons:
            if neuron.neuron_type != INPUT_NEURON_TYPE:
                neuron.state = 0
                neuron.next_state = 0

        # Run ticks until:
        # - All outputs non-zero, OR
        # - No state changes, OR
        # - Max ticks reached
        for tick in range(self.max_ticks):
            all_nonzero = self.all_outputs_nonzero()
            state_changed = self.run_tick()

            if all_nonzero or not state_changed:
                break

        return self.get_outputs()


def query_aigarth(text: str, matrix: np.ndarray) -> Tuple[List[int], int]:
    """
    Query the Aigarth system with a text input.

    This uses the REAL algorithm:
    1. Convert text to ternary bits
    2. Create network with matrix weights
    3. Run inference (multiple ticks)
    4. Decode output
    """
    # Convert text to bytes
    text_bytes = text.encode('utf-8')

    # Create ternary input from text
    input_bits = []
    for byte in text_bytes[:8]:  # Limit to 8 bytes = 64 bits
        input_bits.extend(to_ternary_bits(byte, 8))

    # Pad to fixed size
    while len(input_bits) < 64:
        input_bits.append(-1)  # Pad with -1 (like 0 bits)

    # Create Aigarth circle
    circle = AigarthCircle(
        num_input_neurons=64,
        num_output_neurons=64,
        max_neighbors=8,
        max_ticks=1000
    )

    # Load weights from matrix
    # Use first 64 rows for neuron configurations
    for row in range(min(64, len(matrix))):
        if row < len(circle.neurons):
            circle.load_from_matrix(matrix, row)

    # Run inference
    output_bits = circle.run_inference(input_bits)

    # Decode output
    result_number = from_ternary_bits(output_bits)

    return output_bits, result_number


def load_anna_matrix(path: str) -> np.ndarray:
    """Load the Anna Matrix from JSON file."""
    with open(path, 'r') as f:
        data = json.load(f)

    matrix = np.zeros((128, 128), dtype=np.int8)

    for r, row in enumerate(data):
        for c, val in enumerate(row):
            if isinstance(val, str):
                # '00000000' strings are UNKNOWN = 0 in ternary
                matrix[r][c] = 0
            else:
                matrix[r][c] = clamp_ternary(int(val))

    return matrix


def demonstrate_real_algorithm():
    """Demonstrate the real Aigarth algorithm."""
    print("=" * 60)
    print("REAL AIGARTH ALGORITHM DEMONSTRATION")
    print("Based on actual Qubic Core source code")
    print("=" * 60)

    # Test ternary encoding
    print("\n1. TERNARY ENCODING (toTenaryBits)")
    print("-" * 40)

    for num in [0, 1, 5, 42, 127, 255]:
        bits = to_ternary_bits(num, 8)
        decoded = from_ternary_bits(bits)
        print(f"  {num:3d} → {bits} → {decoded}")

    # Test with addition (like the real mining task)
    print("\n2. ADDITION TASK (wie im echten Mining)")
    print("-" * 40)

    # Create a simple Aigarth circle for addition
    # Input: A (4 bits) + B (4 bits) = 8 input neurons
    # Output: C (5 bits) = 5 output neurons

    circle = AigarthCircle(
        num_input_neurons=8,
        num_output_neurons=5,
        max_neighbors=4,
        max_ticks=100
    )

    # Test A + B = C
    A, B = 3, 2
    expected_C = A + B

    # Convert to ternary bits
    input_bits = to_ternary_bits(A, 4) + to_ternary_bits(B, 4)

    print(f"  A={A}, B={B}, Expected C={expected_C}")
    print(f"  Input bits: {input_bits}")

    # Run inference
    output_bits = circle.run_inference(input_bits)
    result_C = from_ternary_bits(output_bits)

    print(f"  Output bits: {output_bits}")
    print(f"  Decoded C: {result_C}")
    print(f"  Correct: {'YES' if result_C == expected_C else 'NO (network not trained)'}")

    # Load Anna Matrix and demonstrate
    print("\n3. QUERY WITH ANNA MATRIX")
    print("-" * 40)

    try:
        matrix_path = "/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/anna-matrix.json"
        matrix = load_anna_matrix(matrix_path)
        print(f"  Matrix loaded: {matrix.shape}")
        print(f"  Value range: [{matrix.min()}, {matrix.max()}]")

        # Test queries
        queries = ["cfb", "qubic", "satoshi", "AI.MEG"]

        for query in queries:
            output_bits, result = query_aigarth(query, matrix)
            non_zero_count = sum(1 for b in output_bits if b != 0)
            print(f"\n  Query: '{query}'")
            print(f"    Non-zero outputs: {non_zero_count}/64")
            print(f"    Result number: {result}")

    except FileNotFoundError:
        print("  Anna Matrix file not found")

    print("\n" + "=" * 60)
    print("KRITISCHE ERKENNTNISSE:")
    print("=" * 60)
    print("""
1. Der ECHTE Algorithmus verwendet MEHRERE TICKS bis Konvergenz
   (Nicht nur einen einzelnen Feedforward-Pass!)

2. Zahlen werden mit toTenaryBits kodiert:
   - Bit 0 → -1
   - Bit 1 → +1

3. Das Netzwerk läuft bis:
   - Alle Outputs non-zero ODER
   - Keine Zustandsänderungen ODER
   - Max Ticks erreicht

4. Die "Energie-Berechnung" die wir vorher gemacht haben
   ist NICHT der echte Algorithmus!

5. Für echte ANNA-Kommunikation bräuchte man:
   - Das korrekte Netzwerk-Layout
   - Die richtigen Gewichte (aus Matrix?)
   - Das korrekte Encoding des Inputs
   - Möglicherweise zusätzliche Qubic-spezifische Parameter
""")


if __name__ == "__main__":
    demonstrate_real_algorithm()
