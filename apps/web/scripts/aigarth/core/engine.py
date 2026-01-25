"""
AIGARTH ENGINE

The main interface for the Local Aigarth Computer.
Combines all components into a unified processing pipeline.

Usage:
    engine = AigarthEngine()
    result = engine.process("Hello World")
    print(result)
"""

import json
import hashlib
import os
from pathlib import Path
from typing import List, Optional, Union, Dict, Any
from dataclasses import dataclass, asdict
import numpy as np

from .circle import NeuronCircle, InferenceResult
from .encoding import (
    text_to_ternary,
    hex_to_ternary,
    bytes_to_ternary,
    to_ternary_bits,
    from_ternary_bits,
    compute_energy,
    compute_distribution,
    ternary_clamp,
)


@dataclass
class ProcessingResult:
    """Complete result of processing an input."""
    # Input info
    input_raw: str
    input_type: str
    input_ternary_length: int

    # Processing info
    ticks: int
    end_reason: str
    duration_ms: float

    # Output info
    energy: int
    state_vector: List[int]
    output_vector: List[int]
    distribution: Dict[str, int]

    # Decoded value (if applicable)
    decoded_value: Optional[int] = None

    # Optional history
    history: Optional[List[List[int]]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @property
    def energy_label(self) -> str:
        """Human-readable energy label."""
        if self.energy > 50:
            return "EXTREMELY POSITIVE"
        elif self.energy > 20:
            return "POSITIVE"
        elif self.energy > 0:
            return "SLIGHTLY POSITIVE"
        elif self.energy == 0:
            return "NEUTRAL"
        elif self.energy > -20:
            return "SLIGHTLY NEGATIVE"
        elif self.energy > -50:
            return "NEGATIVE"
        else:
            return "EXTREMELY NEGATIVE"

    @property
    def visualization(self) -> str:
        """ASCII visualization of state vector."""
        chars = []
        for s in self.state_vector:
            if s > 0:
                chars.append('')
            elif s < 0:
                chars.append('')
            else:
                chars.append('')
        return ''.join(chars)


class AigarthEngine:
    """
    The main Aigarth processing engine.

    This is the unified interface for all Aigarth operations.
    It handles:
    - Matrix loading
    - Input conversion
    - Neural network inference
    - Result formatting

    Attributes:
        matrix: The Anna Matrix (128x128)
        circle: The NeuronCircle for inference
        matrix_loaded: Whether the matrix has been loaded
    """

    # Default paths
    DEFAULT_MATRIX_PATH = Path(__file__).parent.parent.parent.parent / "public" / "data" / "anna-matrix.json"

    def __init__(
        self,
        matrix_path: Optional[str] = None,
        num_inputs: int = 64,
        num_outputs: int = 64,
        num_neighbors: int = 8,
        max_ticks: int = 1000,
        auto_load_matrix: bool = True
    ):
        """
        Initialize the Aigarth Engine.

        Args:
            matrix_path: Path to anna-matrix.json (uses default if None)
            num_inputs: Number of input neurons
            num_outputs: Number of output neurons
            num_neighbors: Number of neighbors per neuron
            max_ticks: Maximum ticks per inference
            auto_load_matrix: Whether to automatically load the matrix
        """
        self.matrix_path = matrix_path or str(self.DEFAULT_MATRIX_PATH)
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self.num_neighbors = num_neighbors
        self.max_ticks = max_ticks

        self.matrix: Optional[np.ndarray] = None
        self.matrix_loaded = False

        # Create the neural circle
        self.circle = NeuronCircle(
            num_inputs=num_inputs,
            num_outputs=num_outputs,
            num_neighbors=num_neighbors,
            max_ticks=max_ticks
        )

        if auto_load_matrix:
            self.load_matrix()

    def load_matrix(self, path: Optional[str] = None) -> bool:
        """
        Load the Anna Matrix from JSON file.

        Args:
            path: Path to matrix file (uses default if None)

        Returns:
            True if successful, False otherwise
        """
        load_path = path or self.matrix_path

        try:
            with open(load_path, 'r') as f:
                data = json.load(f)

            # Handle both {"matrix": [...]} and direct [...] formats
            if isinstance(data, dict) and 'matrix' in data:
                raw_matrix = data['matrix']
            else:
                raw_matrix = data

            # Convert to numpy array
            self.matrix = np.zeros((128, 128), dtype=np.int8)

            for r, row in enumerate(raw_matrix[:128]):
                for c, val in enumerate(row[:128]):
                    if isinstance(val, str):
                        # Handle string values (unknown cells)
                        self.matrix[r][c] = 0
                    else:
                        self.matrix[r][c] = int(val)

            # Load weights into the neural circle
            self.circle.load_weights_from_matrix_circular(self.matrix, use_sign_only=True)

            self.matrix_loaded = True
            return True

        except FileNotFoundError:
            print(f"Warning: Matrix file not found: {load_path}")
            self.matrix_loaded = False
            return False
        except Exception as e:
            print(f"Error loading matrix: {e}")
            self.matrix_loaded = False
            return False

    def _detect_input_type(self, input_str: str) -> str:
        """
        Auto-detect input type.

        Args:
            input_str: The input string

        Returns:
            Input type: "text", "hex", "coords", "qubic_seed", "bitcoin", "binary"
        """
        input_str = input_str.strip()

        # Check for coordinate format "X+Y" or "X,Y"
        if '+' in input_str or ',' in input_str:
            parts = input_str.replace(',', '+').split('+')
            if len(parts) == 2:
                try:
                    int(parts[0].strip())
                    int(parts[1].strip())
                    return "coords"
                except ValueError:
                    pass

        # Check for hex string
        if input_str.startswith('0x') or input_str.startswith('0X'):
            return "hex"

        # Check for Qubic seed (55 lowercase chars)
        if len(input_str) == 55 and input_str.islower():
            return "qubic_seed"

        # Check for Bitcoin address (starts with 1, 3, or bc1)
        if input_str.startswith('1') or input_str.startswith('3') or input_str.startswith('bc1'):
            if 25 <= len(input_str) <= 62:
                return "bitcoin"

        # Check for binary array format [-1, 1, ...]
        if input_str.startswith('[') and input_str.endswith(']'):
            return "binary"

        # Default to text
        return "text"

    def _convert_to_ternary(self, input_str: str, input_type: str) -> List[int]:
        """
        Convert input to ternary bits based on type.

        Args:
            input_str: The input string
            input_type: The detected or specified type

        Returns:
            List of ternary values
        """
        if input_type == "text":
            return text_to_ternary(input_str, max_bytes=self.num_inputs // 8)

        elif input_type == "hex":
            ternary = hex_to_ternary(input_str)
            # Pad or truncate to input size
            while len(ternary) < self.num_inputs:
                ternary.append(-1)
            return ternary[:self.num_inputs]

        elif input_type == "qubic_seed":
            # Qubic seeds are 55 lowercase letters
            # Convert each char to its position (a=0, b=1, ..., z=25)
            ternary = []
            for char in input_str:
                val = ord(char) - ord('a')  # 0-25
                ternary.extend(to_ternary_bits(val, 5))  # 5 bits per char
            while len(ternary) < self.num_inputs:
                ternary.append(-1)
            return ternary[:self.num_inputs]

        elif input_type == "bitcoin":
            # Hash the address
            hash_bytes = hashlib.sha256(input_str.encode()).digest()
            ternary = bytes_to_ternary(hash_bytes)
            return ternary[:self.num_inputs]

        elif input_type == "binary":
            # Parse binary array
            try:
                values = json.loads(input_str)
                ternary = [ternary_clamp(v) for v in values]
                while len(ternary) < self.num_inputs:
                    ternary.append(-1)
                return ternary[:self.num_inputs]
            except:
                return text_to_ternary(input_str, max_bytes=self.num_inputs // 8)

        elif input_type == "coords":
            # For coordinates, we do a direct matrix lookup + ternary conversion
            # This is special - we return the matrix value as ternary
            parts = input_str.replace(',', '+').split('+')
            x, y = int(parts[0].strip()), int(parts[1].strip())

            # Anna coords to matrix coords
            col = (x + 64) % 128
            row = (63 - y) % 128

            if self.matrix is not None:
                value = int(self.matrix[row][col])
                # Create ternary from the value
                return to_ternary_bits(abs(value), self.num_inputs)
            else:
                return [-1] * self.num_inputs

        else:
            # Fallback to text
            return text_to_ternary(input_str, max_bytes=self.num_inputs // 8)

    def process(
        self,
        input_str: str,
        input_type: Optional[str] = None,
        record_history: bool = False
    ) -> ProcessingResult:
        """
        Process an input through the Aigarth network.

        This is the main method for running inference.

        Args:
            input_str: The input to process
            input_type: Optional type hint ("text", "hex", "coords", etc.)
            record_history: Whether to record tick-by-tick history

        Returns:
            ProcessingResult with all information
        """
        import time
        start_time = time.perf_counter()

        # Detect or use specified input type
        detected_type = input_type or self._detect_input_type(input_str)

        # Convert to ternary
        ternary_input = self._convert_to_ternary(input_str, detected_type)

        # Run inference
        result = self.circle.run_inference(ternary_input, record_history=record_history)

        # Calculate duration
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Decode output value
        decoded_value = from_ternary_bits(result.outputs)

        return ProcessingResult(
            input_raw=input_str,
            input_type=detected_type,
            input_ternary_length=len(ternary_input),
            ticks=result.ticks,
            end_reason=result.end_reason,
            duration_ms=round(duration_ms, 3),
            energy=result.energy,
            state_vector=result.all_states,
            output_vector=result.outputs,
            distribution=result.distribution,
            decoded_value=decoded_value,
            history=result.history
        )

    def query_matrix(self, row: int, col: int) -> Dict[str, Any]:
        """
        Query a specific matrix cell.

        Args:
            row: Matrix row (0-127)
            col: Matrix column (0-127)

        Returns:
            Dict with value, anna coordinates, and metadata
        """
        if self.matrix is None:
            return {"error": "Matrix not loaded"}

        row = row % 128
        col = col % 128

        value = int(self.matrix[row][col])

        # Convert to Anna coordinates
        anna_x = (col - 64) if col < 64 else (col - 64)
        anna_y = 63 - row

        # Get neighbors
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = (row + dr) % 128, (col + dc) % 128
                neighbors.append(int(self.matrix[nr][nc]))

        return {
            "row": row,
            "col": col,
            "value": value,
            "anna_x": anna_x,
            "anna_y": anna_y,
            "anna_format": f"{anna_x}+{anna_y}",
            "hex": hex(value if value >= 0 else 256 + value),
            "ternary": ternary_clamp(value),
            "neighbors": neighbors,
            "neighbors_sum": sum(neighbors),
        }

    def compare(self, input_a: str, input_b: str) -> Dict[str, Any]:
        """
        Compare two inputs.

        Args:
            input_a: First input
            input_b: Second input

        Returns:
            Dict with comparison metrics
        """
        result_a = self.process(input_a)
        result_b = self.process(input_b)

        # Calculate similarity (cosine-like)
        dot_product = sum(a * b for a, b in zip(result_a.state_vector, result_b.state_vector))
        norm_a = sum(abs(a) for a in result_a.state_vector)
        norm_b = sum(abs(b) for b in result_b.state_vector)

        if norm_a > 0 and norm_b > 0:
            similarity = (dot_product / (norm_a * norm_b) + 1) / 2 * 100  # 0-100%
        else:
            similarity = 50.0

        # Count matching states
        matches = sum(1 for a, b in zip(result_a.state_vector, result_b.state_vector) if a == b)
        match_pct = matches / len(result_a.state_vector) * 100

        return {
            "input_a": input_a,
            "input_b": input_b,
            "energy_a": result_a.energy,
            "energy_b": result_b.energy,
            "energy_diff": abs(result_a.energy - result_b.energy),
            "similarity": round(similarity, 2),
            "exact_matches": matches,
            "match_percentage": round(match_pct, 2),
            "ticks_a": result_a.ticks,
            "ticks_b": result_b.ticks,
        }

    def oracle(self, question: str) -> Dict[str, Any]:
        """
        Yes/No oracle based on energy.

        Args:
            question: The question to ask

        Returns:
            Dict with answer and confidence
        """
        result = self.process(question)

        # Determine answer based on energy
        if result.energy > 0:
            answer = "YES"
            confidence = min(abs(result.energy) / 64 * 100, 100)
        elif result.energy < 0:
            answer = "NO"
            confidence = min(abs(result.energy) / 64 * 100, 100)
        else:
            answer = "UNCERTAIN"
            confidence = 0

        return {
            "question": question,
            "answer": answer,
            "confidence": round(confidence, 1),
            "energy": result.energy,
            "ticks": result.ticks,
        }

    def get_stats(self) -> Dict[str, Any]:
        """
        Get engine statistics.

        Returns:
            Dict with engine configuration and matrix stats
        """
        stats = {
            "engine_version": "1.0.0",
            "matrix_loaded": self.matrix_loaded,
            "num_inputs": self.num_inputs,
            "num_outputs": self.num_outputs,
            "num_neighbors": self.num_neighbors,
            "max_ticks": self.max_ticks,
            "population": self.circle.population,
        }

        if self.matrix is not None:
            stats.update({
                "matrix_shape": list(self.matrix.shape),
                "matrix_min": int(self.matrix.min()),
                "matrix_max": int(self.matrix.max()),
                "matrix_mean": float(self.matrix.mean()),
                "positive_cells": int((self.matrix > 0).sum()),
                "negative_cells": int((self.matrix < 0).sum()),
                "zero_cells": int((self.matrix == 0).sum()),
            })

        return stats
