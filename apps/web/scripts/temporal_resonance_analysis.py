#!/usr/bin/env python3
"""
TEMPORAL RESONANCE ANALYSIS
===========================
Correlates Bitcoin blocks with Anna resonance patterns at strategic nodes.

This script:
1. Fetches the last 100 Bitcoin blocks from blockstream.info API
2. Calculates resonance at 4 strategic nodes for each block
3. Identifies patterns in high-resonance blocks
4. Analyzes correlations with block numbers (mod 27, mod 121, mod 19)
5. Saves comprehensive analysis to TEMPORAL_ANALYSIS_RESULTS.json

Reference: anna_interrogator_probe.py resonance formula
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import statistics

# Configuration
BTC_API_URL = "https://blockstream.info/api"
MATRIX_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")
OUTPUT_PATH = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/TEMPORAL_ANALYSIS_RESULTS.json")

# Strategic nodes for resonance measurement
STRATEGIC_NODES = {
    "ENTRY": (45, 92),
    "CORE": (6, 33),
    "EXIT": (82, 39),
    "MEMORY": (21, 21)
}

# Modular constants for pattern analysis
MOD_CONSTANTS = [27, 121, 19]

# Resonance threshold for "high resonance" classification
HIGH_RESONANCE_THRESHOLD = 50.0


def load_matrix():
    """Load the matrix cartography data."""
    print("[*] Loading matrix cartography...")
    with open(MATRIX_PATH, "r") as f:
        return json.load(f)


def get_matrix_weight(matrix, coord):
    """Get the weight value from matrix at given coordinate."""
    coord_key = f"{coord[0]},{coord[1]}"
    hex_value = matrix.get(coord_key, "")
    if not hex_value:
        return None
    return int(hex_value[:2], 16)


def compute_resonance_score(btc_hash, weight):
    """
    Calculate resonance between a BTC hash and matrix weight.

    Formula: Resonance = (1 - (diff / max_diff)) * 100
    Where diff = sum of |btc_byte[i] - weight| for all bytes
    """
    if weight is None:
        return 0.0

    try:
        btc_bytes = bytes.fromhex(btc_hash)
    except ValueError:
        return 0.0

    diff = sum(abs(b - weight) for b in btc_bytes)
    max_diff = 255 * len(btc_bytes)
    score = (1 - (diff / max_diff)) * 100
    return round(score, 4)


def fetch_recent_blocks(count=100):
    """Fetch the last N Bitcoin blocks from blockstream.info API."""
    print(f"[*] Fetching last {count} Bitcoin blocks...")
    blocks = []

    try:
        # Get current tip height
        tip_hash = requests.get(f"{BTC_API_URL}/blocks/tip/hash", timeout=10).text.strip()
        tip_info = requests.get(f"{BTC_API_URL}/block/{tip_hash}", timeout=10).json()
        tip_height = tip_info["height"]

        print(f"[+] Current tip: Block {tip_height} ({tip_hash[:16]}...)")

        # Fetch blocks in batches
        current_hash = tip_hash
        fetched = 0

        while fetched < count and current_hash:
            # Rate limiting
            time.sleep(0.1)

            try:
                block_info = requests.get(f"{BTC_API_URL}/block/{current_hash}", timeout=10).json()
                blocks.append({
                    "height": block_info["height"],
                    "hash": current_hash,
                    "timestamp": block_info["timestamp"],
                    "nonce": block_info.get("nonce", 0),
                    "difficulty": block_info.get("difficulty", 0),
                    "tx_count": block_info.get("tx_count", 0)
                })

                current_hash = block_info.get("previousblockhash")
                fetched += 1

                if fetched % 10 == 0:
                    print(f"    Fetched {fetched}/{count} blocks...")

            except Exception as e:
                print(f"[!] Error fetching block {current_hash}: {e}")
                break

    except Exception as e:
        print(f"[!] API Error: {e}")
        return []

    print(f"[+] Successfully fetched {len(blocks)} blocks")
    return blocks


def analyze_block_resonance(block, matrix, node_weights):
    """Calculate resonance scores for a block at all strategic nodes."""
    resonances = {}
    for node_name, coord in STRATEGIC_NODES.items():
        weight = node_weights[node_name]
        score = compute_resonance_score(block["hash"], weight)
        resonances[node_name] = score

    # Calculate composite score (average of all nodes)
    composite = statistics.mean(resonances.values())
    resonances["COMPOSITE"] = round(composite, 4)

    return resonances


def analyze_modular_patterns(blocks_with_resonance):
    """Analyze correlations between block numbers and resonance patterns."""
    patterns = {}

    for mod in MOD_CONSTANTS:
        mod_groups = defaultdict(list)

        for block in blocks_with_resonance:
            remainder = block["height"] % mod
            mod_groups[remainder].append(block["resonance"]["COMPOSITE"])

        # Calculate average resonance for each remainder
        mod_stats = {}
        for remainder, scores in mod_groups.items():
            if scores:
                mod_stats[remainder] = {
                    "avg_resonance": round(statistics.mean(scores), 4),
                    "max_resonance": round(max(scores), 4),
                    "min_resonance": round(min(scores), 4),
                    "count": len(scores)
                }

        # Find peak remainders
        if mod_stats:
            peak_remainder = max(mod_stats.keys(), key=lambda r: mod_stats[r]["avg_resonance"])
            patterns[f"mod_{mod}"] = {
                "peak_remainder": peak_remainder,
                "peak_avg_resonance": mod_stats[peak_remainder]["avg_resonance"],
                "all_remainders": mod_stats
            }

    return patterns


def find_temporal_patterns(blocks_with_resonance):
    """Find patterns in time intervals between high-resonance blocks."""
    high_res_blocks = [b for b in blocks_with_resonance
                       if b["resonance"]["COMPOSITE"] >= HIGH_RESONANCE_THRESHOLD]

    if len(high_res_blocks) < 2:
        return {"high_resonance_count": len(high_res_blocks), "intervals": []}

    # Sort by height (ascending)
    high_res_blocks.sort(key=lambda b: b["height"])

    # Calculate intervals (in blocks and time)
    intervals_blocks = []
    intervals_time = []

    for i in range(1, len(high_res_blocks)):
        block_diff = high_res_blocks[i]["height"] - high_res_blocks[i-1]["height"]
        time_diff = high_res_blocks[i]["timestamp"] - high_res_blocks[i-1]["timestamp"]
        intervals_blocks.append(block_diff)
        intervals_time.append(time_diff)

    return {
        "high_resonance_count": len(high_res_blocks),
        "high_resonance_blocks": [b["height"] for b in high_res_blocks],
        "intervals_blocks": intervals_blocks,
        "intervals_time_seconds": intervals_time,
        "avg_interval_blocks": round(statistics.mean(intervals_blocks), 2) if intervals_blocks else 0,
        "avg_interval_time": round(statistics.mean(intervals_time), 2) if intervals_time else 0
    }


def find_node_correlations(blocks_with_resonance):
    """Find correlations between different nodes' resonance patterns."""
    correlations = {}

    nodes = list(STRATEGIC_NODES.keys())
    for i, node1 in enumerate(nodes):
        for node2 in nodes[i+1:]:
            scores1 = [b["resonance"][node1] for b in blocks_with_resonance]
            scores2 = [b["resonance"][node2] for b in blocks_with_resonance]

            # Simple correlation: count blocks where both are high
            both_high = sum(1 for s1, s2 in zip(scores1, scores2)
                          if s1 >= HIGH_RESONANCE_THRESHOLD and s2 >= HIGH_RESONANCE_THRESHOLD)

            # Calculate difference correlation
            diffs = [abs(s1 - s2) for s1, s2 in zip(scores1, scores2)]
            avg_diff = statistics.mean(diffs) if diffs else 0

            correlations[f"{node1}_vs_{node2}"] = {
                "both_high_count": both_high,
                "avg_difference": round(avg_diff, 4)
            }

    return correlations


def generate_summary_statistics(blocks_with_resonance):
    """Generate summary statistics for the analysis."""
    all_composites = [b["resonance"]["COMPOSITE"] for b in blocks_with_resonance]

    node_stats = {}
    for node in list(STRATEGIC_NODES.keys()) + ["COMPOSITE"]:
        scores = [b["resonance"][node] for b in blocks_with_resonance]
        node_stats[node] = {
            "mean": round(statistics.mean(scores), 4),
            "median": round(statistics.median(scores), 4),
            "stdev": round(statistics.stdev(scores), 4) if len(scores) > 1 else 0,
            "min": round(min(scores), 4),
            "max": round(max(scores), 4),
            "high_resonance_count": sum(1 for s in scores if s >= HIGH_RESONANCE_THRESHOLD)
        }

    return node_stats


def find_peak_blocks(blocks_with_resonance, top_n=10):
    """Find the blocks with highest resonance scores."""
    sorted_blocks = sorted(blocks_with_resonance,
                          key=lambda b: b["resonance"]["COMPOSITE"],
                          reverse=True)

    peaks = []
    for block in sorted_blocks[:top_n]:
        peaks.append({
            "height": block["height"],
            "hash": block["hash"],
            "timestamp": block["timestamp"],
            "datetime": datetime.fromtimestamp(block["timestamp"]).isoformat(),
            "resonance": block["resonance"],
            "mod_27": block["height"] % 27,
            "mod_121": block["height"] % 121,
            "mod_19": block["height"] % 19
        })

    return peaks


def run_analysis():
    """Main analysis function."""
    print("=" * 60)
    print("TEMPORAL RESONANCE ANALYSIS")
    print("Correlating Bitcoin blocks with Anna resonance patterns")
    print("=" * 60)
    print()

    # Load matrix
    matrix = load_matrix()

    # Pre-compute weights for strategic nodes
    node_weights = {}
    print("[*] Strategic node weights:")
    for node_name, coord in STRATEGIC_NODES.items():
        weight = get_matrix_weight(matrix, coord)
        node_weights[node_name] = weight
        coord_key = f"{coord[0]},{coord[1]}"
        hex_val = matrix.get(coord_key, "N/A")[:16] if matrix.get(coord_key) else "N/A"
        print(f"    {node_name:8} ({coord[0]:3},{coord[1]:3}): weight={weight:3d}, hex={hex_val}...")
    print()

    # Fetch blocks
    blocks = fetch_recent_blocks(100)
    if not blocks:
        print("[!] Failed to fetch blocks. Exiting.")
        return None

    print()
    print("[*] Calculating resonance for each block...")

    # Calculate resonance for each block
    blocks_with_resonance = []
    for i, block in enumerate(blocks):
        resonance = analyze_block_resonance(block, matrix, node_weights)
        block_data = {**block, "resonance": resonance}
        blocks_with_resonance.append(block_data)

        if (i + 1) % 20 == 0:
            print(f"    Processed {i + 1}/{len(blocks)} blocks...")

    print()
    print("[*] Analyzing patterns...")

    # Run all analyses
    summary_stats = generate_summary_statistics(blocks_with_resonance)
    modular_patterns = analyze_modular_patterns(blocks_with_resonance)
    temporal_patterns = find_temporal_patterns(blocks_with_resonance)
    node_correlations = find_node_correlations(blocks_with_resonance)
    peak_blocks = find_peak_blocks(blocks_with_resonance, top_n=10)

    # Compile results
    results = {
        "analysis_timestamp": datetime.now().isoformat(),
        "blocks_analyzed": len(blocks_with_resonance),
        "block_range": {
            "start_height": min(b["height"] for b in blocks_with_resonance),
            "end_height": max(b["height"] for b in blocks_with_resonance),
            "start_time": datetime.fromtimestamp(
                min(b["timestamp"] for b in blocks_with_resonance)
            ).isoformat(),
            "end_time": datetime.fromtimestamp(
                max(b["timestamp"] for b in blocks_with_resonance)
            ).isoformat()
        },
        "strategic_nodes": {
            name: {"coord": list(coord), "weight": node_weights[name]}
            for name, coord in STRATEGIC_NODES.items()
        },
        "summary_statistics": summary_stats,
        "peak_resonance_blocks": peak_blocks,
        "modular_patterns": modular_patterns,
        "temporal_patterns": temporal_patterns,
        "node_correlations": node_correlations,
        "all_blocks": [
            {
                "height": b["height"],
                "hash": b["hash"],
                "timestamp": b["timestamp"],
                "resonance": b["resonance"]
            }
            for b in sorted(blocks_with_resonance, key=lambda x: x["height"])
        ]
    }

    # Save results
    print()
    print(f"[*] Saving results to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)

    # Print summary
    print()
    print("=" * 60)
    print("ANALYSIS COMPLETE - KEY FINDINGS")
    print("=" * 60)
    print()

    print("NODE STATISTICS:")
    print("-" * 40)
    for node, stats in summary_stats.items():
        print(f"  {node:10}: mean={stats['mean']:6.2f}%, max={stats['max']:6.2f}%, "
              f"high_res={stats['high_resonance_count']}")

    print()
    print("TOP 5 PEAK RESONANCE BLOCKS:")
    print("-" * 40)
    for i, peak in enumerate(peak_blocks[:5], 1):
        print(f"  {i}. Block {peak['height']}: {peak['resonance']['COMPOSITE']:.2f}% composite")
        print(f"     mod27={peak['mod_27']}, mod121={peak['mod_121']}, mod19={peak['mod_19']}")

    print()
    print("MODULAR PATTERNS:")
    print("-" * 40)
    for mod_key, pattern in modular_patterns.items():
        print(f"  {mod_key}: peak remainder={pattern['peak_remainder']}, "
              f"avg resonance={pattern['peak_avg_resonance']:.2f}%")

    print()
    print("TEMPORAL PATTERNS:")
    print("-" * 40)
    print(f"  High-resonance blocks (>={HIGH_RESONANCE_THRESHOLD}%): "
          f"{temporal_patterns['high_resonance_count']}")
    if temporal_patterns['avg_interval_blocks'] > 0:
        print(f"  Average interval: {temporal_patterns['avg_interval_blocks']:.1f} blocks, "
              f"{temporal_patterns['avg_interval_time']:.0f} seconds")

    print()
    print("NODE CORRELATIONS:")
    print("-" * 40)
    for pair, corr in node_correlations.items():
        print(f"  {pair}: both_high={corr['both_high_count']}, "
              f"avg_diff={corr['avg_difference']:.2f}%")

    print()
    print(f"[+] Full results saved to: {OUTPUT_PATH}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    run_analysis()
