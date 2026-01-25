"""
TERNARY ENCODING MODULE

EXACT implementation from Qubic Core (score_common.h):

template <unsigned long long bitCount>
static void toTenaryBits(long long A, char* bits) {
    for (unsigned long long i = 0; i < bitCount; ++i) {
        char bitValue = static_cast<char>((A >> i) & 1);
        bits[i] = (bitValue == 0) ? -1 : bitValue;
    }
}

Key insight: Binary 0 -> -1, Binary 1 -> +1
This creates ternary states: -1 (FALSE/inhibited), 0 (UNKNOWN/neutral), +1 (TRUE/excited)
"""

from typing import List, Literal, Union
from enum import IntEnum


class TernaryState(IntEnum):
    """Ternary state values."""
    INHIBITED = -1  # FALSE, negation
    NEUTRAL = 0     # UNKNOWN, undecided
    EXCITED = 1     # TRUE, activation


def ternary_clamp(value: int) -> int:
    """
    Clamp value to ternary range [-1, 0, +1].

    This is the fundamental operation that converts weighted sums
    to ternary neuron states.

    Args:
        value: Any integer

    Returns:
        -1 if value < 0
        +1 if value > 0
        0 if value == 0
    """
    if value > 0:
        return 1
    elif value < 0:
        return -1
    return 0


def to_ternary_bits(number: int, bit_count: int) -> List[int]:
    """
    Convert number to ternary bits.

    EXACT implementation from Qubic Core score_common.h:
    - Binary bit 0 -> -1 (FALSE)
    - Binary bit 1 -> +1 (TRUE)

    Args:
        number: Integer to convert
        bit_count: Number of bits to extract

    Returns:
        List of ternary values (-1 or +1)

    Example:
        >>> to_ternary_bits(5, 4)  # 5 = 0101 in binary
        [1, -1, 1, -1]  # LSB first: bit0=1->+1, bit1=0->-1, bit2=1->+1, bit3=0->-1
    """
    bits = []
    for i in range(bit_count):
        bit_value = (number >> i) & 1
        # Key transformation: 0 -> -1, 1 -> +1
        bits.append(-1 if bit_value == 0 else 1)
    return bits


def from_ternary_bits(bits: List[int]) -> int:
    """
    Convert ternary bits back to integer.

    Based on extractLastOutput from Qubic Core:
    - Positive values -> 1
    - Non-positive values -> 0

    Args:
        bits: List of ternary values

    Returns:
        Decoded integer

    Example:
        >>> from_ternary_bits([1, -1, 1, -1])
        5  # bit0=1, bit1=0, bit2=1, bit3=0 = 0101 = 5
    """
    result = 0
    for i, bit in enumerate(bits):
        # Positive -> 1, otherwise -> 0
        if bit > 0:
            result |= (1 << i)
    return result


def bytes_to_ternary(data: bytes) -> List[int]:
    """
    Convert bytes to ternary bits.

    Each byte produces 8 ternary values.

    Args:
        data: Bytes to convert

    Returns:
        List of ternary values (8 per byte)
    """
    result = []
    for byte in data:
        result.extend(to_ternary_bits(byte, 8))
    return result


def text_to_ternary(text: str, max_bytes: int = 64) -> List[int]:
    """
    Convert text to ternary bits.

    UTF-8 encodes the text, then converts to ternary.
    Pads with -1 (like 0 bits) if needed.

    Args:
        text: Text to convert
        max_bytes: Maximum bytes to use (default 64 = 512 ternary bits)

    Returns:
        List of ternary values
    """
    # Encode to UTF-8
    text_bytes = text.encode('utf-8')[:max_bytes]

    # Convert to ternary
    result = bytes_to_ternary(text_bytes)

    # Pad to fixed size
    target_size = max_bytes * 8
    while len(result) < target_size:
        result.append(-1)  # Pad with -1 (like binary 0)

    return result[:target_size]


def hex_to_ternary(hex_string: str) -> List[int]:
    """
    Convert hex string to ternary bits.

    Handles both with and without '0x' prefix.

    Args:
        hex_string: Hex string (e.g., "0xDEADBEEF" or "deadbeef")

    Returns:
        List of ternary values
    """
    # Remove 0x prefix if present
    clean_hex = hex_string.lower().replace('0x', '')

    # Pad to even length
    if len(clean_hex) % 2 != 0:
        clean_hex = '0' + clean_hex

    # Convert to bytes
    data = bytes.fromhex(clean_hex)

    return bytes_to_ternary(data)


def coords_to_ternary(coord_string: str) -> tuple[int, int, int]:
    """
    Parse Anna coordinate format "X+Y" or "X,Y".

    Args:
        coord_string: Coordinate string (e.g., "6+33" or "6,33")

    Returns:
        Tuple of (anna_x, anna_y, matrix_value) - matrix_value requires external lookup

    Raises:
        ValueError: If format is invalid
    """
    # Try different separators
    for sep in ['+', ',', ' ']:
        if sep in coord_string:
            parts = coord_string.split(sep)
            if len(parts) == 2:
                try:
                    x = int(parts[0].strip())
                    y = int(parts[1].strip())
                    return (x, y, 0)  # matrix_value needs external lookup
                except ValueError:
                    continue

    raise ValueError(f"Invalid coordinate format: {coord_string}. Expected 'X+Y' or 'X,Y'")


def compute_energy(states: List[int]) -> int:
    """
    Compute total energy of ternary states.

    Energy is simply the sum of all states.
    Positive energy = more excited neurons
    Negative energy = more inhibited neurons
    Zero energy = balanced

    Args:
        states: List of ternary values

    Returns:
        Sum of all states
    """
    return sum(states)


def compute_distribution(states: List[int]) -> dict[str, int]:
    """
    Compute distribution of ternary states.

    Args:
        states: List of ternary values

    Returns:
        Dict with counts for positive, neutral, negative
    """
    positive = sum(1 for s in states if s > 0)
    negative = sum(1 for s in states if s < 0)
    neutral = sum(1 for s in states if s == 0)

    return {
        "positive": positive,
        "neutral": neutral,
        "negative": negative,
    }
