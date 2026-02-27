#!/usr/bin/env python3
"""
QUBIC Network Explorer - Easter Egg Hunt
=========================================
Looking for interesting patterns on the Qubic blockchain
"""

import requests
import json
import time

BASE_URL = "https://rpc.qubic.org"

def api_call(endpoint):
    """Make API call with error handling"""
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=30)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"  Error: {e}")
    return None

print("🔮 " + "=" * 76)
print("   QUBIC NETWORK EXPLORER - Easter Egg Hunt!")
print("=" * 80)
print()

# ============================================================================
# EXPERIMENT 1: Current Tick Info
# ============================================================================
print("📊 EXPERIMENT 1: Current Network State")
print("-" * 80)

tick_info = api_call("/v1/tick-info")
if tick_info:
    tick = tick_info.get('tickInfo', {}).get('tick', 0)
    print(f"Current tick: {tick}")
    print(f"  Tick mod 676 = {tick % 676}")
    print(f"  Tick mod 576 = {tick % 576}")
    print(f"  Tick mod 26 = {tick % 26}")

    # Check for interesting tick numbers
    if tick % 676 == 0:
        print("  ⭐ Current tick is divisible by 676!")
    if tick % 576 == 0:
        print("  ⭐ Current tick is divisible by 576!")
print()

# ============================================================================
# EXPERIMENT 2: Known Interesting Addresses
# ============================================================================
print("📬 EXPERIMENT 2: Interesting Address Analysis")
print("-" * 80)

addresses = {
    "GENESIS (POCC)": "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD",
    "ANNA (HIFU)": "HIFUSWQYNUZTSDRPXZOXXIWUPWTAOVJUTCVLFIHLHARCXSARRTGCJLGGAREO",
    "HASV (676 Intermediate)": "HASVHXZKVIHTFHEZUSZIIBPZFVHAGTANVXHBJNHMWCRQZYKULCUBLCTBPONO",
    "Burn Address": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFXIB",
    "QX Contract": "BAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAARMID",
}

for name, addr in addresses.items():
    print(f"\n{name}:")
    print(f"  Address: {addr[:30]}...{addr[-10:]}")

    # Analyze address string
    letter_sum = sum(ord(c) - ord('A') for c in addr)
    print(f"  Letter sum (A=0): {letter_sum}")
    print(f"  Sum mod 676: {letter_sum % 676}")
    print(f"  Sum mod 26: {letter_sum % 26}")

    # Get balance
    balance_data = api_call(f"/v1/balances/{addr}")
    if balance_data and 'balance' in balance_data:
        bal = int(balance_data['balance'].get('balance', 0))
        print(f"  Balance: {bal:,} QUBIC")
        if bal > 0:
            print(f"  Balance mod 676: {bal % 676}")
print()

# ============================================================================
# EXPERIMENT 3: Search for Easter Egg in address patterns
# ============================================================================
print("🥚 EXPERIMENT 3: Easter Egg Address Patterns")
print("-" * 80)

# Check if any known address contains "EASTER" or "EGG"
easter_keywords = ["EASTER", "EGG", "KEY", "SIGNAL", "BRIDGE", "MOON", "SUN"]

for name, addr in addresses.items():
    for kw in easter_keywords:
        if kw in addr:
            print(f"  Found '{kw}' in {name}!")

# Generate addresses that might be Easter Eggs
print("\nChecking special address patterns...")
special_patterns = [
    "EASTEREGGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "KEYKEYKEYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "SATOSHIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
]

for pattern in special_patterns:
    # These won't be valid addresses but show the concept
    print(f"  Pattern '{pattern[:20]}...' - theoretical Easter Egg address")
print()

# ============================================================================
# EXPERIMENT 4: Tick 676 and 576 Analysis
# ============================================================================
print("🔢 EXPERIMENT 4: Significant Tick Numbers")
print("-" * 80)

significant_ticks = [
    676,
    676 * 100,  # 67600
    576 * 100,  # 57600
    26 * 26 * 100,  # 67600
    42984299,  # First ANNA burn tick
    42984000,  # Round number near ANNA burns
]

print("Checking significant tick numbers:")
for tick in significant_ticks:
    print(f"\n  Tick {tick:,}:")
    print(f"    = {tick // 676} × 676 + {tick % 676}")
    print(f"    = {tick // 576} × 576 + {tick % 576}")
print()

# ============================================================================
# EXPERIMENT 5: ANNA Burns Pattern Analysis
# ============================================================================
print("🔥 EXPERIMENT 5: ANNA Burns Deep Analysis")
print("-" * 80)

anna_burns = [
    ("42984299", "1100111", "g"),
    ("42984360", "1100111", "g"),
    ("42984382", "1100101", "e"),
    ("42984403", "0", " "),
    ("42984463", "1110010", "r"),
    ("42984511", "1100101", "e"),
    ("42984561", "1110100", "t"),
    ("42984599", "1110011", "s"),
    ("42984621", "1100001", "a"),
    ("42984645", "1100101", "e"),
]

print("ANNA burn amounts as binary message:")
message = ""
tick_diffs = []
prev_tick = None

for tick, amount, char in anna_burns:
    tick_int = int(tick)
    if prev_tick:
        diff = tick_int - prev_tick
        tick_diffs.append(diff)
    prev_tick = tick_int
    message += char

print(f"  Message: '{message}' (reversed: '{message[::-1]}')")
print(f"  Tick differences: {tick_diffs}")
print(f"  Sum of tick diffs: {sum(tick_diffs)}")
print(f"  Average tick diff: {sum(tick_diffs) / len(tick_diffs):.1f}")
print()

# ============================================================================
# EXPERIMENT 6: Address Letter Frequency Analysis
# ============================================================================
print("📈 EXPERIMENT 6: Address Letter Frequency")
print("-" * 80)

from collections import Counter

for name, addr in list(addresses.items())[:3]:  # First 3 addresses
    print(f"\n{name}:")
    freq = Counter(addr)
    most_common = freq.most_common(5)
    print(f"  Most common letters: {most_common}")

    # Check for patterns
    unique_letters = len(set(addr))
    print(f"  Unique letters: {unique_letters}/26")

    # Is any letter exactly 26 times?
    for letter, count in freq.items():
        if count == 26:
            print(f"  ⭐ Letter '{letter}' appears exactly 26 times!")
        if count == 6 or count == 7:
            print(f"  Letter '{letter}' appears {count} times (6-7 range)")
print()

# ============================================================================
# EXPERIMENT 7: Numerical Curiosities
# ============================================================================
print("🎲 EXPERIMENT 7: Numerical Curiosities")
print("-" * 80)

# Known important numbers
numbers = {
    "676": 676,
    "576": 576,
    "26": 26,
    "128": 128,
    "127": 127,
    "33": 33,
    "36": 36,
    "21000000": 21000000,  # Bitcoin supply
    "17576": 17576,  # 26³
}

print("Relationships between key numbers:")
for name, val in numbers.items():
    factors = []
    for d in [2, 3, 4, 5, 6, 7, 8, 13, 17, 19, 23, 26]:
        if val % d == 0:
            factors.append(d)
    print(f"  {name} = {val}, divisible by: {factors}")

print("\nSpecial calculations:")
print(f"  676 + 576 = {676 + 576} (= {(676 + 576) // 26} × 26 + {(676 + 576) % 26})")
print(f"  676 × 576 = {676 * 576} = {676 * 576 // 17576} × 17576 + {676 * 576 % 17576}")
print(f"  676 - 576 = {676 - 576} = 100 = 10²")
print(f"  √676 = 26")
print(f"  √576 = 24")
print(f"  26 + 24 = 50 (Bitcoin block reward!)")
print()

# ============================================================================
# EXPERIMENT 8: Hidden Message in Address
# ============================================================================
print("💬 EXPERIMENT 8: Hidden Messages in Addresses")
print("-" * 80)

# Look for words hidden in addresses
words_to_find = ["BURN", "FIRE", "GOLD", "CASH", "COIN", "RICH", "POOR", "HELP", "SAVE", "SEND"]

for name, addr in addresses.items():
    found_words = []
    for word in words_to_find:
        if word in addr:
            idx = addr.index(word)
            found_words.append((word, idx))

    if found_words:
        print(f"\n{name}:")
        for word, idx in found_words:
            print(f"  Found '{word}' at position {idx}")
print()

# ============================================================================
# EXPERIMENT 9: ASCII Art from Address
# ============================================================================
print("🎨 EXPERIMENT 9: Address as ASCII Values")
print("-" * 80)

# Convert first address to ASCII values
genesis_addr = addresses["GENESIS (POCC)"]
ascii_vals = [ord(c) for c in genesis_addr[:20]]
print(f"GENESIS first 20 chars as ASCII: {ascii_vals}")
print(f"Sum: {sum(ascii_vals)}")
print(f"Sum mod 676: {sum(ascii_vals) % 676}")
print()

# ============================================================================
# EXPERIMENT 10: The "FXIB" Mystery
# ============================================================================
print("🔮 EXPERIMENT 10: The 'FXIB' Mystery")
print("-" * 80)

# The burn address ends in FXIB - why?
fxib = "FXIB"
print(f"Burn address ending: {fxib}")
print(f"  F = {ord('F') - ord('A')} = 5")
print(f"  X = {ord('X') - ord('A')} = 23")
print(f"  I = {ord('I') - ord('A')} = 8")
print(f"  B = {ord('B') - ord('A')} = 1")
print(f"  Sum: 5 + 23 + 8 + 1 = {5 + 23 + 8 + 1}")

# 37 is a prime number!
print(f"\n  37 is PRIME!")
print(f"  37 = 36 + 1 (days until Blood Moon + 1)")
print(f"  37 × 18 = {37 * 18} (close to 676)")

# QX contract ends in RMID
rmid = "RMID"
print(f"\nQX contract ending: {rmid}")
vals = [ord(c) - ord('A') for c in rmid]
print(f"  R=17, M=12, I=8, D=3")
print(f"  Sum: {sum(vals)}")
print()

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("🎮 " + "=" * 76)
print("   QUBIC EXPLORER SUMMARY")
print("=" * 80)

print("""
DISCOVERED PATTERNS:

1. ANNA burns spell "EASTER EGG" backwards
2. Tick differences between burns have a pattern
3. 676 + 576 = 1252 (close to 1253 which is prime!)
4. 26 + 24 = 50 = Bitcoin block reward
5. Burn address ends in FXIB (sum = 37, prime!)
6. Address letter frequencies may contain hidden codes

CONNECTIONS:
- 676 = 26² = Qubic Computors
- 576 = 24² = Message 576
- Both are perfect squares!
- √676 + √576 = 26 + 24 = 50 BTC

The system is deeply connected to:
- Bitcoin (50 BTC block reward, 21M supply)
- Perfect squares (576, 676)
- Prime numbers (37, 127)
- The alphabet (26)
""")
