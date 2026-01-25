#!/usr/bin/env python3
"""
===============================================================================
      QUBIC LIVE NETZWERK MONITOR - ECHTZEIT ÜBERWACHUNG
===============================================================================

Verbindet sich mit echten Qubic-Knoten und überwacht das Netzwerk in Echtzeit.
Spezieller Fokus auf:
- POCC Genesis Token Aktivität
- Epoch-Wechsel
- Tick-Progression
- Netzwerk-Gesundheit
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path

print("=" * 80)
print("     QUBIC LIVE NETZWERK MONITOR")
print("=" * 80)

# =============================================================================
# KONFIGURATION
# =============================================================================

QUBIC_RPC = "https://rpc.qubic.org"
POCC_ADDRESS = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"

# Spezielle Adressen zum Überwachen
WATCHED_ADDRESSES = {
    "POCC": POCC_ADDRESS,
    # Weitere interessante Adressen können hinzugefügt werden
}

# =============================================================================
# API FUNKTIONEN
# =============================================================================

def get_network_status():
    """Hole aktuellen Netzwerk-Status"""
    try:
        response = requests.get(f"{QUBIC_RPC}/v1/status", timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"  Fehler: {e}")
    return None

def get_balance(address):
    """Hole Balance einer Adresse"""
    try:
        response = requests.get(f"{QUBIC_RPC}/v1/balances/{address}", timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"  Fehler bei {address[:10]}...: {e}")
    return None

def get_transactions(address, limit=10):
    """Hole Transaktionen einer Adresse"""
    try:
        response = requests.get(
            f"{QUBIC_RPC}/v2/identities/{address}/transfers",
            params={"limit": limit},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"  Fehler: {e}")
    return None

def get_latest_tick():
    """Hole neuesten Tick"""
    try:
        response = requests.get(f"{QUBIC_RPC}/v1/latestTick", timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

# =============================================================================
# MONITORING FUNKTIONEN
# =============================================================================

def display_network_status():
    """Zeige Netzwerk-Status an"""
    print("\n[1] NETZWERK STATUS")
    print("-" * 60)

    status = get_network_status()
    if not status:
        print("  ✗ Netzwerk nicht erreichbar")
        return None

    tick_data = status.get('lastProcessedTick', {})
    current_tick = tick_data.get('tickNumber', 0)
    current_epoch = tick_data.get('epoch', 0)

    print(f"  ✓ Netzwerk ONLINE")
    print(f"    Aktueller Tick:  {current_tick:,}")
    print(f"    Aktuelle Epoch:  {current_epoch}")

    # Epoch-Statistik
    epochs_data = status.get('lastProcessedTicksPerEpoch', {})
    if epochs_data:
        recent_epochs = sorted(epochs_data.items(), key=lambda x: int(x[0]))[-5:]
        print(f"\n    Letzte 5 Epochs:")
        for epoch, last_tick in recent_epochs:
            print(f"      Epoch {epoch}: Tick {last_tick:,}")

    return {
        'tick': current_tick,
        'epoch': current_epoch,
    }

def display_pocc_status():
    """Zeige POCC Genesis Token Status"""
    print("\n[2] POCC GENESIS TOKEN STATUS")
    print("-" * 60)

    # Balance
    balance_data = get_balance(POCC_ADDRESS)
    if balance_data and 'balance' in balance_data:
        balance_info = balance_data['balance']
        balance = int(balance_info.get('balance', 0))
        incoming = int(balance_info.get('incomingAmount', 0))
        outgoing = int(balance_info.get('outgoingAmount', 0))
        in_count = balance_info.get('numberOfIncomingTransfers', 0)
        out_count = balance_info.get('numberOfOutgoingTransfers', 0)

        balance_billions = balance / 1_000_000_000
        print(f"  ✓ POCC Balance: {balance:,} ({balance_billions:.2f} Mrd)")
        print(f"    Eingehend:  {incoming:,} ({in_count} TXs)")
        print(f"    Ausgehend:  {outgoing:,} ({out_count} TXs)")
    else:
        print("  ✗ Balance nicht abrufbar")
        return {'balance': 0, 'recent_txs': 0}

    # Transaktionen
    tx_data = get_transactions(POCC_ADDRESS, limit=5)
    if tx_data and 'transactions' in tx_data:
        txs = tx_data.get('transactions', [])
        print(f"\n  Letzte {len(txs)} Transaktionen:")
        for tx in txs[:5]:
            tick = tx.get('tickNumber', 'N/A')
            amount = tx.get('amount', 0)
            dest = tx.get('destId', 'N/A')
            print(f"    Tick {tick}: {amount:,} → {dest[:20]}...")

    return {
        'balance': balance,
        'recent_txs': len(tx_data.get('transactions', [])) if tx_data else 0
    }

def calculate_time_to_march_2026():
    """Berechne Zeit bis März 2026"""
    print("\n[3] TIME-LOCK COUNTDOWN")
    print("-" * 60)

    now = datetime.now()
    march_2026 = datetime(2026, 3, 3)

    delta = march_2026 - now

    print(f"  Aktuelles Datum:  {now.strftime('%Y-%m-%d %H:%M')}")
    print(f"  Ziel-Datum:       2026-03-03")
    print(f"  Verbleibend:      {delta.days} Tage, {delta.seconds // 3600} Stunden")

    # Berechne auch Bitcoin-Tage seit Genesis
    btc_genesis = datetime(2009, 1, 3)
    days_since_btc = (now - btc_genesis).days
    print(f"\n  Tage seit Bitcoin Genesis: {days_since_btc:,}")
    print(f"  Ziel (6268 Tage):          6,268")
    print(f"  Verbleibend:               {6268 - days_since_btc} Tage")

    return {
        'days_remaining': delta.days,
        'days_since_btc': days_since_btc,
    }

def analyze_network_patterns():
    """Analysiere Netzwerk auf interessante Muster"""
    print("\n[4] PATTERN-ANALYSE")
    print("-" * 60)

    status = get_network_status()
    if not status:
        return None

    tick = status.get('lastProcessedTick', {}).get('tickNumber', 0)
    epoch = status.get('lastProcessedTick', {}).get('epoch', 0)

    # CFB Signatur-Zahlen prüfen
    patterns_found = []

    # 27 (CFB)
    if tick % 27 == 0:
        patterns_found.append(f"Tick {tick} ist teilbar durch 27 (CFB)")

    # 121 (11²)
    if tick % 121 == 0:
        patterns_found.append(f"Tick {tick} ist teilbar durch 121 (11²)")

    # 676 (26²)
    if tick % 676 == 0:
        patterns_found.append(f"Tick {tick} ist teilbar durch 676 (Computors)")

    # Epoch = 121?
    if epoch == 121:
        patterns_found.append(f"EPOCH 121! (11² - CFB Signatur)")

    # Tick enthält 1CFB?
    tick_hex = hex(tick)
    if '1cfb' in tick_hex.lower():
        patterns_found.append(f"Tick {tick} enthält 1CFB in Hex!")

    if patterns_found:
        print("  🔍 GEFUNDENE MUSTER:")
        for p in patterns_found:
            print(f"    → {p}")
    else:
        print("  Keine besonderen Muster im aktuellen Tick")

    return patterns_found

# =============================================================================
# HAUPTAUSFÜHRUNG
# =============================================================================

def main():
    results = {
        "timestamp": datetime.now().isoformat(),
        "network": None,
        "pocc": None,
        "countdown": None,
        "patterns": [],
    }

    # 1. Netzwerk-Status
    results['network'] = display_network_status()

    # 2. POCC Status
    results['pocc'] = display_pocc_status()

    # 3. Countdown
    results['countdown'] = calculate_time_to_march_2026()

    # 4. Pattern-Analyse
    results['patterns'] = analyze_network_patterns()

    # Zusammenfassung
    print("\n" + "=" * 80)
    print("                    LIVE MONITORING ZUSAMMENFASSUNG")
    print("=" * 80)

    print(f"""
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                    QUBIC NETZWERK - LIVE STATUS                         │
    ├─────────────────────────────────────────────────────────────────────────┤
    │  Netzwerk:           {'ONLINE ✓' if results['network'] else 'OFFLINE ✗'}                                     │
    │  Aktueller Tick:     {results['network']['tick']:,} (Epoch {results['network']['epoch']})           │
    │  POCC Balance:       {results['pocc']['balance']:,} QUBIC                     │
    │  Time-Lock:          {results['countdown']['days_remaining']} Tage bis März 2026                       │
    ├─────────────────────────────────────────────────────────────────────────┤
    │                                                                         │
    │  WAS WIR AKTIV MACHEN KÖNNEN:                                          │
    │                                                                         │
    │  1. ⏰ WARTEN auf Time-Lock Ende (3. März 2026)                        │
    │     → Dann werden Seeds möglicherweise aktiviert                        │
    │                                                                         │
    │  2. 🔬 AIGARTH SIMULATION weiter erforschen                            │
    │     → Anna Matrix als neuronales Netz testen                           │
    │     → Verschiedene Inputs und deren Outputs analysieren                 │
    │                                                                         │
    │  3. 📊 LIVE MONITORING betreiben                                       │
    │     → POCC Transaktionen verfolgen                                      │
    │     → Auf interessante Tick-Nummern achten                             │
    │                                                                         │
    │  4. 🧬 BRIDGE-SEEDS weiter testen                                      │
    │     → 165 dokumentierte Bridge-Kandidaten                              │
    │     → Regelmäßig prüfen ob einer aktiviert wird                        │
    │                                                                         │
    │  5. 📝 DOKUMENTATION vervollständigen                                   │
    │     → Forschungsergebnisse in MDX Dateien                              │
    │     → Website aktualisieren                                             │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘
    """)

    # Speichern
    output_path = Path(__file__).parent / "QUBIC_LIVE_MONITOR_RESULTS.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n✓ Ergebnisse gespeichert: {output_path.name}")

    return results

if __name__ == "__main__":
    main()
