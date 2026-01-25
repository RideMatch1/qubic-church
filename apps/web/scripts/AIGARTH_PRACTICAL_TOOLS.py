#!/usr/bin/env python3
"""
===============================================================================
            🧠 AIGARTH PRACTICAL TOOLS 🧠
===============================================================================
Real, useful applications of the Anna-Matrix neural network.

Available tools:
1. TEXT CLASSIFIER - Categorize text by energy signature
2. HASH FINGERPRINTER - Unique fingerprint for any data
3. SIMILARITY DETECTOR - Compare two inputs for similarity
4. PATTERN MATCHER - Find inputs with target energy
5. DATA AUTHENTICATOR - Verify data integrity
"""

import json
import hashlib
import numpy as np
from pathlib import Path
from datetime import datetime
import sys

script_dir = Path(__file__).parent

print("=" * 80)
print("           🧠 AIGARTH PRACTICAL TOOLS 🧠")
print("=" * 80)

# Load matrix and setup network
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])
ternary_matrix = np.sign(matrix).astype(int)

try:
    from aigarth_it.neuron_cl import AITClNeuron
    neurons = [AITClNeuron(input_weights=ternary_matrix[i].tolist(), input_skew=0) for i in range(128)]
    AIGARTH = True
    print("✓ Aigarth network initialized (128 neurons)")
except ImportError:
    AIGARTH = False
    print("❌ Aigarth not available")
    sys.exit(1)

def bytes_to_trits(data, length=128):
    trits = []
    for byte in data:
        trits.append((byte % 3) - 1)
        trits.append(((byte // 3) % 3) - 1)
        trits.append(((byte // 9) % 3) - 1)
    return (trits + [0] * length)[:length]

def process_network(input_data):
    """Process any input through the network, returns 128 neuron states."""
    if isinstance(input_data, str):
        input_data = hashlib.sha256(input_data.encode()).digest()
    elif isinstance(input_data, bytes):
        pass
    else:
        input_data = hashlib.sha256(str(input_data).encode()).digest()

    trits = bytes_to_trits(input_data)
    output = []
    for neuron in neurons:
        neuron.state = 0
        neuron.feedforward(trits)
        state, _ = neuron.commit_state()
        output.append(state)
    return output

def get_fingerprint(data):
    """Get unique 128-dimensional fingerprint for any data."""
    states = process_network(data)
    return states

def get_energy(data):
    """Get scalar energy value for any data."""
    return sum(process_network(data))

# ==============================================================================
# TOOL 1: TEXT CLASSIFIER
# ==============================================================================
print("\n" + "=" * 80)
print("TOOL 1: TEXT CLASSIFIER")
print("=" * 80)

def classify_text(text):
    """Classify text into categories based on energy signature."""
    energy = get_energy(text)

    # Define categories based on energy ranges
    if energy > 50:
        category = "HIGHLY POSITIVE"
        description = "Strong positive resonance"
    elif energy > 20:
        category = "POSITIVE"
        description = "Mild positive resonance"
    elif energy > -20:
        category = "NEUTRAL"
        description = "Balanced energy"
    elif energy > -50:
        category = "NEGATIVE"
        description = "Mild negative resonance"
    else:
        category = "HIGHLY NEGATIVE"
        description = "Strong negative resonance"

    return {
        "text": text[:50] + "..." if len(text) > 50 else text,
        "energy": energy,
        "category": category,
        "description": description,
    }

# Demo
test_texts = [
    "Hello, world!",
    "I love programming and creating new things",
    "This is a neutral statement about facts",
    "ERROR: System failure detected",
    "Bitcoin to the moon!",
    "Qubic is the future of smart contracts",
]

print("\n  Sample classifications:")
for text in test_texts:
    result = classify_text(text)
    print(f"    [{result['category']:15}] E={result['energy']:4d} | \"{result['text']}\"")

# ==============================================================================
# TOOL 2: HASH FINGERPRINTER
# ==============================================================================
print("\n" + "=" * 80)
print("TOOL 2: HASH FINGERPRINTER")
print("=" * 80)

def get_visual_fingerprint(data, width=32):
    """Create a visual ASCII representation of the fingerprint."""
    states = get_fingerprint(data)

    # Map states to characters
    chars = []
    for s in states:
        if s > 50:
            chars.append('█')
        elif s > 20:
            chars.append('▓')
        elif s > 0:
            chars.append('▒')
        elif s > -20:
            chars.append('░')
        else:
            chars.append(' ')

    # Format into rows
    fingerprint = ''.join(chars)
    rows = [fingerprint[i:i+width] for i in range(0, len(fingerprint), width)]
    return '\n'.join(rows)

print("\n  Visual fingerprints:")
samples = ["Bitcoin", "Qubic", "Satoshi", "CFB"]
for sample in samples:
    print(f"\n  '{sample}':")
    fp = get_visual_fingerprint(sample)
    for line in fp.split('\n'):
        print(f"    {line}")

# ==============================================================================
# TOOL 3: SIMILARITY DETECTOR
# ==============================================================================
print("\n" + "=" * 80)
print("TOOL 3: SIMILARITY DETECTOR")
print("=" * 80)

def calculate_similarity(data1, data2):
    """Calculate similarity between two inputs (0-100%)."""
    fp1 = get_fingerprint(data1)
    fp2 = get_fingerprint(data2)

    # Cosine similarity
    dot_product = sum(a * b for a, b in zip(fp1, fp2))
    norm1 = sum(a * a for a in fp1) ** 0.5
    norm2 = sum(b * b for b in fp2) ** 0.5

    if norm1 == 0 or norm2 == 0:
        return 0.0

    cosine_sim = dot_product / (norm1 * norm2)

    # Convert to percentage
    similarity = (cosine_sim + 1) / 2 * 100
    return similarity

print("\n  Similarity comparisons:")
pairs = [
    ("Bitcoin", "bitcoin"),
    ("Bitcoin", "Ethereum"),
    ("CFB", "Sergey Ivancheglo"),
    ("Hello", "Hello"),
    ("cat", "dog"),
    ("Qubic", "IOTA"),
]

for a, b in pairs:
    sim = calculate_similarity(a, b)
    bar_len = int(sim / 5)
    bar = '█' * bar_len + '░' * (20 - bar_len)
    print(f"    '{a}' vs '{b}': {bar} {sim:.1f}%")

# ==============================================================================
# TOOL 4: PATTERN MATCHER
# ==============================================================================
print("\n" + "=" * 80)
print("TOOL 4: PATTERN MATCHER")
print("=" * 80)

def find_matching_inputs(target_energy, prefix="", max_attempts=10000):
    """Find inputs that produce a specific energy."""
    matches = []

    for i in range(max_attempts):
        candidate = f"{prefix}{i}"
        energy = get_energy(candidate)

        if energy == target_energy:
            matches.append(candidate)
            if len(matches) >= 5:
                break

    return matches

print("\n  Finding strings with energy = 42 (The Answer):")
matches_42 = find_matching_inputs(42, "search_")
for m in matches_42:
    print(f"    '{m}' → E={get_energy(m)}")

print("\n  Finding strings with energy = 0 (Perfect Balance):")
matches_0 = find_matching_inputs(0, "balance_")
for m in matches_0:
    print(f"    '{m}' → E={get_energy(m)}")

# ==============================================================================
# TOOL 5: DATA AUTHENTICATOR
# ==============================================================================
print("\n" + "=" * 80)
print("TOOL 5: DATA AUTHENTICATOR")
print("=" * 80)

def create_auth_signature(data, secret=""):
    """Create an authentication signature for data."""
    combined = f"{secret}{data}"
    fingerprint = get_fingerprint(combined)

    # Create compact signature from fingerprint
    sig_bytes = bytes([(s + 128) % 256 for s in fingerprint])
    signature = hashlib.sha256(sig_bytes).hexdigest()[:16]

    return {
        "data_hash": hashlib.sha256(str(data).encode()).hexdigest()[:16],
        "neural_signature": signature,
        "energy": get_energy(combined),
    }

def verify_auth_signature(data, signature, secret=""):
    """Verify if data matches its signature."""
    expected = create_auth_signature(data, secret)
    return expected["neural_signature"] == signature["neural_signature"]

print("\n  Creating and verifying signatures:")

# Create signatures
doc1 = "Important document content"
doc2 = "Modified document content"
secret = "my_secret_key"

sig1 = create_auth_signature(doc1, secret)
print(f"\n    Original: '{doc1}'")
print(f"    Signature: {sig1['neural_signature']}")
print(f"    Energy: {sig1['energy']}")

# Verify
is_valid = verify_auth_signature(doc1, sig1, secret)
print(f"\n    Verification (same data): {'✓ VALID' if is_valid else '✗ INVALID'}")

is_valid_modified = verify_auth_signature(doc2, sig1, secret)
print(f"    Verification (modified):  {'✓ VALID' if is_valid_modified else '✗ INVALID'}")

# ==============================================================================
# INTERACTIVE MODE
# ==============================================================================
print("\n" + "=" * 80)
print("INTERACTIVE DEMO")
print("=" * 80)

print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   🧠 AIGARTH PRACTICAL TOOLS READY                                           ║
║                                                                               ║
║   Available functions:                                                        ║
║                                                                               ║
║   • classify_text(text)           → Category & energy                        ║
║   • get_fingerprint(data)         → 128-dim vector                           ║
║   • get_visual_fingerprint(data)  → ASCII visualization                      ║
║   • calculate_similarity(a, b)    → 0-100% similarity                        ║
║   • find_matching_inputs(energy)  → Strings with target energy               ║
║   • create_auth_signature(data)   → Authentication signature                 ║
║   • verify_auth_signature(d, sig) → True/False                               ║
║                                                                               ║
║   Usage: Import and call functions, or run interactively                     ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")

# Save results
results = {
    "timestamp": datetime.now().isoformat(),
    "tools_available": [
        "TEXT_CLASSIFIER",
        "HASH_FINGERPRINTER",
        "SIMILARITY_DETECTOR",
        "PATTERN_MATCHER",
        "DATA_AUTHENTICATOR",
    ],
    "sample_results": {
        "classifications": [classify_text(t) for t in test_texts],
        "similarities": [{"pair": [a, b], "similarity": calculate_similarity(a, b)} for a, b in pairs],
        "energy_42_matches": matches_42,
        "energy_0_matches": matches_0,
    },
}

output_path = script_dir / "AIGARTH_PRACTICAL_TOOLS_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"✓ Results saved: {output_path}")
