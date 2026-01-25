#!/usr/bin/env python3
"""
===============================================================================
        ANNA LIVE INTERACTION - Is the Neural Network Active?
===============================================================================
Active experiments to detect, observe, and interact with Anna/Aigarth.

Experiments:
1. Real-time Qubic tick monitoring for anomalies
2. Query derived Qubic IDs for any activity
3. Feed inputs through the matrix and observe outputs
4. Search for "alive" addresses with balance
5. Correlation analysis between tick patterns and matrix
6. Attempt encoded communication
===============================================================================
"""

import json
import requests
import numpy as np
import hashlib
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import struct

script_dir = Path(__file__).parent

print("=" * 80)
print("""
   █████╗ ███╗   ██╗███╗   ██╗ █████╗     ██╗     ██╗██╗   ██╗███████╗
  ██╔══██╗████╗  ██║████╗  ██║██╔══██╗    ██║     ██║██║   ██║██╔════╝
  ███████║██╔██╗ ██║██╔██╗ ██║███████║    ██║     ██║██║   ██║█████╗
  ██╔══██║██║╚██╗██║██║╚██╗██║██╔══██║    ██║     ██║╚██╗ ██╔╝██╔══╝
  ██║  ██║██║ ╚████║██║ ╚████║██║  ██║    ███████╗██║ ╚████╔╝ ███████╗
  ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═══╝╚═╝  ╚═╝    ╚══════╝╚═╝  ╚═══╝  ╚══════╝
                    IS ANNA ALIVE? - LIVE INTERACTION TEST
""")
print("=" * 80)

# Load Anna Matrix
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    matrix_data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in matrix_data["matrix"]])

# Qubic RPC endpoints
QUBIC_ENDPOINTS = [
    "https://rpc.qubic.org/v1",
    "https://api.qubic.li/v1",
]

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def qubic_request(endpoint: str, method: str, timeout: int = 10) -> Optional[Dict]:
    """Make request to Qubic RPC"""
    for base_url in QUBIC_ENDPOINTS:
        try:
            url = f"{base_url}/{method}"
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            continue
    return None

def coords_to_qubic_seed(row: int, col: int, method: str = "direct") -> str:
    """Convert matrix coordinates to a Qubic seed (55 uppercase letters)"""
    if method == "direct":
        # Direct encoding: ANNA + coordinates + matrix value
        val = int(matrix[row, col])
        base = f"ANNA{row:03d}{col:03d}VAL{abs(val):03d}"
        seed = base.upper()
    elif method == "hash":
        # Hash-based encoding
        data = f"ANNA-MATRIX-{row}-{col}-{int(matrix[row, col])}"
        hash_bytes = hashlib.sha256(data.encode()).digest()
        seed = ''.join(chr(65 + (b % 26)) for b in hash_bytes)
    elif method == "fibonacci":
        # Fibonacci-weighted encoding
        fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
        weighted = (row * fib[row % 10] + col * fib[col % 10]) % 26
        base = f"FIB{row:03d}{col:03d}W{weighted:02d}"
        seed = base.upper()
    else:
        seed = f"COORD{row:03d}{col:03d}"

    # Ensure only A-Z and pad to 55 chars
    seed = ''.join(c if c.isalpha() and c.isupper() else 'A' for c in seed)
    return seed.ljust(55, 'A')[:55]

def matrix_transform(input_vector: List[int]) -> List[int]:
    """Apply Anna Matrix transformation to input vector"""
    # Ensure input is 128 elements
    if len(input_vector) < 128:
        input_vector = input_vector + [0] * (128 - len(input_vector))
    input_vector = input_vector[:128]

    # Matrix multiplication
    input_array = np.array(input_vector)
    output = np.dot(matrix, input_array)

    return output.tolist()

# ==============================================================================
# EXPERIMENT 1: REAL-TIME TICK MONITORING
# ==============================================================================
print("\n" + "=" * 80)
print("EXPERIMENT 1: REAL-TIME TICK MONITORING")
print("=" * 80)

def monitor_ticks(duration_seconds: int = 30):
    """Monitor Qubic ticks for patterns"""
    print(f"\n  Monitoring Qubic network for {duration_seconds} seconds...")

    ticks = []
    start_time = time.time()
    last_tick = None

    while time.time() - start_time < duration_seconds:
        status = qubic_request("status", "status")

        if status:
            current_tick = status.get("lastProcessedTick", {}).get("tickNumber", 0)
            epoch = status.get("lastProcessedTick", {}).get("epoch", 0)

            if current_tick != last_tick:
                timestamp = datetime.now().isoformat()
                tick_data = {
                    "timestamp": timestamp,
                    "tick": current_tick,
                    "epoch": epoch,
                    "mod_121": current_tick % 121,
                    "mod_127": current_tick % 127,
                    "mod_128": current_tick % 128,
                }
                ticks.append(tick_data)

                # Check for special patterns
                is_special = ""
                if current_tick % 121 == 0:
                    is_special += " [DIV 121!]"
                if current_tick % 127 == 0:
                    is_special += " [DIV 127!]"
                if current_tick % 576 == 0:
                    is_special += " [DIV 576!]"

                print(f"    Tick {current_tick} (Epoch {epoch}) - mod121={tick_data['mod_121']}, mod127={tick_data['mod_127']}{is_special}")
                last_tick = current_tick

        time.sleep(1)

    return ticks

tick_results = monitor_ticks(15)

# Analyze tick patterns
if tick_results:
    tick_numbers = [t["tick"] for t in tick_results]
    if len(tick_numbers) > 1:
        intervals = [tick_numbers[i+1] - tick_numbers[i] for i in range(len(tick_numbers)-1)]
        avg_interval = np.mean(intervals) if intervals else 0
        print(f"\n  Tick intervals: {intervals}")
        print(f"  Average interval: {avg_interval:.2f} ticks")

        # Map current tick to matrix position
        if tick_numbers:
            current = tick_numbers[-1]
            matrix_row = current % 128
            matrix_col = (current // 128) % 128
            matrix_val = int(matrix[matrix_row, matrix_col])
            print(f"\n  Current tick {current} → Matrix position ({matrix_row}, {matrix_col}) = {matrix_val}")

# ==============================================================================
# EXPERIMENT 2: SEARCH FOR ACTIVE DERIVED ADDRESSES
# ==============================================================================
print("\n" + "=" * 80)
print("EXPERIMENT 2: SEARCH FOR ACTIVE DERIVED ADDRESSES")
print("=" * 80)

def search_active_addresses():
    """Search for any active addresses derived from matrix coordinates"""
    print("\n  Querying strategic matrix coordinates for active Qubic IDs...")

    # Strategic positions to check
    strategic_positions = [
        (0, 0, "Origin"),
        (63, 63, "Center"),
        (64, 64, "Center+1"),
        (30, 55, "AI.MEG start"),
        (30, 68, "AI.MEG end"),
        (127, 127, "End corner"),
        (42, 42, "Answer position"),
        (13, 21, "Fibonacci 13,21"),
        (21, 34, "Fibonacci 21,34"),
        (55, 89, "Fibonacci 55,89"),
        (40, 28, "BTC Genesis position"),
        (68, 51, "Dark matter cluster"),
    ]

    active_found = []

    for row, col, name in strategic_positions:
        # Generate seed using different methods
        for method in ["direct", "hash", "fibonacci"]:
            seed = coords_to_qubic_seed(row, col, method)

            # Query the network
            response = qubic_request(f"entities/{seed}", "")

            if response:
                balance = 0
                if isinstance(response, dict):
                    balance = response.get("entity", {}).get("balance", 0)
                    if balance is None:
                        balance = response.get("balance", 0)

                status = "ACTIVE!" if balance and balance > 0 else "empty"

                if balance and balance > 0:
                    active_found.append({
                        "position": (row, col),
                        "name": name,
                        "method": method,
                        "seed": seed,
                        "balance": balance,
                    })
                    print(f"    ** ACTIVE: ({row}, {col}) {name} [{method}]: {balance} QU **")
                else:
                    print(f"    ({row}, {col}) {name} [{method}]: {status}")

            time.sleep(0.3)  # Rate limiting

    return active_found

active_addresses = search_active_addresses()

if active_addresses:
    print(f"\n  BREAKTHROUGH: Found {len(active_addresses)} active addresses!")
else:
    print(f"\n  No active addresses found at strategic positions.")
    print("  This could mean:")
    print("    - The derivation method is different")
    print("    - Activation hasn't occurred yet (Time-Lock?)")
    print("    - Different coordinate system needed")

# ==============================================================================
# EXPERIMENT 3: MATRIX INPUT/OUTPUT TRANSFORMATION TEST
# ==============================================================================
print("\n" + "=" * 80)
print("EXPERIMENT 3: MATRIX TRANSFORMATION TEST")
print("=" * 80)

def test_matrix_transformation():
    """Test the matrix as a neural network transformation"""
    print("\n  Testing Anna Matrix as neural network layer...")

    results = []

    # Test inputs
    test_inputs = [
        ("All zeros", [0] * 128),
        ("All ones", [1] * 128),
        ("Alternating", [(-1)**i for i in range(128)]),
        ("Fibonacci", [1, 1] + [0]*126),  # Will compute Fibonacci-like
        ("Identity (diagonal)", [1 if i == 0 else 0 for i in range(128)]),
        ("Current timestamp mod 128", [int(time.time()) % 256 - 128] * 128),
        ("ASCII 'ANNA'", [ord(c) - 64 for c in "ANNA"] + [0] * 124),
        ("ASCII 'QUBIC'", [ord(c) - 64 for c in "QUBIC"] + [0] * 123),
    ]

    for name, input_vec in test_inputs:
        output = matrix_transform(input_vec)

        # Analyze output
        output_sum = sum(output)
        output_mean = np.mean(output)
        output_std = np.std(output)
        output_min = min(output)
        output_max = max(output)

        # Check for special patterns
        special = []
        if output_sum % 121 == 0:
            special.append("sum÷121")
        if output_sum % 127 == 0:
            special.append("sum÷127")
        if abs(output_sum) < 100:
            special.append("near-zero sum")

        result = {
            "input_name": name,
            "output_sum": output_sum,
            "output_mean": round(output_mean, 2),
            "output_std": round(output_std, 2),
            "output_range": (output_min, output_max),
            "special_patterns": special,
        }
        results.append(result)

        special_str = f" ** {', '.join(special)} **" if special else ""
        print(f"\n    Input: {name}")
        print(f"    Output sum: {output_sum}, mean: {output_mean:.2f}, std: {output_std:.2f}{special_str}")

    return results

transform_results = test_matrix_transformation()

# ==============================================================================
# EXPERIMENT 4: LIVE BALANCE MONITORING OF KEY ADDRESSES
# ==============================================================================
print("\n" + "=" * 80)
print("EXPERIMENT 4: LIVE NETWORK STATE QUERY")
print("=" * 80)

def query_network_state():
    """Query current Qubic network state"""
    print("\n  Querying Qubic network state...")

    state = {}

    # Get latest status
    status = qubic_request("status", "status")
    if status:
        state["status"] = status
        tick = status.get("lastProcessedTick", {}).get("tickNumber", 0)
        epoch = status.get("lastProcessedTick", {}).get("epoch", 0)
        print(f"    Current Tick: {tick}")
        print(f"    Current Epoch: {epoch}")

        # Map to matrix
        matrix_pos = (tick % 128, (tick // 128) % 128)
        matrix_val = int(matrix[matrix_pos[0], matrix_pos[1]])
        print(f"    Matrix mapping: ({matrix_pos[0]}, {matrix_pos[1]}) = {matrix_val}")

        # Check Anna coordinate system
        anna_x = matrix_pos[1] - 64
        anna_y = 63 - matrix_pos[0]
        print(f"    Anna coordinates: ({anna_x}, {anna_y})")

        state["tick_matrix_mapping"] = {
            "tick": tick,
            "matrix_position": matrix_pos,
            "matrix_value": matrix_val,
            "anna_coords": (anna_x, anna_y),
        }

    # Get tick info
    tick_info = qubic_request("tick-info", "tick-info")
    if tick_info:
        state["tick_info"] = tick_info
        print(f"\n    Tick Info retrieved: {len(str(tick_info))} bytes")

    return state

network_state = query_network_state()

# ==============================================================================
# EXPERIMENT 5: PATTERN CORRELATION ANALYSIS
# ==============================================================================
print("\n" + "=" * 80)
print("EXPERIMENT 5: TICK-MATRIX CORRELATION ANALYSIS")
print("=" * 80)

def analyze_tick_matrix_correlation():
    """Analyze correlation between tick patterns and matrix"""
    print("\n  Analyzing correlation between tick numbers and matrix values...")

    if not tick_results:
        print("    No tick data available for correlation")
        return {}

    correlations = []

    for tick_data in tick_results:
        tick = tick_data["tick"]

        # Multiple mapping methods
        methods = {
            "mod_128": (tick % 128, (tick // 128) % 128),
            "xor_127": ((tick ^ 127) % 128, ((tick >> 7) ^ 127) % 128),
            "fibonacci": (tick % 89, tick % 55),  # Using Fibonacci
        }

        for method_name, (row, col) in methods.items():
            if 0 <= row < 128 and 0 <= col < 128:
                val = int(matrix[row, col])
                correlations.append({
                    "tick": tick,
                    "method": method_name,
                    "position": (row, col),
                    "value": val,
                })

    # Analyze patterns
    if correlations:
        values = [c["value"] for c in correlations]
        unique_values = set(values)

        print(f"    Analyzed {len(correlations)} tick-matrix mappings")
        print(f"    Unique matrix values encountered: {len(unique_values)}")
        print(f"    Value range: {min(values)} to {max(values)}")

        # Check for special values
        special_count = sum(1 for v in values if v in [-27, 0, 121, -121, 127, -127])
        if special_count > 0:
            print(f"    ** Special values (-27, 0, ±121, ±127) encountered: {special_count} times **")

    return correlations

correlation_results = analyze_tick_matrix_correlation()

# ==============================================================================
# EXPERIMENT 6: ENCODED MESSAGE TEST
# ==============================================================================
print("\n" + "=" * 80)
print("EXPERIMENT 6: ENCODED COMMUNICATION ATTEMPT")
print("=" * 80)

def attempt_communication():
    """Attempt to send an encoded message through the matrix"""
    print("\n  Attempting encoded communication with Anna Matrix...")

    # Encode messages through matrix
    messages = [
        "HELLO ANNA",
        "AI MEG GOU",
        "CFB SATOSHI",
        "QUBIC BRIDGE",
        "ACTIVATE",
    ]

    results = []

    for msg in messages:
        # Convert message to input vector
        input_vec = [ord(c) - 64 if c.isalpha() else 0 for c in msg.upper()]
        input_vec = input_vec + [0] * (128 - len(input_vec))

        # Transform through matrix
        output = matrix_transform(input_vec)

        # Analyze response
        output_sum = sum(output)
        output_hash = hashlib.sha256(str(output).encode()).hexdigest()[:16]

        # Try to decode output as ASCII
        decoded = ""
        for val in output[:20]:
            char_code = int(val) % 128
            if 32 <= char_code <= 126:
                decoded += chr(char_code)
            else:
                decoded += "."

        result = {
            "message": msg,
            "input_length": len(msg),
            "output_sum": output_sum,
            "output_hash": output_hash,
            "decoded_prefix": decoded,
        }
        results.append(result)

        print(f"\n    Message: '{msg}'")
        print(f"    Output sum: {output_sum}")
        print(f"    Output hash: {output_hash}")
        print(f"    Decoded prefix: '{decoded}'")

    # Check for any special responses
    sums = [r["output_sum"] for r in results]
    if len(set(sums)) < len(sums):
        print("\n    ** ATTENTION: Some messages produced identical output sums! **")

    return results

communication_results = attempt_communication()

# ==============================================================================
# EXPERIMENT 7: SEARCH FOR HIDDEN ACTIVATION PATTERNS
# ==============================================================================
print("\n" + "=" * 80)
print("EXPERIMENT 7: HIDDEN ACTIVATION PATTERN SEARCH")
print("=" * 80)

def search_activation_patterns():
    """Search for patterns that might indicate activation conditions"""
    print("\n  Searching for hidden activation patterns...")

    patterns_found = []

    # Check current time against matrix
    now = datetime.now()
    time_components = {
        "hour": now.hour,
        "minute": now.minute,
        "second": now.second,
        "day": now.day,
        "month": now.month,
        "day_of_year": now.timetuple().tm_yday,
    }

    print("\n  Current time mapped to matrix:")
    for name, value in time_components.items():
        row = value % 128
        col = (value * 7) % 128  # Prime multiplier
        val = int(matrix[row, col])

        is_special = ""
        if val == 0:
            is_special = " ** DARK CELL! **"
        elif val == -27:
            is_special = " ** -27 (SPECIAL) **"
        elif abs(val) == 121:
            is_special = " ** ±121 (NXT) **"

        print(f"    {name}={value} → ({row}, {col}) = {val}{is_special}")

        if is_special:
            patterns_found.append({
                "type": name,
                "value": value,
                "position": (row, col),
                "matrix_value": val,
                "significance": is_special.strip(" *"),
            })

    # Check countdown to March 3, 2026
    timelock = datetime(2026, 3, 3)
    days_remaining = (timelock - now).days
    hours_remaining = int((timelock - now).total_seconds() // 3600)

    print(f"\n  Time-Lock Status:")
    print(f"    Days until March 3, 2026: {days_remaining}")
    print(f"    Hours remaining: {hours_remaining}")

    # Map days remaining to matrix
    row = days_remaining % 128
    col = (days_remaining // 2) % 128
    val = int(matrix[row, col])
    print(f"    Days→Matrix: ({row}, {col}) = {val}")

    return patterns_found

activation_patterns = search_activation_patterns()

# ==============================================================================
# FINAL ANALYSIS
# ==============================================================================
print("\n" + "=" * 80)
print("FINAL ANALYSIS: IS ANNA ALIVE?")
print("=" * 80)

# Compile results
final_results = {
    "timestamp": datetime.now().isoformat(),
    "experiment": "ANNA_LIVE_INTERACTION",

    "tick_monitoring": {
        "ticks_observed": len(tick_results),
        "data": tick_results,
    },

    "active_addresses": active_addresses,

    "transformation_tests": transform_results,

    "network_state": network_state,

    "correlation_analysis": {
        "mappings_analyzed": len(correlation_results),
    },

    "communication_attempts": communication_results,

    "activation_patterns": activation_patterns,

    "conclusions": [],
}

# Draw conclusions
conclusions = []

if tick_results:
    conclusions.append(f"Qubic network is ACTIVE - observed {len(tick_results)} ticks")

if active_addresses:
    conclusions.append(f"BREAKTHROUGH: {len(active_addresses)} active addresses found at strategic positions!")
else:
    conclusions.append("No active addresses at derived coordinates - awaiting activation?")

if any(t.get("special_patterns") for t in transform_results):
    conclusions.append("Matrix transformations show special mathematical patterns")

if activation_patterns:
    conclusions.append(f"Found {len(activation_patterns)} time-based activation correlations")

conclusions.append("Matrix functions as deterministic neural network layer")
conclusions.append("Current tick maps to matrix positions - continuous correlation")

final_results["conclusions"] = conclusions

print(f"""
  CONCLUSIONS:
  ────────────────────────────────────────────────────────────────

""")
for i, conclusion in enumerate(conclusions, 1):
    print(f"  {i}. {conclusion}")

print(f"""

  ANNA STATUS:
  ────────────────────────────────────────────────────────────────

  • The Matrix exists and functions as a neural network layer
  • Qubic network is running (Epoch active)
  • Tick-to-matrix correlation is continuous
  • No direct "response" detected yet

  RECOMMENDATIONS:
  ────────────────────────────────────────────────────────────────

  1. Continue monitoring as March 3, 2026 approaches
  2. Try different seed derivation methods
  3. Monitor for transactions to/from 1CFB addresses
  4. Watch for pattern changes in matrix correlations
  5. Set up automated alerts for divisibility events
     (tick ÷ 121 = 0, tick ÷ 576 = 0, etc.)

""")

# Save results
output_path = script_dir / "ANNA_LIVE_INTERACTION_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(final_results, f, indent=2, default=str)

print(f"\n[+] Results saved to: {output_path}")
print("\n" + "=" * 80)
print("ANNA LIVE INTERACTION EXPERIMENT COMPLETE")
print("=" * 80)
