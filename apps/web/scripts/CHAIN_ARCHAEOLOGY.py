#!/usr/bin/env python3
"""
CHAIN ARCHAEOLOGY - ExtraNonce Miner Fingerprinting
=====================================================

Analyzes Bitcoin coinbase scriptSig data to identify individual miners
by tracking the extraNonce field progression, exactly like the research at:
https://bitcointalk.org/index.php?topic=507458.0

The early Bitcoin mining code (v0.1) incremented extraNonce monotonically
until the application was restarted. A reset/drop in extraNonce indicates
a new mining session (possibly a different miner or a client restart).

Coinbase ScriptSig structure (early blocks):
  [push nBits] [push extraNonce]
  04 ffff001d  02 XXYY          (XX YY = extraNonce, little-endian)

This script:
1. Parses extraNonce from scan results
2. Detects mining session boundaries
3. Groups blocks into miner sessions
4. Identifies known miners (Satoshi pattern, etc.)
5. Exports data for visualization

Usage:
    python3 CHAIN_ARCHAEOLOGY.py --input block-scan-results/blocks_9000_10000.json
    python3 CHAIN_ARCHAEOLOGY.py --input block-scan-results/blocks_9000_10000.json --plot

Author: Claude Code (Senior Developer Agent)
Date: 2026-02-26
"""

import json
import csv
import argparse
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

OUTPUT_DIR = Path(__file__).parent / "block-scan-results"


# ==============================================================================
# EXTRANONCE PARSER
# ==============================================================================

def parse_extranonce(scriptsig_hex: str) -> Dict:
    """
    Parse the extraNonce from early Bitcoin coinbase scriptSig.

    Early Bitcoin coinbase structure:
      04 ffff001d  XX YYYY...
      ^            ^  ^
      |            |  +-- extraNonce bytes (little-endian)
      |            +-- push length for extraNonce
      +-- push 4 bytes of nBits

    Later (after block ~200k), the structure changes to include block height
    per BIP 34.

    Returns dict with:
      - extranonce_int: integer value of extraNonce
      - extranonce_hex: hex string of extraNonce bytes
      - extranonce_bytes: raw bytes count
      - nbits_hex: the nBits field
      - structure: description of the parsed structure
    """
    result = {
        "extranonce_int": None,
        "extranonce_hex": "",
        "extranonce_bytes": 0,
        "nbits_hex": "",
        "full_hex": scriptsig_hex,
        "parse_method": "unknown",
    }

    if not scriptsig_hex or len(scriptsig_hex) < 4:
        return result

    try:
        raw = bytes.fromhex(scriptsig_hex)
    except ValueError:
        return result

    pos = 0

    # --- Parse first push (usually nBits) ---
    if pos >= len(raw):
        return result

    first_push_len = raw[pos]
    pos += 1

    if first_push_len <= 75 and pos + first_push_len <= len(raw):
        nbits_data = raw[pos:pos + first_push_len]
        result["nbits_hex"] = nbits_data.hex()
        pos += first_push_len
    else:
        return result

    # --- Parse second push (extraNonce) ---
    if pos >= len(raw):
        # No extraNonce (e.g., genesis block)
        result["extranonce_int"] = 0
        result["parse_method"] = "no_extranonce"
        return result

    second_push_len = raw[pos]
    pos += 1

    if second_push_len <= 75 and pos + second_push_len <= len(raw):
        extranonce_data = raw[pos:pos + second_push_len]
        result["extranonce_hex"] = extranonce_data.hex()
        result["extranonce_bytes"] = second_push_len

        # Convert to integer (little-endian, as used in early Bitcoin)
        extranonce_int = int.from_bytes(extranonce_data, byteorder='little')
        result["extranonce_int"] = extranonce_int
        result["parse_method"] = "standard_v01"
    else:
        # Might be a different format - try to read remaining as extraNonce
        remaining = raw[pos - 1:]  # include the length byte
        result["extranonce_hex"] = remaining.hex()
        result["extranonce_bytes"] = len(remaining)
        result["extranonce_int"] = int.from_bytes(remaining, byteorder='little')
        result["parse_method"] = "fallback"

    # --- Check for additional data after extraNonce (later blocks) ---
    end_pos = pos + (second_push_len if second_push_len <= 75 else 0)
    if end_pos < len(raw):
        extra_data = raw[end_pos:]
        result["trailing_data_hex"] = extra_data.hex()
        try:
            result["trailing_data_ascii"] = extra_data.decode('ascii', errors='replace')
        except:
            pass

    return result


# ==============================================================================
# SESSION DETECTOR
# ==============================================================================

def detect_sessions(blocks: List[Dict], reset_threshold: float = 0.5) -> List[Dict]:
    """
    Detect mining sessions by finding extraNonce resets.

    A new session starts when:
    1. ExtraNonce drops significantly (> reset_threshold of previous value)
    2. ExtraNonce resets to a very low value
    3. There's a large gap between consecutive blocks mined by the same entity

    Args:
        blocks: sorted list of block dicts with extranonce_int
        reset_threshold: fraction drop that triggers new session (0.5 = 50% drop)

    Returns:
        List of session dicts with start/end blocks and characteristics
    """
    if not blocks:
        return []

    sessions = []
    current_session = {
        "start_block": blocks[0]["height"],
        "end_block": blocks[0]["height"],
        "blocks": [blocks[0]],
        "start_extranonce": blocks[0].get("extranonce_int", 0),
        "max_extranonce": blocks[0].get("extranonce_int", 0),
        "min_extranonce": blocks[0].get("extranonce_int", 0),
    }

    for i in range(1, len(blocks)):
        block = blocks[i]
        prev_block = blocks[i - 1]

        curr_en = block.get("extranonce_int")
        prev_en = prev_block.get("extranonce_int")

        if curr_en is None or prev_en is None:
            continue

        # Detect session break
        is_reset = False
        reason = ""

        # 1. Significant drop in extraNonce
        if prev_en > 0 and curr_en < prev_en * (1 - reset_threshold):
            is_reset = True
            reason = f"drop {prev_en}->{curr_en}"

        # 2. ExtraNonce resets to very low value (< 10) after being high
        if curr_en < 10 and prev_en > 50:
            is_reset = True
            reason = f"reset to {curr_en}"

        # 3. Large block gap (>20 blocks) with extraNonce discontinuity
        block_gap = block["height"] - prev_block["height"]
        if block_gap > 20 and abs(curr_en - prev_en) > 100:
            is_reset = True
            reason = f"gap={block_gap} blocks, en jump {prev_en}->{curr_en}"

        if is_reset:
            # Close current session
            current_session["end_block"] = prev_block["height"]
            current_session["block_count"] = len(current_session["blocks"])
            current_session["extranonce_range"] = (
                current_session["min_extranonce"],
                current_session["max_extranonce"]
            )
            current_session["break_reason"] = reason
            sessions.append(current_session)

            # Start new session
            current_session = {
                "start_block": block["height"],
                "end_block": block["height"],
                "blocks": [block],
                "start_extranonce": curr_en,
                "max_extranonce": curr_en,
                "min_extranonce": curr_en,
            }
        else:
            # Continue session
            current_session["blocks"].append(block)
            current_session["end_block"] = block["height"]
            if curr_en is not None:
                current_session["max_extranonce"] = max(
                    current_session["max_extranonce"] or 0, curr_en
                )
                current_session["min_extranonce"] = min(
                    current_session["min_extranonce"] or curr_en, curr_en
                )

    # Close last session
    current_session["block_count"] = len(current_session["blocks"])
    current_session["extranonce_range"] = (
        current_session["min_extranonce"],
        current_session["max_extranonce"]
    )
    current_session["break_reason"] = "end_of_range"
    sessions.append(current_session)

    return sessions


# ==============================================================================
# MINER IDENTIFICATION
# ==============================================================================

def identify_miner_patterns(sessions: List[Dict]) -> List[Dict]:
    """
    Try to identify known miner patterns.

    Known patterns from Chain Archaeology research:
    - Satoshi (Patoshi): consistent incremental extraNonce, specific nonce patterns
    - Hal Finney: identified around block 78
    - Other early miners: various patterns

    For blocks 9000-10000 (~March 2009), mostly Satoshi was mining.
    """
    for session in sessions:
        blocks = session.get("blocks", [])
        if not blocks:
            continue

        # Check extraNonce monotonicity (Satoshi pattern)
        extranonces = [b.get("extranonce_int", 0) for b in blocks if b.get("extranonce_int") is not None]
        if len(extranonces) < 2:
            session["pattern"] = "single_block"
            session["likely_miner"] = "unknown"
            continue

        # Count how many times extraNonce strictly increases
        increases = sum(1 for i in range(1, len(extranonces)) if extranonces[i] > extranonces[i-1])
        monotonic_ratio = increases / (len(extranonces) - 1) if len(extranonces) > 1 else 0

        session["monotonic_ratio"] = round(monotonic_ratio, 3)
        session["avg_extranonce_step"] = round(
            sum(extranonces[i] - extranonces[i-1] for i in range(1, len(extranonces))) / (len(extranonces) - 1),
            2
        ) if len(extranonces) > 1 else 0

        # Classify
        if monotonic_ratio > 0.8:
            session["pattern"] = "monotonic_increasing"
            session["likely_miner"] = "satoshi_pattern"
        elif monotonic_ratio > 0.5:
            session["pattern"] = "mostly_increasing"
            session["likely_miner"] = "likely_satoshi"
        else:
            session["pattern"] = "non_monotonic"
            session["likely_miner"] = "unknown_miner"

    return sessions


# ==============================================================================
# MAIN ANALYSIS
# ==============================================================================

def analyze(input_file: Path) -> Dict:
    """Run the full Chain Archaeology analysis."""
    print("=" * 70)
    print("CHAIN ARCHAEOLOGY - ExtraNonce Miner Fingerprinting")
    print("=" * 70)

    # Load scan results
    print(f"\nLoading: {input_file}")
    with open(input_file, "r") as f:
        scan_data = json.load(f)

    blocks_raw = scan_data.get("blocks", {})
    scan_range = scan_data.get("scan_range", {})
    print(f"Block range: {scan_range.get('start', '?')} - {scan_range.get('end', '?')}")
    print(f"Blocks loaded: {len(blocks_raw)}")

    # Parse extraNonce for each block
    print("\nParsing extraNonce values...")
    blocks = []
    parse_failures = 0

    for height_str in sorted(blocks_raw.keys(), key=int):
        block_data = blocks_raw[height_str]
        coinbase = block_data.get("coinbase", {})
        scriptsig = coinbase.get("scriptsig_hex", "")

        en = parse_extranonce(scriptsig)

        blocks.append({
            "height": block_data["height"],
            "hash": block_data.get("hash", ""),
            "timestamp": block_data.get("timestamp", 0),
            "date": block_data.get("date", ""),
            "nonce": block_data.get("nonce", 0),
            "tx_count": block_data.get("tx_count", 0),
            "scriptsig_hex": scriptsig,
            "extranonce_int": en["extranonce_int"],
            "extranonce_hex": en["extranonce_hex"],
            "extranonce_bytes": en["extranonce_bytes"],
            "nbits_hex": en["nbits_hex"],
            "parse_method": en["parse_method"],
            "trailing_data": en.get("trailing_data_ascii", ""),
        })

        if en["extranonce_int"] is None:
            parse_failures += 1

    print(f"Parsed: {len(blocks)} blocks ({parse_failures} parse failures)")

    # Show extraNonce range
    valid_en = [b["extranonce_int"] for b in blocks if b["extranonce_int"] is not None]
    if valid_en:
        print(f"ExtraNonce range: {min(valid_en)} - {max(valid_en)}")

    # Detect sessions
    print("\nDetecting mining sessions...")
    sessions = detect_sessions(blocks)
    sessions = identify_miner_patterns(sessions)
    print(f"Sessions found: {len(sessions)}")

    # Print session summary
    print("\n" + "=" * 70)
    print("MINING SESSIONS")
    print("=" * 70)
    print(f"{'#':>3} | {'Start':>6}-{'End':>6} | {'Blocks':>6} | {'ExtraNonce Range':>20} | {'Pattern':>20} | {'Miner':>16}")
    print("-" * 95)

    for i, session in enumerate(sessions):
        en_range = session.get("extranonce_range", (0, 0))
        # Don't include the full blocks list in the output
        block_count = session.get("block_count", len(session.get("blocks", [])))
        print(
            f"{i+1:3d} | {session['start_block']:>6}-{session['end_block']:>6} | "
            f"{block_count:>6} | "
            f"{en_range[0]:>8} - {en_range[1]:<8} | "
            f"{session.get('pattern', 'n/a'):>20} | "
            f"{session.get('likely_miner', 'n/a'):>16}"
        )

    # Block-level statistics
    print("\n" + "=" * 70)
    print("EXTRANONCE PROGRESSION (sampled every 50 blocks)")
    print("=" * 70)
    print(f"{'Block':>7} | {'ExtraNonce':>10} | {'Hex':>12} | {'nBits':>10} | {'Date':>12} | Bar")
    print("-" * 85)

    max_en = max(valid_en) if valid_en else 1
    for block in blocks:
        if block["height"] % 50 == 0 or block["height"] == blocks[0]["height"] or block["height"] == blocks[-1]["height"]:
            en = block["extranonce_int"]
            bar_len = int((en / max_en) * 40) if en and max_en > 0 else 0
            bar = "#" * bar_len
            date_short = block["date"][:10] if block["date"] else ""
            print(
                f"{block['height']:>7} | {en or 0:>10} | {block['extranonce_hex']:>12} | "
                f"{block['nbits_hex']:>10} | {date_short:>12} | {bar}"
            )

    # Interesting blocks (extraNonce anomalies)
    print("\n" + "=" * 70)
    print("NOTABLE BLOCKS (extraNonce drops/anomalies)")
    print("=" * 70)

    for i in range(1, len(blocks)):
        curr_en = blocks[i].get("extranonce_int")
        prev_en = blocks[i-1].get("extranonce_int")

        if curr_en is None or prev_en is None:
            continue

        # Significant drop
        if prev_en > 0 and curr_en < prev_en * 0.5:
            print(f"  Block {blocks[i]['height']}: ExtraNonce DROP {prev_en} -> {curr_en} (session break?)")

        # Large jump (>1000)
        elif curr_en - prev_en > 1000:
            print(f"  Block {blocks[i]['height']}: ExtraNonce JUMP {prev_en} -> {curr_en} (+{curr_en - prev_en})")

        # Reset to low value
        elif curr_en < 5 and prev_en > 20:
            print(f"  Block {blocks[i]['height']}: ExtraNonce RESET to {curr_en} (from {prev_en})")

    # Build results
    results = {
        "scan_range": scan_range,
        "total_blocks": len(blocks),
        "parse_failures": parse_failures,
        "extranonce_stats": {
            "min": min(valid_en) if valid_en else None,
            "max": max(valid_en) if valid_en else None,
            "mean": round(sum(valid_en) / len(valid_en), 2) if valid_en else None,
        },
        "sessions": [
            {
                "id": i + 1,
                "start_block": s["start_block"],
                "end_block": s["end_block"],
                "block_count": s.get("block_count", len(s.get("blocks", []))),
                "extranonce_range": s.get("extranonce_range"),
                "pattern": s.get("pattern"),
                "likely_miner": s.get("likely_miner"),
                "monotonic_ratio": s.get("monotonic_ratio"),
                "avg_extranonce_step": s.get("avg_extranonce_step"),
                "break_reason": s.get("break_reason"),
            }
            for i, s in enumerate(sessions)
        ],
        "blocks": [
            {
                "height": b["height"],
                "timestamp": b["timestamp"],
                "date": b["date"],
                "nonce": b["nonce"],
                "extranonce_int": b["extranonce_int"],
                "extranonce_hex": b["extranonce_hex"],
                "nbits_hex": b["nbits_hex"],
                "parse_method": b["parse_method"],
            }
            for b in blocks
        ],
    }

    return results


def export_results(results: Dict, output_dir: Path):
    """Export analysis results to JSON and CSV."""
    output_dir.mkdir(parents=True, exist_ok=True)

    start = results["scan_range"].get("start", 0)
    end = results["scan_range"].get("end", 0)

    # JSON
    json_file = output_dir / f"archaeology_{start}_{end}.json"
    with open(json_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nJSON saved: {json_file}")

    # CSV - block level (for spreadsheet analysis like the bitcointalk thread)
    csv_file = output_dir / f"archaeology_{start}_{end}.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Block", "Date", "Nonce", "ExtraNonce", "ExtraNonce_Hex",
            "nBits", "Parse_Method"
        ])
        for b in results["blocks"]:
            writer.writerow([
                b["height"],
                b["date"][:10] if b["date"] else "",
                b["nonce"],
                b["extranonce_int"],
                b["extranonce_hex"],
                b["nbits_hex"],
                b["parse_method"],
            ])
    print(f"CSV saved: {csv_file}")

    # CSV - sessions
    sessions_csv = output_dir / f"sessions_{start}_{end}.csv"
    with open(sessions_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Session", "Start_Block", "End_Block", "Block_Count",
            "EN_Min", "EN_Max", "Pattern", "Likely_Miner",
            "Monotonic_Ratio", "Avg_Step", "Break_Reason"
        ])
        for s in results["sessions"]:
            en_range = s.get("extranonce_range", (None, None))
            writer.writerow([
                s["id"],
                s["start_block"],
                s["end_block"],
                s["block_count"],
                en_range[0] if en_range else "",
                en_range[1] if en_range else "",
                s.get("pattern", ""),
                s.get("likely_miner", ""),
                s.get("monotonic_ratio", ""),
                s.get("avg_extranonce_step", ""),
                s.get("break_reason", ""),
            ])
    print(f"Sessions CSV saved: {sessions_csv}")

    # Gnuplot / matplotlib-compatible data file
    dat_file = output_dir / f"extranonce_{start}_{end}.dat"
    with open(dat_file, "w") as f:
        f.write("# Block ExtraNonce Nonce\n")
        for b in results["blocks"]:
            en = b["extranonce_int"] if b["extranonce_int"] is not None else 0
            f.write(f"{b['height']} {en} {b['nonce']}\n")
    print(f"Plot data saved: {dat_file}")


def try_plot(results: Dict, output_dir: Path):
    """Try to generate a matplotlib plot (optional)."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        start = results["scan_range"].get("start", 0)
        end = results["scan_range"].get("end", 0)

        heights = [b["height"] for b in results["blocks"]]
        extranonces = [b["extranonce_int"] or 0 for b in results["blocks"]]

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), sharex=True)

        # ExtraNonce progression
        ax1.scatter(heights, extranonces, s=2, alpha=0.7, c='blue')
        ax1.set_ylabel("ExtraNonce")
        ax1.set_title(f"Chain Archaeology: ExtraNonce Progression (Blocks {start}-{end})")
        ax1.grid(True, alpha=0.3)

        # Mark session boundaries
        for s in results["sessions"]:
            ax1.axvline(x=s["start_block"], color='red', alpha=0.3, linestyle='--')

        # Block nonce (secondary pattern)
        nonces = [b["nonce"] for b in results["blocks"]]
        ax2.scatter(heights, nonces, s=2, alpha=0.5, c='green')
        ax2.set_xlabel("Block Height")
        ax2.set_ylabel("Block Nonce")
        ax2.set_title("Block Nonce Distribution")
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        plot_file = output_dir / f"archaeology_{start}_{end}.png"
        plt.savefig(plot_file, dpi=150)
        plt.close()
        print(f"Plot saved: {plot_file}")

    except ImportError:
        print("(matplotlib not available - skipping plot)")
    except Exception as e:
        print(f"(Plot error: {e})")


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chain Archaeology - ExtraNonce Analysis")
    parser.add_argument("--input", type=str, required=True, help="Input JSON from BLOCK_RANGE_SCANNER.py")
    parser.add_argument("--plot", action="store_true", help="Generate matplotlib plot")
    parser.add_argument("--output", type=str, default=None, help="Output directory (default: same as input)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: {input_path} not found")
        sys.exit(1)

    output_path = Path(args.output) if args.output else input_path.parent

    results = analyze(input_path)
    export_results(results, output_path)

    if args.plot:
        try_plot(results, output_path)

    print("\nDone!")
