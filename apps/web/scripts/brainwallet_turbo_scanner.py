"""
Brainwallet Turbo Scanner - Multi-API Parallel Scanner

Uses multiple blockchain API providers with concurrent threads
to achieve 5-10x speedup over the single-threaded scanner.

API Providers:
  - Blockstream (blockstream.info/api)
  - Blockchain.info (blockchain.info)  
  - Blockcypher (api.blockcypher.com)
  - Mempool.space (mempool.space/api)

Usage:
  python brainwallet_turbo_scanner.py                # Start/resume
  python brainwallet_turbo_scanner.py --status       # Show progress
  python brainwallet_turbo_scanner.py --reset        # Reset checkpoint
  python brainwallet_turbo_scanner.py --workers 8    # Set thread count
"""

from __future__ import annotations

import hashlib
import json
import os
import queue
import re
import signal
import sys
import threading
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, NamedTuple

# --- Paths ---
SCRIPT_DIR = Path(__file__).parent
PHRASES_FILE = SCRIPT_DIR / "brainwallet_phrases.txt"
CHECKPOINT_FILE = SCRIPT_DIR / "brainwallet_turbo_checkpoint.json"
HITS_FILE = SCRIPT_DIR / "brainwallet_turbo_hits.json"
LOG_FILE = SCRIPT_DIR / "brainwallet_turbo.log"

# --- Config ---
DEFAULT_WORKERS = 6
MAX_MUTATIONS_PER_PHRASE = 80
CHECK_BOTH_FORMATS = True

# --- Multi-API providers ---
API_PROVIDERS = [
    {
        "name": "blockstream",
        "base": "https://blockstream.info/api",
        "address_endpoint": "/address/{addr}",
        "parse": lambda d: {
            "tx_count": d.get("chain_stats", {}).get("tx_count", 0) + d.get("mempool_stats", {}).get("tx_count", 0),
            "received_sat": d.get("chain_stats", {}).get("funded_txo_sum", 0),
            "balance_sat": d.get("chain_stats", {}).get("funded_txo_sum", 0) - d.get("chain_stats", {}).get("spent_txo_sum", 0),
        },
        "rate_limit": 0.12,
    },
    {
        "name": "mempool",
        "base": "https://mempool.space/api",
        "address_endpoint": "/address/{addr}",
        "parse": lambda d: {
            "tx_count": d.get("chain_stats", {}).get("tx_count", 0) + d.get("mempool_stats", {}).get("tx_count", 0),
            "received_sat": d.get("chain_stats", {}).get("funded_txo_sum", 0),
            "balance_sat": d.get("chain_stats", {}).get("funded_txo_sum", 0) - d.get("chain_stats", {}).get("spent_txo_sum", 0),
        },
        "rate_limit": 0.12,
    },
    {
        "name": "blockcypher",
        "base": "https://api.blockcypher.com/v1/btc/main",
        "address_endpoint": "/addrs/{addr}/balance",
        "parse": lambda d: {
            "tx_count": d.get("n_tx", 0),
            "received_sat": d.get("total_received", 0),
            "balance_sat": d.get("balance", 0),
        },
        "rate_limit": 0.35,
    },
]

# --- Crypto primitives ---
BITCOIN_MAINNET_VERSION = b"\x00"
BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

class BrainwalletResult(NamedTuple):
    passphrase: str
    private_key_hex: str
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
    return BrainwalletResult(passphrase, priv.hex(), addr_c, addr_u)


# --- Mutation engine (compact) ---
LEET_MAP = {"a": ["@", "4"], "e": ["3"], "i": ["1", "!"], "o": ["0"], "s": ["$", "5"], "t": ["7"], "l": ["1"]}
COMMON_SUFFIXES = ["", "1", "12", "123", "1234", "!", "!!", "?", ".", "#", "$", "*", "2024", "2025", "2026", "btc", "BTC", "bitcoin"]
COMMON_PREFIXES = ["", "the ", "The ", "my ", "My "]

def _ws(p):
    s = p.strip(); yield s
    ns = s.replace(" ", "")
    if ns != s: yield ns
    ss = re.sub(r"\s+", " ", s)
    if ss != s: yield ss
    yield s.replace(" ", "_"); yield s.replace(" ", "-")

def _case(p):
    yield p; yield p.lower(); yield p.upper(); yield p.capitalize(); yield p.title()
    if p: yield p[0].lower() + p[1:]

def _suffix(p):
    for s in COMMON_SUFFIXES: yield p + s

def _prefix(p):
    for pr in COMMON_PREFIXES: yield pr + p

def _punct(p):
    yield p
    np = re.sub(r"[^\w\s]", "", p)
    if np != p: yield np
    sp = p.rstrip(".,!?;:'\"")
    if sp != p: yield sp

def _leet(p):
    lo = p.lower(); yield lo
    for c, rs in LEET_MAP.items():
        if c in lo:
            for r in rs: yield lo.replace(c, r)

def generate_mutations(phrase):
    cands = set()
    for w in _ws(phrase):
        for c in _case(w):
            for p in _punct(c):
                cands.add(p)
                for s in _suffix(p): cands.add(s)
    for l in _leet(phrase): cands.add(l)
    for pr in _prefix(phrase): cands.add(pr)
    for pr in _prefix(phrase.lower()): cands.add(pr)
    return sorted(cands)


# --- Thread-safe API pool ---
class APIPool:
    """Round-robin API provider pool with per-provider rate limiting."""
    
    def __init__(self, providers):
        self._providers = providers
        self._locks = {p["name"]: threading.Lock() for p in providers}
        self._last_call = {p["name"]: 0.0 for p in providers}
        self._errors = {p["name"]: 0 for p in providers}
        self._calls = {p["name"]: 0 for p in providers}
        self._idx = 0
        self._idx_lock = threading.Lock()
    
    def _get_provider(self):
        with self._idx_lock:
            # Pick provider with fewest errors, round-robin among equal
            available = [p for p in self._providers if self._errors[p["name"]] < 10]
            if not available:
                # Reset errors and try all
                for p in self._providers:
                    self._errors[p["name"]] = 0
                available = self._providers
            p = available[self._idx % len(available)]
            self._idx += 1
            return p
    
    def check_address(self, address: str) -> dict:
        """Check address using next available API provider."""
        last_error = None
        for attempt in range(len(self._providers)):
            provider = self._get_provider()
            name = provider["name"]
            
            # Per-provider rate limiting
            with self._locks[name]:
                elapsed = time.time() - self._last_call[name]
                if elapsed < provider["rate_limit"]:
                    time.sleep(provider["rate_limit"] - elapsed)
                self._last_call[name] = time.time()
            
            try:
                endpoint = provider["address_endpoint"].format(addr=address)
                url = provider["base"] + endpoint
                req = urllib.request.Request(url, headers={"User-Agent": "BrainwalletResearch/2.0"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode())
                
                result = provider["parse"](data)
                result["address"] = address
                result["provider"] = name
                result["error"] = None
                
                with self._idx_lock:
                    self._calls[name] += 1
                
                return result
                
            except Exception as e:
                last_error = str(e)
                with self._idx_lock:
                    self._errors[name] += 1
                if "429" in str(e):
                    time.sleep(3)
                continue
        
        return {"address": address, "tx_count": 0, "received_sat": 0, "balance_sat": 0, "provider": "none", "error": last_error}
    
    def stats(self):
        return {name: {"calls": self._calls[name], "errors": self._errors[name]} for name in self._calls}


# --- Checkpoint & logging ---
_log_lock = threading.Lock()
_hits_lock = threading.Lock()

def load_checkpoint():
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE) as f:
            return json.load(f)
    return {"completed_phrases": [], "current_index": 0, "total_checked": 0, "total_hits": 0, "started_at": None, "last_update": None}

def save_checkpoint(cp):
    cp["last_update"] = datetime.now(timezone.utc).isoformat()
    tmp = str(CHECKPOINT_FILE) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(cp, f, indent=2)
    os.replace(tmp, str(CHECKPOINT_FILE))

def load_hits():
    if HITS_FILE.exists():
        with open(HITS_FILE) as f:
            return json.load(f)
    return []

def save_hits(hits):
    tmp = str(HITS_FILE) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(hits, f, indent=2)
    os.replace(tmp, str(HITS_FILE))

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    with _log_lock:
        print(line, flush=True)
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")

def sat_to_btc(sat):
    return f"{sat / 1e8:.8f}"

def load_phrases():
    if not PHRASES_FILE.exists():
        log(f"ERROR: {PHRASES_FILE} not found"); sys.exit(1)
    phrases = []
    with open(PHRASES_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                phrases.append(line)
    return phrases


# --- Worker function ---
def check_candidate(candidate, api_pool):
    """Derive addresses and check both on blockchain. Returns list of hits."""
    hits = []
    try:
        bw = derive_brainwallet(candidate)
    except Exception as e:
        return hits, str(e)
    
    # Check uncompressed (historical)
    info_u = api_pool.check_address(bw.addr_uncompressed)
    if info_u["tx_count"] > 0:
        hits.append({
            "passphrase": candidate,
            "address": bw.addr_uncompressed,
            "type": "uncompressed",
            "private_key": bw.private_key_hex,
            "tx_count": info_u["tx_count"],
            "received_sat": info_u["received_sat"],
            "balance_sat": info_u["balance_sat"],
            "provider": info_u.get("provider", "unknown"),
            "found_at": datetime.now(timezone.utc).isoformat(),
        })
    
    # Check compressed (modern)
    if CHECK_BOTH_FORMATS:
        info_c = api_pool.check_address(bw.addr_compressed)
        if info_c["tx_count"] > 0:
            hits.append({
                "passphrase": candidate,
                "address": bw.addr_compressed,
                "type": "compressed",
                "private_key": bw.private_key_hex,
                "tx_count": info_c["tx_count"],
                "received_sat": info_c["received_sat"],
                "balance_sat": info_c["balance_sat"],
                "provider": info_c.get("provider", "unknown"),
                "found_at": datetime.now(timezone.utc).isoformat(),
            })
    
    return hits, None


# --- Main scanner with thread pool ---
_shutdown = False

def _handle_signal(sig, frame):
    global _shutdown
    log("Shutdown signal received. Finishing current batch...")
    _shutdown = True

def show_status():
    cp = load_checkpoint()
    hits = load_hits()
    print("=" * 60)
    print("Brainwallet TURBO Scanner Status")
    print("=" * 60)
    print(f"  Started:          {cp.get('started_at', 'N/A')}")
    print(f"  Last update:      {cp.get('last_update', 'N/A')}")
    print(f"  Phrases done:     {len(cp.get('completed_phrases', []))}")
    print(f"  Current index:    {cp.get('current_index', 0)}")
    print(f"  Total checked:    {cp.get('total_checked', 0)}")
    print(f"  Total hits:       {cp.get('total_hits', 0)}")
    print(f"  Hits file:        {len(hits)} entries")
    if hits:
        # Count those with balance > 0
        with_balance = [h for h in hits if h.get("balance_sat", 0) > 0]
        print(f"  WITH BALANCE > 0: {len(with_balance)} (!)")
        print(f"\n  Recent hits:")
        for h in hits[-5:]:
            bal = "***BAL***" if h.get("balance_sat", 0) > 0 else ""
            print(f"    {h['passphrase'][:40]:<42} {h['address'][:36]:<36} {sat_to_btc(h['received_sat'])} BTC {bal}")
    print("=" * 60)


def scan(num_workers=DEFAULT_WORKERS):
    global _shutdown
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    phrases = load_phrases()
    cp = load_checkpoint()
    all_hits = load_hits()
    api_pool = APIPool(API_PROVIDERS)

    if not cp.get("started_at"):
        cp["started_at"] = datetime.now(timezone.utc).isoformat()

    start_idx = cp.get("current_index", 0)
    completed = set(cp.get("completed_phrases", []))

    log(f"TURBO Scanner starting. {len(phrases)} phrases, {num_workers} workers, {len(API_PROVIDERS)} APIs")
    log(f"APIs: {', '.join(p['name'] for p in API_PROVIDERS)}")
    log(f"Resuming from index {start_idx}, {cp.get('total_checked', 0)} checked, {cp.get('total_hits', 0)} hits")

    for i in range(start_idx, len(phrases)):
        if _shutdown:
            break

        base = phrases[i]
        if base in completed:
            continue

        mutations = generate_mutations(base)[:MAX_MUTATIONS_PER_PHRASE]
        log(f"[{i+1}/{len(phrases)}] '{base[:50]}' -> {len(mutations)} mutations ({num_workers} threads)")

        batch_hits = []
        batch_checked = 0

        # Process mutations in parallel
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = {}
            for candidate in mutations:
                if _shutdown:
                    break
                f = executor.submit(check_candidate, candidate, api_pool)
                futures[f] = candidate

            for future in as_completed(futures):
                if _shutdown:
                    break
                candidate = futures[future]
                try:
                    hits, error = future.result(timeout=30)
                    batch_checked += 1
                    if hits:
                        for h in hits:
                            h["base_phrase"] = base
                            batch_hits.append(h)
                            log(f"  ** HIT ** '{h['passphrase'][:40]}' -> {h['address']} "
                                f"({h['tx_count']} txs, {sat_to_btc(h['received_sat'])} BTC"
                                f"{' ***BALANCE: ' + sat_to_btc(h['balance_sat']) + ' BTC***' if h['balance_sat'] > 0 else ''})")
                except Exception as e:
                    batch_checked += 1

        # Save after each phrase
        if batch_hits:
            with _hits_lock:
                all_hits.extend(batch_hits)
                save_hits(all_hits)

        if not _shutdown:
            completed.add(base)
            cp["completed_phrases"] = list(completed)
            cp["current_index"] = i + 1
            cp["total_checked"] = cp.get("total_checked", 0) + batch_checked
            cp["total_hits"] = len(all_hits)
            save_checkpoint(cp)

            rate = batch_checked / max(1, len(mutations)) * 60
            log(f"  Done. +{batch_checked} checked, +{len(batch_hits)} hits. "
                f"Total: {cp['total_checked']} checked, {cp['total_hits']} hits")

    if _shutdown:
        cp["current_index"] = i
        save_checkpoint(cp)
        log("Graceful shutdown. Run again to resume.")
    else:
        stats = api_pool.stats()
        log(f"SCAN COMPLETE. {cp['total_checked']} checked, {cp['total_hits']} hits.")
        log(f"API stats: {json.dumps(stats)}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Brainwallet TURBO Scanner")
    parser.add_argument("--reset", action="store_true")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    args = parser.parse_args()

    if args.status:
        show_status()
    elif args.reset:
        for f in [CHECKPOINT_FILE, HITS_FILE, LOG_FILE]:
            if f.exists(): f.unlink(); print(f"Deleted {f}")
        print("Reset complete.")
    else:
        scan(num_workers=args.workers)
