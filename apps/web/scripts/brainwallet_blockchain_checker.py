"""
Brainwallet Blockchain Checker - Unified Academic Research Tool

Combines passphrase generation, Bitcoin address derivation, and blockchain
balance checking into a single pipeline. Generates candidate passphrases,
derives their corresponding Bitcoin addresses, and queries the Blockstream
API to check for historical transaction activity.

This tool merges functionality from:
  - brainwallet_analysis.py (address derivation pipeline)
  - brainwallet_passphrase_generator.py (mutation strategies)
  - brainwallet_retrospective_analysis.py (blockchain queries)

References:
  - Castellucci, R. (2013). "Cracking Cryptocurrency Brainwallets"
  - Vasek, M. et al. (2016). "The Bitcoin Brain Drain"

Data source: Blockstream public API (blockstream.info/api)

Usage:
  python brainwallet_blockchain_checker.py
  python brainwallet_blockchain_checker.py --phrases "password" "hello" "bitcoin"
  python brainwallet_blockchain_checker.py --file phrases.txt
  python brainwallet_blockchain_checker.py --no-mutations
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterator, NamedTuple


# ============================================================================
# PART 1: Cryptographic Primitives & Address Derivation
# (from brainwallet_analysis.py)
# ============================================================================

BITCOIN_MAINNET_VERSION = b"\x00"
BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


class BrainwalletResult(NamedTuple):
    """Result of a brainwallet derivation."""
    passphrase: str
    private_key_hex: str
    public_key_compressed_hex: str
    public_key_uncompressed_hex: str
    address_compressed: str
    address_uncompressed: str


def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def hash160(data: bytes) -> bytes:
    return hashlib.new("ripemd160", sha256(data)).digest()


def double_sha256(data: bytes) -> bytes:
    return sha256(sha256(data))


def base58encode(payload: bytes) -> str:
    n = int.from_bytes(payload, "big")
    result = []
    while n > 0:
        n, remainder = divmod(n, 58)
        result.append(BASE58_ALPHABET[remainder])
    for byte in payload:
        if byte == 0:
            result.append("1")
        else:
            break
    return "".join(reversed(result))


def base58check_encode(version: bytes, payload: bytes) -> str:
    versioned = version + payload
    checksum = double_sha256(versioned)[:4]
    return base58encode(versioned + checksum)


def passphrase_to_private_key(passphrase: str) -> bytes:
    """SHA-256(passphrase) -> private key. Intentionally insecure (brainwallet method)."""
    return sha256(passphrase.encode("utf-8"))


def private_key_to_public_key(private_key: bytes, compressed: bool = True) -> bytes:
    """Derive public key from private key using secp256k1."""
    from ecdsa import SECP256k1, SigningKey
    signing_key = SigningKey.from_string(private_key, curve=SECP256k1)
    verifying_key = signing_key.get_verifying_key()
    if compressed:
        x = verifying_key.pubkey.point.x()
        y = verifying_key.pubkey.point.y()
        prefix = b"\x02" if y % 2 == 0 else b"\x03"
        return prefix + x.to_bytes(32, "big")
    else:
        return b"\x04" + verifying_key.to_string()


def public_key_to_address(public_key: bytes) -> str:
    h160 = hash160(public_key)
    return base58check_encode(BITCOIN_MAINNET_VERSION, h160)


def derive_brainwallet(passphrase: str) -> BrainwalletResult:
    """Full pipeline: passphrase -> SHA-256 -> privkey -> pubkey -> P2PKH address."""
    private_key = passphrase_to_private_key(passphrase)
    pub_compressed = private_key_to_public_key(private_key, compressed=True)
    pub_uncompressed = private_key_to_public_key(private_key, compressed=False)
    addr_compressed = public_key_to_address(pub_compressed)
    addr_uncompressed = public_key_to_address(pub_uncompressed)
    return BrainwalletResult(
        passphrase=passphrase,
        private_key_hex=private_key.hex(),
        public_key_compressed_hex=pub_compressed.hex(),
        public_key_uncompressed_hex=pub_uncompressed.hex(),
        address_compressed=addr_compressed,
        address_uncompressed=addr_uncompressed,
    )


# ============================================================================
# PART 2: Passphrase Mutation Engine
# (from brainwallet_passphrase_generator.py)
# ============================================================================

LEET_MAP: dict[str, list[str]] = {
    "a": ["@", "4"], "e": ["3"], "i": ["1", "!"],
    "o": ["0"], "s": ["$", "5"], "t": ["7"], "l": ["1"],
}

COMMON_SUFFIXES = [
    "", "1", "12", "123", "1234",
    "!", "!!", "!!!", "?", ".", "..", "...",
    "#", "$", "*", "2024", "2025", "2026",
    "btc", "BTC", "bitcoin", "Bitcoin",
]

COMMON_PREFIXES = ["", "the ", "The ", "my ", "My "]


def _normalize_whitespace(phrase: str) -> Iterator[str]:
    stripped = phrase.strip()
    yield stripped
    no_spaces = stripped.replace(" ", "")
    if no_spaces != stripped:
        yield no_spaces
    single_spaced = re.sub(r"\s+", " ", stripped)
    if single_spaced != stripped:
        yield single_spaced
    yield stripped.replace(" ", "_")
    yield stripped.replace(" ", "-")


def _case_variants(phrase: str) -> Iterator[str]:
    yield phrase
    yield phrase.lower()
    yield phrase.upper()
    yield phrase.capitalize()
    yield phrase.title()
    if len(phrase) > 0:
        yield phrase[0].lower() + phrase[1:]


def _suffix_variants(phrase: str) -> Iterator[str]:
    for suffix in COMMON_SUFFIXES:
        yield phrase + suffix


def _prefix_variants(phrase: str) -> Iterator[str]:
    for prefix in COMMON_PREFIXES:
        yield prefix + phrase


def _punctuation_variants(phrase: str) -> Iterator[str]:
    yield phrase
    no_punct = re.sub(r"[^\w\s]", "", phrase)
    if no_punct != phrase:
        yield no_punct
    stripped = phrase.rstrip(".,!?;:'\"")
    if stripped != phrase:
        yield stripped


def _leet_speak(phrase: str) -> Iterator[str]:
    lower = phrase.lower()
    yield lower
    for char, replacements in LEET_MAP.items():
        if char in lower:
            for replacement in replacements:
                yield lower.replace(char, replacement)


def generate_mutations(phrase: str) -> list[str]:
    """Generate all passphrase mutations for a given input phrase."""
    candidates: set[str] = set()
    for ws_variant in _normalize_whitespace(phrase):
        for case_variant in _case_variants(ws_variant):
            for punct_variant in _punctuation_variants(case_variant):
                candidates.add(punct_variant)
                for suffix_variant in _suffix_variants(punct_variant):
                    candidates.add(suffix_variant)
    for leet_variant in _leet_speak(phrase):
        candidates.add(leet_variant)
    for prefix_variant in _prefix_variants(phrase):
        candidates.add(prefix_variant)
    for prefix_variant in _prefix_variants(phrase.lower()):
        candidates.add(prefix_variant)
    return sorted(candidates)


# ============================================================================
# PART 3: Blockchain API Client
# (from brainwallet_retrospective_analysis.py, extended)
# ============================================================================

BLOCKSTREAM_API = "https://blockstream.info/api"
REQUEST_DELAY_S = 0.5


@dataclass
class AddressInfo:
    """Parsed address data from the Blockstream API."""
    address: str
    total_received_sat: int = 0
    total_sent_sat: int = 0
    tx_count: int = 0
    current_balance_sat: int = 0
    first_seen: datetime | None = None
    first_drain: datetime | None = None
    drain_delay_seconds: int | None = None
    error: str | None = None


def _api_get(endpoint: str) -> Any:
    """GET request to Blockstream API with error handling and rate-limit retry."""
    url = f"{BLOCKSTREAM_API}/{endpoint}"
    req = urllib.request.Request(url, headers={"User-Agent": "BrainwalletResearch/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 429:
            time.sleep(5)
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode())
        raise
    except urllib.error.URLError as e:
        raise ConnectionError(f"API request failed: {e}") from e


def fetch_address_info(address: str) -> AddressInfo:
    """Fetch address summary and basic transaction data from Blockstream."""
    info = AddressInfo(address=address)
    try:
        summary = _api_get(f"address/{address}")
        chain = summary.get("chain_stats", {})
        mempool = summary.get("mempool_stats", {})
        info.total_received_sat = chain.get("funded_txo_sum", 0)
        info.total_sent_sat = chain.get("spent_txo_sum", 0)
        info.tx_count = chain.get("tx_count", 0) + mempool.get("tx_count", 0)
        info.current_balance_sat = info.total_received_sat - info.total_sent_sat
        time.sleep(REQUEST_DELAY_S)

        if info.tx_count > 0:
            txs = _api_get(f"address/{address}/txs")
            timestamps = []
            for tx in txs:
                if tx.get("status", {}).get("confirmed"):
                    bt = tx["status"].get("block_time")
                    if bt:
                        timestamps.append(bt)
            if timestamps:
                info.first_seen = datetime.fromtimestamp(min(timestamps), tz=timezone.utc)
                for tx in txs:
                    is_outgoing = any(
                        vin.get("prevout", {}).get("scriptpubkey_address") == address
                        for vin in tx.get("vin", [])
                    )
                    if is_outgoing and tx.get("status", {}).get("block_time"):
                        info.first_drain = datetime.fromtimestamp(
                            tx["status"]["block_time"], tz=timezone.utc
                        )
                if info.first_seen and info.first_drain:
                    delta = info.first_drain.timestamp() - info.first_seen.timestamp()
                    info.drain_delay_seconds = int(abs(delta))
            time.sleep(REQUEST_DELAY_S)
    except Exception as e:
        info.error = str(e)
    return info


def sat_to_btc(sat: int) -> str:
    return f"{sat / 1e8:.8f}"


def format_duration(seconds: int | None) -> str:
    if seconds is None:
        return "N/A"
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    if seconds < 86400:
        return f"{seconds // 3600}h {(seconds % 3600) // 60}m"
    return f"{seconds // 86400}d {(seconds % 86400) // 3600}h"


# ============================================================================
# PART 4: Unified Pipeline - Generate, Derive, Check
# ============================================================================

@dataclass
class CheckResult:
    """Result of checking one passphrase against the blockchain."""
    passphrase: str
    address_compressed: str
    address_uncompressed: str
    private_key_hex: str
    compressed_info: AddressInfo | None = None
    uncompressed_info: AddressInfo | None = None

    @property
    def has_activity(self) -> bool:
        c = self.compressed_info
        u = self.uncompressed_info
        c_active = c is not None and c.tx_count > 0
        u_active = u is not None and u.tx_count > 0
        return c_active or u_active

    @property
    def total_received_sat(self) -> int:
        total = 0
        if self.compressed_info:
            total += self.compressed_info.total_received_sat
        if self.uncompressed_info:
            total += self.uncompressed_info.total_received_sat
        return total


def check_passphrase(passphrase: str, check_both: bool = True) -> CheckResult:
    """Derive addresses from passphrase and check blockchain activity."""
    bw = derive_brainwallet(passphrase)
    result = CheckResult(
        passphrase=passphrase,
        address_compressed=bw.address_compressed,
        address_uncompressed=bw.address_uncompressed,
        private_key_hex=bw.private_key_hex,
    )
    # Always check uncompressed (historical brainwallets used uncompressed)
    result.uncompressed_info = fetch_address_info(bw.address_uncompressed)
    # Optionally check compressed too (modern tools use compressed)
    if check_both:
        result.compressed_info = fetch_address_info(bw.address_compressed)
    return result


def run_pipeline(
    base_phrases: list[str],
    use_mutations: bool = True,
    check_both_formats: bool = True,
    max_mutations_per_phrase: int = 50,
    output_csv: str | None = None,
) -> list[CheckResult]:
    """
    Full pipeline: take base phrases, optionally mutate them,
    derive addresses, and check blockchain for activity.
    """
    print("=" * 72)
    print("Brainwallet Blockchain Checker")
    print("Unified Academic Research Tool")
    print("=" * 72)

    # Step 1: Build candidate list
    all_candidates: list[str] = []
    if use_mutations:
        print(f"\n[1] Generating mutations for {len(base_phrases)} base phrase(s)...\n")
        for phrase in base_phrases:
            mutations = generate_mutations(phrase)
            limited = mutations[:max_mutations_per_phrase]
            print(f"  '{phrase}' -> {len(mutations)} mutations"
                  f" (using first {len(limited)})")
            all_candidates.extend(limited)
    else:
        print(f"\n[1] Using {len(base_phrases)} phrase(s) without mutations.\n")
        all_candidates = list(base_phrases)

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for c in all_candidates:
        if c not in seen:
            seen.add(c)
            unique.append(c)
    all_candidates = unique

    print(f"\n  Total unique candidates: {len(all_candidates)}")
    addr_format = "compressed + uncompressed" if check_both_formats else "uncompressed only"
    print(f"  Address format: {addr_format}")
    api_calls = len(all_candidates) * (2 if check_both_formats else 1)
    est_time = api_calls * (REQUEST_DELAY_S + 0.3)
    print(f"  Estimated API calls: {api_calls}")
    print(f"  Estimated time: ~{int(est_time)}s ({est_time/60:.1f} min)")

    # Step 2: Derive and check
    print(f"\n[2] Checking addresses on blockchain...\n")
    results: list[CheckResult] = []
    hits: list[CheckResult] = []

    for i, passphrase in enumerate(all_candidates):
        display = repr(passphrase) if len(passphrase) < 40 else repr(passphrase[:37] + "...")
        sys.stdout.write(f"\r  [{i+1}/{len(all_candidates)}] Checking {display}...")
        sys.stdout.flush()

        cr = check_passphrase(passphrase, check_both=check_both_formats)
        results.append(cr)

        if cr.has_activity:
            hits.append(cr)
            sys.stdout.write(f"\r  [{i+1}/{len(all_candidates)}] ** HIT ** {display}"
                           f" - {sat_to_btc(cr.total_received_sat)} BTC received\n")
            sys.stdout.flush()

    print(f"\r  Done. Checked {len(all_candidates)} passphrases."
          + " " * 40)

    # Step 3: Report
    print(f"\n[3] Results\n")
    print("-" * 72)

    if not hits:
        print("  No addresses with blockchain activity found.")
        print("  (This is expected for novel/random passphrases.)")
    else:
        print(f"  FOUND {len(hits)} address(es) with blockchain activity:\n")
        header = (f"  {'Passphrase':<30} {'Address':<36} {'Txs':>5} "
                  f"{'Received (BTC)':>16} {'Balance':>14} {'Drain':>10}")
        print(header)
        print("  " + "-" * (len(header) - 2))

        for cr in hits:
            for label, info in [("uncompr", cr.uncompressed_info),
                                ("compr", cr.compressed_info)]:
                if info and info.tx_count > 0:
                    pp = cr.passphrase if len(cr.passphrase) < 28 else cr.passphrase[:25] + "..."
                    drain = format_duration(info.drain_delay_seconds)
                    print(f"  {pp:<30} {info.address[:34]:<36} "
                          f"{info.tx_count:>5} "
                          f"{sat_to_btc(info.total_received_sat):>16} "
                          f"{sat_to_btc(info.current_balance_sat):>14} "
                          f"{drain:>10}")

    # Aggregate stats
    total_received = sum(r.total_received_sat for r in hits)
    total_txs = sum(
        (r.compressed_info.tx_count if r.compressed_info else 0)
        + (r.uncompressed_info.tx_count if r.uncompressed_info else 0)
        for r in hits
    )

    print(f"\n" + "-" * 72)
    print("AGGREGATE STATISTICS")
    print("-" * 72)
    print(f"  Passphrases checked:     {len(all_candidates)}")
    print(f"  Addresses with activity: {len(hits)}")
    print(f"  Total transactions:      {total_txs}")
    print(f"  Total BTC received:      {sat_to_btc(total_received)}")
    print(f"  Hit rate:                {len(hits)/len(all_candidates)*100:.2f}%")

    # Step 4: CSV export
    if output_csv:
        _export_csv(output_csv, results)
        print(f"\n  Results exported to: {output_csv}")

    print("\n" + "=" * 72)
    print("NOTE: Brainwallets are fundamentally insecure. This tool exists")
    print("solely for academic analysis. Never use brainwallets for real funds.")
    print("=" * 72)

    return results


def _export_csv(path: str, results: list[CheckResult]) -> None:
    """Export all results to CSV for further analysis."""
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "passphrase", "private_key_hex",
            "address_uncompressed", "uncompr_tx_count",
            "uncompr_received_btc", "uncompr_balance_btc",
            "address_compressed", "compr_tx_count",
            "compr_received_btc", "compr_balance_btc",
            "has_activity",
        ])
        for r in results:
            u = r.uncompressed_info
            c = r.compressed_info
            writer.writerow([
                r.passphrase, r.private_key_hex,
                r.address_uncompressed,
                u.tx_count if u else 0,
                sat_to_btc(u.total_received_sat) if u else "0",
                sat_to_btc(u.current_balance_sat) if u else "0",
                r.address_compressed,
                c.tx_count if c else 0,
                sat_to_btc(c.total_received_sat) if c else "0",
                sat_to_btc(c.current_balance_sat) if c else "0",
                r.has_activity,
            ])


# ============================================================================
# PART 5: CLI Interface
# ============================================================================

DEFAULT_PHRASES = [
    "",
    "password",
    "hello",
    "bitcoin",
    "satoshi",
    "correct horse battery staple",
    "To be or not to be",
    "I think therefore I am",
    "Let there be light",
    "In the beginning",
    "1",
    "cat",
    "sausage",
    "brainwallet",
]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Brainwallet Blockchain Checker - Academic Research Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Check default known-weak passphrases
  %(prog)s --phrases "password" "test"        # Check specific phrases
  %(prog)s --file phrases.txt                 # Read phrases from file (one per line)
  %(prog)s --no-mutations                     # Skip mutation generation
  %(prog)s --max-mutations 20                 # Limit mutations per phrase
  %(prog)s --csv results.csv                  # Export results to CSV
  %(prog)s --uncompressed-only                # Only check uncompressed addresses
        """,
    )
    parser.add_argument(
        "--phrases", nargs="+", default=None,
        help="Passphrases to check (overrides defaults)",
    )
    parser.add_argument(
        "--file", type=str, default=None,
        help="Read passphrases from file (one per line)",
    )
    parser.add_argument(
        "--no-mutations", action="store_true",
        help="Disable mutation generation, check phrases as-is",
    )
    parser.add_argument(
        "--max-mutations", type=int, default=50,
        help="Maximum mutations per base phrase (default: 50)",
    )
    parser.add_argument(
        "--csv", type=str, default=None,
        help="Export results to CSV file",
    )
    parser.add_argument(
        "--uncompressed-only", action="store_true",
        help="Only check uncompressed addresses (faster, historical focus)",
    )

    args = parser.parse_args()

    # Determine phrase source
    if args.file:
        with open(args.file) as f:
            phrases = [line.strip() for line in f if line.strip()]
        print(f"Loaded {len(phrases)} phrases from {args.file}")
    elif args.phrases:
        phrases = args.phrases
    else:
        phrases = DEFAULT_PHRASES
        print(f"Using {len(phrases)} default known-weak passphrases.")

    run_pipeline(
        base_phrases=phrases,
        use_mutations=not args.no_mutations,
        check_both_formats=not args.uncompressed_only,
        max_mutations_per_phrase=args.max_mutations,
        output_csv=args.csv,
    )


if __name__ == "__main__":
    main()
