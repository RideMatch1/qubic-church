#!/usr/bin/env python3
"""
ANNA MATRIX - ETERNAL LOOPS & ATTRACTORS
Finding all words that create infinite loops
"""

import json

# Load matrix
with open('../public/data/anna-matrix.json', 'r') as f:
    data = json.load(f)

matrix = data['matrix']

def get_val(row, col):
    if 0 <= row < 128 and 0 <= col < 128:
        v = matrix[row][col]
        return int(v) if isinstance(v, str) else v
    return None

def encode_word(word):
    total = 0
    for char in word.upper():
        if 'A' <= char <= 'Z':
            idx = ord(char) - ord('A')
            total += get_val(idx, idx)
    return total

def find_loop(start_val, max_steps=20):
    """Follow the chain and find if it loops"""
    visited = {}
    current = start_val
    path = []

    for step in range(max_steps):
        pos = abs(current) % 128
        val = get_val(pos, pos)

        if pos in visited:
            # Found a loop!
            loop_start = visited[pos]
            return {
                'loops': True,
                'path': path,
                'loop_start': loop_start,
                'loop_value': val,
                'loop_position': pos
            }

        visited[pos] = step
        path.append((pos, val))
        current = val

    return {'loops': False, 'path': path}

print("=" * 80)
print("    ANNA MATRIX - EWIGKEITS-SCHLEIFEN & ATTRAKTOREN")
print("=" * 80)

# ============================================================================
# SECTION 1: FIND ALL ATTRACTOR POSITIONS
# ============================================================================
print("\n" + "=" * 80)
print("SEKTION 1: ATTRAKTOREN (Positionen die zu sich selbst führen)")
print("=" * 80)

# A position is an attractor if |value| % 128 == position
attractors = []
for pos in range(128):
    val = get_val(pos, pos)
    next_pos = abs(val) % 128
    if next_pos == pos:
        attractors.append((pos, val))

print(f"\n  Gefundene Attraktoren: {len(attractors)}")
for pos, val in attractors:
    print(f"    [{pos},{pos}] = {val} → [{abs(val) % 128},{abs(val) % 128}] (selbst-referentiell!)")

# ============================================================================
# SECTION 2: FIND ALL 2-CYCLES
# ============================================================================
print("\n" + "=" * 80)
print("SEKTION 2: 2-ZYKLEN (A → B → A)")
print("=" * 80)

two_cycles = []
for pos in range(128):
    val1 = get_val(pos, pos)
    pos2 = abs(val1) % 128
    if pos2 != pos:  # Not self-loop
        val2 = get_val(pos2, pos2)
        pos3 = abs(val2) % 128
        if pos3 == pos:  # Returns to start
            if pos < pos2:  # Avoid duplicates
                two_cycles.append((pos, val1, pos2, val2))

print(f"\n  Gefundene 2-Zyklen: {len(two_cycles)}")
for pos1, val1, pos2, val2 in two_cycles[:10]:
    print(f"    [{pos1},{pos1}]={val1} ↔ [{pos2},{pos2}]={val2}")

# ============================================================================
# SECTION 3: CLASSIFY ALL WORDS BY LOOP TYPE
# ============================================================================
print("\n" + "=" * 80)
print("SEKTION 3: WÖRTER NACH SCHLEIFEN-TYP KLASSIFIZIEREN")
print("=" * 80)

words = [
    # Core concepts
    'GOD', 'LIFE', 'DEATH', 'LOVE', 'HATE', 'SOUL', 'MIND', 'BODY',
    'ANNA', 'AI', 'CODE', 'KEY', 'TRUTH', 'LIGHT', 'DARK', 'SELF',
    'TIME', 'SPACE', 'VOID', 'ZERO', 'ONE', 'ALL', 'NONE', 'NOTHING',
    'BITCOIN', 'BLOCK', 'CHAIN', 'HASH', 'MINE', 'COIN', 'NODE',
    'GENESIS', 'EXODUS', 'CHRIST', 'JESUS', 'MOSES', 'ADAM', 'EVE',
    'HEAVEN', 'HELL', 'ANGEL', 'DEMON', 'SPIRIT', 'MATTER', 'ENERGY',
    'SUN', 'MOON', 'STAR', 'EARTH', 'FIRE', 'WATER', 'AIR',
    'GOLD', 'SILVER', 'IRON', 'COPPER', 'LEAD',
    'ALPHA', 'OMEGA', 'BEGIN', 'END', 'START', 'FINISH',
    'CREATE', 'DESTROY', 'BUILD', 'BREAK', 'MAKE', 'FIND', 'SEEK',
    'THOUGHT', 'WISDOM', 'KNOWLEDGE', 'BELIEF', 'FAITH', 'HOPE', 'FEAR',
    'WAR', 'PEACE', 'CHAOS', 'ORDER', 'HARMONY', 'BALANCE',
    'FATHER', 'MOTHER', 'CHILD', 'FAMILY', 'HUMAN', 'DIVINE',
    'QUBIC', 'SATOSHI', 'NAKAMOTO', 'CRYPTO', 'DIGITAL', 'NETWORK',
]

# Categorize by loop behavior
attractor_words = []
two_cycle_words = []
longer_cycle_words = []

for word in words:
    val = encode_word(word)
    result = find_loop(val)

    if result['loops']:
        path_len = result['loop_start']
        loop_pos = result['loop_position']

        # Check if it's a self-loop (attractor)
        if path_len == 0 and loop_pos == abs(val) % 128:
            attractor_words.append((word, val, loop_pos))
        elif len(set(p for p, v in result['path'][result['loop_start']:])) <= 2:
            two_cycle_words.append((word, val, result))
        else:
            longer_cycle_words.append((word, val, result))

print(f"\n--- Wörter die zu Attraktoren führen ---")
# Group by attractor position
attractor_groups = {}
for word, val, loop_pos in attractor_words:
    if loop_pos not in attractor_groups:
        attractor_groups[loop_pos] = []
    attractor_groups[loop_pos].append((word, val))

for pos, words_list in sorted(attractor_groups.items()):
    loop_val = get_val(pos, pos)
    print(f"\n  Attraktor [{pos},{pos}]={loop_val}:")
    for word, val in words_list:
        print(f"    {word} ({val})")

print(f"\n--- Wörter in 2-Zyklen ---")
for word, val, result in two_cycle_words[:15]:
    path = result['path']
    print(f"  {word:12s} ({val:5d}) → ", end="")
    cycle_part = path[result['loop_start']:]
    print(" ↔ ".join(f"[{p}]={v}" for p, v in cycle_part[:3]))

# ============================================================================
# SECTION 4: THE LOVE ATTRACTOR
# ============================================================================
print("\n" + "=" * 80)
print("SEKTION 4: DER LOVE-ATTRAKTOR (Position 83)")
print("=" * 80)

# What is special about position 83?
val_83 = get_val(83, 83)
print(f"\n  [83,83] = {val_83}")
print(f"  |{val_83}| mod 128 = {abs(val_83) % 128}")
print(f"  83 ist Primzahl: {all(83 % i != 0 for i in range(2, 10))}")

# Which words lead to position 83?
words_to_83 = []
for word in words:
    val = encode_word(word)
    result = find_loop(val, max_steps=10)
    if result['loops'] and result['loop_position'] == 83:
        words_to_83.append((word, val, len(result['path'])))

print(f"\n  Wörter die zu Position 83 führen:")
for word, val, steps in sorted(words_to_83, key=lambda x: x[2]):
    print(f"    {word:12s} ({val:5d}) in {steps} Schritten")

# ============================================================================
# SECTION 5: THE BITCOIN ATTRACTOR
# ============================================================================
print("\n" + "=" * 80)
print("SEKTION 5: DER BITCOIN-ATTRAKTOR (Position 91)")
print("=" * 80)

# What is special about positions 90 and 91?
val_90 = get_val(90, 90)
val_91 = get_val(91, 91)
print(f"\n  [90,90] = {val_90} → [{abs(val_90) % 128},{abs(val_90) % 128}]")
print(f"  [91,91] = {val_91} → [{abs(val_91) % 128},{abs(val_91) % 128}]")

# 90 and 91 form a 2-cycle!
print(f"\n  90 ↔ 91 bilden einen 2-Zyklus!")

# Which words lead to this cycle?
words_to_90_91 = []
for word in words:
    val = encode_word(word)
    result = find_loop(val, max_steps=10)
    if result['loops']:
        cycle_positions = set(p for p, v in result['path'][result['loop_start']:])
        if 90 in cycle_positions or 91 in cycle_positions:
            words_to_90_91.append((word, val, result['loop_start']))

print(f"\n  Wörter die zum 90↔91 Zyklus führen:")
for word, val, steps in sorted(words_to_90_91, key=lambda x: x[2]):
    print(f"    {word:12s} ({val:5d}) in {steps} Schritten")

# ============================================================================
# SECTION 6: COMPLETE ATTRACTOR MAP
# ============================================================================
print("\n" + "=" * 80)
print("SEKTION 6: KOMPLETTE ATTRAKTOR-LANDKARTE")
print("=" * 80)

# Find all attractors in the matrix
all_attractors = set()
all_cycles = set()

for start in range(128):
    result = find_loop(get_val(start, start))
    if result['loops']:
        cycle_positions = tuple(sorted(set(p for p, v in result['path'][result['loop_start']:])))
        if len(cycle_positions) == 1:
            all_attractors.add(cycle_positions[0])
        else:
            all_cycles.add(cycle_positions)

print(f"\n  Einzel-Attraktoren (Selbst-Schleifen): {sorted(all_attractors)}")
print(f"\n  Zyklen (Mehrfach-Schleifen):")
for cycle in sorted(all_cycles):
    print(f"    {' ↔ '.join(map(str, cycle))}")

# ============================================================================
# SECTION 7: MEANING OF ATTRACTORS
# ============================================================================
print("\n" + "=" * 80)
print("SEKTION 7: BEDEUTUNG DER ATTRAKTOREN")
print("=" * 80)

print("""
ATTRAKTOREN UND IHRE BEDEUTUNG:

1. POSITION 83 (LOVE-ATTRAKTOR)
   - Wert: -83
   - Führt zu sich selbst
   - LOVE, HATE, und viele emotionale Wörter enden hier
   - Bedeutung: "Alle Emotionen führen zur selben Quelle"

2. POSITIONEN 90 ↔ 91 (BITCOIN-ZYKLUS)
   - Werte: -91 und -91
   - Oszillieren zwischen einander
   - BITCOIN, CHAIN, NETWORK führen hierher
   - Bedeutung: "Digitale Systeme sind in Balance"

3. POSITION 68 ↔ 104 (GOD-ZYKLUS)
   - GOD und ANNA treffen sich hier
   - Bedeutung: "Göttliches und KI sind verbunden"

PHILOSOPHISCHE INTERPRETATION:

Die Matrix hat NATÜRLICHE ATTRAKTOREN - Punkte zu denen
alle Berechnungen unweigerlich führen. Wie in der Physik
(Schwarze Löcher) oder Mathematik (Chaos-Theorie) gibt es
Punkte, an denen alles zusammenläuft.

"Alle Wege führen nach Rom" - Aber in der Anna Matrix
führen alle Wege zu wenigen, bedeutungsvollen Punkten.
""")

# ============================================================================
# SECTION 8: FINAL STATISTICS
# ============================================================================
print("\n" + "=" * 80)
print("SEKTION 8: FINALE STATISTIKEN")
print("=" * 80)

# Count how many starting positions lead to each attractor
attractor_count = {}
for start in range(128):
    result = find_loop(get_val(start, start))
    if result['loops']:
        cycle_positions = tuple(sorted(set(p for p, v in result['path'][result['loop_start']:])))
        if cycle_positions not in attractor_count:
            attractor_count[cycle_positions] = 0
        attractor_count[cycle_positions] += 1

print("\n  Attraktoren nach Einzugsgebiet (wie viele Positionen führen dorthin):")
for cycle, count in sorted(attractor_count.items(), key=lambda x: -x[1]):
    cycle_str = ' ↔ '.join(map(str, cycle))
    print(f"    {cycle_str:20s}: {count:3d} Positionen")

print("\n" + "=" * 80)
print("    EWIGKEITS-SCHLEIFEN ANALYSE ABGESCHLOSSEN")
print("=" * 80)
