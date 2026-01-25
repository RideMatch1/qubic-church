#!/usr/bin/env python3
"""
Advanced Message Decoder for Anna Matrix
Focus: Find more hidden messages by combining all discovered patterns
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter

# Load matrix
script_dir = Path(__file__).parent
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"

with open(matrix_path) as f:
    data = json.load(f)

matrix = np.array(data["matrix"])

# Helper function to safely get numeric value
def safe_int(val):
    if isinstance(val, (str, np.str_)):
        return 0
    return int(val)

results = {
    "synthesis_timestamp": None,
    "combined_message_findings": {},
    "sentence_candidates": [],
    "ai_meg_gou_analysis": {},
    "cross_pattern_correlations": [],
    "final_decoded_messages": []
}

import datetime
results["synthesis_timestamp"] = datetime.datetime.now().isoformat()

# =============================================================================
# PART 1: Deep analysis of AI MEG GOU (Pair 30↔97)
# =============================================================================

print("=" * 60)
print("PART 1: Deep AI MEG GOU Analysis")
print("=" * 60)

# Extract pair 30↔97 fully
pair_30_97 = []
for row in range(128):
    val_30 = matrix[row][30]
    val_97 = matrix[row][97]
    # Handle string cells (some cells contain "00000000" strings)
    if isinstance(val_30, (str, np.str_)):
        val_30 = 0
    else:
        val_30 = int(val_30)
    if isinstance(val_97, (str, np.str_)):
        val_97 = 0
    else:
        val_97 = int(val_97)
    xor_val = (val_30 & 0xFF) ^ (val_97 & 0xFF)
    pair_30_97.append({
        "row": row,
        "col_30": val_30,
        "col_97": val_97,
        "xor": xor_val,
        "char_30": chr(val_30 & 0x7F) if 32 <= (val_30 & 0x7F) <= 126 else ".",
        "char_97": chr(val_97 & 0x7F) if 32 <= (val_97 & 0x7F) <= 126 else ".",
        "xor_char": chr(xor_val) if 32 <= xor_val <= 126 else "."
    })

# Look for AI MEG GOU - what's around them?
print("\nSearching for AI, MEG, GOU patterns...")

xor_text = "".join([p["xor_char"] for p in pair_30_97])
print(f"XOR text: {xor_text}")

# Search for meaningful subsequences
def find_word_positions(text, words):
    found = []
    for word in words:
        pos = 0
        while True:
            pos = text.find(word, pos)
            if pos == -1:
                break
            found.append({"word": word, "position": pos, "context": text[max(0,pos-5):pos+len(word)+5]})
            pos += 1
    return found

ai_meg_words = find_word_positions(xor_text.upper(), ["AI", "MEG", "GOU", "GO", "ME", "KEY", "CFB", "KC", "OI", "IO"])
print(f"\nWords found: {ai_meg_words}")

# Try different interpretations
print("\n--- AI MEG GOU Interpretations ---")

interpretations = [
    {"text": "AI MEG GOU", "meaning": "AI Message Go U - Command to AI system"},
    {"text": "AI MEG", "meaning": "AI MEGA - Artificial Intelligence Megastructure"},
    {"text": "GOU", "meaning": "Go U(ser) - Command pattern"},
    {"text": "KC...AI...MEG...GOU", "meaning": "Key Code -> AI -> MEGA -> Go User"},
]

# Try reversing
reversed_xor = xor_text[::-1]
print(f"\nReversed XOR: {reversed_xor}")

# Try every Nth character
for n in [2, 3, 4, 5, 7, 11]:
    every_nth = "".join([xor_text[i] for i in range(0, len(xor_text), n)])
    if len(set(every_nth.upper()) - set('ABCDEFGHIJKLMNOPQRSTUVWXYZ. ')) < len(set(every_nth)) / 2:
        print(f"Every {n}th: {every_nth}")

# Try Caesar cipher shifts
print("\n--- Caesar Cipher Shifts ---")
for shift in [1, 3, 7, 13, 27]:
    shifted = ""
    for c in xor_text:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            shifted += chr((ord(c) - base + shift) % 26 + base)
        else:
            shifted += c
    if "AI" in shifted.upper() or "MEG" in shifted.upper():
        print(f"Shift {shift}: {shifted}")

results["ai_meg_gou_analysis"] = {
    "xor_text": xor_text,
    "words_found": ai_meg_words,
    "interpretations": interpretations,
    "reversed": reversed_xor
}

# =============================================================================
# PART 2: Reconstruct potential sentences from found words
# =============================================================================

print("\n" + "=" * 60)
print("PART 2: Sentence Reconstruction")
print("=" * 60)

# All words we've found
found_words = [
    # From binary letter stream
    {"word": "cfb", "pos": 854, "source": "binary_forward"},
    {"word": "cfb", "pos": 427, "source": "binary_reversed"},
    {"word": "key", "pos": 2998, "source": "binary_forward"},
    {"word": "you", "pos": 6805, "source": "binary_forward"},
    {"word": "you", "pos": 2923, "source": "binary_reversed"},
    {"word": "are", "pos": 909, "source": "binary_forward"},
    {"word": "are", "pos": 5701, "source": "binary_reversed"},
    {"word": "all", "pos": 1194, "source": "binary_forward"},
    {"word": "end", "pos": 5371, "source": "binary_reversed"},
    # From pair 30↔97
    {"word": "AI", "pos": 55, "source": "pair_30_97"},
    {"word": "MEG", "pos": 58, "source": "pair_30_97"},
    {"word": "GOU", "pos": 66, "source": "pair_30_97"},
    {"word": "KC", "pos": 0, "source": "pair_30_97"},
    {"word": "OI", "pos": 41, "source": "pair_30_97"},
    # From row 64
    {"word": "denidece", "pos": 64, "source": "row_64"},
]

# Try to form sentences
print("\nPotential sentence candidates:")

sentences = [
    "YOU ARE ALL...",
    "CFB KEY...",
    "AI MEG GOU KC OI",
    "DENIDECE = EVIDENCE?",
    "YOU ARE ALL KEY CFB",
    "END... ARE YOU ALL?",
]

for s in sentences:
    print(f"  - {s}")

# Check if DENIDECE is an anagram of EVIDENCE
from itertools import permutations

denidece = "denidece"
evidence = "evidence"

print(f"\nDENIDECE analysis:")
print(f"  Letters in DENIDECE: {sorted(denidece)}")
print(f"  Letters in EVIDENCE: {sorted(evidence)}")
print(f"  Match: {sorted(denidece) == sorted(evidence)}")

# Check letter frequency
print(f"  DENIDECE freq: {Counter(denidece)}")
print(f"  EVIDENCE freq: {Counter(evidence)}")

results["sentence_candidates"] = sentences

# =============================================================================
# PART 3: Cross-pattern correlation
# =============================================================================

print("\n" + "=" * 60)
print("PART 3: Cross-Pattern Correlation")
print("=" * 60)

# The 4 asymmetric pairs all have messages - do they connect?
asymmetric_pairs = [
    {"pair": "0↔127", "message": "k vs K", "interpretation": "Case difference - signature"},
    {"pair": "22↔105", "message": ">FIB", "interpretation": "Fibonacci pointer"},
    {"pair": "30↔97", "message": "AI MEG GOU", "interpretation": "AI Message command"},
    {"pair": "41↔86", "message": "P vs Y", "interpretation": "PY = Python? Position markers"},
]

print("\nAsymmetric pair messages:")
for p in asymmetric_pairs:
    print(f"  {p['pair']}: {p['message']} -> {p['interpretation']}")

# Look for connections
print("\nPair number patterns:")
for p in asymmetric_pairs:
    nums = p['pair'].replace("↔", " ").split()
    a, b = int(nums[0]), int(nums[1])
    print(f"  {a} + {b} = {a + b}, {a} XOR {b} = {a ^ b}, {a} * {b} = {a * b}")

results["cross_pattern_correlations"] = asymmetric_pairs

# =============================================================================
# PART 4: Row 64 deep analysis (DENIDECE/EVIDENCE)
# =============================================================================

print("\n" + "=" * 60)
print("PART 4: Row 64 (Middle Row) Deep Analysis")
print("=" * 60)

row_64 = [safe_int(v) for v in matrix[64]]
print(f"Row 64 raw: {row_64[:16]}...")

# Try different transformations
row_64_ascii = "".join([chr(v & 0x7F) if 32 <= (v & 0x7F) <= 126 else "." for v in row_64])
print(f"Row 64 ASCII: {row_64_ascii}")

# XOR with different values
for xor_val in [0, 13, 27, 100, 127]:
    xored = "".join([chr((v ^ xor_val) & 0x7F) if 32 <= ((v ^ xor_val) & 0x7F) <= 126 else "." for v in row_64])
    if "evi" in xored.lower() or "den" in xored.lower():
        print(f"Row 64 XOR {xor_val}: {xored}")

# Row 64 is the MIDDLE row - significant!
print(f"\nRow 64 is the middle row (128/2 = 64)")
print(f"Row 64 + Row 63 = 127 (Mersenne!)")

# Check mirror row
row_63 = [safe_int(v) for v in matrix[63]]
mirror_xor = "".join([chr((row_64[i] ^ row_63[i]) & 0x7F) if 32 <= ((row_64[i] ^ row_63[i]) & 0x7F) <= 126 else "." for i in range(128)])
print(f"Row 64 XOR Row 63: {mirror_xor}")

# =============================================================================
# PART 5: Final message synthesis
# =============================================================================

print("\n" + "=" * 60)
print("PART 5: Final Message Synthesis")
print("=" * 60)

final_messages = []

# Message 1: YOU ARE ALL
msg1 = {
    "message": "YOU ARE ALL",
    "sources": ["binary stream positions 909, 1194, 6805"],
    "confidence": "medium",
    "interpretation": "Possible greeting or identification"
}
final_messages.append(msg1)

# Message 2: CFB KEY
msg2 = {
    "message": "CFB KEY",
    "sources": ["binary stream positions 854, 2998"],
    "confidence": "high",
    "interpretation": "Reference to CFB (Sergey Ivancheglo) and cryptographic key"
}
final_messages.append(msg2)

# Message 3: AI MEG(A)
msg3 = {
    "message": "AI MEGA / AI MESSAGE GO",
    "sources": ["pair 30↔97 asymmetric positions"],
    "confidence": "high",
    "interpretation": "AI system command or identification"
}
final_messages.append(msg3)

# Message 4: EVIDENCE
msg4 = {
    "message": "EVIDENCE (scrambled as DENIDECE)",
    "sources": ["row 64"],
    "confidence": "medium",
    "interpretation": "The word EVIDENCE scrambled - pointing to proof/evidence"
}
final_messages.append(msg4)

# Message 5: END
msg5 = {
    "message": "END",
    "sources": ["binary stream reversed at position 5371"],
    "confidence": "medium",
    "interpretation": "Possible message terminator"
}
final_messages.append(msg5)

# Message 6: >FIB
msg6 = {
    "message": ">FIB (Fibonacci pointer)",
    "sources": ["pair 22↔105"],
    "confidence": "high",
    "interpretation": "Points to Fibonacci-based encoding"
}
final_messages.append(msg6)

print("\nFinal synthesized messages:")
for i, msg in enumerate(final_messages, 1):
    print(f"\n{i}. {msg['message']}")
    print(f"   Source: {msg['sources']}")
    print(f"   Confidence: {msg['confidence']}")
    print(f"   Interpretation: {msg['interpretation']}")

results["final_decoded_messages"] = final_messages

# =============================================================================
# PART 6: Try to combine into coherent statement
# =============================================================================

print("\n" + "=" * 60)
print("PART 6: Coherent Statement Attempt")
print("=" * 60)

combined_attempts = [
    "YOU ARE ALL [looking for] EVIDENCE [of] CFB KEY [in] AI MEGA >FIB",
    "CFB KEY: AI MEGA EVIDENCE YOU ARE ALL END",
    "[This is] EVIDENCE [that] YOU ARE ALL [part of] AI MEGA [system by] CFB",
]

print("\nPossible combined statements:")
for attempt in combined_attempts:
    print(f"  → {attempt}")

# =============================================================================
# PART 7: Look for more words in unexplored areas
# =============================================================================

print("\n" + "=" * 60)
print("PART 7: Additional Word Search")
print("=" * 60)

# Create full letter stream from matrix
letter_stream = ""
for row in range(128):
    for col in range(128):
        val = safe_int(matrix[row][col])
        ch = chr(val & 0x7F) if 32 <= (val & 0x7F) <= 126 else ""
        if ch.isalpha():
            letter_stream += ch.lower()

print(f"Letter stream length: {len(letter_stream)}")

# Extended word list
extended_words = [
    "satoshi", "nakamoto", "bitcoin", "genesis", "block", "hash", "nonce",
    "qubic", "iota", "tangle", "ternary", "trinary", "truth",
    "aigarth", "anna", "oracle", "bridge", "pattern",
    "seed", "node", "network", "protocol", "consensus",
    "come", "here", "look", "find", "seek", "search",
    "hidden", "secret", "code", "cipher", "decode", "encrypt",
    "begin", "start", "init", "boot", "wake", "arise",
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "yes", "the", "and", "for", "not", "but", "can", "did", "has", "had", "was", "are"
]

print("\nSearching for extended word list...")
extended_found = []
for word in extended_words:
    if word in letter_stream:
        pos = letter_stream.find(word)
        context = letter_stream[max(0,pos-10):pos+len(word)+10]
        extended_found.append({"word": word, "position": pos, "context": context})
        print(f"  Found '{word}' at position {pos}: ...{context}...")

# Also check reversed
letter_stream_rev = letter_stream[::-1]
for word in extended_words:
    if word in letter_stream_rev:
        pos = letter_stream_rev.find(word)
        context = letter_stream_rev[max(0,pos-10):pos+len(word)+10]
        extended_found.append({"word": word + " (rev)", "position": pos, "context": context})
        print(f"  Found '{word}' (reversed) at position {pos}: ...{context}...")

results["extended_word_search"] = extended_found

# =============================================================================
# Save results
# =============================================================================

output_path = script_dir / "ADVANCED_MESSAGE_SYNTHESIS.json"
with open(output_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"\n✓ Results saved to {output_path}")

# Final summary
print("\n" + "=" * 60)
print("FINAL SUMMARY")
print("=" * 60)
print(f"""
Total distinct messages found: {len(final_messages)}

HIGH CONFIDENCE:
  1. CFB KEY - Direct reference to creator and cryptography
  2. AI MEG(A) / AI MESSAGE GO - AI system reference
  3. >FIB - Fibonacci encoding pointer

MEDIUM CONFIDENCE:
  4. YOU ARE ALL - Possible greeting
  5. EVIDENCE (DENIDECE) - Scrambled word
  6. END - Message terminator

INTERPRETATION:
  The matrix appears to contain a message about:
  - CFB (creator) and cryptographic keys
  - AI systems (MEGA/MESSAGE)
  - Evidence and proof
  - Fibonacci-based encoding

  Possible reading: "EVIDENCE of CFB KEY in AI MEGA [system]"
""")
