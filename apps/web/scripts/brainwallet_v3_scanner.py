"""
Brainwallet V3 Scanner - SegWit + Batch API

Improvements over turbo scanner:
  1. SegWit addresses: P2SH-P2WPKH (3...) and P2WPKH (bc1q...) 
  2. Blockcypher batch API: check up to 50 addresses in ONE call
  3. 4 address types per key = 2x coverage, same API cost via batching

Address types per private key:
  - P2PKH uncompressed (1...)     - legacy, historical brainwallets
  - P2PKH compressed (1...)       - modern standard  
  - P2SH-P2WPKH compressed (3...) - wrapped SegWit
  - P2WPKH compressed (bc1q...)   - native SegWit

Usage:
  python brainwallet_v3_scanner.py                # Start/resume
  python brainwallet_v3_scanner.py --status       # Show progress
  python brainwallet_v3_scanner.py --reset        # Reset checkpoint
  python brainwallet_v3_scanner.py --workers 6    # Set thread count
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import signal
import sys
import threading
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, NamedTuple

# --- Paths ---
SCRIPT_DIR = Path(__file__).parent
PHRASES_FILE = SCRIPT_DIR / "brainwallet_phrases_prioritized.txt"  # Use prioritized list
CHECKPOINT_FILE = SCRIPT_DIR / "brainwallet_v3_checkpoint.json"
HITS_FILE = SCRIPT_DIR / "brainwallet_v3_hits.json"
LOG_FILE = SCRIPT_DIR / "brainwallet_v3.log"

# --- Config ---
DEFAULT_WORKERS = 6
MAX_MUTATIONS_PER_PHRASE = 80
BATCH_SIZE = 50  # Blockcypher batch limit

# ====== CRYPTO PRIMITIVES ======

BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
BECH32_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"

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
        if byte == 0: result.append("1")
        else: break
    return "".join(reversed(result))

def base58check_encode(version: bytes, payload: bytes) -> str:
    versioned = version + payload
    return base58encode(versioned + double_sha256(versioned)[:4])

# --- Bech32 encoding (BIP173) ---
def _bech32_polymod(values):
    GEN = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
    chk = 1
    for v in values:
        b = chk >> 25
        chk = ((chk & 0x1ffffff) << 5) ^ v
        for i in range(5):
            chk ^= GEN[i] if ((b >> i) & 1) else 0
    return chk

def _bech32_hrp_expand(hrp):
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]

def _bech32_checksum(hrp, data):
    values = _bech32_hrp_expand(hrp) + data
    polymod = _bech32_polymod(values + [0]*6) ^ 1
    return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]

def _convertbits(data, frombits, tobits, pad=True):
    acc, bits, ret = 0, 0, []
    maxv = (1 << tobits) - 1
    for value in data:
        acc = (acc << frombits) | value
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)
    if pad and bits:
        ret.append((acc << (tobits - bits)) & maxv)
    return ret

def bech32_encode(hrp, witver, witprog_bytes):
    """Encode a SegWit address (BIP173 bech32)."""
    data = [witver] + _convertbits(list(witprog_bytes), 8, 5)
    return hrp + "1" + "".join(BECH32_CHARSET[d] for d in data + _bech32_checksum(hrp, data))

# --- Address derivation ---
class DerivedAddresses(NamedTuple):
    passphrase: str
    private_key_hex: str
    p2pkh_uncompressed: str   # 1... (uncompressed pubkey)
    p2pkh_compressed: str     # 1... (compressed pubkey)
    p2sh_p2wpkh: str          # 3... (wrapped SegWit)
    p2wpkh: str               # bc1q... (native SegWit)

def derive_all_addresses(passphrase: str) -> DerivedAddresses:
    """Derive all 4 address types from a passphrase."""
    from ecdsa import SECP256k1, SigningKey
    priv = sha256(passphrase.encode("utf-8"))
    sk = SigningKey.from_string(priv, curve=SECP256k1)
    vk = sk.get_verifying_key()
    x = vk.pubkey.point.x()
    y = vk.pubkey.point.y()
    
    # Uncompressed public key
    pub_u = b"\x04" + vk.to_string()
    # Compressed public key
    prefix = b"\x02" if y % 2 == 0 else b"\x03"
    pub_c = prefix + x.to_bytes(32, "big")
    
    # P2PKH addresses (1...)
    addr_u = base58check_encode(b"\x00", hash160(pub_u))
    addr_c = base58check_encode(b"\x00", hash160(pub_c))
    
    # SegWit addresses (from compressed key only)
    keyhash = hash160(pub_c)
    # P2SH-P2WPKH (3...) - witness script wraps keyhash
    witness_script = b"\x00\x14" + keyhash
    addr_p2sh = base58check_encode(b"\x05", hash160(witness_script))
    # P2WPKH (bc1q...) - native SegWit
    addr_bech32 = bech32_encode("bc", 0, keyhash)
    
    return DerivedAddresses(passphrase, priv.hex(), addr_u, addr_c, addr_p2sh, addr_bech32)


# ====== MUTATION ENGINE ======
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


# ====== MULTI-API POOL WITH BATCH SUPPORT ======

class APIPool:
    """Multi-API pool with batch support for Blockcypher."""
    
    def __init__(self):
        self._providers = [
            {"name": "blockstream", "base": "https://blockstream.info/api", "rate": 0.12},
            {"name": "mempool", "base": "https://mempool.space/api", "rate": 0.12},
            {"name": "blockcypher", "base": "https://api.blockcypher.com/v1/btc/main", "rate": 0.35},
        ]
        self._locks = {p["name"]: threading.Lock() for p in self._providers}
        self._last_call = {p["name"]: 0.0 for p in self._providers}
        self._errors = {p["name"]: 0 for p in self._providers}
        self._calls = {p["name"]: 0 for p in self._providers}
        self._idx = 0
        self._idx_lock = threading.Lock()
    
    def _rate_wait(self, name, rate):
        with self._locks[name]:
            elapsed = time.time() - self._last_call[name]
            if elapsed < rate:
                time.sleep(rate - elapsed)
            self._last_call[name] = time.time()
    
    def _pick_single_provider(self):
        """Pick next single-address provider (blockstream/mempool only)."""
        with self._idx_lock:
            singles = [p for p in self._providers if p["name"] != "blockcypher" and self._errors[p["name"]] < 10]
            if not singles:
                for p in self._providers:
                    if p["name"] != "blockcypher": self._errors[p["name"]] = 0
                singles = [p for p in self._providers if p["name"] != "blockcypher"]
            p = singles[self._idx % len(singles)]
            self._idx += 1
            return p
    
    def check_single(self, address: str) -> dict:
        """Check one address via Blockstream/Mempool."""
        for _ in range(3):
            provider = self._pick_single_provider()
            name = provider["name"]
            self._rate_wait(name, provider["rate"])
            try:
                url = f"{provider['base']}/address/{address}"
                req = urllib.request.Request(url, headers={"User-Agent": "BrainwalletV3/1.0"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    d = json.loads(resp.read().decode())
                cs = d.get("chain_stats", {})
                ms = d.get("mempool_stats", {})
                with self._idx_lock: self._calls[name] += 1
                return {
                    "tx_count": cs.get("tx_count", 0) + ms.get("tx_count", 0),
                    "received_sat": cs.get("funded_txo_sum", 0),
                    "balance_sat": cs.get("funded_txo_sum", 0) - cs.get("spent_txo_sum", 0),
                    "provider": name, "error": None,
                }
            except Exception as e:
                with self._idx_lock: self._errors[name] += 1
                if "429" in str(e): time.sleep(3)
        return {"tx_count": 0, "received_sat": 0, "balance_sat": 0, "provider": "none", "error": "all_failed"}
    
    def check_batch_blockcypher(self, addresses: list[str]) -> dict[str, dict]:
        """Check up to 50 addresses in one Blockcypher call."""
        results = {}
        if not addresses:
            return results
        
        # Filter: Blockcypher supports 1... and 3... but NOT bc1q (must check those individually)
        base58_addrs = [a for a in addresses if a.startswith("1") or a.startswith("3")]
        bech32_addrs = [a for a in addresses if a.startswith("bc1")]
        
        # Batch check base58 addresses
        for chunk_start in range(0, len(base58_addrs), BATCH_SIZE):
            chunk = base58_addrs[chunk_start:chunk_start + BATCH_SIZE]
            self._rate_wait("blockcypher", 0.5)  # Be generous on batch calls
            try:
                addr_str = ";".join(chunk)
                url = f"https://api.blockcypher.com/v1/btc/main/addrs/{addr_str}/balance"
                req = urllib.request.Request(url, headers={"User-Agent": "BrainwalletV3/1.0"})
                with urllib.request.urlopen(req, timeout=20) as resp:
                    data = json.loads(resp.read().decode())
                
                with self._idx_lock: self._calls["blockcypher"] += 1
                
                # If single address, API returns dict; if multiple, returns list
                if isinstance(data, dict):
                    data = [data]
                
                for entry in data:
                    addr = entry.get("address", "")
                    results[addr] = {
                        "tx_count": entry.get("n_tx", 0),
                        "received_sat": entry.get("total_received", 0),
                        "balance_sat": entry.get("balance", 0),
                        "provider": "blockcypher_batch", "error": None,
                    }
            except Exception as e:
                with self._idx_lock: self._errors["blockcypher"] += 1
                if "429" in str(e): time.sleep(5)
                # Fall through - addresses without results get checked individually
        
        # Mark missing addresses
        for addr in base58_addrs:
            if addr not in results:
                results[addr] = None  # Signal to check individually
        for addr in bech32_addrs:
            results[addr] = None  # Must check individually
        
        return results
    
    def stats(self):
        return {n: {"calls": self._calls[n], "errors": self._errors[n]} for n in self._calls}


# ====== CHECKPOINT & LOGGING ======
_log_lock = threading.Lock()
_hits_lock = threading.Lock()

def load_checkpoint():
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE) as f: return json.load(f)
    return {"completed_phrases": [], "current_index": 0, "total_checked": 0, 
            "total_hits": 0, "total_api_calls": 0, "started_at": None, "last_update": None}

def save_checkpoint(cp):
    cp["last_update"] = datetime.now(timezone.utc).isoformat()
    tmp = str(CHECKPOINT_FILE) + ".tmp"
    with open(tmp, "w") as f: json.dump(cp, f, indent=2)
    os.replace(tmp, str(CHECKPOINT_FILE))

def load_hits():
    if HITS_FILE.exists():
        with open(HITS_FILE) as f: return json.load(f)
    return []

def save_hits(hits):
    tmp = str(HITS_FILE) + ".tmp"
    with open(tmp, "w") as f: json.dump(hits, f, indent=2)
    os.replace(tmp, str(HITS_FILE))

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    with _log_lock:
        print(line, flush=True)
        with open(LOG_FILE, "a") as f: f.write(line + "\n")

def sat_to_btc(sat): return f"{sat / 1e8:.8f}"

def load_phrases():
    if not PHRASES_FILE.exists():
        log(f"ERROR: {PHRASES_FILE} not found"); sys.exit(1)
    phrases = []
    with open(PHRASES_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"): phrases.append(line)
    return phrases


# ====== MAIN SCANNER - BATCH-FIRST STRATEGY ======
# Strategy: For each batch of mutations:
#   1. Derive all 4 address types per mutation (CPU only, no API)
#   2. Batch-check up to 50 base58 addresses via Blockcypher (1 API call!)
#   3. Check bech32 + failed batch addresses individually via Blockstream/Mempool
#   4. Log hits with full details

_shutdown = False

def _handle_signal(sig, frame):
    global _shutdown
    log("Shutdown signal received. Finishing current batch...")
    _shutdown = True


def process_phrase_batch(base_phrase: str, mutations: list[str], api_pool: APIPool) -> tuple[list[dict], int]:
    """Process all mutations for one base phrase. Returns (hits, addresses_checked)."""
    hits = []
    checked = 0
    
    # Step 1: Derive all addresses (CPU only)
    derived = []
    for m in mutations:
        try:
            d = derive_all_addresses(m)
            derived.append(d)
        except Exception:
            continue
    
    if not derived:
        return hits, 0
    
    # Step 2: Collect ALL addresses for batch check
    all_addrs = {}  # address -> (DerivedAddresses, addr_type)
    for d in derived:
        all_addrs[d.p2pkh_uncompressed] = (d, "p2pkh_uncompressed")
        all_addrs[d.p2pkh_compressed] = (d, "p2pkh_compressed")
        all_addrs[d.p2sh_p2wpkh] = (d, "p2sh_p2wpkh")
        all_addrs[d.p2wpkh] = (d, "p2wpkh")
    
    addr_list = list(all_addrs.keys())
    total_addrs = len(addr_list)
    
    # Step 3: Try batch API first (Blockcypher, handles 1... and 3... addresses)
    batch_results = api_pool.check_batch_blockcypher(addr_list)
    
    # Step 4: Process batch results + individually check remaining
    need_individual = []
    for addr in addr_list:
        if _shutdown:
            break
        result = batch_results.get(addr)
        if result is None:
            need_individual.append(addr)
        elif result.get("tx_count", 0) > 0:
            d, atype = all_addrs[addr]
            hits.append({
                "passphrase": d.passphrase,
                "address": addr,
                "type": atype,
                "private_key": d.private_key_hex,
                "tx_count": result["tx_count"],
                "received_sat": result["received_sat"],
                "balance_sat": result["balance_sat"],
                "provider": result["provider"],
                "base_phrase": base_phrase,
                "found_at": datetime.now(timezone.utc).isoformat(),
            })
        checked += 1
    
    # Step 5: Check remaining addresses individually (bc1q + batch failures)
    # Use ThreadPoolExecutor for parallel individual checks
    if need_individual and not _shutdown:
        # Log progress
        bc1q_count = sum(1 for a in need_individual if a.startswith("bc1"))
        other_count = len(need_individual) - bc1q_count
        if bc1q_count > 0 or other_count > 0:
            log(f"    Individual checks: {bc1q_count} bc1q + {other_count} others = {len(need_individual)} total")
        
        with ThreadPoolExecutor(max_workers=8) as executor:  # Increased from 4 to 8
            future_map = {}
            for addr in need_individual:
                if _shutdown: break
                f = executor.submit(api_pool.check_single, addr)
                future_map[f] = addr
            
            completed_count = 0
            for future in as_completed(future_map):
                if _shutdown: break
                addr = future_map[future]
                try:
                    result = future.result(timeout=15)
                    checked += 1
                    completed_count += 1
                    
                    # Log progress every 10 addresses
                    if completed_count % 10 == 0 or completed_count == len(need_individual):
                        log(f"      Progress: {completed_count}/{len(need_individual)} individual checks done")
                    
                    if result.get("tx_count", 0) > 0:
                        d, atype = all_addrs[addr]
                        hits.append({
                            "passphrase": d.passphrase,
                            "address": addr,
                            "type": atype,
                            "private_key": d.private_key_hex,
                            "tx_count": result["tx_count"],
                            "received_sat": result["received_sat"],
                            "balance_sat": result["balance_sat"],
                            "provider": result.get("provider", "unknown"),
                            "base_phrase": base_phrase,
                            "found_at": datetime.now(timezone.utc).isoformat(),
                        })
                except Exception as e:
                    checked += 1
                    completed_count += 1
    
    return hits, checked


def show_status():
    cp = load_checkpoint()
    hits = load_hits()
    print("=" * 65)
    print("Brainwallet V3 Scanner Status (SegWit + Batch)")
    print("=" * 65)
    print(f"  Started:          {cp.get('started_at', 'N/A')}")
    print(f"  Last update:      {cp.get('last_update', 'N/A')}")
    print(f"  Phrases done:     {len(cp.get('completed_phrases', []))}/{cp.get('total_phrases', '?')}")
    print(f"  Total addresses:  {cp.get('total_checked', 0)}")
    print(f"  Total hits:       {cp.get('total_hits', 0)}")
    print(f"  API calls:        {cp.get('total_api_calls', '?')}")
    if hits:
        with_balance = [h for h in hits if h.get("balance_sat", 0) > 0]
        print(f"  WITH BALANCE > 0: {len(with_balance)} (!)")
        addr_types = {}
        for h in hits:
            t = h.get("type", "unknown")
            addr_types[t] = addr_types.get(t, 0) + 1
        print(f"  Hit types:        {addr_types}")
        print(f"\n  Recent hits:")
        for h in hits[-8:]:
            bal = " ***BAL***" if h.get("balance_sat", 0) > 0 else ""
            print(f"    [{h.get('type','?')[:6]:6s}] {h['passphrase'][:35]:<37} {h['address'][:38]:<38} {sat_to_btc(h['received_sat'])} BTC{bal}")
    print("=" * 65)


def scan(num_workers=DEFAULT_WORKERS):
    global _shutdown
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    phrases = load_phrases()
    cp = load_checkpoint()
    all_hits = load_hits()
    api_pool = APIPool()

    if not cp.get("started_at"):
        cp["started_at"] = datetime.now(timezone.utc).isoformat()
    cp["total_phrases"] = len(phrases)

    start_idx = cp.get("current_index", 0)
    completed = set(cp.get("completed_phrases", []))

    log(f"V3 Scanner starting. {len(phrases)} phrases, SegWit+Batch mode")
    log(f"Address types: P2PKH(u), P2PKH(c), P2SH-P2WPKH, P2WPKH = 4 per key")
    log(f"Resuming from index {start_idx}, {cp.get('total_checked', 0)} checked, {cp.get('total_hits', 0)} hits")

    scan_start = time.time()
    
    for i in range(start_idx, len(phrases)):
        if _shutdown:
            break

        base = phrases[i]
        if base in completed:
            continue

        mutations = generate_mutations(base)[:MAX_MUTATIONS_PER_PHRASE]
        n_addrs = len(mutations) * 4
        log(f"[{i+1}/{len(phrases)}] '{base[:50]}' -> {len(mutations)} mutations x 4 addr = {n_addrs} addresses")

        batch_start = time.time()
        batch_hits, batch_checked = process_phrase_batch(base, mutations, api_pool)
        batch_time = time.time() - batch_start

        # Log hits
        for h in batch_hits:
            bal_str = f" ***BALANCE: {sat_to_btc(h['balance_sat'])} BTC***" if h["balance_sat"] > 0 else ""
            log(f"  ** HIT ** [{h['type'][:6]}] '{h['passphrase'][:40]}' -> {h['address']} "
                f"({h['tx_count']} txs, {sat_to_btc(h['received_sat'])} BTC{bal_str})")

        # Save
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
            cp["total_api_calls"] = sum(v["calls"] for v in api_pool.stats().values())
            save_checkpoint(cp)

            elapsed = time.time() - scan_start
            rate = cp["total_checked"] / max(1, elapsed) * 60
            log(f"  Done. +{batch_checked} addrs ({batch_time:.1f}s), +{len(batch_hits)} hits. "
                f"Total: {cp['total_checked']} addrs, {cp['total_hits']} hits, ~{rate:.0f} addrs/min")

    if _shutdown:
        cp["current_index"] = i
        save_checkpoint(cp)
        log("Graceful shutdown. Run again to resume.")
    else:
        stats = api_pool.stats()
        log(f"SCAN COMPLETE. {cp['total_checked']} addrs, {cp['total_hits']} hits.")
        log(f"API stats: {json.dumps(stats)}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Brainwallet V3 Scanner (SegWit + Batch)")
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
