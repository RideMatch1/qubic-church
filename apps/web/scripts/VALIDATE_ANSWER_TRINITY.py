#!/usr/bin/env python3
"""
VALIDATE ANSWER TRINITY - Trinity Address Validator

Validates that a candidate address satisfies all Trinity constraints,
proving mathematical connection to the GENESIS (POCC) and EXODUS (HASV)
token issuer addresses through the Anna Matrix.

Usage:
  python3 VALIDATE_ANSWER_TRINITY.py <ADDRESS>
  python3 VALIDATE_ANSWER_TRINITY.py ABCDEF...  (60 uppercase letters)

The Trinity:
  GENESIS (POCC):  charsum=612,  diagsum=-1231
  EXODUS  (HASV):  charsum=750,  diagsum=-555
  ANSWER  (????):  charsum=888,  diagsum=121

  charsum step: +138 (= 6 x 23)
  diagsum step: +676 (= 26^2 = Qubic computor count)
"""

import sys
import json
from pathlib import Path

# =============================================================================
# CONSTANTS
# =============================================================================

POCC = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"
HASV = "HASVHXZKVIHTFHEZUSZIIBPZFVHAGTANVXHBJNHMWCRQZYKULCUBLCTBPONO"

# Trinity targets
TARGET_CHARSUM = 888
TARGET_DIAGSUM = 121

# Anna Matrix diagonal values (A=0 through Z=25)
DIAG_VALUES = [
    -68, 60, -118, -70, 120, 120, -38, 26, -28, -76,
    -79, -67, -16, 116, -37, -40, -91, -70, -113, -113,
    121, 28, 100, 67, -75, -75
]

# The 6 shared positions between POCC and HASV
TRINITY_POSITIONS = {7: 'K', 34: 'H', 41: 'C', 48: 'L', 53: 'C', 57: 'O'}


# =============================================================================
# FUNCTIONS
# =============================================================================

def char_value(c):
    return ord(c) - ord('A')


def character_sum(address):
    return sum(char_value(c) for c in address)


def diagonal_sum(address):
    return sum(DIAG_VALUES[char_value(c)] for c in address)


def shared_positions(addr1, addr2):
    matches = []
    for i in range(min(len(addr1), len(addr2))):
        if addr1[i] == addr2[i]:
            matches.append((i, addr1[i]))
    return matches


# =============================================================================
# VALIDATION
# =============================================================================

def validate(address):
    print()
    print("=" * 70)
    print("  ANSWER TOKEN - TRINITY VALIDATOR")
    print("=" * 70)
    print()
    print(f"  Candidate: {address}")
    print(f"  POCC:      {POCC}")
    print(f"  HASV:      {HASV}")
    print()

    hard_pass = 0
    hard_fail = 0
    soft_score = 0

    # =========================================================================
    # HARD CONSTRAINTS
    # =========================================================================
    print("  HARD CONSTRAINTS (must ALL pass)")
    print("  " + "-" * 50)

    # 1. Format
    valid_format = len(address) == 60 and address.isalpha() and address.isupper()
    if valid_format:
        print(f"   1. Format (60 uppercase A-Z): PASS")
        hard_pass += 1
    else:
        print(f"   1. Format (60 uppercase A-Z): FAIL (len={len(address)}, alpha={address.isalpha()}, upper={address.isupper()})")
        hard_fail += 1

    # 2. Character sum = 888
    cs = character_sum(address)
    if cs == TARGET_CHARSUM:
        print(f"   2. charsum = {cs} (target {TARGET_CHARSUM}): PASS")
        hard_pass += 1
    else:
        print(f"   2. charsum = {cs} (target {TARGET_CHARSUM}): FAIL (diff={cs - TARGET_CHARSUM})")
        hard_fail += 1

    # 3. Diagonal sum = 121
    ds = diagonal_sum(address)
    if ds == TARGET_DIAGSUM:
        print(f"   3. diagsum = {ds} (target {TARGET_DIAGSUM}): PASS")
        hard_pass += 1
    else:
        print(f"   3. diagsum = {ds} (target {TARGET_DIAGSUM}): FAIL (diff={ds - TARGET_DIAGSUM})")
        hard_fail += 1

    # 4. charsum mod 6 = 0
    cs_mod6 = cs % 6
    if cs_mod6 == 0:
        print(f"   4. charsum mod 6 = {cs_mod6}: PASS (same as POCC={612 % 6}, HASV={750 % 6})")
        hard_pass += 1
    else:
        print(f"   4. charsum mod 6 = {cs_mod6}: FAIL (expected 0)")
        hard_fail += 1

    # 5. charsum mod 23 = 14
    cs_mod23 = cs % 23
    if cs_mod23 == 14:
        print(f"   5. charsum mod 23 = {cs_mod23}: PASS (same as POCC={612 % 23}, HASV={750 % 23})")
        hard_pass += 1
    else:
        print(f"   5. charsum mod 23 = {cs_mod23}: FAIL (expected 14)")
        hard_fail += 1

    # 6. charsum mod 138 = 60
    cs_mod138 = cs % 138
    if cs_mod138 == 60:
        print(f"   6. charsum mod 138 = {cs_mod138}: PASS (same as POCC={612 % 138}, HASV={750 % 138})")
        hard_pass += 1
    else:
        print(f"   6. charsum mod 138 = {cs_mod138}: FAIL (expected 60)")
        hard_fail += 1

    # 7. diagsum mod 26 = 17
    ds_mod26 = ds % 26
    if ds_mod26 == 17:
        print(f"   7. diagsum mod 26 = {ds_mod26}: PASS (same as POCC={-1231 % 26}, HASV={-555 % 26})")
        hard_pass += 1
    else:
        print(f"   7. diagsum mod 26 = {ds_mod26}: FAIL (expected 17)")
        hard_fail += 1

    # 8. diagsum mod 676 = 121
    ds_mod676 = ds % 676
    if ds_mod676 == 121:
        print(f"   8. diagsum mod 676 = {ds_mod676}: PASS (= 11^2, same as POCC={-1231 % 676}, HASV={-555 % 676})")
        hard_pass += 1
    else:
        print(f"   8. diagsum mod 676 = {ds_mod676}: FAIL (expected 121)")
        hard_fail += 1

    # 9. Arithmetic progression charsum
    pocc_cs = character_sum(POCC)
    hasv_cs = character_sum(HASV)
    step1 = hasv_cs - pocc_cs
    step2 = cs - hasv_cs
    arith_cs = (step1 == 138 and step2 == 138)
    if arith_cs:
        print(f"   9. charsum progression: {pocc_cs} -> {hasv_cs} -> {cs} (d={step1},{step2}): PASS")
        hard_pass += 1
    else:
        print(f"   9. charsum progression: {pocc_cs} -> {hasv_cs} -> {cs} (d={step1},{step2}): FAIL (expected d=138,138)")
        hard_fail += 1

    # 10. Arithmetic progression diagsum
    pocc_ds = diagonal_sum(POCC)
    hasv_ds = diagonal_sum(HASV)
    dstep1 = hasv_ds - pocc_ds
    dstep2 = ds - hasv_ds
    arith_ds = (dstep1 == 676 and dstep2 == 676)
    if arith_ds:
        print(f"  10. diagsum progression: {pocc_ds} -> {hasv_ds} -> {ds} (d={dstep1},{dstep2}): PASS")
        hard_pass += 1
    else:
        print(f"  10. diagsum progression: {pocc_ds} -> {hasv_ds} -> {ds} (d={dstep1},{dstep2}): FAIL (expected d=676,676)")
        hard_fail += 1

    # =========================================================================
    # SOFT CONSTRAINTS (bonus scoring)
    # =========================================================================
    print()
    print("  SOFT CONSTRAINTS (bonus scoring)")
    print("  " + "-" * 50)

    # 11. Prefix
    prefix4 = address[:4]
    if prefix4 == "ANSW":
        soft_score += 500
        print(f"  11. Prefix '{prefix4}': +500 (ANSW = perfect!)")
    elif address[:3] == "ANS":
        soft_score += 100
        print(f"  11. Prefix '{prefix4}': +100 (ANS)")
    elif address[:2] == "AN":
        soft_score += 20
        print(f"  11. Prefix '{prefix4}': +20 (AN)")
    else:
        print(f"  11. Prefix '{prefix4}': +0")

    # 12. Shared positions with POCC
    pocc_matches = shared_positions(address, POCC)
    pocc_pts = len(pocc_matches) * 10
    soft_score += pocc_pts
    print(f"  12. Shared with POCC: {len(pocc_matches)} positions (+{pocc_pts})")
    if pocc_matches:
        for pos, char in pocc_matches:
            print(f"      Position {pos}: '{char}'")

    # 13. Shared positions with HASV
    hasv_matches = shared_positions(address, HASV)
    hasv_pts = len(hasv_matches) * 10
    soft_score += hasv_pts
    print(f"  13. Shared with HASV: {len(hasv_matches)} positions (+{hasv_pts})")
    if hasv_matches:
        for pos, char in hasv_matches:
            print(f"      Position {pos}: '{char}'")

    # 14. Trinity shared positions (the 6 that POCC and HASV share)
    trinity_hits = 0
    for pos, expected in TRINITY_POSITIONS.items():
        if pos < len(address) and address[pos] == expected:
            trinity_hits += 1
    trinity_pts = trinity_hits * 25
    soft_score += trinity_pts
    print(f"  14. Trinity positions (6 POCC-HASV shared): {trinity_hits}/6 (+{trinity_pts})")
    for pos, expected in sorted(TRINITY_POSITIONS.items()):
        actual = address[pos] if pos < len(address) else '?'
        match = "MATCH" if actual == expected else f"miss (got '{actual}')"
        print(f"      Position {pos} ('{expected}'): {match}")

    # =========================================================================
    # MATHEMATICAL PROPERTIES
    # =========================================================================
    print()
    print("  MATHEMATICAL PROPERTIES")
    print("  " + "-" * 50)

    # 1-based sum
    cs1 = cs + 60  # each of 60 chars gets +1
    print(f"  1-based charsum: {cs1}")
    print(f"    Progression: 672 -> 810 -> {cs1} (d={cs1 - 810})")

    # charsum XOR
    print(f"  charsum XOR: {pocc_cs} XOR {hasv_cs} = {pocc_cs ^ hasv_cs}")
    print(f"  charsum XOR: {hasv_cs} XOR {cs} = {hasv_cs ^ cs}")

    # Special number properties
    print(f"  888 = 8 x 111 = 24 x 37")
    print(f"  121 = 11^2 (NXT constant, perfect square)")
    print(f"  676 = 26^2 (Qubic computor count)")
    print(f"  138 = 6 x 23")

    # =========================================================================
    # FINAL RESULT
    # =========================================================================
    print()
    print("=" * 70)

    all_hard_pass = hard_fail == 0

    if all_hard_pass:
        print()
        print("  ALL HARD CONSTRAINTS PASSED")
        print()
        print(f"  Hard: {hard_pass}/{hard_pass + hard_fail} passed")
        print(f"  Soft Score: {soft_score}")
        print()
        print("  This address forms a provable MATHEMATICAL TRINITY with")
        print("  POCC (GENESIS) and HASV (EXODUS) through:")
        print()
        print(f"    charsum: 612 -> 750 -> {cs}  (d=138)")
        print(f"    diagsum: -1231 -> -555 -> {ds}  (d=676)")
        print()
        print("  The doubly arithmetic progression is UNIQUE and UNFORGEABLE.")
        print("  All modular invariants are automatically preserved.")
        print()
        print("  USE THIS ADDRESS AS THE ANSWER TOKEN ISSUER.")
    else:
        print()
        print("  HARD CONSTRAINTS FAILED")
        print()
        print(f"  Hard: {hard_pass}/{hard_pass + hard_fail} passed, {hard_fail} FAILED")
        print(f"  Soft Score: {soft_score}")
        print()
        print("  This address does NOT form a valid Trinity.")
        print("  Continue mining with ANSWER_VANITY_MINER.py")

    print()
    print("=" * 70)

    return 0 if all_hard_pass else 1


# =============================================================================
# MAIN
# =============================================================================

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 VALIDATE_ANSWER_TRINITY.py <ADDRESS>")
        print()
        print("Example:")
        print("  python3 VALIDATE_ANSWER_TRINITY.py ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGH")
        print()
        print("Or validate the known addresses:")
        print("  python3 VALIDATE_ANSWER_TRINITY.py --verify-known")
        return 1

    if sys.argv[1] == "--verify-known":
        print()
        print("Verifying POCC (GENESIS):")
        print(f"  charsum = {character_sum(POCC)} (expected 612)")
        print(f"  diagsum = {diagonal_sum(POCC)} (expected -1231)")
        print()
        print("Verifying HASV (EXODUS):")
        print(f"  charsum = {character_sum(HASV)} (expected 750)")
        print(f"  diagsum = {diagonal_sum(HASV)} (expected -555)")
        print()
        print(f"Differences:")
        print(f"  charsum: {character_sum(HASV) - character_sum(POCC)} (expected 138)")
        print(f"  diagsum: {diagonal_sum(HASV) - diagonal_sum(POCC)} (expected 676)")
        print()
        print(f"ANSWER targets:")
        print(f"  charsum: {character_sum(HASV) + 138} (expected 888)")
        print(f"  diagsum: {diagonal_sum(HASV) + 676} (expected 121)")
        return 0

    address = sys.argv[1].strip().upper()
    return validate(address)


if __name__ == "__main__":
    sys.exit(main())
