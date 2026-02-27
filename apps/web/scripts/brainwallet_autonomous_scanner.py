"""
Brainwallet Autonomous Scanner - Background Checkpoint-Based Scanner

Reads phrases from brainwallet_phrases.txt, generates mutations,
derives Bitcoin addresses, checks blockchain via Blockstream API,
and saves all hits. Uses a JSON checkpoint file to resume after
interruption.

Usage:
  python brainwallet_autonomous_scanner.py                  # Start/resume scan
  python brainwallet_autonomous_scanner.py --reset          # Reset checkpoint
  python brainwallet_autonomous_scanner.py --status         # Show progress
  nohup python brainwallet_autonomous_scanner.py &          # Run in background
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import signal
import sys
import time
import urllib.request
import urllib.error
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, NamedTuple

# --- Paths ---
SCRIPT_DIR = Path(__file__).parent
PHRASES_FILE = SCRIPT_DIR / "brainwallet_phrases.txt"
CHECKPOINT_FILE = SCRIPT_DIR / "brainwallet_checkpoint.json"
HITS_FILE = SCRIPT_DIR / "brainwallet_hits.json"
LOG_FILE = SCRIPT_DIR / "brainwallet_scanner.log"

# --- Config ---
BLOCKSTREAM_API = "https://blockstream.info/api"
REQUEST_DELAY_S = 0.35
MAX_MUTATIONS_PER_PHRASE = 80
CHECK_BOTH_FORMATS = True  # compressed + uncompressed

# --- Crypto primitives ---
BITCOIN_MAINNET_VERSION = b"\x00"
BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


class BrainwalletResult(NamedTuple):
    passphrase: str
    private_key_hex: str
    pub_compressed_hex: str
    pub_uncompressed_hex: str
    addr_compressed: str
    addr_uncompressed: str


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

def derive_brainwallet(passphrase: str) -> BrainwalletResult:
    from ecdsa import SECP256k1, SigningKey
    priv = sha256(passphrase.encode("utf-8"))
    sk = SigningKey.from_string(priv, curve=SECP256k1)
    vk = sk.get_verifying_key()
    x = vk.pubkey.point.x()
    y = vk.pubkey.point.y()
    prefix = b"\x02" if y % 2 == 0 else b"\x03"
    pub_c = prefix + x.to_bytes(32, "big")
    pub_u = b"\x04" + vk.to_string()
    addr_c = base58check_encode(BITCOIN_MAINNET_VERSION, hash160(pub_c))
    addr_u = base58check_encode(BITCOIN_MAINNET_VERSION, hash160(pub_u))
    return BrainwalletResult(passphrase, priv.hex(), pub_c.hex(), pub_u.hex(), addr_c, addr_u)


# --- Mutation engine ---
LEET_MAP = {"a": ["@", "4"], "e": ["3"], "i": ["1", "!"], "o": ["0"], "s": ["$", "5"], "t": ["7"], "l": ["1"]}
COMMON_SUFFIXES = ["", "1", "12", "123", "1234", "!", "!!", "?", ".", "#", "$", "*", "2024", "2025", "2026", "btc", "BTC", "bitcoin"]
COMMON_PREFIXES = ["", "the ", "The ", "my ", "My "]

def _ws(p: str) -> Iterator[str]:
    s = p.strip(); yield s
    ns = s.replace(" ", "")
    if ns != s: yield ns
    ss = re.sub(r"\s+", " ", s)
    if ss != s: yield ss
    yield s.replace(" ", "_"); yield s.replace(" ", "-")

def _case(p: str) -> Iterator[str]:
    yield p; yield p.lower(); yield p.upper(); yield p.capitalize(); yield p.title()
    if p: yield p[0].lower() + p[1:]

def _suffix(p: str) -> Iterator[str]:
    for s in COMMON_SUFFIXES: yield p + s

def _prefix(p: str) -> Iterator[str]:
    for pr in COMMON_PREFIXES: yield pr + p

def _punct(p: str) -> Iterator[str]:
    yield p
    np = re.sub(r"[^\w\s]", "", p)
    if np != p: yield np
    sp = p.rstrip(".,!?;:'\"")
    if sp != p: yield sp

def _leet(p: str) -> Iterator[str]:
    lo = p.lower(); yield lo
    for c, rs in LEET_MAP.items():
        if c in lo:
            for r in rs: yield lo.replace(c, r)

def generate_mutations(phrase: str) -> list[str]:
    cands: set[str] = set()
    for w in _ws(phrase):
        for c in _case(w):
            for p in _punct(c):
                cands.add(p)
                for s in _suffix(p): cands.add(s)
    for l in _leet(phrase): cands.add(l)
    for pr in _prefix(phrase): cands.add(pr)
    for pr in _prefix(phrase.lower()): cands.add(pr)
    return sorted(cands)


# --- API ---
def _api_get(endpoint: str) -> Any:
    url = f"{BLOCKSTREAM_API}/{endpoint}"
    req = urllib.request.Request(url, headers={"User-Agent": "BrainwalletResearch/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 429:
            time.sleep(10)
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode())
        raise

def check_address(address: str) -> dict:
    try:
        s = _api_get(f"address/{address}")
        chain = s.get("chain_stats", {})
        mp = s.get("mempool_stats", {})
        received = chain.get("funded_txo_sum", 0)
        sent = chain.get("spent_txo_sum", 0)
        txs = chain.get("tx_count", 0) + mp.get("tx_count", 0)
        return {"address": address, "tx_count": txs, "received_sat": received, "sent_sat": sent, "balance_sat": received - sent, "error": None}
    except Exception as e:
        return {"address": address, "tx_count": 0, "received_sat": 0, "sent_sat": 0, "balance_sat": 0, "error": str(e)}


# --- Checkpoint system ---
def load_checkpoint() -> dict:
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE) as f:
            return json.load(f)
    return {"completed_phrases": [], "current_index": 0, "total_checked": 0, "total_hits": 0, "started_at": None, "last_update": None}

def save_checkpoint(cp: dict) -> None:
    cp["last_update"] = datetime.now(timezone.utc).isoformat()
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(cp, f, indent=2)

def load_hits() -> list:
    if HITS_FILE.exists():
        with open(HITS_FILE) as f:
            return json.load(f)
    return []

def save_hits(hits: list) -> None:
    with open(HITS_FILE, "w") as f:
        json.dump(hits, f, indent=2)

def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def sat_to_btc(sat: int) -> str:
    return f"{sat / 1e8:.8f}"


# --- Load phrases ---
def load_phrases() -> list[str]:
    if not PHRASES_FILE.exists():
        log(f"ERROR: {PHRASES_FILE} not found")
        sys.exit(1)
    phrases = []
    with open(PHRASES_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                phrases.append(line)
    return phrases


# --- Main scanner ---
_shutdown = False

def _handle_signal(sig, frame):
    global _shutdown
    log("Received shutdown signal. Saving checkpoint and exiting gracefully...")
    _shutdown = True

def show_status():
    cp = load_checkpoint()
    hits = load_hits()
    print("=" * 60)
    print("Brainwallet Scanner Status")
    print("=" * 60)
    print(f"  Started:          {cp.get('started_at', 'N/A')}")
    print(f"  Last update:      {cp.get('last_update', 'N/A')}")
    print(f"  Phrases done:     {len(cp.get('completed_phrases', []))}")
    print(f"  Current index:    {cp.get('current_index', 0)}")
    print(f"  Total checked:    {cp.get('total_checked', 0)}")
    print(f"  Total hits:       {cp.get('total_hits', 0)}")
    print(f"  Hits file:        {len(hits)} entries")
    if hits:
        print("\n  Recent hits:")
        for h in hits[-5:]:
            print(f"    {h['passphrase'][:40]:<42} {h['address']:<36} {sat_to_btc(h['received_sat'])} BTC")
    print("=" * 60)


def scan():
    global _shutdown
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    phrases = load_phrases()
    cp = load_checkpoint()
    hits = load_hits()

    if not cp.get("started_at"):
        cp["started_at"] = datetime.now(timezone.utc).isoformat()

    start_idx = cp.get("current_index", 0)
    completed = set(cp.get("completed_phrases", []))

    log(f"Scanner starting. {len(phrases)} base phrases, resuming from index {start_idx}")
    log(f"Checkpoint: {cp.get('total_checked', 0)} checked, {cp.get('total_hits', 0)} hits so far")

    for i in range(start_idx, len(phrases)):
        if _shutdown:
            break

        base = phrases[i]
        if base in completed:
            continue

        mutations = generate_mutations(base)[:MAX_MUTATIONS_PER_PHRASE]
        log(f"[{i+1}/{len(phrases)}] Base: '{base[:50]}' -> {len(mutations)} mutations")

        for j, candidate in enumerate(mutations):
            if _shutdown:
                break

            try:
                bw = derive_brainwallet(candidate)
            except Exception as e:
                log(f"  Derivation error for '{candidate[:30]}': {e}")
                continue

            # Check uncompressed (historical)
            info_u = check_address(bw.addr_uncompressed)
            time.sleep(REQUEST_DELAY_S)

            if info_u["tx_count"] > 0:
                hit = {
                    "passphrase": candidate,
                    "base_phrase": base,
                    "address": bw.addr_uncompressed,
                    "type": "uncompressed",
                    "private_key": bw.private_key_hex,
                    "tx_count": info_u["tx_count"],
                    "received_sat": info_u["received_sat"],
                    "balance_sat": info_u["balance_sat"],
                    "found_at": datetime.now(timezone.utc).isoformat(),
                }
                hits.append(hit)
                save_hits(hits)
                cp["total_hits"] = len(hits)
                log(f"  ** HIT ** '{candidate[:40]}' -> {bw.addr_uncompressed} "
                    f"({info_u['tx_count']} txs, {sat_to_btc(info_u['received_sat'])} BTC)")

            # Check compressed (modern)
            if CHECK_BOTH_FORMATS:
                info_c = check_address(bw.addr_compressed)
                time.sleep(REQUEST_DELAY_S)

                if info_c["tx_count"] > 0:
                    hit = {
                        "passphrase": candidate,
                        "base_phrase": base,
                        "address": bw.addr_compressed,
                        "type": "compressed",
                        "private_key": bw.private_key_hex,
                        "tx_count": info_c["tx_count"],
                        "received_sat": info_c["received_sat"],
                        "balance_sat": info_c["balance_sat"],
                        "found_at": datetime.now(timezone.utc).isoformat(),
                    }
                    hits.append(hit)
                    save_hits(hits)
                    cp["total_hits"] = len(hits)
                    log(f"  ** HIT ** '{candidate[:40]}' -> {bw.addr_compressed} "
                        f"({info_c['tx_count']} txs, {sat_to_btc(info_c['received_sat'])} BTC)")

            cp["total_checked"] = cp.get("total_checked", 0) + 1

            # Save checkpoint every 10 candidates
            if (j + 1) % 10 == 0:
                cp["current_index"] = i
                save_checkpoint(cp)

        # Mark phrase complete
        if not _shutdown:
            completed.add(base)
            cp["completed_phrases"] = list(completed)
            cp["current_index"] = i + 1
            save_checkpoint(cp)
            log(f"  Phrase '{base[:40]}' complete. Total: {cp['total_checked']} checked, {cp['total_hits']} hits")

    if _shutdown:
        cp["current_index"] = i
        save_checkpoint(cp)
        log("Graceful shutdown complete. Run again to resume.")
    else:
        log(f"SCAN COMPLETE. {cp['total_checked']} addresses checked, {cp['total_hits']} hits found.")
        log(f"Results: {HITS_FILE}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Brainwallet Autonomous Scanner")
    parser.add_argument("--reset", action="store_true", help="Reset checkpoint and start fresh")
    parser.add_argument("--status", action="store_true", help="Show current scan progress")
    args = parser.parse_args()

    if args.status:
        show_status()
    elif args.reset:
        for f in [CHECKPOINT_FILE, HITS_FILE, LOG_FILE]:
            if f.exists():
                f.unlink()
                print(f"Deleted {f}")
        print("Checkpoint reset. Ready for fresh scan.")
    else:
        scan()
