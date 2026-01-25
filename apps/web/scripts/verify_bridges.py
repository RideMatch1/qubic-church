#!/usr/bin/env python3
"""
BRIDGE VERIFICATION SCRIPT
==========================

Verifies Bitcoin and Qubic bridges against their respective blockchains.

- Bitcoin: Uses blockstream.info API
- Qubic: Uses rpc.qubic.org API

Author: qubic-academic-docs
Date: 2026-01-23
"""

import json
import time
import argparse
import random
from pathlib import Path
from typing import Dict, List, Any, Optional
import urllib.request
import urllib.error
from datetime import datetime


def check_btc_address(address: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Check if a Bitcoin address exists on the blockchain.

    Args:
        address: Bitcoin address to check
        timeout: Request timeout in seconds

    Returns:
        Dict with verification results
    """
    url = f"https://blockstream.info/api/address/{address}"

    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; QubicResearch/1.0)'
        })
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = json.loads(response.read().decode())

            return {
                "exists": True,
                "address": address,
                "chain_stats": data.get("chain_stats", {}),
                "mempool_stats": data.get("mempool_stats", {}),
                "funded_txo_count": data.get("chain_stats", {}).get("funded_txo_count", 0),
                "funded_txo_sum": data.get("chain_stats", {}).get("funded_txo_sum", 0),
                "spent_txo_count": data.get("chain_stats", {}).get("spent_txo_count", 0),
                "spent_txo_sum": data.get("chain_stats", {}).get("spent_txo_sum", 0),
                "error": None
            }
    except urllib.error.HTTPError as e:
        if e.code == 400:
            return {
                "exists": False,
                "address": address,
                "error": "Invalid address format"
            }
        return {
            "exists": None,
            "address": address,
            "error": f"HTTP Error {e.code}"
        }
    except urllib.error.URLError as e:
        return {
            "exists": None,
            "address": address,
            "error": f"Network error: {e.reason}"
        }
    except Exception as e:
        return {
            "exists": None,
            "address": address,
            "error": str(e)
        }


def check_qubic_identity(identity: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Check if a Qubic identity exists on the network.

    Args:
        identity: 60-character Qubic identity
        timeout: Request timeout in seconds

    Returns:
        Dict with verification results
    """
    if not identity or len(identity) != 60:
        return {
            "exists": False,
            "identity": identity,
            "error": "Invalid identity format (must be 60 characters)"
        }

    url = f"https://rpc.qubic.org/v1/balances/{identity}"

    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; QubicResearch/1.0)',
            'Accept': 'application/json'
        })
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = json.loads(response.read().decode())

            balance_data = data.get("balance", {})
            return {
                "exists": True,
                "identity": identity,
                "balance": balance_data.get("balance", "0"),
                "valid_for_tick": balance_data.get("validForTick", 0),
                "latest_incoming_transfer_tick": balance_data.get("latestIncomingTransferTick", 0),
                "latest_outgoing_transfer_tick": balance_data.get("latestOutgoingTransferTick", 0),
                "error": None
            }
    except urllib.error.HTTPError as e:
        if e.code == 404:
            # 404 means the identity doesn't have any balance history
            # But it could still be a valid identity
            return {
                "exists": True,  # Identity is valid, just no transactions
                "identity": identity,
                "balance": "0",
                "error": None
            }
        return {
            "exists": None,
            "identity": identity,
            "error": f"HTTP Error {e.code}"
        }
    except urllib.error.URLError as e:
        return {
            "exists": None,
            "identity": identity,
            "error": f"Network error: {e.reason}"
        }
    except Exception as e:
        return {
            "exists": None,
            "identity": identity,
            "error": str(e)
        }


def verify_bridge(bridge: Dict[str, Any], delay: float = 1.0) -> Dict[str, Any]:
    """
    Verify a single bridge against both blockchains.

    Args:
        bridge: Bridge dictionary
        delay: Delay between API calls (seconds)

    Returns:
        Verification result dictionary
    """
    result = {
        "bridge_id": bridge.get("id"),
        "bridge_name": bridge.get("name"),
        "verified_at": datetime.now().isoformat(),
        "bitcoin": None,
        "qubic": None,
        "overall_status": "UNKNOWN"
    }

    # Check Bitcoin
    btc_address = bridge.get("bitcoin", {}).get("address", "")
    if btc_address:
        result["bitcoin"] = check_btc_address(btc_address)
        time.sleep(delay)

    # Check Qubic (XOR seed identity)
    qubic_identity = bridge.get("qubic_xor", {}).get("identity", "")
    if qubic_identity:
        result["qubic"] = check_qubic_identity(qubic_identity)

    # Determine overall status
    btc_exists = result["bitcoin"].get("exists") if result["bitcoin"] else None
    qubic_exists = result["qubic"].get("exists") if result["qubic"] else None

    if btc_exists is True and qubic_exists is True:
        result["overall_status"] = "BOTH_VERIFIED"
    elif btc_exists is True and qubic_exists is None:
        result["overall_status"] = "BTC_ONLY"
    elif btc_exists is None and qubic_exists is True:
        result["overall_status"] = "QUBIC_ONLY"
    elif btc_exists is False or qubic_exists is False:
        result["overall_status"] = "INVALID"
    else:
        result["overall_status"] = "UNKNOWN"

    return result


def verify_sample(bridges: List[Dict[str, Any]],
                  sample_size: int = 10,
                  delay: float = 1.0,
                  verbose: bool = True) -> List[Dict[str, Any]]:
    """
    Verify a random sample of bridges.

    Args:
        bridges: List of all bridges
        sample_size: Number of bridges to verify
        delay: Delay between API calls
        verbose: Print progress

    Returns:
        List of verification results
    """
    # Select random sample
    if sample_size >= len(bridges):
        sample = bridges
    else:
        sample = random.sample(bridges, sample_size)

    results = []

    if verbose:
        print(f"\nVerifying {len(sample)} bridges...")
        print("=" * 60)

    for i, bridge in enumerate(sample):
        if verbose:
            print(f"[{i+1}/{len(sample)}] Verifying: {bridge.get('name', 'Unknown')}")

        result = verify_bridge(bridge, delay)
        results.append(result)

        if verbose:
            status = result["overall_status"]
            btc = "OK" if result["bitcoin"] and result["bitcoin"].get("exists") else "?"
            qubic = "OK" if result["qubic"] and result["qubic"].get("exists") else "?"
            print(f"   BTC: {btc}, Qubic: {qubic} -> {status}")

    return results


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Verify Bitcoin-Qubic bridges")
    parser.add_argument("--sample", type=int, default=10,
                        help="Number of bridges to verify (default: 10)")
    parser.add_argument("--delay", type=float, default=1.0,
                        help="Delay between API calls in seconds (default: 1.0)")
    parser.add_argument("--input", type=str, default="COMPLETE_BRIDGE_DATASET.json",
                        help="Input JSON file with bridges")
    parser.add_argument("--output", type=str, default="VERIFICATION_RESULTS.json",
                        help="Output JSON file for verification results")
    args = parser.parse_args()

    print("=" * 60)
    print("BRIDGE VERIFICATION")
    print("=" * 60)

    # Load bridges
    input_path = Path(__file__).parent / args.input
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        print("Run COMPLETE_BRIDGE_GENERATOR.py first to generate bridges.")
        return

    print(f"\nLoading bridges from: {input_path}")
    with open(input_path, 'r') as f:
        data = json.load(f)

    bridges = data.get("bridges", [])
    print(f"Loaded {len(bridges)} bridges")

    # Verify sample
    results = verify_sample(bridges, args.sample, args.delay, verbose=True)

    # Calculate summary
    summary = {
        "total_verified": len(results),
        "both_verified": sum(1 for r in results if r["overall_status"] == "BOTH_VERIFIED"),
        "btc_only": sum(1 for r in results if r["overall_status"] == "BTC_ONLY"),
        "qubic_only": sum(1 for r in results if r["overall_status"] == "QUBIC_ONLY"),
        "invalid": sum(1 for r in results if r["overall_status"] == "INVALID"),
        "unknown": sum(1 for r in results if r["overall_status"] == "UNKNOWN")
    }

    # Create output
    output = {
        "metadata": {
            "verified_at": datetime.now().isoformat(),
            "input_file": args.input,
            "sample_size": args.sample
        },
        "summary": summary,
        "results": results
    }

    # Save results
    output_path = Path(__file__).parent / args.output
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    # Print summary
    print(f"\n{'=' * 60}")
    print("VERIFICATION SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total verified: {summary['total_verified']}")
    print(f"Both chains verified: {summary['both_verified']}")
    print(f"Bitcoin only: {summary['btc_only']}")
    print(f"Qubic only: {summary['qubic_only']}")
    print(f"Invalid: {summary['invalid']}")
    print(f"Unknown: {summary['unknown']}")
    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
