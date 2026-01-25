#!/usr/bin/env python3
"""
===============================================================================
                    ⛏️ PATOSHI NONCE PATTERN ANALYSIS ⛏️
===============================================================================
Das EIGENTLICHE Patoshi-Pattern: Das Nonce-Muster in den ersten ~22,000 Blöcken.

Das Patoshi-Pattern zeigt:
1. Bestimmte LSB-Muster in den Nonces
2. Charakteristische Mining-Abstände
3. Hinweise auf spezielle Mining-Software
"""

import json
import hashlib
import struct
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
import re

script_dir = Path(__file__).parent

print("⛏️" * 40)
print("       PATOSHI NONCE PATTERN ANALYSIS")
print("⛏️" * 40)

# =============================================================================
# PATOSHI-PATTERN HINTERGRUND
# =============================================================================
print("\n" + "=" * 80)
print("PATOSHI-PATTERN HINTERGRUND")
print("=" * 80)

print("""
Das Patoshi-Pattern wurde von Sergio Demian Lerner entdeckt:

1. NONCE LSB MUSTER:
   - Satoshis Miner verwendete Nonces mit bestimmten niedersten Bits
   - Diese Bits zeigen ein charakteristisches Muster
   - Andere frühe Miner hatten ANDERE Muster

2. EXTRA-NONCE MUSTER:
   - Satoshi's Miner inkrementierte den ExtraNonce anders
   - Charakteristische "Streifen" im Nonce-Raum

3. BLOCK-ABSTÄNDE:
   - Durchschnittlich längere Pausen zwischen Satoshi-Blöcken
   - Hinweis auf bewusstes "Zurückhalten"

4. GESCHÄTZTE MENGE:
   - ~1.1 Millionen BTC in Patoshi-Adressen
   - Davon NIE ausgegeben!
""")

# =============================================================================
# LADE PATOSHI-DATEN
# =============================================================================
print("\n" + "=" * 80)
print("LADE PATOSHI-DATEN")
print("=" * 80)

patoshi_path = script_dir.parent / "public" / "data" / "patoshi-addresses.json"

# Versuche vollständige Daten zu laden
try:
    with open(patoshi_path, 'r') as f:
        patoshi_data = json.load(f)

    if isinstance(patoshi_data, list):
        records = patoshi_data
    elif isinstance(patoshi_data, dict):
        records = patoshi_data.get('records', patoshi_data.get('data', []))
    else:
        records = []

    print(f"✓ Geladene Records: {len(records)}")

    # Zeige Struktur
    if records and len(records) > 0:
        sample = records[0]
        print(f"  Record-Struktur: {list(sample.keys()) if isinstance(sample, dict) else type(sample)}")
except Exception as e:
    print(f"✗ Fehler beim Laden: {e}")
    records = []

# =============================================================================
# ANALYSIERE VERFÜGBARE DATEN
# =============================================================================
print("\n" + "=" * 80)
print("DATEN-ANALYSE")
print("=" * 80)

if records:
    # Extrahiere Felder
    blocks = []
    nonces = []
    addresses = []
    timestamps = []

    for record in records[:1000]:  # Erste 1000 für Analyse
        if isinstance(record, dict):
            if 'block' in record:
                blocks.append(record['block'])
            if 'nonce' in record:
                nonces.append(record['nonce'])
            if 'address' in record:
                addresses.append(record['address'])
            if 'timestamp' in record:
                timestamps.append(record['timestamp'])

    print(f"  Blöcke: {len(blocks)}")
    print(f"  Nonces: {len(nonces)}")
    print(f"  Adressen: {len(addresses)}")
    print(f"  Timestamps: {len(timestamps)}")

    # Block-Statistiken
    if blocks:
        print(f"\n  Block-Range: {min(blocks)} - {max(blocks)}")
        print(f"  Erste 10 Blöcke: {sorted(blocks)[:10]}")

# =============================================================================
# NONCE LSB ANALYSE (Wenn Nonces verfügbar)
# =============================================================================
print("\n" + "=" * 80)
print("NONCE LSB ANALYSE")
print("=" * 80)

if nonces:
    print(f"\nAnalysiere {len(nonces)} Nonces...")

    # LSB-Verteilung
    lsb_counts = Counter()
    lsb_4bit_counts = Counter()

    for nonce in nonces:
        if isinstance(nonce, int):
            lsb = nonce & 0x1  # Niederster Bit
            lsb_4 = nonce & 0xF  # Niedrigste 4 Bits
            lsb_counts[lsb] += 1
            lsb_4bit_counts[lsb_4] += 1

    print("\n  LSB (1 Bit) Verteilung:")
    for bit, count in sorted(lsb_counts.items()):
        pct = 100 * count / len(nonces)
        bar = "█" * int(pct / 2)
        print(f"    {bit}: {count:5d} ({pct:5.1f}%) {bar}")

    print("\n  LSB (4 Bit) Verteilung:")
    for bits, count in sorted(lsb_4bit_counts.items())[:8]:
        pct = 100 * count / len(nonces)
        print(f"    0x{bits:X}: {count:5d} ({pct:5.1f}%)")

    # Patoshi-Charakteristik: Bestimmte LSB-Muster überrepräsentiert
    expected_per_bit = len(nonces) / 16
    anomalies = [(b, c) for b, c in lsb_4bit_counts.items() if c > expected_per_bit * 1.5]
    if anomalies:
        print("\n  ⚠️ Überrepräsentierte LSB-Muster:")
        for bits, count in anomalies:
            ratio = count / expected_per_bit
            print(f"    0x{bits:X}: {ratio:.2f}x erwartet")
else:
    print("  Keine Nonce-Daten verfügbar")
    print("  Hinweis: Patoshi-JSON enthält möglicherweise nur Adressen, nicht Nonces")

# =============================================================================
# BLOCK-ABSTANDS-ANALYSE
# =============================================================================
print("\n" + "=" * 80)
print("BLOCK-ABSTANDS-ANALYSE")
print("=" * 80)

if len(blocks) > 1:
    sorted_blocks = sorted(blocks)
    gaps = [sorted_blocks[i+1] - sorted_blocks[i] for i in range(len(sorted_blocks)-1)]

    print(f"\nAnalysiere {len(gaps)} Block-Abstände...")

    gap_counts = Counter(gaps)
    print("\n  Häufigste Abstände:")
    for gap, count in gap_counts.most_common(15):
        pct = 100 * count / len(gaps)
        print(f"    Δ{gap:3d} Blöcke: {count:4d} ({pct:5.1f}%)")

    # Durchschnittlicher Abstand
    avg_gap = sum(gaps) / len(gaps)
    print(f"\n  Durchschnittlicher Abstand: {avg_gap:.2f} Blöcke")

    # Patoshi-Charakteristik: Größere Abstände als erwartet
    # Bei konstantem Mining würde man Poisson-Verteilung erwarten
    large_gaps = [g for g in gaps if g > 10]
    print(f"  Große Abstände (>10): {len(large_gaps)} ({100*len(large_gaps)/len(gaps):.1f}%)")

    # Spezielle Abstände (Fibonacci, heilige Zahlen)
    fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
    sacred = [7, 11, 13, 21, 27, 33, 42]

    fib_gaps = sum(1 for g in gaps if g in fib)
    sacred_gaps = sum(1 for g in gaps if g in sacred)

    print(f"\n  Fibonacci-Abstände: {fib_gaps} ({100*fib_gaps/len(gaps):.1f}%)")
    print(f"  Heilige Zahl-Abstände: {sacred_gaps} ({100*sacred_gaps/len(gaps):.1f}%)")
else:
    print("  Nicht genug Block-Daten für Abstands-Analyse")

# =============================================================================
# ADRESS-WIEDERVERWENDUNG
# =============================================================================
print("\n" + "=" * 80)
print("ADRESS-WIEDERVERWENDUNGS-ANALYSE")
print("=" * 80)

if addresses:
    addr_counts = Counter(addresses)
    unique_addrs = len(addr_counts)
    total_uses = len(addresses)

    print(f"\n  Eindeutige Adressen: {unique_addrs}")
    print(f"  Gesamte Verwendungen: {total_uses}")
    print(f"  Durchschnittliche Wiederverwendung: {total_uses/unique_addrs:.2f}x")

    # Mehrfach verwendete Adressen
    reused = [(addr, count) for addr, count in addr_counts.items() if count > 1]
    print(f"\n  Wiederverwendete Adressen: {len(reused)}")

    if reused:
        print("\n  Top 5 am häufigsten verwendete:")
        for addr, count in sorted(reused, key=lambda x: -x[1])[:5]:
            print(f"    {addr[:30]}...: {count}x")

# =============================================================================
# MINING-MUSTER-REKONSTRUKTION
# =============================================================================
print("\n" + "=" * 80)
print("MINING-MUSTER-REKONSTRUKTION")
print("=" * 80)

print("""
Basierend auf Lerners Forschung:

PATOSHI-MINER CHARAKTERISTIKEN:
1. Multi-Thread Mining mit ~51 parallelen Threads
2. Charakteristische ExtraNonce-Inkrementierung
3. Spezielle Nonce-Aufteilung in "Streifen"
4. Bewusstes "Throttling" um Netzwerk nicht zu dominieren

UNTERSCHEIDUNG VON ANDEREN MINERN:
- Andere frühe Miner hatten ANDERE Nonce-Muster
- Das erlaubt Trennung von Satoshi vs. Nicht-Satoshi Blöcken
- ~22,000 Blöcke werden Satoshi zugeordnet
""")

# =============================================================================
# FAZIT
# =============================================================================
print("\n" + "=" * 80)
print("FAZIT: PATOSHI NONCE ANALYSE")
print("=" * 80)

print(f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║   PATOSHI-MUSTER ERKENNTNISSE:                                            ║
║                                                                           ║
║   1. DATEN-SITUATION:                                                     ║
║      Records geladen: {len(records):,}                                       ║
║      Blöcke: {len(blocks):,}, Adressen: {len(addresses):,}                              ║
║                                                                           ║
║   2. NONCE-MUSTER:                                                        ║
║      {"Nonces verfügbar für LSB-Analyse" if nonces else "Keine Nonces in Daten - nur Adressen":50s}║
║                                                                           ║
║   3. BLOCK-ABSTÄNDE:                                                      ║
║      {"Durchschnitt: " + f"{avg_gap:.1f} Blöcke" if len(blocks) > 1 else "Nicht genug Daten":50s}║
║                                                                           ║
║   4. ADRESS-WIEDERVERWENDUNG:                                            ║
║      {f"{unique_addrs:,} unique / {total_uses:,} total" if addresses else "Keine Daten":50s}║
║                                                                           ║
║   KRITISCHE ERKENNTNIS:                                                   ║
║   Das Patoshi-Pattern basiert auf NONCE-MUSTERN, nicht Adressen!          ║
║   Um es vollständig zu analysieren, brauchen wir Block-Header-Daten       ║
║   mit Nonces und ExtraNonces.                                             ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")

# Speichere Ergebnisse
output = {
    "timestamp": datetime.now().isoformat(),
    "records_loaded": len(records),
    "blocks_analyzed": len(blocks),
    "addresses_analyzed": len(addresses),
    "nonces_available": len(nonces) > 0,
    "unique_addresses": len(set(addresses)) if addresses else 0,
    "avg_block_gap": avg_gap if len(blocks) > 1 else None,
    "conclusion": "Patoshi pattern requires nonce data from block headers",
}

output_path = script_dir / "PATOSHI_NONCE_ANALYSIS_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"\n✓ Ergebnisse: {output_path}")
