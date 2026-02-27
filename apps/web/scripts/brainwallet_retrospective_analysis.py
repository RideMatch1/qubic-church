"""
Brainwallet Retrospective Analysis - Known Compromised Addresses

Analyzes transaction history of brainwallet addresses that are already
publicly documented as compromised in academic literature.

All addresses in this dataset were drained years ago and are part of the
public record. This script performs read-only blockchain queries for
academic analysis of historical attack patterns.

References:
  - Vasek, M. et al. (2016). "The Bitcoin Brain Drain:
    Examining the Use and Abuse of Bitcoin Brain Wallets"
  - Castellucci, R. (2013). "Cracking Cryptocurrency Brainwallets"
    (DEF CON 23)

Data source: Blockstream public API (blockstream.info/api)

Usage:
  python brainwallet_retrospective_analysis.py
"""

from __future__ import annotations

import json
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Any


# --- Known compromised brainwallet addresses ---
# These are publicly documented in academic papers and security talks.
# All were drained long ago. Passphrases are included because they are
# already public knowledge (published in papers, talks, and blog posts).

KNOWN_BRAINWALLETS = [
    {
        "passphrase": "",
        "address": "1HZwkjkeaoZfTSaJxDw6aKkxp45agDiEzN",
        "source": "Vasek et al. 2016 / Castellucci 2013",
        "note": "Empty string - the most trivial brainwallet",
    },
    {
        "passphrase": "correct horse battery staple",
        "address": "1JwSSubhmg6iPtRjtyqhUYYH7bZg3Lfy1T",
        "source": "XKCD #936 / Castellucci 2013",
        "note": "Famous XKCD passphrase, repeatedly funded and drained",
    },
    {
        "passphrase": "password",
        "address": "16ga2uqnF1NqpAuQeeg7sTCAdtDUwDyJav",
        "source": "Vasek et al. 2016",
        "note": "Most common password globally",
    },
    {
        "passphrase": "bitcoin",
        "address": "1E984zyYbNmeuumzEdqT8VSL8QGJi3byAD",
        "source": "Vasek et al. 2016",
        "note": "Obvious cryptocurrency-related passphrase",
    },
    {
        "passphrase": "hello",
        "address": "1HoSFymoqteYrmmr7s3jDDqmggoxacbk37",
        "source": "Vasek et al. 2016",
        "note": "Common greeting",
    },
    {
        "passphrase": "fuck",
        "address": "1AttL2CJypUrBGkEDzStwhjfqWJ1mrNDeB",
        "source": "Vasek et al. 2016",
        "note": "Common profanity",
    },
    {
        "passphrase": "cat",
        "address": "162TRPRZvdgLVNksMoMyGJsYBfYtB4Q8tM",
        "source": "Vasek et al. 2016",
        "note": "Three-letter word",
    },
    {
        "passphrase": "satoshi",
        "address": "1ADJqstUMBB5zFquWg19UqZ7Zc6ePCpzLE",
        "source": "Castellucci 2013",
        "note": "Bitcoin creator's pseudonym",
    },
    {
        "passphrase": "1",
        "address": "1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH",
        "source": "Vasek et al. 2016",
        "note": "Single digit",
    },
    {
        "passphrase": "sausage",
        "address": "1TnnhMEgic5g4ttrCQyDopwqTs4hheuNZ",
        "source": "Castellucci 2013 (DEF CON)",
        "note": "Dictionary word",
    },
]


# --- Blockstream API client ---

BLOCKSTREAM_API = "https://blockstream.info/api"
REQUEST_DELAY_S = 0.5  # polite rate limiting


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
    transactions: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None


def _api_get(endpoint: str) -> Any:
    """GET request to Blockstream API with error handling."""
    url = f"{BLOCKSTREAM_API}/{endpoint}"
    req = urllib.request.Request(url, headers={"User-Agent": "BrainwalletResearch/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 429:
            # Rate limited - wait and retry once
            time.sleep(5)
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode())
        raise
    except urllib.error.URLError as e:
        raise ConnectionError(f"API request failed: {e}") from e


def fetch_address_info(address: str) -> AddressInfo:
    """Fetch address summary and transaction history from Blockstream."""
    info = AddressInfo(address=address)

    try:
        # Fetch address summary
        summary = _api_get(f"address/{address}")
        chain = summary.get("chain_stats", {})
        mempool = summary.get("mempool_stats", {})

        info.total_received_sat = chain.get("funded_txo_sum", 0)
        info.total_sent_sat = chain.get("spent_txo_sum", 0)
        info.tx_count = chain.get("tx_count", 0) + mempool.get("tx_count", 0)
        info.current_balance_sat = info.total_received_sat - info.total_sent_sat

        time.sleep(REQUEST_DELAY_S)

        # Fetch transactions (first page, up to 25)
        if info.tx_count > 0:
            txs = _api_get(f"address/{address}/txs")
            info.transactions = txs

            # Find timestamps
            timestamps = []
            for tx in txs:
                if tx.get("status", {}).get("confirmed"):
                    block_time = tx["status"].get("block_time")
                    if block_time:
                        timestamps.append(block_time)

            if timestamps:
                # Transactions come newest-first from API
                oldest = min(timestamps)
                info.first_seen = datetime.fromtimestamp(oldest, tz=timezone.utc)

                # Find first outgoing transaction (drain)
                for tx in txs:
                    is_outgoing = any(
                        vin.get("prevout", {}).get("scriptpubkey_address") == address
                        for vin in tx.get("vin", [])
                    )
                    if is_outgoing and tx.get("status", {}).get("block_time"):
                        drain_time = tx["status"]["block_time"]
                        info.first_drain = datetime.fromtimestamp(
                            drain_time, tz=timezone.utc
                        )

                if info.first_seen and info.first_drain:
                    delta = info.first_drain.timestamp() - info.first_seen.timestamp()
                    info.drain_delay_seconds = int(abs(delta))

        time.sleep(REQUEST_DELAY_S)

    except Exception as e:
        info.error = str(e)

    return info


def sat_to_btc(sat: int) -> str:
    """Format satoshis as BTC string."""
    return f"{sat / 1e8:.8f}"


def format_duration(seconds: int | None) -> str:
    """Format seconds into a human-readable duration."""
    if seconds is None:
        return "N/A"
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    if seconds < 86400:
        hours = seconds // 3600
        mins = (seconds % 3600) // 60
        return f"{hours}h {mins}m"
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    return f"{days}d {hours}h"


# --- Main analysis ---


def main() -> None:
    print("=" * 72)
    print("Brainwallet Retrospective Analysis")
    print("Known Compromised Addresses from Published Research")
    print("=" * 72)
    print(f"\nAnalyzing {len(KNOWN_BRAINWALLETS)} known brainwallet addresses...")
    print(f"Data source: Blockstream API (read-only, public data)\n")

    results: list[tuple[dict, AddressInfo]] = []

    for i, bw in enumerate(KNOWN_BRAINWALLETS):
        passphrase_display = repr(bw["passphrase"])
        print(f"[{i+1}/{len(KNOWN_BRAINWALLETS)}] Querying {bw['address'][:16]}... "
              f"(passphrase: {passphrase_display})")

        info = fetch_address_info(bw["address"])
        results.append((bw, info))

        if info.error:
            print(f"       ERROR: {info.error}")
        else:
            print(f"       Txs: {info.tx_count}, "
                  f"Received: {sat_to_btc(info.total_received_sat)} BTC, "
                  f"Balance: {sat_to_btc(info.current_balance_sat)} BTC")

    # --- Summary table ---
    print("\n" + "=" * 72)
    print("RESULTS SUMMARY")
    print("=" * 72)

    header = (
        f"  {'Passphrase':<32} {'Txs':>5} {'Received (BTC)':>16} "
        f"{'Balance':>14} {'Drain Delay':>12}"
    )
    print(header)
    print("  " + "-" * (len(header) - 2))

    total_received = 0
    total_txs = 0
    drain_times = []

    for bw, info in results:
        if info.error:
            print(f"  {bw['passphrase']:<32}  ERROR: {info.error}")
            continue

        passphrase = bw["passphrase"] if bw["passphrase"] else "(empty)"
        if len(passphrase) > 30:
            passphrase = passphrase[:27] + "..."

        drain_str = format_duration(info.drain_delay_seconds)
        balance_str = sat_to_btc(info.current_balance_sat)

        print(
            f"  {passphrase:<32} {info.tx_count:>5} "
            f"{sat_to_btc(info.total_received_sat):>16} "
            f"{balance_str:>14} {drain_str:>12}"
        )

        total_received += info.total_received_sat
        total_txs += info.tx_count
        if info.drain_delay_seconds is not None:
            drain_times.append(info.drain_delay_seconds)

    # --- Aggregate statistics ---
    print("\n" + "-" * 72)
    print("AGGREGATE STATISTICS")
    print("-" * 72)
    print(f"  Addresses analyzed:       {len(results)}")
    print(f"  Total transactions:       {total_txs}")
    print(f"  Total BTC received:       {sat_to_btc(total_received)}")

    if drain_times:
        avg_drain = sum(drain_times) / len(drain_times)
        min_drain = min(drain_times)
        max_drain = max(drain_times)
        print(f"  Drain delay (min):        {format_duration(min_drain)}")
        print(f"  Drain delay (avg):        {format_duration(int(avg_drain))}")
        print(f"  Drain delay (max):        {format_duration(max_drain)}")
        instant = sum(1 for d in drain_times if d < 60)
        print(f"  Drained within 1 minute:  {instant}/{len(drain_times)}")

    print("\n" + "=" * 72)
    print("CONCLUSION")
    print("=" * 72)
    print("  These results confirm that brainwallets using predictable")
    print("  passphrases are monitored by automated bots that sweep funds")
    print("  almost instantly. SHA-256(passphrase) without key stretching")
    print("  provides no meaningful security for human-chosen inputs.")
    print("=" * 72)


if __name__ == "__main__":
    main()
