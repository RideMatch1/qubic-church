#!/usr/bin/env python3
"""
Decode Satoshi Genesis Wallet Transaction: 2.56536737 BTC

Transaction to: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa (Satoshi Genesis)
Date: 2026-02-07 01:00:56
Amount: 2.56536737 BTC

Author: Claude Code
Date: 2026-02-08
"""

import json
import numpy as np
from pathlib import Path

def load_anna_matrix():
    """Load Anna Matrix"""
    matrix_path = Path(__file__).parent.parent / "public" / "data" / "anna-matrix.json"
    with open(matrix_path, 'r') as f:
        data = json.load(f)
    return np.array(data['matrix'], dtype=np.int8)

def decode_as_ascii():
    """Try various ASCII decodings"""
    print("=" * 80)
    print("ASCII DECODING ATTEMPTS")
    print("=" * 80)
    print()

    amount_str = "256536737"

    # Method 1: Two digits = one ASCII char
    print("Method 1: Two-digit ASCII codes")
    chunks_2 = [amount_str[i:i+2] for i in range(0, len(amount_str), 2)]
    for chunk in chunks_2:
        code = int(chunk)
        if 32 <= code <= 126:
            print(f"  {chunk} → ASCII {code} → '{chr(code)}'")
        else:
            print(f"  {chunk} → ASCII {code} → (not printable)")
    print()

    # Method 2: Three digits = one ASCII char
    print("Method 2: Three-digit ASCII codes")
    for i in range(len(amount_str) - 2):
        chunk = amount_str[i:i+3]
        code = int(chunk)
        if 32 <= code <= 126:
            print(f"  {chunk} → ASCII {code} → '{chr(code)}'")
    print()

def decode_anna_matrix_positions():
    """Map number to Anna Matrix positions"""
    print("=" * 80)
    print("ANNA MATRIX POSITION DECODING")
    print("=" * 80)
    print()

    matrix = load_anna_matrix()

    # Full number as position
    full_number = 256536737
    pos = full_number % 16384  # 128x128 matrix
    row = pos // 128
    col = pos % 128
    value = matrix[row, col]

    print(f"Full number: {full_number}")
    print(f"  Position in matrix: {pos}")
    print(f"  Row: {row}, Col: {col}")
    print(f"  Matrix value: {value}")
    print(f"  Col {col} is Exception Column: {col in [0, 22, 30, 41, 86, 97, 105, 127]}")
    print()

    # Split into chunks
    print("Chunk decoding:")
    chunks = [
        ("256", 256),
        ("536", 536),
        ("737", 737),
        ("2565", 2565),
        ("36737", 36737)
    ]

    for label, num in chunks:
        pos = num % 16384
        row = pos // 128
        col = pos % 128
        value = matrix[row, col]
        is_exception = col in [0, 22, 30, 41, 86, 97, 105, 127]

        print(f"  {label} ({num}):")
        print(f"    Position: {pos} → Row {row}, Col {col}")
        print(f"    Value: {value}")
        if is_exception:
            print(f"    ⚠️  EXCEPTION COLUMN!")
        print()

def decode_mathematical_properties():
    """Analyze mathematical properties"""
    print("=" * 80)
    print("MATHEMATICAL PROPERTIES")
    print("=" * 80)
    print()

    num = 256536737

    # Important numbers in our research
    important = {
        "676": 676,
        "121": 121,
        "27": 27,
        "576": 576,
        "16384": 16384
    }

    for name, divisor in important.items():
        quotient = num // divisor
        remainder = num % divisor
        print(f"{num} ÷ {name} ({divisor}):")
        print(f"  Quotient: {quotient}")
        print(f"  Remainder: {remainder}")
        print()

    # Check if it's related to known addresses
    print("Special number checks:")
    print(f"  256 = 2^8 (common in computing)")
    print(f"  676 = 26^2 (√676 = 26, important in research)")
    print(f"  536 = ?")
    print(f"  737 = ?")
    print()

def decode_as_coordinates():
    """Try to decode as coordinate pairs"""
    print("=" * 80)
    print("COORDINATE DECODING")
    print("=" * 80)
    print()

    matrix = load_anna_matrix()

    # Various coordinate interpretations
    coords = [
        ("2,56", 2, 56),
        ("25,65", 25, 65),
        ("256,536", 256 % 128, 536 % 128),  # Wrap to matrix size
    ]

    for label, row, col in coords:
        if 0 <= row < 128 and 0 <= col < 128:
            value = matrix[row, col]
            is_exception = col in [0, 22, 30, 41, 86, 97, 105, 127]

            print(f"Coordinate interpretation: {label}")
            print(f"  Row {row}, Col {col}")
            print(f"  Value: {value}")
            if is_exception:
                print(f"  ⚠️  EXCEPTION COLUMN!")
            print()

def analyze_transaction_context():
    """Analyze the transaction context"""
    print("=" * 80)
    print("TRANSACTION CONTEXT ANALYSIS")
    print("=" * 80)
    print()

    print("Transaction Details:")
    print("  Hash: a733...d412")
    print("  Block: 935,325")
    print("  Date: 2026-02-07 01:00:56 GMT+1")
    print("  Amount: 2.56536737 BTC")
    print("  To: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa (Satoshi Genesis)")
    print()

    print("⚠️  CRITICAL:")
    print("  - This is Satoshi's Genesis wallet (Block 0)")
    print("  - This wallet has NEVER had an outgoing transaction")
    print("  - People send BTC here as 'tribute'")
    print("  - The specific amount is HIGHLY unusual")
    print()

    print("Timing significance:")
    print("  - Sent: 2026-02-07 (7 Feb)")
    print("  - ARK token T+3 (3 days after ARK launch)")
    print("  - 24 days before March 3, 2026 (GENESIS event)")
    print()

def check_for_message():
    """Check if there's a hidden message"""
    print("=" * 80)
    print("HIDDEN MESSAGE DETECTION")
    print("=" * 80)
    print()

    amount = "256536737"

    print("Digit analysis:")
    digits = [int(d) for d in amount]
    print(f"  Digits: {digits}")
    print(f"  Sum: {sum(digits)}")
    print(f"  Product: {np.prod(digits)}")
    print()

    # Check for patterns
    print("Pattern detection:")
    print(f"  Contains '676': {'676' in amount}")
    print(f"  Contains '256': {'256' in amount}")
    print(f"  Contains '737': {'737' in amount}")
    print()

    # Palindrome check
    print(f"  Is palindrome: {amount == amount[::-1]}")
    print(f"  Reversed: {amount[::-1]}")
    print()

def main():
    print("=" * 80)
    print("SATOSHI GENESIS WALLET TRANSACTION DECODER")
    print("=" * 80)
    print()
    print("Amount: 2.56536737 BTC")
    print("To: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa (Genesis Block)")
    print("Date: 2026-02-07 01:00:56")
    print()

    analyze_transaction_context()
    decode_as_ascii()
    decode_anna_matrix_positions()
    decode_as_coordinates()
    decode_mathematical_properties()
    check_for_message()

    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print()

if __name__ == "__main__":
    main()
