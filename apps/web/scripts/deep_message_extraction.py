#!/usr/bin/env python3
"""
Deep Message Extraction from Anna Matrix
Applies every possible decoding method to find hidden messages.
"""

import json
import re
from collections import defaultdict
from datetime import datetime
from typing import List, Tuple, Dict, Any


def normalize_value(val) -> int:
    """Normalize a matrix value to an integer."""
    if isinstance(val, int):
        return val
    if isinstance(val, str):
        # Handle string values like "00000000"
        try:
            return int(val)
        except ValueError:
            return 0
    return 0


def load_matrix(filepath: str) -> List[List[int]]:
    """Load the Anna Matrix from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    # Normalize all values to integers
    matrix = []
    for row in data['matrix']:
        matrix.append([normalize_value(v) for v in row])
    return matrix


def is_printable(char: str) -> bool:
    """Check if character is printable ASCII."""
    return 32 <= ord(char) <= 126


def to_char(val: int) -> str:
    """Convert value to ASCII character, handling negative values."""
    # Normalize to 0-255 range
    normalized = val & 0xFF
    if 32 <= normalized <= 126:
        return chr(normalized)
    return '.'


def extract_readable_sequences(text: str, min_length: int = 3) -> List[str]:
    """Extract all readable sequences of min_length or more printable characters."""
    sequences = []
    current = ""
    for char in text:
        if is_printable(char):
            current += char
        else:
            if len(current) >= min_length:
                # Filter out sequences that are just dots or single repeated chars
                if not all(c == '.' for c in current) and not all(c == current[0] for c in current):
                    sequences.append(current)
            current = ""
    if len(current) >= min_length:
        if not all(c == '.' for c in current) and not all(c == current[0] for c in current):
            sequences.append(current)
    return sequences


def extract_words(text: str) -> List[str]:
    """Extract potential words (letters only, 3+ chars)."""
    # Find sequences of letters
    words = re.findall(r'[a-zA-Z]{3,}', text)
    return words


def xor_row(row: List[int], constant: int) -> List[int]:
    """XOR each value in row with a constant."""
    return [(val ^ constant) & 0xFF for val in row]


def xor_rows(row1: List[int], row2: List[int]) -> List[int]:
    """XOR two rows together."""
    return [(a ^ b) & 0xFF for a, b in zip(row1, row2)]


def row_to_text(row: List[int]) -> str:
    """Convert a row of values to text."""
    return ''.join(to_char(v) for v in row)


def get_column(matrix: List[List[int]], col: int) -> List[int]:
    """Extract a column from the matrix."""
    return [row[col] for row in matrix]


def get_diagonal(matrix: List[List[int]], start_row: int = 0, start_col: int = 0, direction: int = 1) -> List[int]:
    """Extract a diagonal from the matrix.
    direction: 1 for down-right, -1 for down-left
    """
    result = []
    row, col = start_row, start_col
    while 0 <= row < len(matrix) and 0 <= col < len(matrix[0]):
        result.append(matrix[row][col])
        row += 1
        col += direction
    return result


def get_antidiagonal(matrix: List[List[int]], start_row: int = 0, start_col: int = 0) -> List[int]:
    """Extract an anti-diagonal (top-right to bottom-left)."""
    result = []
    row, col = start_row, start_col
    while 0 <= row < len(matrix) and 0 <= col < len(matrix[0]):
        result.append(matrix[row][col])
        row += 1
        col -= 1
    return result


def interleave(seq1: List[int], seq2: List[int]) -> List[int]:
    """Interleave two sequences."""
    result = []
    for a, b in zip(seq1, seq2):
        result.extend([a, b])
    return result


class DeepMessageExtractor:
    def __init__(self, matrix_path: str):
        self.matrix = load_matrix(matrix_path)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "methods_applied": [],
            "findings": [],
            "word_candidates": [],
            "all_readable_sequences": defaultdict(list),
            "special_findings": [],
            "statistics": {}
        }

        # Known constants
        self.XOR_CONSTANTS = [
            (13, "1CFB constant"),
            (27, "CFB signature"),
            (100, "decode key"),
            (127, "symmetry axis"),
            (42, "answer to everything"),
            (64, "ASCII offset"),
            (85, "0x55 pattern"),
            (170, "0xAA pattern"),
            (255, "inversion"),
            (21, "blackjack"),
            (88, "byte X"),
            (37, "prime"),
            (73, "IOTA I"),
            (123, "0x7B"),
        ]

        # Fibonacci positions
        self.FIBONACCI_POSITIONS = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
        self.FIBONACCI_UNIQUE = sorted(set(self.FIBONACCI_POSITIONS))

        # Anomalous pairs
        self.ANOMALOUS_PAIRS = [
            (0, 127),
            (22, 105),
            (30, 97),
            (41, 86)
        ]

    def add_finding(self, method: str, content: str, words: List[str], sequences: List[str], significance: str = "low"):
        """Add a finding to results."""
        if words or sequences:
            finding = {
                "method": method,
                "readable_content": content[:500],  # Truncate long content
                "words_found": list(set(words))[:50],
                "sequences_found": list(set(sequences))[:50],
                "word_count": len(words),
                "sequence_count": len(sequences),
                "significance": significance
            }
            self.results["findings"].append(finding)

            # Track all readable sequences
            for seq in sequences:
                self.results["all_readable_sequences"][method].append(seq)

            # Collect word candidates
            for word in words:
                if len(word) >= 3:
                    self.results["word_candidates"].append({
                        "word": word,
                        "method": method
                    })

    def method_xor_with_constants(self):
        """XOR entire matrix with various constants."""
        self.results["methods_applied"].append("XOR with constants")

        for constant, name in self.XOR_CONSTANTS:
            all_text = ""
            for row in self.matrix:
                xored = xor_row(row, constant)
                all_text += row_to_text(xored)

            words = extract_words(all_text)
            sequences = extract_readable_sequences(all_text)
            self.add_finding(
                f"XOR with {constant} ({name})",
                all_text,
                words,
                sequences,
                "medium" if len(words) > 10 else "low"
            )

    def method_row_regions(self):
        """Extract specific row regions."""
        self.results["methods_applied"].append("Row region extraction")

        regions = [
            ((0, 32), "First quarter (rows 0-31)"),
            ((27, 35), "Fibonacci region (rows 27-34)"),
            ((64, 65), "Middle row 64"),
            ((96, 128), "Last quarter (rows 96-127)"),
            ((60, 68), "Central 8 rows"),
        ]

        for (start, end), name in regions:
            all_text = ""
            for row in self.matrix[start:end]:
                all_text += row_to_text(row)

            words = extract_words(all_text)
            sequences = extract_readable_sequences(all_text)
            self.add_finding(f"Region: {name}", all_text, words, sequences)

    def method_fibonacci_positions(self):
        """Extract values at Fibonacci row positions."""
        self.results["methods_applied"].append("Fibonacci position extraction")

        # Rows at Fibonacci indices
        fib_text = ""
        for pos in self.FIBONACCI_UNIQUE:
            if pos < len(self.matrix):
                fib_text += row_to_text(self.matrix[pos])

        words = extract_words(fib_text)
        sequences = extract_readable_sequences(fib_text)
        self.add_finding("Fibonacci rows", fib_text, words, sequences, "high")

        # Columns at Fibonacci indices
        fib_cols_text = ""
        for col in self.FIBONACCI_UNIQUE:
            if col < 128:
                col_data = get_column(self.matrix, col)
                fib_cols_text += row_to_text(col_data)

        words = extract_words(fib_cols_text)
        sequences = extract_readable_sequences(fib_cols_text)
        self.add_finding("Fibonacci columns", fib_cols_text, words, sequences, "high")

    def method_diagonals(self):
        """Extract diagonals from the matrix."""
        self.results["methods_applied"].append("Diagonal extraction")

        # Main diagonal
        main_diag = get_diagonal(self.matrix, 0, 0)
        text = row_to_text(main_diag)
        words = extract_words(text)
        sequences = extract_readable_sequences(text)
        self.add_finding("Main diagonal", text, words, sequences, "medium")

        # Anti-diagonal
        anti_diag = get_antidiagonal(self.matrix, 0, 127)
        text = row_to_text(anti_diag)
        words = extract_words(text)
        sequences = extract_readable_sequences(text)
        self.add_finding("Anti-diagonal", text, words, sequences, "medium")

        # All major diagonals
        all_diag_text = ""
        for i in range(128):
            diag = get_diagonal(self.matrix, i, 0)
            all_diag_text += row_to_text(diag)
        for i in range(1, 128):
            diag = get_diagonal(self.matrix, 0, i)
            all_diag_text += row_to_text(diag)

        words = extract_words(all_diag_text)
        sequences = extract_readable_sequences(all_diag_text)
        self.add_finding("All diagonals", all_diag_text, words, sequences)

    def method_character_filters(self):
        """Apply character type filters."""
        self.results["methods_applied"].append("Character filters")

        full_text = ""
        for row in self.matrix:
            full_text += row_to_text(row)

        # Uppercase only
        uppercase = ''.join(c for c in full_text if c.isupper())
        words = extract_words(uppercase)
        sequences = extract_readable_sequences(uppercase)
        self.add_finding("Uppercase only", uppercase, words, sequences, "high")

        # Lowercase only
        lowercase = ''.join(c for c in full_text if c.islower())
        words = extract_words(lowercase)
        sequences = extract_readable_sequences(lowercase)
        self.add_finding("Lowercase only", lowercase, words, sequences, "high")

        # Digits only
        digits = ''.join(c for c in full_text if c.isdigit())
        if len(digits) >= 3:
            self.add_finding("Digits only", digits, [], [digits], "medium")

        # Letters only
        letters = ''.join(c for c in full_text if c.isalpha())
        words = extract_words(letters)
        sequences = extract_readable_sequences(letters)
        self.add_finding("Letters only", letters, words, sequences, "high")

    def method_nibble_extraction(self):
        """Extract high and low nibbles."""
        self.results["methods_applied"].append("Nibble extraction")

        high_nibbles = []
        low_nibbles = []

        for row in self.matrix:
            for val in row:
                normalized = val & 0xFF
                high_nibbles.append((normalized >> 4) & 0x0F)
                low_nibbles.append(normalized & 0x0F)

        # Convert nibbles to text (shifted to printable range)
        high_text = ''.join(chr(n + 65) if 0 <= n <= 25 else '.' for n in high_nibbles)  # A-Z for 0-15
        low_text = ''.join(chr(n + 65) if 0 <= n <= 25 else '.' for n in low_nibbles)

        words = extract_words(high_text)
        sequences = extract_readable_sequences(high_text)
        self.add_finding("High nibbles (as A-P)", high_text, words, sequences)

        words = extract_words(low_text)
        sequences = extract_readable_sequences(low_text)
        self.add_finding("Low nibbles (as A-P)", low_text, words, sequences)

    def method_nth_character(self):
        """Read every Nth character."""
        self.results["methods_applied"].append("Every Nth character")

        full_data = []
        for row in self.matrix:
            full_data.extend(row)

        for n in [2, 3, 5, 7, 8, 13, 27]:
            nth_data = full_data[::n]
            text = row_to_text(nth_data)
            words = extract_words(text)
            sequences = extract_readable_sequences(text)
            self.add_finding(f"Every {n}th value", text, words, sequences)

    def method_pair_analysis(self):
        """Analyze anomalous pairs with various operations."""
        self.results["methods_applied"].append("Anomalous pair analysis")

        for col_a, col_b in self.ANOMALOUS_PAIRS:
            row_a = get_column(self.matrix, col_a)
            row_b = get_column(self.matrix, col_b)

            # XOR the pair columns
            xored = xor_rows(row_a, row_b)
            text = row_to_text(xored)
            words = extract_words(text)
            sequences = extract_readable_sequences(text)
            self.add_finding(f"Pair {col_a}<->{col_b} XOR", text, words, sequences, "high")

            # Difference
            diff = [(a - b) & 0xFF for a, b in zip(row_a, row_b)]
            text = row_to_text(diff)
            words = extract_words(text)
            sequences = extract_readable_sequences(text)
            self.add_finding(f"Pair {col_a}<->{col_b} difference", text, words, sequences)

            # Average
            avg = [((a + b) // 2) & 0xFF for a, b in zip(row_a, row_b)]
            text = row_to_text(avg)
            words = extract_words(text)
            sequences = extract_readable_sequences(text)
            self.add_finding(f"Pair {col_a}<->{col_b} average", text, words, sequences)

    def method_multi_pair_combination(self):
        """Combine multiple anomalous pairs."""
        self.results["methods_applied"].append("Multi-pair combination")

        # XOR pair 22<->105 WITH pair 30<->97
        col22 = get_column(self.matrix, 22)
        col105 = get_column(self.matrix, 105)
        col30 = get_column(self.matrix, 30)
        col97 = get_column(self.matrix, 97)

        pair1_xor = xor_rows(col22, col105)
        pair2_xor = xor_rows(col30, col97)
        combined_xor = xor_rows(pair1_xor, pair2_xor)

        text = row_to_text(combined_xor)
        words = extract_words(text)
        sequences = extract_readable_sequences(text)
        self.add_finding("Pair 22<->105 XOR Pair 30<->97", text, words, sequences, "high")

        # Concatenate asymmetric portions
        all_asymmetric = ""
        for col_a, col_b in self.ANOMALOUS_PAIRS:
            row_a = get_column(self.matrix, col_a)
            row_b = get_column(self.matrix, col_b)
            # Extract only where values differ
            for i, (a, b) in enumerate(zip(row_a, row_b)):
                if a != b:
                    all_asymmetric += to_char(a) + to_char(b)

        words = extract_words(all_asymmetric)
        sequences = extract_readable_sequences(all_asymmetric)
        self.add_finding("All asymmetric values concatenated", all_asymmetric, words, sequences, "high")

    def method_reverse_mirror(self):
        """Apply reverse and mirror operations."""
        self.results["methods_applied"].append("Reverse/mirror operations")

        # Read matrix backwards
        full_data = []
        for row in self.matrix:
            full_data.extend(row)

        reversed_text = row_to_text(full_data[::-1])
        words = extract_words(reversed_text)
        sequences = extract_readable_sequences(reversed_text)
        self.add_finding("Matrix reversed", reversed_text, words, sequences)

        # Each row reversed
        row_reversed_text = ""
        for row in self.matrix:
            row_reversed_text += row_to_text(row[::-1])

        words = extract_words(row_reversed_text)
        sequences = extract_readable_sequences(row_reversed_text)
        self.add_finding("Each row reversed", row_reversed_text, words, sequences)

        # Interleave forward and backward
        forward = full_data
        backward = full_data[::-1]
        interleaved = interleave(forward, backward)
        text = row_to_text(interleaved)
        words = extract_words(text)
        sequences = extract_readable_sequences(text)
        self.add_finding("Interleaved forward/backward", text, words, sequences)

    def method_column_extraction(self):
        """Extract specific columns."""
        self.results["methods_applied"].append("Column extraction")

        # All columns as text
        all_cols_text = ""
        for col in range(128):
            col_data = get_column(self.matrix, col)
            all_cols_text += row_to_text(col_data)

        words = extract_words(all_cols_text)
        sequences = extract_readable_sequences(all_cols_text)
        self.add_finding("All columns read down", all_cols_text, words, sequences)

        # Anomalous pair columns specifically
        for col_a, col_b in self.ANOMALOUS_PAIRS:
            col_data_a = get_column(self.matrix, col_a)
            col_data_b = get_column(self.matrix, col_b)
            text_a = row_to_text(col_data_a)
            text_b = row_to_text(col_data_b)

            words = extract_words(text_a + text_b)
            sequences = extract_readable_sequences(text_a + text_b)
            self.add_finding(f"Columns {col_a} and {col_b}", text_a + text_b, words, sequences)

    def method_bit_patterns(self):
        """Extract specific bit patterns."""
        self.results["methods_applied"].append("Bit pattern extraction")

        # Extract bit 7 (sign bit) from each byte
        sign_bits = []
        for row in self.matrix:
            for val in row:
                normalized = val & 0xFF
                sign_bits.append((normalized >> 7) & 1)

        # Convert to binary string
        binary_str = ''.join(str(b) for b in sign_bits)

        # Convert groups of 8 bits to characters
        bit_chars = []
        for i in range(0, len(binary_str) - 7, 8):
            byte_val = int(binary_str[i:i+8], 2)
            if 32 <= byte_val <= 126:
                bit_chars.append(chr(byte_val))

        text = ''.join(bit_chars)
        words = extract_words(text)
        sequences = extract_readable_sequences(text)
        self.add_finding("Sign bits as bytes", text, words, sequences)

    def method_caesar_shift(self):
        """Apply Caesar cipher shifts."""
        self.results["methods_applied"].append("Caesar shifts")

        full_text = ""
        for row in self.matrix:
            full_text += row_to_text(row)

        # Get letters only
        letters = ''.join(c for c in full_text if c.isalpha())

        for shift in [1, 3, 7, 13, 25]:
            shifted = ""
            for c in letters:
                if c.isupper():
                    shifted += chr((ord(c) - 65 + shift) % 26 + 65)
                else:
                    shifted += chr((ord(c) - 97 + shift) % 26 + 97)

            words = extract_words(shifted)
            sequences = extract_readable_sequences(shifted)
            self.add_finding(f"Caesar shift +{shift}", shifted, words, sequences)

    def method_row_xor_adjacent(self):
        """XOR adjacent rows."""
        self.results["methods_applied"].append("Adjacent row XOR")

        all_xor_text = ""
        for i in range(len(self.matrix) - 1):
            xored = xor_rows(self.matrix[i], self.matrix[i + 1])
            all_xor_text += row_to_text(xored)

        words = extract_words(all_xor_text)
        sequences = extract_readable_sequences(all_xor_text)
        self.add_finding("Adjacent rows XORed", all_xor_text, words, sequences)

    def method_symmetry_center(self):
        """Analyze the symmetry center of the matrix."""
        self.results["methods_applied"].append("Symmetry center analysis")

        # Extract rows around center (rows 60-67)
        center_text = ""
        for row in self.matrix[60:68]:
            center_text += row_to_text(row)

        words = extract_words(center_text)
        sequences = extract_readable_sequences(center_text)
        self.add_finding("Center rows (60-67)", center_text, words, sequences, "medium")

        # Extract center columns (60-67)
        center_cols_text = ""
        for col in range(60, 68):
            col_data = get_column(self.matrix, col)
            center_cols_text += row_to_text(col_data)

        words = extract_words(center_cols_text)
        sequences = extract_readable_sequences(center_cols_text)
        self.add_finding("Center columns (60-67)", center_cols_text, words, sequences, "medium")

    def method_modular_extraction(self):
        """Extract values at modular positions."""
        self.results["methods_applied"].append("Modular position extraction")

        full_data = []
        for row in self.matrix:
            full_data.extend(row)

        # Extract where index % N == specific value
        for mod in [7, 13, 19, 27]:
            for remainder in [0, 1]:
                extracted = [full_data[i] for i in range(len(full_data)) if i % mod == remainder]
                text = row_to_text(extracted)
                words = extract_words(text)
                sequences = extract_readable_sequences(text)
                self.add_finding(f"Index % {mod} == {remainder}", text, words, sequences)

    def method_row_specific(self):
        """Analyze specific important rows."""
        self.results["methods_applied"].append("Specific row analysis")

        important_rows = [
            (0, "First row"),
            (13, "Row 13 (1CFB)"),
            (27, "Row 27 (CFB)"),
            (42, "Row 42 (Answer)"),
            (64, "Row 64 (Center)"),
            (73, "Row 73 (IOTA I)"),
            (88, "Row 88 (Byte X)"),
            (127, "Row 127 (Last)"),
        ]

        for row_idx, name in important_rows:
            if row_idx < len(self.matrix):
                text = row_to_text(self.matrix[row_idx])
                words = extract_words(text)
                sequences = extract_readable_sequences(text)
                self.add_finding(name, text, words, sequences, "medium")

    def method_ascii_sum_patterns(self):
        """Look for patterns in ASCII sums."""
        self.results["methods_applied"].append("ASCII sum patterns")

        # Sum each row
        row_sums = []
        for row in self.matrix:
            row_sum = sum(v & 0xFF for v in row)
            row_sums.append(row_sum)

        # Look for sums that spell something when converted to ASCII
        sum_chars = []
        for s in row_sums:
            mod_sum = s % 256
            if 32 <= mod_sum <= 126:
                sum_chars.append(chr(mod_sum))

        text = ''.join(sum_chars)
        words = extract_words(text)
        sequences = extract_readable_sequences(text)
        self.add_finding("Row sums as ASCII", text, words, sequences)

    def method_special_values(self):
        """Look for special value patterns."""
        self.results["methods_applied"].append("Special value extraction")

        # Find positions of specific interesting values
        special_values = [65, 73, 71, 65, 82, 84, 72]  # AIGARTH in ASCII

        positions = []
        for r_idx, row in enumerate(self.matrix):
            for c_idx, val in enumerate(row):
                normalized = val & 0xFF
                if normalized in special_values:
                    positions.append((r_idx, c_idx, chr(normalized)))

        # Extract just these characters
        aigarth_chars = ''.join(p[2] for p in positions[:100])
        words = extract_words(aigarth_chars)
        sequences = extract_readable_sequences(aigarth_chars)
        self.add_finding("AIGARTH letter positions", aigarth_chars, words, sequences, "high")

    def method_difference_from_center(self):
        """Calculate difference from center value."""
        self.results["methods_applied"].append("Difference from center")

        # Use 64 as center
        diff_text = ""
        for row in self.matrix:
            for val in row:
                normalized = val & 0xFF
                diff = (normalized - 64) & 0xFF
                diff_text += to_char(diff)

        words = extract_words(diff_text)
        sequences = extract_readable_sequences(diff_text)
        self.add_finding("Values - 64", diff_text, words, sequences)

    def compile_results(self):
        """Compile final results and statistics."""
        # Count unique words
        all_words = []
        for finding in self.results["findings"]:
            all_words.extend(finding["words_found"])

        word_counts = defaultdict(int)
        for word in all_words:
            word_counts[word.upper()] += 1

        # Find words that appear multiple times across methods
        repeated_words = {word: count for word, count in word_counts.items() if count >= 2}

        # Look for meaningful patterns
        english_like = []
        for word in set(all_words):
            # Simple heuristic: contains vowels and is reasonable length
            has_vowel = any(c in 'aeiouAEIOU' for c in word)
            if has_vowel and 3 <= len(word) <= 15:
                english_like.append(word)

        self.results["statistics"] = {
            "total_findings": len(self.results["findings"]),
            "methods_applied": len(self.results["methods_applied"]),
            "unique_words_found": len(set(all_words)),
            "repeated_words": repeated_words,
            "english_like_words": sorted(set(english_like))[:100],
            "high_significance_count": len([f for f in self.results["findings"] if f["significance"] == "high"])
        }

        # Identify special findings
        special_patterns = ["FIB", "AI", "MEG", "GOU", "CFB", "QUBIC", "IOTA", "KEY", "SEED",
                          "BTC", "ANNA", "AIGARTH", "BRIDGE", "SATOSHI", "BITCOIN"]

        for pattern in special_patterns:
            for finding in self.results["findings"]:
                for word in finding["words_found"]:
                    if pattern in word.upper():
                        self.results["special_findings"].append({
                            "pattern": pattern,
                            "word": word,
                            "method": finding["method"]
                        })

    def run_all_methods(self):
        """Run all extraction methods."""
        print("Running deep message extraction...")

        self.method_xor_with_constants()
        print("  - XOR with constants: done")

        self.method_row_regions()
        print("  - Row regions: done")

        self.method_fibonacci_positions()
        print("  - Fibonacci positions: done")

        self.method_diagonals()
        print("  - Diagonals: done")

        self.method_character_filters()
        print("  - Character filters: done")

        self.method_nibble_extraction()
        print("  - Nibble extraction: done")

        self.method_nth_character()
        print("  - Every Nth character: done")

        self.method_pair_analysis()
        print("  - Pair analysis: done")

        self.method_multi_pair_combination()
        print("  - Multi-pair combination: done")

        self.method_reverse_mirror()
        print("  - Reverse/mirror: done")

        self.method_column_extraction()
        print("  - Column extraction: done")

        self.method_bit_patterns()
        print("  - Bit patterns: done")

        self.method_caesar_shift()
        print("  - Caesar shifts: done")

        self.method_row_xor_adjacent()
        print("  - Adjacent row XOR: done")

        self.method_symmetry_center()
        print("  - Symmetry center: done")

        self.method_modular_extraction()
        print("  - Modular extraction: done")

        self.method_row_specific()
        print("  - Specific rows: done")

        self.method_ascii_sum_patterns()
        print("  - ASCII sum patterns: done")

        self.method_special_values()
        print("  - Special values: done")

        self.method_difference_from_center()
        print("  - Difference from center: done")

        self.compile_results()
        print("  - Results compiled")

        return self.results


def main():
    matrix_path = "/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/anna-matrix.json"
    output_path = "/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/DEEP_MESSAGE_EXTRACTION.json"

    extractor = DeepMessageExtractor(matrix_path)
    results = extractor.run_all_methods()

    # Convert defaultdict to regular dict for JSON serialization
    results["all_readable_sequences"] = dict(results["all_readable_sequences"])

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n=== DEEP MESSAGE EXTRACTION COMPLETE ===")
    print(f"Results saved to: {output_path}")
    print(f"\nStatistics:")
    print(f"  - Methods applied: {results['statistics']['methods_applied']}")
    print(f"  - Total findings: {results['statistics']['total_findings']}")
    print(f"  - Unique words found: {results['statistics']['unique_words_found']}")
    print(f"  - High significance findings: {results['statistics']['high_significance_count']}")

    if results['special_findings']:
        print(f"\n=== SPECIAL FINDINGS ===")
        seen = set()
        for sf in results['special_findings']:
            key = f"{sf['pattern']}:{sf['word']}"
            if key not in seen:
                print(f"  {sf['pattern']} found in '{sf['word']}' via {sf['method']}")
                seen.add(key)

    if results['statistics']['repeated_words']:
        print(f"\n=== REPEATED WORDS (appear in multiple methods) ===")
        sorted_words = sorted(results['statistics']['repeated_words'].items(), key=lambda x: -x[1])[:30]
        for word, count in sorted_words:
            print(f"  {word}: {count} times")

    if results['statistics']['english_like_words']:
        print(f"\n=== ENGLISH-LIKE WORDS (sample) ===")
        for word in results['statistics']['english_like_words'][:40]:
            print(f"  {word}")


if __name__ == "__main__":
    main()
