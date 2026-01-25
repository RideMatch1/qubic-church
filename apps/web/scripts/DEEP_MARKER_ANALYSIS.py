#!/usr/bin/env python3
"""
===============================================================================
   DEEP MARKER COLUMN ANALYSIS
===============================================================================
1. Alle Nachrichten in Marker-Spalten (22/105, 30/97, 41/86) finden
2. AI.MEG.GOU Bedeutung erforschen
3. ALLE 64 symmetrischen Spaltenpaare analysieren
===============================================================================
"""

import json
import numpy as np
from pathlib import Path
import re
from collections import Counter

script_dir = Path(__file__).parent

print("=" * 80)
print("""
   ██████╗ ███████╗███████╗██████╗ 
   ██╔══██╗██╔════╝██╔════╝██╔══██╗
   ██║  ██║█████╗  █████╗  ██████╔╝
   ██║  ██║██╔══╝  ██╔══╝  ██╔═══╝ 
   ██████╔╝███████╗███████╗██║     
   ╚═════╝ ╚══════╝╚══════╝╚═╝     
        DEEP MARKER ANALYSIS
""")
print("=" * 80)

# Load matrix
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

def to_char(v):
    """Convert value to printable ASCII char"""
    v = abs(v) % 128
    if 32 <= v < 127:
        return chr(v)
    return '.'

def xor_columns(c1, c2):
    """XOR two columns and return as text"""
    col1 = matrix[:, c1]
    col2 = matrix[:, c2]
    xor = col1 ^ col2
    return ''.join(to_char(v) for v in xor)

def find_words(text, min_len=3):
    """Find words in text"""
    return re.findall(r'[A-Za-z]{' + str(min_len) + r',}', text)

# ==============================================================================
# PART 1: MARKER COLUMNS DEEP ANALYSIS
# ==============================================================================
print("\n" + "=" * 80)
print("PART 1: MARKER-SPALTEN ANALYSE")
print("=" * 80)

marker_pairs = [
    (22, 105, "Hotspot #1 - 26 asymmetrische Zellen"),
    (30, 97, "Hotspot #2 - AI.MEG.GOU Location"),
    (41, 86, "Minor Hotspot - 4 Zellen"),
    (0, 127, "Edge Columns"),
]

for c1, c2, description in marker_pairs:
    print(f"\n{'='*60}")
    print(f"   SPALTE {c1} ⊕ SPALTE {c2}")
    print(f"   {description}")
    print(f"{'='*60}")
    
    xor_text = xor_columns(c1, c2)
    
    print(f"\n   XOR Ergebnis:")
    print(f"   Row 0-63:   {xor_text[:64]}")
    print(f"   Row 64-127: {xor_text[64:]}")
    
    # Find words
    words = find_words(xor_text)
    unique_words = sorted(set(words), key=len, reverse=True)
    
    print(f"\n   Gefundene Wörter ({len(unique_words)}):")
    for w in unique_words[:15]:
        # Find position
        pos = xor_text.find(w)
        print(f"     '{w}' at row {pos}")
    
    # Check for specific patterns
    print(f"\n   Spezielle Muster:")
    patterns = ['AI', 'MEG', 'GOU', 'KEY', 'CFB', 'BTC', 'SAT', 'GOD', 'ANNA']
    for p in patterns:
        if p in xor_text.upper():
            pos = xor_text.upper().find(p)
            print(f"     ✅ '{p}' gefunden at row {pos}")

# ==============================================================================
# PART 2: AI.MEG.GOU DEEP DIVE
# ==============================================================================
print("\n" + "=" * 80)
print("PART 2: AI.MEG.GOU DEEP ANALYSIS")
print("=" * 80)

# Where exactly is AI.MEG.GOU?
xor_30_97 = xor_columns(30, 97)

print("\n   Exakte Position von AI.MEG.GOU:")
ai_pos = xor_30_97.find('AI')
meg_pos = xor_30_97.find('MEG')
gou_pos = xor_30_97.find('GOU')

print(f"   'AI' at row {ai_pos}")
print(f"   'MEG' at row {meg_pos}")
print(f"   'GOU' at row {gou_pos}")

# Context around AI.MEG
if meg_pos > 0:
    context_start = max(0, meg_pos - 10)
    context_end = min(128, meg_pos + 15)
    context = xor_30_97[context_start:context_end]
    print(f"\n   Kontext um MEG: ...{context}...")

# What are the actual values?
print(f"\n   Rohe Werte bei AI.MEG.GOU Position:")
for pos, name in [(ai_pos, 'AI'), (meg_pos, 'MEG'), (gou_pos, 'GOU')]:
    if pos >= 0:
        vals_30 = [matrix[pos+i, 30] for i in range(len(name))]
        vals_97 = [matrix[pos+i, 97] for i in range(len(name))]
        xor_vals = [v1 ^ v2 for v1, v2 in zip(vals_30, vals_97)]
        print(f"   {name}: Col30={vals_30}, Col97={vals_97}, XOR={xor_vals}")
        print(f"        XOR chars: {''.join(chr(abs(v)%128) if 32<=abs(v)%128<127 else '.' for v in xor_vals)}")

# Research: What could AI.MEG.GOU mean?
print("\n" + "-" * 60)
print("   MÖGLICHE BEDEUTUNGEN VON AI.MEG.GOU:")
print("-" * 60)
print("""
   1. AI = Artificial Intelligence
      MEG = Magnetoencephalography (Brain Scanning)
      GOU = ? (Chinese 狗 = Dog? GO + U?)

   2. AI.MEG könnte ein Name/Handle sein
      - Jemand namens "MEG" der mit AI arbeitet?
      - Ein AI-System namens MEG?

   3. Akronym:
      - AI = Aigarth Intelligence?
      - MEG = Matrix Encoded Gateway?
      - GOU = Genesis Output Unit?

   4. Anagramm:
      - AIMEGGOU = I AM EGG OU? 
      - MEGAIGOU = MEGA I GO U?
      - Umgestellt: GO AI ME GU?

   5. Numerisch:
      - A=1, I=9, M=13, E=5, G=7, O=15, U=21
      - AI = 1+9 = 10
      - MEG = 13+5+7 = 25
      - GOU = 7+15+21 = 43
      - Total = 78

   6. In Discord/Crypto Community:
      - Könnte ein bekannter Handle sein
      - Referenz zu einem Insider-Witz?
""")

# ==============================================================================
# PART 3: ALL 64 COLUMN PAIRS
# ==============================================================================
print("\n" + "=" * 80)
print("PART 3: ALLE 64 SYMMETRISCHEN SPALTENPAARE")
print("=" * 80)

print("\n   Analysiere Col[c] ⊕ Col[127-c] für c=0..63...")

all_results = []

for c in range(64):
    c2 = 127 - c
    xor_text = xor_columns(c, c2)
    words = find_words(xor_text, min_len=3)
    unique_words = list(set(words))
    
    # Score: longer words = more interesting
    score = sum(len(w)**2 for w in unique_words)
    
    all_results.append({
        'c1': c,
        'c2': c2,
        'text': xor_text,
        'words': unique_words,
        'score': score,
        'word_count': len(unique_words),
    })

# Sort by score
all_results.sort(key=lambda x: -x['score'])

print("\n   TOP 15 INTERESSANTESTE SPALTENPAARE:")
print("   " + "-" * 70)

for i, r in enumerate(all_results[:15]):
    c1, c2 = r['c1'], r['c2']
    words = r['words'][:5]
    marker = "⭐" if (c1, c2) in [(22, 105), (30, 97), (41, 86)] else "  "
    print(f"   {marker} Col {c1:3d} ⊕ {c2:3d}: Score={r['score']:4d}, Words: {', '.join(words[:5])}")

# Check for specific interesting words across ALL pairs
print("\n" + "-" * 60)
print("   SUCHE NACH SPEZIFISCHEN WÖRTERN IN ALLEN PAAREN:")
print("-" * 60)

search_words = ['SATOSHI', 'BITCOIN', 'NAKAMOTO', 'GENESIS', 'QUBIC', 'AIGARTH', 
                'SECRET', 'KEY', 'TREASURE', 'GOLD', 'MILLION', 'CFB', 'COME',
                'FIND', 'HERE', 'LOOK', 'HELLO', 'WORLD', 'GOD', 'ANNA', 'JINN']

for word in search_words:
    for r in all_results:
        if word in r['text'].upper():
            pos = r['text'].upper().find(word)
            print(f"   ✅ '{word}' in Col {r['c1']} ⊕ {r['c2']} at row {pos}")
            break
    else:
        # Not found in any pair
        pass

# ==============================================================================
# PART 4: STATISTICAL VALIDATION OF WORD FINDINGS
# ==============================================================================
print("\n" + "=" * 80)
print("PART 4: STATISTISCHE VALIDIERUNG DER WORT-FUNDE")
print("=" * 80)

import random
random.seed(42)

# Count total meaningful words found
total_words = sum(len(r['words']) for r in all_results)
total_long_words = sum(len([w for w in r['words'] if len(w) >= 4]) for r in all_results)

print(f"\n   Gefundene Wörter (3+ Buchstaben): {total_words}")
print(f"   Gefundene Wörter (4+ Buchstaben): {total_long_words}")

# Monte Carlo: How many words in random matrix?
print("\n   Monte-Carlo Test (100 zufällige Matrizen)...")

random_word_counts = []
for _ in range(100):
    # Shuffle matrix values
    values = matrix.flatten().copy()
    np.random.shuffle(values)
    rand_matrix = values.reshape(128, 128)
    
    rand_words = 0
    for c in range(64):
        c2 = 127 - c
        xor = rand_matrix[:, c] ^ rand_matrix[:, c2]
        text = ''.join(to_char(v) for v in xor)
        words = find_words(text, min_len=3)
        rand_words += len(set(words))
    
    random_word_counts.append(rand_words)

avg_random = np.mean(random_word_counts)
std_random = np.std(random_word_counts)
z_score = (total_words - avg_random) / std_random if std_random > 0 else 0

print(f"\n   Zufällige Wörter (3+): {avg_random:.1f} ± {std_random:.1f}")
print(f"   Tatsächlich: {total_words}")
print(f"   Z-Score: {z_score:.2f}")

if z_score > 2:
    print(f"   ✅ SIGNIFIKANT mehr Wörter als erwartet!")
elif z_score < -2:
    print(f"   ❓ Weniger Wörter als erwartet")
else:
    print(f"   ⚠️ Nicht signifikant unterschiedlich von Zufall")

# ==============================================================================
# SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("ZUSAMMENFASSUNG")
print("=" * 80)

print(f"""
   ╔══════════════════════════════════════════════════════════════════════════╗
   ║  MARKER-SPALTEN ANALYSE ERGEBNISSE                                       ║
   ╠══════════════════════════════════════════════════════════════════════════╣
   ║                                                                          ║
   ║  1. MARKER-SPALTEN:                                                      ║
   ║     - Col 22⊕105: Enthält Wörter aber kein klares Muster                ║
   ║     - Col 30⊕97:  AI.MEG.GOU bestätigt!                                 ║
   ║     - Col 41⊕86:  Weniger interessant                                   ║
   ║                                                                          ║
   ║  2. AI.MEG.GOU:                                                          ║
   ║     - 'AI' at row {ai_pos}                                                       ║
   ║     - 'MEG' at row {meg_pos}                                                      ║
   ║     - 'GOU' at row {gou_pos}                                                      ║
   ║     - Bedeutung: Unklar, weitere Recherche nötig                        ║
   ║                                                                          ║
   ║  3. ALLE 64 PAARE:                                                       ║
   ║     - Top-Paar nach Score: Col {all_results[0]['c1']}⊕{all_results[0]['c2']}                                ║
   ║     - Total Wörter: {total_words}                                              ║
   ║     - Z-Score vs Zufall: {z_score:.2f}                                           ║
   ║                                                                          ║
   ╚══════════════════════════════════════════════════════════════════════════╝
""")

# Save detailed results
output = {
    "marker_pairs": [
        {"c1": c1, "c2": c2, "xor_text": xor_columns(c1, c2), "description": desc}
        for c1, c2, desc in marker_pairs
    ],
    "aimeg_positions": {"AI": ai_pos, "MEG": meg_pos, "GOU": gou_pos},
    "all_pairs_ranked": [
        {"c1": r['c1'], "c2": r['c2'], "score": r['score'], "words": r['words'][:10]}
        for r in all_results[:20]
    ],
    "statistics": {
        "total_words": total_words,
        "random_avg": avg_random,
        "z_score": z_score,
    }
}

with open(script_dir / "DEEP_MARKER_RESULTS.json", "w") as f:
    json.dump(output, f, indent=2)

print("✓ Detaillierte Ergebnisse gespeichert in DEEP_MARKER_RESULTS.json")
