#!/usr/bin/env python3
"""
===============================================================================
          PATOSHI ↔ ANNA MATRIX - TIEFENFORSCHUNG
===============================================================================

Analysiert alle Patoshi-Adressen durch das Anna Matrix Neural Network.

Ziele:
1. Klassifiziere alle 21,953 Patoshi-Blöcke
2. Finde Muster in der Attraktor-Verteilung
3. Identifiziere spezielle Blöcke (1776, 2115, 4263, 5151)
4. Suche nach Verbindungen zu 1CFB
5. Analysiere zeitliche Muster
"""

import json
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
from collections import Counter, defaultdict
import struct

print("=" * 80)
print("         PATOSHI ↔ ANNA MATRIX - TIEFENFORSCHUNG")
print("=" * 80)

# =============================================================================
# HELPERS
# =============================================================================

def ternary_clamp(x):
    return 1 if x > 0 else (-1 if x < 0 else 0)

def bytes_to_trits(data: bytes, size: int) -> List[int]:
    trits = []
    for byte in data:
        for bit in range(8):
            trit = 1 if (byte >> bit) & 1 else -1
            trits.append(trit)
            if len(trits) >= size:
                return trits
    while len(trits) < size:
        trits.append(0)
    return trits[:size]

def pubkey_to_hash160(pubkey_hex: str) -> bytes:
    """Konvertiere Public Key zu Hash160"""
    import hashlib
    pubkey_bytes = bytes.fromhex(pubkey_hex)
    sha256_hash = hashlib.sha256(pubkey_bytes).digest()
    # RIPEMD160
    try:
        import hashlib
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256_hash)
        return ripemd160.digest()
    except:
        # Fallback: nur SHA256 verwenden
        return sha256_hash[:20]

def state_hash(state: List[int]) -> str:
    state_bytes = bytes([s + 1 for s in state])
    return hashlib.sha256(state_bytes).hexdigest()[:16]

# =============================================================================
# ANNA MATRIX NETWORK
# =============================================================================

class AnnaNetwork:
    def __init__(self, path: str):
        with open(path) as f:
            data = json.load(f)

        self.raw_matrix = []
        for row in data['matrix']:
            row_vals = []
            for v in row:
                if isinstance(v, str):
                    try:
                        row_vals.append(int(v, 16) if len(v) == 8 else int(v))
                    except:
                        row_vals.append(0)
                else:
                    row_vals.append(int(v))
            self.raw_matrix.append(row_vals)

        self.weights = [[ternary_clamp(v) for v in row] for row in self.raw_matrix]
        self.num_neurons = len(self.weights)
        self.state = [0] * self.num_neurons

        # Known attractor signatures
        self.attractor_names = {
            "7eb24a18990ee4c9": "ZERO (Fixpunkt)",
            "9e50f90fd035924a": "1CFB (ALL_POSITIVE)",
            "38723a2e5e8a17aa": "GENESIS (ALL_NEGATIVE)",
            "b3f704269cb28c10": "BALANCED_A",
            "ea27707d47374c85": "BALANCED_B",
        }

    def process_tick(self) -> List[int]:
        new_state = []
        for i in range(self.num_neurons):
            score = 0
            for j in range(self.num_neurons):
                if j < len(self.weights) and i < len(self.weights[j]):
                    weight = self.weights[j][i]
                    if weight != 0:
                        score += self.state[j] * weight
            new_value = (1 if score > 0 else 0) - (1 if score < 0 else 0)
            new_state.append(new_value)
        return new_state

    def classify(self, data: bytes, max_ticks: int = 50) -> Dict:
        """Klassifiziere Daten und gib Attraktor zurück"""
        trits = bytes_to_trits(data, self.num_neurons)
        self.state = trits[:]

        seen = {tuple(self.state): 0}

        for tick in range(max_ticks):
            new_state = self.process_tick()
            sig = tuple(new_state)

            if sig in seen:
                cycle_start = seen[sig]
                final_hash = state_hash(list(new_state))

                pos = sum(1 for s in new_state if s == 1)
                neg = sum(1 for s in new_state if s == -1)

                return {
                    "attractor_hash": final_hash,
                    "attractor_name": self.attractor_names.get(final_hash, f"UNKNOWN_{final_hash[:8]}"),
                    "cycle_start": cycle_start,
                    "cycle_length": tick + 1 - cycle_start,
                    "distribution": {"positive": pos, "negative": neg, "zero": self.num_neurons - pos - neg}
                }

            seen[sig] = tick + 1
            self.state = new_state

        # Nicht konvergiert
        final_hash = state_hash(self.state)
        return {
            "attractor_hash": final_hash,
            "attractor_name": "NO_CONVERGENCE",
            "cycle_start": None,
            "cycle_length": None
        }

# =============================================================================
# PATOSHI ANALYSIS
# =============================================================================

def analyze_patoshi_blocks(network: AnnaNetwork, patoshi_data: Dict) -> Dict:
    """Analysiere alle Patoshi-Blöcke"""

    results = {
        "total_blocks": 0,
        "attractor_distribution": Counter(),
        "special_blocks": {},
        "by_block_range": defaultdict(Counter),
        "1cfb_matches": [],
        "genesis_matches": [],
        "early_blocks": [],  # Erste 100 Blöcke
    }

    # Spezielle Blöcke
    special_blocks = {1776, 2115, 4263, 5151, 9, 264, 1}

    print(f"\n  Analysiere {patoshi_data['total']} Patoshi-Blöcke...")

    for i, record in enumerate(patoshi_data['records']):
        if i % 2000 == 0:
            print(f"    Fortschritt: {i}/{patoshi_data['total']}")

        block_height = record['blockHeight']
        pubkey = record['pubkey']

        # Hash160 des Public Keys
        try:
            hash160 = pubkey_to_hash160(pubkey)
        except:
            continue

        # Klassifiziere durch Anna Network
        classification = network.classify(hash160)

        results["total_blocks"] += 1
        results["attractor_distribution"][classification["attractor_name"]] += 1

        # Block-Range Statistik (0-1000, 1000-2000, etc.)
        block_range = (block_height // 1000) * 1000
        results["by_block_range"][block_range][classification["attractor_name"]] += 1

        # Spezielle Blöcke
        if block_height in special_blocks:
            results["special_blocks"][block_height] = {
                "pubkey": pubkey[:32] + "...",
                "classification": classification
            }

        # 1CFB Matches (ALL_POSITIVE)
        if classification["attractor_name"] == "1CFB (ALL_POSITIVE)":
            results["1cfb_matches"].append({
                "block": block_height,
                "pubkey_prefix": pubkey[:16]
            })

        # Genesis Matches (ALL_NEGATIVE)
        if classification["attractor_name"] == "GENESIS (ALL_NEGATIVE)":
            results["genesis_matches"].append({
                "block": block_height,
                "pubkey_prefix": pubkey[:16]
            })

        # Frühe Blöcke (erste 100)
        if block_height <= 100:
            results["early_blocks"].append({
                "block": block_height,
                "attractor": classification["attractor_name"],
                "cycle_start": classification.get("cycle_start")
            })

    return results

# =============================================================================
# PATTERN ANALYSIS
# =============================================================================

def analyze_patterns(results: Dict) -> Dict:
    """Analysiere Muster in den Ergebnissen"""

    patterns = {
        "attractor_percentages": {},
        "block_range_trends": {},
        "1cfb_block_gaps": [],
        "genesis_block_gaps": [],
    }

    total = results["total_blocks"]

    # Prozentuale Verteilung
    for attractor, count in results["attractor_distribution"].items():
        patterns["attractor_percentages"][attractor] = round(100 * count / total, 2)

    # Block-Range Trends
    for block_range, dist in sorted(results["by_block_range"].items()):
        range_total = sum(dist.values())
        patterns["block_range_trends"][f"{block_range}-{block_range+999}"] = {
            attractor: round(100 * count / range_total, 1)
            for attractor, count in dist.items()
        }

    # Gaps zwischen 1CFB-Matches
    if len(results["1cfb_matches"]) > 1:
        blocks = [m["block"] for m in results["1cfb_matches"]]
        patterns["1cfb_block_gaps"] = [blocks[i+1] - blocks[i] for i in range(len(blocks)-1)]

    # Gaps zwischen Genesis-Matches
    if len(results["genesis_matches"]) > 1:
        blocks = [m["block"] for m in results["genesis_matches"]]
        patterns["genesis_block_gaps"] = [blocks[i+1] - blocks[i] for i in range(len(blocks)-1)]

    return patterns

# =============================================================================
# SPECIAL TESTS
# =============================================================================

def test_special_inputs(network: AnnaNetwork) -> Dict:
    """Teste spezielle Inputs"""

    tests = {}

    # 1. Satoshi's erste bekannte Transaktion (Block 170)
    satoshi_tx = bytes.fromhex("0e3e2357e806b6cdb1f70b54c3a3a17b6714ee1f0e68bebb44a74b1efd512098")
    tests["satoshi_first_tx"] = network.classify(satoshi_tx)

    # 2. Die 1CFB Adresse selbst
    cfb_hash160 = bytes.fromhex("7b582a5c61c91befcfe2778b6a7c72fceb937c8c")
    tests["1cfb_address"] = network.classify(cfb_hash160)

    # 3. Bitcoin Genesis Block Hash
    genesis = bytes.fromhex("000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f")
    tests["bitcoin_genesis"] = network.classify(genesis)

    # 4. Hal Finney's Adresse (erster Bitcoin-Empfänger außer Satoshi)
    # 1Q2TWHE3GMdB6BZKafqwxXtWAWgFt5Jvm3 → Hash160
    hal_finney = bytes.fromhex("fc916f213a3d7f1369313d5fa30f6168f9446a2d")
    tests["hal_finney"] = network.classify(hal_finney)

    # 5. Block 264 (CFB Genesis Marker)
    block_264 = bytes.fromhex("00000000839a8e6886ab5951d76f411475428afc90947ee320161bbf18eb6048")
    tests["block_264"] = network.classify(block_264)

    # 6. Zahlenfolge 2299 (Matrix-Signatur)
    num_2299 = (2299).to_bytes(4, 'little') * 5  # 20 bytes
    tests["number_2299"] = network.classify(num_2299)

    # 7. ASCII "CFB" wiederholt
    cfb_ascii = b"CFB" * 7  # 21 bytes
    tests["cfb_ascii"] = network.classify(cfb_ascii[:20])

    # 8. ASCII "ANNA" wiederholt
    anna_ascii = b"ANNA" * 5  # 20 bytes
    tests["anna_ascii"] = network.classify(anna_ascii)

    # 9. Block 21e8 (mysteriöser Hash)
    block_21e8 = bytes.fromhex("21e800000000000000000000000000000000000000")
    tests["block_21e8"] = network.classify(block_21e8)

    # 10. Patoshi Nonce Pattern (LSB = 0x08)
    patoshi_nonce = bytes([0x08] * 20)
    tests["patoshi_nonce_pattern"] = network.classify(patoshi_nonce)

    return tests

# =============================================================================
# XOR ANALYSIS
# =============================================================================

def xor_analysis(network: AnnaNetwork, patoshi_data: Dict) -> Dict:
    """XOR-Analyse zwischen Patoshi-Blöcken"""

    # Nimm erste 100 Patoshi-Blöcke
    early_pubkeys = []
    for record in patoshi_data['records'][:100]:
        try:
            hash160 = pubkey_to_hash160(record['pubkey'])
            early_pubkeys.append({
                "block": record['blockHeight'],
                "hash160": hash160
            })
        except:
            continue

    results = {
        "xor_pairs_cfb": [],
        "xor_pairs_genesis": [],
        "cumulative_xor": None
    }

    cfb_hash160 = bytes.fromhex("7b582a5c61c91befcfe2778b6a7c72fceb937c8c")

    # XOR jedes frühen Blocks mit 1CFB
    for pk in early_pubkeys[:20]:
        xored = bytes(a ^ b for a, b in zip(pk["hash160"], cfb_hash160))
        classification = network.classify(xored)

        results["xor_pairs_cfb"].append({
            "block": pk["block"],
            "xor_attractor": classification["attractor_name"]
        })

    # Kumulatives XOR aller frühen Blöcke
    if early_pubkeys:
        cumulative = early_pubkeys[0]["hash160"]
        for pk in early_pubkeys[1:20]:
            cumulative = bytes(a ^ b for a, b in zip(cumulative, pk["hash160"]))

        cumulative_class = network.classify(cumulative)
        results["cumulative_xor"] = {
            "blocks_combined": 20,
            "classification": cumulative_class
        }

    return results

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("\n" + "=" * 80)
    print("PHASE 1: NETZWERK UND DATEN LADEN")
    print("=" * 80)

    network = AnnaNetwork("apps/web/public/data/anna-matrix.json")
    print(f"✓ Anna Network: {network.num_neurons} Neuronen")

    with open("apps/web/public/data/patoshi-addresses.json") as f:
        patoshi_data = json.load(f)
    print(f"✓ Patoshi Daten: {patoshi_data['total']} Blöcke")

    print("\n" + "=" * 80)
    print("PHASE 2: SPEZIELLE INPUTS TESTEN")
    print("=" * 80)

    special_tests = test_special_inputs(network)

    for name, result in special_tests.items():
        print(f"  {name}: {result['attractor_name']}")

    print("\n" + "=" * 80)
    print("PHASE 3: ALLE PATOSHI-BLÖCKE ANALYSIEREN")
    print("=" * 80)

    patoshi_results = analyze_patoshi_blocks(network, patoshi_data)

    print(f"\n  Gesamt analysiert: {patoshi_results['total_blocks']}")
    print(f"\n  Attraktor-Verteilung:")
    for attractor, count in patoshi_results["attractor_distribution"].most_common():
        pct = 100 * count / patoshi_results["total_blocks"]
        print(f"    {attractor}: {count} ({pct:.1f}%)")

    print(f"\n  1CFB-Matches: {len(patoshi_results['1cfb_matches'])}")
    print(f"  Genesis-Matches: {len(patoshi_results['genesis_matches'])}")

    print("\n  Spezielle Blöcke:")
    for block, data in sorted(patoshi_results["special_blocks"].items()):
        print(f"    Block {block}: {data['classification']['attractor_name']}")

    print("\n" + "=" * 80)
    print("PHASE 4: MUSTER-ANALYSE")
    print("=" * 80)

    patterns = analyze_patterns(patoshi_results)

    print("\n  Attraktor-Prozente:")
    for attractor, pct in sorted(patterns["attractor_percentages"].items(), key=lambda x: -x[1]):
        print(f"    {attractor}: {pct}%")

    print("\n  Frühe Blöcke (1-100):")
    for block_info in patoshi_results["early_blocks"][:15]:
        print(f"    Block {block_info['block']}: {block_info['attractor']} (cycle@{block_info['cycle_start']})")

    print("\n" + "=" * 80)
    print("PHASE 5: XOR-ANALYSE")
    print("=" * 80)

    xor_results = xor_analysis(network, patoshi_data)

    print("\n  XOR mit 1CFB:")
    for pair in xor_results["xor_pairs_cfb"][:10]:
        print(f"    Block {pair['block']} ⊕ 1CFB = {pair['xor_attractor']}")

    if xor_results["cumulative_xor"]:
        print(f"\n  Kumulatives XOR (Blöcke 1-20): {xor_results['cumulative_xor']['classification']['attractor_name']}")

    print("\n" + "=" * 80)
    print("PHASE 6: ERGEBNISSE SPEICHERN")
    print("=" * 80)

    output = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "total_patoshi_blocks": patoshi_results["total_blocks"],
            "network_neurons": network.num_neurons
        },
        "special_tests": {k: v for k, v in special_tests.items()},
        "attractor_distribution": dict(patoshi_results["attractor_distribution"]),
        "patterns": patterns,
        "special_blocks": patoshi_results["special_blocks"],
        "1cfb_matches": patoshi_results["1cfb_matches"][:50],  # Erste 50
        "genesis_matches": patoshi_results["genesis_matches"][:50],
        "early_blocks": patoshi_results["early_blocks"],
        "xor_analysis": xor_results,
        "block_range_trends": {k: dict(v) for k, v in patoshi_results["by_block_range"].items()}
    }

    output_path = Path("apps/web/scripts/PATOSHI_ANNA_RESEARCH_RESULTS.json")
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n✓ Ergebnisse gespeichert: {output_path}")

    # Zusammenfassung
    print("\n" + "=" * 80)
    print("ZUSAMMENFASSUNG")
    print("=" * 80)

    cfb_pct = patterns["attractor_percentages"].get("1CFB (ALL_POSITIVE)", 0)
    genesis_pct = patterns["attractor_percentages"].get("GENESIS (ALL_NEGATIVE)", 0)

    print(f"""
PATOSHI-ANALYSE:
  Gesamtblöcke: {patoshi_results['total_blocks']}
  1CFB-Attraktor: {cfb_pct}% aller Blöcke
  Genesis-Attraktor: {genesis_pct}% aller Blöcke

SPEZIELLE ENTDECKUNGEN:
  Block 9 (Satoshi → Hal Finney): {patoshi_results['special_blocks'].get(9, {}).get('classification', {}).get('attractor_name', 'N/A')}
  Block 264 (CFB Marker): {patoshi_results['special_blocks'].get(264, {}).get('classification', {}).get('attractor_name', 'N/A')}
  Block 1776: {patoshi_results['special_blocks'].get(1776, {}).get('classification', {}).get('attractor_name', 'N/A')}

SCHLÜSSEL-FRAGE:
  Sind Patoshi-Blöcke näher an 1CFB oder Genesis?
  → {('1CFB' if cfb_pct > genesis_pct else 'GENESIS')} dominiert!
""")

    return output

if __name__ == "__main__":
    results = main()
