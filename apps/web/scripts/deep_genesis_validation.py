
import hashlib
import base58
import string

# --- CONSTANTS ---
CFB_NUMBERS = [
    45, 92, 3, 77, 14, 58, 29, 81, 6, 33, 70, 48, 95, 22, 61, 9,
    84, 37, 50, 16, 73, 28, 85, 41, 96, 7, 62, 19, 74, 30, 87, 43,
    98, 5, 60, 15, 72, 27, 82, 39
]

# Known addresses
ADDR_1CFB = "1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg"
ADDR_1CFI = "1CFiVYy5wuys6zAbvGGYpE2xh1NopsoHbi"
ADDR_POCC = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"

# --- HELPERS ---
def get_hash160_hex(addr):
    try:
        decoded = base58.b58decode(addr)
        return decoded[1:-4].hex()
    except:
        return None

def letter_to_val(char):
    # A=0, B=1, ...
    if 'A' <= char <= 'Z':
        return ord(char) - ord('A')
    return 0

# --- ANALYSIS ---

print("=== 1. 1CFB / 1CFi vs CFB-40 Numbers ===")
h160_cfb = get_hash160_hex(ADDR_1CFB)
h160_cfi = get_hash160_hex(ADDR_1CFI)

print(f"1CFB Hash160: {h160_cfb}")
print(f"1CFi Hash160: {h160_cfi}")

# Convert hash hex to bytes (integers)
bytes_cfb = list(bytes.fromhex(h160_cfb))
bytes_cfi = list(bytes.fromhex(h160_cfi))

print(f"1CFB Bytes: {bytes_cfb}")
print(f"1CFi Bytes: {bytes_cfi}")
print(f"CFB-40 Num: {CFB_NUMBERS}")

# Intersections
intersection_cfb = set(bytes_cfb) & set(CFB_NUMBERS)
intersection_cfi = set(bytes_cfi) & set(CFB_NUMBERS)

print(f"\nValues in 1CFB matching CFB-40: {intersection_cfb} (Count: {len(intersection_cfb)})")
print(f"Values in 1CFi matching CFB-40: {intersection_cfi} (Count: {len(intersection_cfi)})")

# Explicit matches
# 45 is in CFB-40 (First number!). 45 is 0x2D. Last byte of 1CFB is 0x2D.
print(f"\nMatch Check:")
print(f"45 (Start of CFB-40) in 1CFB? {'Yes' if 45 in bytes_cfb else 'No'}")
print(f"39 (End of CFB-40) in 1CFB? {'Yes' if 39 in bytes_cfb else 'No'}")

print("\n=== 2. POCC Address Analysis ===")
# POCC is 60 chars. Qubic ID standard.
pocc_vals = [letter_to_val(c) for c in ADDR_POCC]
print(f"POCC Values (0-25): {pocc_vals}")
print(f"Sum of POCC vals: {sum(pocc_vals)}")

# Check groupings
# First 4: POCC = 15, 14, 2, 2. Sum=33.
# 33 is in CFB-40 (6, 33).
print(f"First 4 sum: {sum(pocc_vals[:4])}")

# Convert POCC to generic seed/bytes if possible (26 chars alphabet)
# Basic check for 121, 137, 27 patterns in the sequence
print("Checking POCC slices for sums:")
found_sigs = []
for i in range(len(pocc_vals)-1):
    s = pocc_vals[i] + pocc_vals[i+1]
    if s == 27: found_sigs.append(f"Sum 27 at {i}: {ADDR_POCC[i:i+2]}")
    if s == 19: found_sigs.append(f"Sum 19 at {i}: {ADDR_POCC[i:i+2]}")

print(found_sigs)

print("\n=== 3. Matrix Mapping of POCC ===")
# Try interpreting pairs of POCC values as Matrix coordinates
# Values are 0-25. Matrix is 128x128.
# Maybe they map to the top-left 26x26 quadrant?
pocc_pairs = [(pocc_vals[i], pocc_vals[i+1]) for i in range(0, len(pocc_vals), 2)]
print(f"POCC Pairs: {pocc_pairs}")

# We'll need the matrix lookup from previous scripts to check these stats 
# (simulated here via shell later)

