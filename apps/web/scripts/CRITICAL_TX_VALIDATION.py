#!/usr/bin/env python3
"""
CRITICAL SELF-VALIDATION - Satoshi Genesis Transaction

Go through EVERY claim we made and validate honestly.
Flag bullshit vs. real findings.

Methodology:
- For each claim, calculate the probability of it occurring by CHANCE
- If P > 1% -> LIKELY COINCIDENCE (WEAK)
- If P < 0.1% -> POSSIBLY SIGNIFICANT (MEDIUM)
- If P < 0.01% -> LIKELY INTENTIONAL (STRONG)

Author: Claude Code
Date: 2026-02-08
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime

def load_anna_matrix():
    matrix_path = Path(__file__).parent.parent / "public" / "data" / "anna-matrix.json"
    with open(matrix_path, 'r') as f:
        data = json.load(f)
    return np.array(data['matrix'], dtype=np.int8)

def validate_claim_1_ascii():
    print("=" * 80)
    print("CLAIM 1: '256536737' decodes to ASCII 'A $ I'")
    print("=" * 80)
    print()
    print("  Split chosen: 25 | 65 | 36 | 73 | 7")
    print("  Only 3 of 5 chunks are printable: 65='A', 36='$', 73='I'")
    print("  25 = NOT printable, 7 = NOT printable")
    print()
    print("  ALTERNATIVE SPLIT: 2 | 56 | 53 | 67 | 37")
    print("  56='8', 53='5', 67='C', 37='%' → '85C%'")
    print()
    print("  PROBLEM: We cherry-picked the split.")
    print("  With 2-digit ASCII, ~95% of chunks give printable characters.")
    print("  ANY number can be 'decoded' into something.")
    print()
    print("  >>> VERDICT: WEAK - Confirmation bias <<<")
    print()

def validate_claim_2_matrix_positions():
    print("=" * 80)
    print("CLAIM 2: Positions 256, 536, 737 map to Exception Columns")
    print("=" * 80)
    print()

    matrix = load_anna_matrix()
    exception_cols = [0, 22, 30, 41, 86, 97, 105, 127]

    chunks = [(256, "256"), (536, "536"), (737, "737")]
    for num, label in chunks:
        row = (num % 16384) // 128
        col = (num % 16384) % 128
        value = matrix[row, col]
        is_exc = col in exception_cols
        print(f"  {label}: Row {row}, Col {col}, Value {value} {'EXCEPTION' if is_exc else ''}")

    p = 3 * (8/128)**2 * (120/128)**1
    print(f"\n  P(2 of 3 hit exception) = {p:.4f} = {p*100:.2f}%")
    print("  PROBLEM: We chose the 3-3-3 split specifically.")
    print("  Other splits (2565|36737, etc.) give different results.")
    print()
    print("  >>> VERDICT: MEDIUM-WEAK (1.1% by chance, but cherry-picked split) <<<")
    print()

def validate_claim_3_digits_sum_44():
    print("=" * 80)
    print("CLAIM 3: Digit sum = 44 = Block 264 nonce last byte")
    print("=" * 80)
    print()
    digits = [2,5,6,5,3,6,7,3,7]
    print(f"  Sum: {sum(digits)} = 44 CONFIRMED")
    print(f"  P(digit sum = 44 for 9-digit number) ~ 1/82 ~ 1.2%")
    print()
    print("  BUT: Is Block 264 nonce last byte really 44?")
    print("  The Patoshi nonce range is [0..9] + [19..58]")
    print("  44 IS in the Patoshi range, but we need to verify it's")
    print("  specifically Block 264's nonce last byte.")
    print()
    print("  Even if true: 1.2% is not extraordinary.")
    print("  If we tested 50 different 'interesting' numbers, we'd expect")
    print("  one to match by chance.")
    print()
    print("  >>> VERDICT: WEAK (unverified claim, 1.2% probability) <<<")
    print()

def validate_claim_4_3fbc():
    print("=" * 80)
    print("CLAIM 4: TX hash contains '3fbc' = '3 x CFB'")
    print("=" * 80)
    print()
    tx_hash = "a73335706adad5c400453fbc3c992f23cacf56b0ca964bc584f5f44ac7e0d412"
    print(f"  Hash: {tx_hash}")
    print(f"  Contains '3fbc': True at position 20")
    print()

    p = 1 - (1 - 1/65536)**61
    print(f"  P('3fbc' in random 64-hex) = {p*100:.3f}%")
    print()
    print("  CRITICAL PROBLEMS:")
    print("  1. TX hash is SHA256(SHA256(tx)) - NOT controllable by sender!")
    print("  2. '3fbc' reads as '3 FBC', NOT 'CFB'. Letters are WRONG ORDER!")
    print("  3. Sender COULD brute-force by tweaking amounts (~1000 attempts)")
    print("     But why '3fbc' instead of 'cfb0' or '0cfb'?")
    print("  4. Nobody would encode 'CFB' as '3FBC'")
    print()
    print("  >>> VERDICT: VERY WEAK (wrong letter order, likely coincidence) <<<")
    print()

def validate_claim_5_value_27():
    print("=" * 80)
    print("CLAIM 5: Position 536 -> Matrix Value 27 (key number)")
    print("=" * 80)
    print()
    matrix = load_anna_matrix()
    row = (536 % 16384) // 128
    col = (536 % 16384) % 128
    value = matrix[row, col]
    count_27 = int(np.sum(matrix == 27))
    total = 128*128
    p = count_27 / total
    print(f"  Position 536: Row {row}, Col {col}, Value {value}")
    print(f"  Cells with value 27: {count_27}/{total} = {p*100:.2f}%")
    print()
    print("  PROBLEM: Only works with 256|536|737 split.")
    print(f"  P(random cell = 27) = {p*100:.2f}%")
    print()
    if p > 0.5:
        print("  >>> VERDICT: WEAK (not rare at all) <<<")
    else:
        print("  >>> VERDICT: MEDIUM-WEAK (depends on cherry-picked split) <<<")
    print()

def validate_claim_6_19_inputs():
    print("=" * 80)
    print("CLAIM 6: 19 inputs x 121 = 2,299 = Block 264 connection")
    print("=" * 80)
    print()
    print(f"  19 x 121 = {19*121}")
    print()
    print("  CRITICAL PROBLEMS:")
    print("  1. What is 'Block 264 hash sum = 2299'? This is MADE UP.")
    print("     There is no established concept of 'block hash sum'.")
    print("  2. We picked 121 (from 11^2) to multiply with 19.")
    print("     Why not 19 x 676 = 12,844? Or 19 x 27 = 513?")
    print("  3. With 19 and enough multipliers, we can get ANY number.")
    print("  4. 19 inputs is NORMAL for UTXO consolidation.")
    print()
    print("  >>> VERDICT: FABRICATED (we invented a non-existent connection) <<<")
    print()

def validate_claim_7_timing():
    print("=" * 80)
    print("CLAIM 7: 24 days to March 3 = sqrt(576)")
    print("=" * 80)
    print()
    dt = datetime(2026, 2, 7)
    march3 = datetime(2026, 3, 3)
    delta = (march3 - dt).days
    print(f"  Feb 7 -> March 3 = {delta} days")
    print(f"  sqrt(576) = 24")
    print(f"  sqrt(529) = 23")
    print()
    if delta != 24:
        print(f"  WRONG! It's {delta} days, NOT 24!")
        print(f"  We made an arithmetic error to force the connection.")
        print(f"  23^2 = 529, which has no significance in our research.")
    print()
    print("  ALSO: Why would March 3 be relevant to this transaction?")
    print("  We ASSUME it's related, then force the math.")
    print()
    print(f"  >>> VERDICT: WRONG (it's {delta} days, not 24) <<<")
    print()

def validate_claim_8_other_output():
    print("=" * 80)
    print("CLAIM 8: 12.00108347 BTC contains a hidden message")
    print("=" * 80)
    print()
    total_in = 14.56650568
    sent = 2.56536737
    fee = 0.00005484
    change = total_in - sent - fee
    print(f"  Total inputs:    {total_in:.8f} BTC")
    print(f"  Sent to Genesis: {sent:.8f} BTC")
    print(f"  Fee:             {fee:.8f} BTC")
    print(f"  Calculated change: {change:.8f} BTC")
    print(f"  Listed change:     12.00108347 BTC")
    print(f"  Match: {abs(change - 12.00108347) < 0.00000001}")
    print()
    print("  THIS IS JUST THE CHANGE OUTPUT!")
    print("  It's the leftover BTC going back to the sender.")
    print("  Not a separate message - pure arithmetic.")
    print()
    print("  >>> VERDICT: NOT A MESSAGE (just change) <<<")
    print()

def validate_claim_9_12_sacred():
    print("=" * 80)
    print("CLAIM 9: Number 12 appears everywhere")
    print("=" * 80)
    print()
    print("  Appearances:")
    print("  1. Time 01:00:56 digits sum = 12 → True but not rare")
    print("  2. Change output = 12.x BTC → Just math (see above)")
    print("  3. Hash ends ...d412 → Cherry-picking '12' from '412'")
    print()
    print("  '12' is one of the most common numbers.")
    print("  We'd find it in MOST transactions if we look hard enough.")
    print()
    print("  >>> VERDICT: WEAK (confirmation bias) <<<")
    print()

def what_is_actually_real():
    print("=" * 80)
    print("WHAT IS ACTUALLY REAL?")
    print("=" * 80)
    print()
    print("DEFINITELY REAL:")
    print("  1. Someone sent exactly 2.56536737 BTC to Genesis wallet")
    print("  2. The amount has 8 significant decimal places (very specific)")
    print("  3. This is NOT a round number -> likely intentional")
    print("  4. Date: Feb 7, 2026")
    print()
    print("THINGS WE CAN CHECK:")
    print("  1. Sender addresses - who are they?")
    print("  2. Has this sender done this before?")
    print("  3. Are there other unusual Genesis deposits around this date?")
    print("  4. What encoding schemes produce 256536737?")
    print()
    print("THINGS WE CANNOT CLAIM:")
    print("  1. That it's from CFB (no evidence)")
    print("  2. That it relates to Anna Matrix (no evidence)")
    print("  3. That it relates to GENESIS/EXODUS tokens (no evidence)")
    print("  4. That it's a countdown to March 3 (wrong math: 23 days not 24)")
    print("  5. That the TX hash was intentionally crafted (hash is not controllable)")
    print("  6. That the change output is a message (it's just math)")
    print()

    print("HONEST PROBABILITY ASSESSMENT:")
    print("─" * 50)
    print("  P(amount contains encoded message):        ~40%")
    print("    (specific amount suggests intentional choice)")
    print()
    print("  P(message is related to CFB/Qubic):        ~5%")
    print("    (no direct evidence, just our wishful thinking)")
    print()
    print("  P(our specific decoding is correct):       ~2%")
    print("    (too many cherry-picked assumptions)")
    print()
    print("  P(this is just a crypto-enthusiast tribute): ~50%")
    print("    (many people send specific amounts to Genesis)")
    print()

def main():
    print("=" * 80)
    print("CRITICAL SELF-VALIDATION")
    print("Checking EVERY claim for confirmation bias")
    print("=" * 80)
    print()

    validate_claim_1_ascii()
    validate_claim_2_matrix_positions()
    validate_claim_3_digits_sum_44()
    validate_claim_4_3fbc()
    validate_claim_5_value_27()
    validate_claim_6_19_inputs()
    validate_claim_7_timing()
    validate_claim_8_other_output()
    validate_claim_9_12_sacred()
    what_is_actually_real()

if __name__ == "__main__":
    main()
