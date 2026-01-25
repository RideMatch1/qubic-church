#!/usr/bin/env python3
"""
ACTUAL DECODE ATTEMPT - Stop playing with statistics, find the message
"""

SEQ = [45, 92, 3, 77, 14, 58, 29, 81, 6, 33, 70, 48, 95, 22, 61, 9, 84, 37, 50, 16, 73, 28, 85, 41, 96, 7, 62, 19, 74, 30, 87, 43, 98, 5, 60, 15, 72, 27, 82, 39]

print("="*70)
print("ACTUAL DECODE ATTEMPTS")
print("="*70)

# Attempt 1: Direct ASCII (numbers as-is)
print("\n[1] DIRECT ASCII (printable only):")
ascii_direct = ''.join(chr(n) if 32 <= n <= 126 else '.' for n in SEQ)
print(f"    {ascii_direct}")

# Attempt 2: ASCII + 64 (A=65)
print("\n[2] ASCII + offset 64:")
ascii_64 = ''.join(chr(n+64) if 32 <= n+64 <= 126 else '.' for n in SEQ)
print(f"    {ascii_64}")

# Attempt 3: A=1, B=2... (mod 26)
print("\n[3] As alphabet positions (mod 26, A=0):")
alpha = ''.join(chr((n % 26) + ord('A')) for n in SEQ)
print(f"    {alpha}")

# Attempt 4: Pairs as coordinates, look up in Anna Matrix
print("\n[4] As 20 coordinate pairs:")
pairs = [(SEQ[i], SEQ[i+1]) for i in range(0, len(SEQ), 2)]
for i, (x, y) in enumerate(pairs):
    print(f"    Pair {i+1:2d}: ({x:2d}, {y:2d}) sum={x+y:3d}")

# Attempt 5: Differences encode something?
print("\n[5] Consecutive differences:")
diffs = [SEQ[i+1] - SEQ[i] for i in range(len(SEQ)-1)]
print(f"    {diffs}")
# As ASCII?
diff_ascii = ''.join(chr(abs(d)) if 32 <= abs(d) <= 126 else '.' for d in diffs)
print(f"    Diff as ASCII: {diff_ascii}")

# Attempt 6: XOR with a key?
print("\n[6] XOR with constant keys:")
for key in [27, 37, 121, 137]:
    xored = [n ^ key for n in SEQ]
    ascii_xor = ''.join(chr(x) if 32 <= x <= 126 else '.' for x in xored)
    print(f"    XOR with {key:3d}: {ascii_xor}")

# Attempt 7: Binary concatenation
print("\n[7] All numbers as 7-bit binary concatenated:")
bits = ''.join(format(n, '07b') for n in SEQ)
print(f"    {len(bits)} bits total")
# Split into 8-bit bytes
bytes_list = [bits[i:i+8] for i in range(0, len(bits)-7, 8)]
ascii_from_bits = ''
for b in bytes_list:
    val = int(b, 2)
    if 32 <= val <= 126:
        ascii_from_bits += chr(val)
    else:
        ascii_from_bits += '.'
print(f"    As ASCII: {ascii_from_bits}")

# Attempt 8: Reverse the sequence
print("\n[8] Reversed sequence ASCII:")
rev = SEQ[::-1]
ascii_rev = ''.join(chr(n) if 32 <= n <= 126 else '.' for n in rev)
print(f"    {ascii_rev}")

# Attempt 9: Every other number
print("\n[9] Odd positions vs Even positions:")
odd_pos = [SEQ[i] for i in range(0, len(SEQ), 2)]
even_pos = [SEQ[i] for i in range(1, len(SEQ), 2)]
print(f"    Odd:  {odd_pos}")
print(f"    Even: {even_pos}")
odd_ascii = ''.join(chr(n) if 32 <= n <= 126 else '.' for n in odd_pos)
even_ascii = ''.join(chr(n) if 32 <= n <= 126 else '.' for n in even_pos)
print(f"    Odd ASCII:  {odd_ascii}")
print(f"    Even ASCII: {even_ascii}")

# Attempt 10: Sort and see pattern
print("\n[10] Sorted sequence:")
sorted_seq = sorted(SEQ)
print(f"    {sorted_seq}")
print(f"    Gaps: {[sorted_seq[i+1]-sorted_seq[i] for i in range(len(sorted_seq)-1)]}")

# Attempt 11: Position encoding (where does each number 1-99 appear?)
print("\n[11] Position of number 27 (CFB signature):")
if 27 in SEQ:
    pos = SEQ.index(27)
    print(f"    27 is at index {pos} (position {pos+1})")

# Attempt 12: Hex interpretation
print("\n[12] As hex bytes (pairs):")
hex_pairs = []
for i in range(0, len(SEQ)-1, 2):
    hex_val = SEQ[i] * 256 + SEQ[i+1]
    hex_pairs.append(hex_val)
print(f"    {[hex(h) for h in hex_pairs[:10]]}...")

# Attempt 13: Base conversion
print("\n[13] Pairs as base-100 number:")
base100 = sum(SEQ[i] * (100 ** (len(SEQ)-1-i)) for i in range(len(SEQ)))
print(f"    Huge number, last 20 digits: ...{str(base100)[-20:]}")

# Attempt 14: Look for "QUBIC" or "NXT" or "CFB" encoded
print("\n[14] Search for encoded words:")
# QUBIC = 81, 85, 66, 73, 67
# NXT = 78, 88, 84
# CFB = 67, 70, 66
targets = {
    'Q': 81, 'U': 85, 'B': 66, 'I': 73, 'C': 67,
    'N': 78, 'X': 88, 'T': 84,
    'F': 70
}
for letter, code in targets.items():
    if code in SEQ:
        idx = SEQ.index(code)
        print(f"    '{letter}' ({code}) found at position {idx+1}")

# Attempt 15: Cumulative sum pattern
print("\n[15] Cumulative sum (mod 256):")
cumsum = []
total = 0
for n in SEQ:
    total = (total + n) % 256
    cumsum.append(total)
print(f"    {cumsum}")
cumsum_ascii = ''.join(chr(c) if 32 <= c <= 126 else '.' for c in cumsum)
print(f"    As ASCII: {cumsum_ascii}")

# Attempt 16: Prime indices only
print("\n[16] Numbers at prime positions (2,3,5,7,11,13,17,19,23,29,31,37):")
primes = [2,3,5,7,11,13,17,19,23,29,31,37]
prime_vals = [SEQ[p-1] for p in primes if p <= len(SEQ)]
print(f"    Positions {primes[:len(prime_vals)]}")
print(f"    Values: {prime_vals}")
print(f"    Sum: {sum(prime_vals)}")

# Attempt 17: Fibonacci positions
print("\n[17] Numbers at Fibonacci positions (1,2,3,5,8,13,21,34):")
fibs = [1,2,3,5,8,13,21,34]
fib_vals = [SEQ[f-1] for f in fibs if f <= len(SEQ)]
print(f"    Positions {fibs[:len(fib_vals)]}")
print(f"    Values: {fib_vals}")
print(f"    Sum: {sum(fib_vals)}")

# Attempt 18: The MIDDLE 34 numbers - what are they?
print("\n[18] The MIDDLE content (positions 4-37):")
middle = SEQ[3:37]
print(f"    {middle}")
print(f"    Length: {len(middle)}")
print(f"    As ASCII: {''.join(chr(n) if 32 <= n <= 126 else '.' for n in middle)}")

# Attempt 19: What if pairs are (row, col) in a 10x10 grid of letters?
print("\n[19] If pairs index into alphabet grid (10x10):")
# A-Z = 0-25, then symbols or wrap
for i, (x, y) in enumerate(pairs[:5]):
    letter_idx = (x % 10) + (y % 10) * 10
    print(f"    ({x},{y}) -> index {letter_idx}")

# Attempt 20: Decode using the 137/121 as keys
print("\n[20] XOR sequence with running key 137,121,137,121...:")
key_pattern = [137, 121] * 20
xored_pattern = [SEQ[i] ^ key_pattern[i] for i in range(len(SEQ))]
print(f"    {xored_pattern}")

print("\n" + "="*70)
print("WHAT STANDS OUT?")
print("="*70)
print("""
Looking at the direct ASCII (printable chars):
- 45 = '-'
- 92 = '\\'
- 77 = 'M'
- 58 = ':'
- 81 = 'Q'
- 33 = '!'
- 70 = 'F'
- 48 = '0'
- 95 = '_'
- 61 = '='
- 84 = 'T'
- 37 = '%'
- 50 = '2'
- 73 = 'I'
- 85 = 'U'
- 41 = ')'
- 96 = '`'
- 62 = '>'
- 74 = 'J'
- 87 = 'W'
- 43 = '+'
- 98 = 'b'
- 60 = '<'
- 72 = 'H'
- 82 = 'R'
- 39 = "'"

Letters found: M, Q, F, T, I, U, J, W, H, R
""")
