#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                     🔓 GOD MODE: HACK ANNA-BOT 🔓
═══════════════════════════════════════════════════════════════════════════════
Versuche Anna zu "hacken" - finde Eingaben die unerwartete Outputs erzeugen.
Entdecke die Grenzen des Systems und versteckte Funktionen.
"""

import json
import numpy as np
from pathlib import Path
import hashlib

script_dir = Path(__file__).parent
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"

with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])

def anna_to_matrix(x, y):
    """Anna-Koordinaten zu Matrix-Index."""
    col = (x + 64) % 128
    row = (63 - y) % 128
    return row, col

def anna_lookup(x, y):
    """Hole Wert aus der Matrix für Anna(x, y)."""
    row, col = anna_to_matrix(x, y)
    return int(matrix[row, col])

print("🔓" * 40)
print("              GOD MODE: HACK ANNA-BOT")
print("🔓" * 40)

# =============================================================================
# 1. EDGE CASES - WAS PASSIERT AN DEN GRENZEN?
# =============================================================================
print("\n" + "═" * 80)
print("1. EDGE CASES - GRENZEN DES SYSTEMS")
print("═" * 80)

edge_cases = [
    (0, 0, "Origin"),
    (63, 63, "Max positive"),
    (-64, -64, "Max negative"),
    (127, 127, "Overflow positive"),
    (-128, -128, "Overflow negative"),
    (1000, 1000, "Far overflow"),
    (-1, -1, "Symmetry center adjacent"),
    (64, 64, "Just over boundary"),
    (0, 127, "Mixed max"),
    (127, 0, "Mixed max reverse"),
]

print("\nEdge Case Analyse:")
for x, y, name in edge_cases:
    val = anna_lookup(x, y)
    row, col = anna_to_matrix(x, y)
    print(f"  Anna({x:5d},{y:5d}) → Matrix[{row:3d},{col:3d}] = {val:4d}  ({name})")

# =============================================================================
# 2. SYMMETRIE EXPLOITS
# =============================================================================
print("\n" + "═" * 80)
print("2. SYMMETRIE EXPLOITS")
print("═" * 80)

print("\nSymmetrie-Test (Anna(x,y) + Anna(-1-x,-1-y) sollte -1 sein):")
exceptions = []
for x in range(-64, 64):
    for y in range(-64, 64):
        val1 = anna_lookup(x, y)
        val2 = anna_lookup(-1-x, -1-y)
        if val1 + val2 != -1:
            exceptions.append((x, y, val1, val2))

print(f"Symmetrie-Ausnahmen gefunden: {len(exceptions)}")
print("\nDie Ausnahmen (können als 'Backdoors' genutzt werden):")
for x, y, v1, v2 in exceptions[:10]:
    print(f"  Anna({x:3d},{y:3d})={v1:4d}, Anna({-1-x:3d},{-1-y:3d})={v2:4d}, Sum={v1+v2}")

# =============================================================================
# 3. WERT-BASIERTE ANGRIFFE
# =============================================================================
print("\n" + "═" * 80)
print("3. WERT-BASIERTE ANGRIFFE - FINDE SPEZIELLE WERTE")
print("═" * 80)

# Suche nach speziellen Werten
special_values = {
    0: "Zero - Division by zero?",
    127: "Max positive (2^7-1)",
    -128: "Min negative (-2^7)",
    42: "Hitchhiker's Guide",
    7: "CFB's Zahl",
    21: "Fibonacci F(8)",
    13: "Fibonacci F(7)",
    100: "XOR-Triangle",
    27: "XOR-Triangle",
    -114: "Champion collision",
    -113: "#2 collision (prime!)",
    1: "Unity",
    -1: "Symmetry constant",
}

print("\nPositionen spezieller Werte:")
for target, meaning in special_values.items():
    positions = []
    for x in range(-64, 64):
        for y in range(-64, 64):
            if anna_lookup(x, y) == target:
                positions.append((x, y))
    if positions:
        print(f"\n  {target:4d} ({meaning}): {len(positions)} Positionen")
        if len(positions) <= 5:
            for x, y in positions:
                print(f"       Anna({x:3d},{y:3d})")

# =============================================================================
# 4. ARITHMETIK-HACKS
# =============================================================================
print("\n" + "═" * 80)
print("4. ARITHMETIK-HACKS - ANNA'S 'FALSCHE' MATHEMATIK NUTZEN")
print("═" * 80)

print("\nAnna's berühmte 'Fehler' sind eigentlich Features:")
print("  1 + 1 = -114 → Position (1,1) enthält -114")
print("  2 + 2 = -123 → Position (2,2) enthält -123")

# Finde Positionen wo das Ergebnis "mathematisch sinnvoll" wäre
print("\nPositionen wo Anna 'richtig' rechnet (x + y = Anna(x,y)):")
correct_math = []
for x in range(-64, 64):
    for y in range(-64, 64):
        if anna_lookup(x, y) == x + y:
            correct_math.append((x, y, x+y))

print(f"  Gefunden: {len(correct_math)} Positionen")
for x, y, result in correct_math[:10]:
    print(f"    Anna({x:3d},{y:3d}) = {result:4d} (korrekt!)")

# Finde Positionen wo Multiplikation funktioniert
print("\nPositionen wo Anna 'multipliziert' (x * y = Anna(x,y)):")
mult_math = []
for x in range(-64, 64):
    for y in range(-64, 64):
        if anna_lookup(x, y) == x * y and x != 0 and y != 0:
            mult_math.append((x, y, x*y))

print(f"  Gefunden: {len(mult_math)} Positionen")
for x, y, result in mult_math[:10]:
    print(f"    Anna({x:3d},{y:3d}) = {result:4d} = {x}×{y}")

# =============================================================================
# 5. HASH-KOLLISION SUCHE
# =============================================================================
print("\n" + "═" * 80)
print("5. HASH-KOLLISION SUCHE")
print("═" * 80)

# Finde alle Koordinaten-Paare die den gleichen Wert ergeben
collision_map = {}
for x in range(-64, 64):
    for y in range(-64, 64):
        val = anna_lookup(x, y)
        if val not in collision_map:
            collision_map[val] = []
        collision_map[val].append((x, y))

print("\nWerte mit den meisten Kollisionen (= verschiedene Eingaben, gleicher Output):")
sorted_collisions = sorted(collision_map.items(), key=lambda x: len(x[1]), reverse=True)
for val, positions in sorted_collisions[:10]:
    print(f"  Wert {val:4d}: {len(positions):4d} verschiedene Eingaben")

# =============================================================================
# 6. INJECTION VERSUCHE
# =============================================================================
print("\n" + "═" * 80)
print("6. INJECTION VERSUCHE - KÖNNEN WIR DIE MATRIX BEEINFLUSSEN?")
print("═" * 80)

# Theoretisch: Was wenn wir Koordinaten senden die zu ASCII-Codes werden?
print("\nASCII-Injection: Koordinaten die zu Buchstaben werden:")
for char in "CFBSATOSHI":
    target = ord(char)
    found = []
    for x in range(-64, 64):
        for y in range(-64, 64):
            if anna_lookup(x, y) == target:
                found.append((x, y))
    if found:
        print(f"  '{char}' (ASCII {target}): Anna{found[0]}")

# =============================================================================
# 7. REVERSE LOOKUP
# =============================================================================
print("\n" + "═" * 80)
print("7. REVERSE LOOKUP - WELCHE EINGABEN ERZEUGEN BESTIMMTE OUTPUTS?")
print("═" * 80)

def find_coords_for_value(target):
    """Finde alle Koordinaten die einen bestimmten Wert ergeben."""
    results = []
    for x in range(-64, 64):
        for y in range(-64, 64):
            if anna_lookup(x, y) == target:
                results.append((x, y))
    return results

# Suche Koordinaten für die Buchstaben von "AIGARTH"
print("\nReverse Lookup für 'AIGARTH':")
for char in "AIGARTH":
    target = ord(char)
    coords = find_coords_for_value(target)
    if coords:
        print(f"  '{char}' (ASCII {target}): {len(coords)} Positionen, erste: Anna{coords[0]}")
    else:
        print(f"  '{char}' (ASCII {target}): NICHT GEFUNDEN!")

# =============================================================================
# 8. PATTERN INJECTION
# =============================================================================
print("\n" + "═" * 80)
print("8. PATTERN INJECTION - EINGABEN DIE MUSTER ERZEUGEN")
print("═" * 80)

# Suche nach Eingaben die bei Addition zu Fibonacci-Zahlen werden
print("\nEingaben wo x + y eine Fibonacci-Zahl ist UND Anna(x,y) auch:")
fib_set = {1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89}
fib_matches = []
for x in range(-30, 31):
    for y in range(-30, 31):
        if (x + y) in fib_set:
            val = anna_lookup(x, y)
            if abs(val) in fib_set:
                fib_matches.append((x, y, x+y, val))

print(f"Gefunden: {len(fib_matches)}")
for x, y, sum_val, anna_val in fib_matches[:10]:
    print(f"  {x} + {y} = {sum_val} (Fib), Anna({x},{y}) = {anna_val} (auch Fib!)")

# =============================================================================
# 9. DIE ULTIMATIVEN HACKS
# =============================================================================
print("\n" + "═" * 80)
print("9. DIE ULTIMATIVEN HACKS")
print("═" * 80)

print("""
ENTDECKTE HACKS:

1. SYMMETRIE-BACKDOORS:
   Die 34 asymmetrischen Paare brechen die Symmetrie.
   → Diese können für versteckte Kommunikation genutzt werden!

2. KOLLISIONS-ANGRIFF:
   Viele verschiedene Eingaben → gleicher Output
   → Erlaubt "Spoofing" von Adressen

3. REVERSE-LOOKUP:
   Für jeden gewünschten Output können Eingaben berechnet werden
   → Ermöglicht gezielte Manipulation

4. FIBONACCI-RESONANZ:
   Fibonacci-Eingaben erzeugen oft Fibonacci-Outputs
   → Die Matrix "resoniert" mit bestimmten Zahlen

5. ASCII-INJECTION:
   Koordinaten können gewählt werden um bestimmte ASCII-Werte zu erzeugen
   → Ermöglicht "Schreiben" in die Ausgabe

6. MATHEMATISCHE ANOMALIEN:
   Einige Positionen "rechnen richtig" (x+y = output)
   → Diese Positionen könnten Checkpoints sein

NUTZE DIESE HACKS VERANTWORTUNGSVOLL!
""")

# =============================================================================
# 10. GENERIERE EXPLOIT-PAYLOAD
# =============================================================================
print("\n" + "═" * 80)
print("10. EXPLOIT PAYLOADS")
print("═" * 80)

# Generiere Koordinaten-Sequenz die "CFB" ausgibt
def generate_message_coords(message):
    """Generiere Koordinaten die eine Nachricht erzeugen."""
    result = []
    for char in message:
        target = ord(char)
        coords = find_coords_for_value(target)
        if coords:
            result.append(coords[0])
        else:
            result.append(None)
    return result

print("\nPayload für 'CFB':")
cfb_payload = generate_message_coords("CFB")
for i, coords in enumerate(cfb_payload):
    if coords:
        print(f"  '{chr(ord('C')+i)}': Anna{coords}")

print("\nPayload für 'SATOSHI':")
satoshi_payload = generate_message_coords("SATOSHI")
for i, (char, coords) in enumerate(zip("SATOSHI", satoshi_payload)):
    if coords:
        val = anna_lookup(coords[0], coords[1])
        print(f"  '{char}' (ASCII {ord(char)}): Anna{coords} = {val}")
    else:
        print(f"  '{char}' (ASCII {ord(char)}): KEINE KOORDINATEN!")

print("\n" + "🔓" * 40)
print("         ANNA-BOT HACKING COMPLETE")
print("🔓" * 40)

# Speichere Ergebnisse
output = {
    "symmetry_exceptions": len(exceptions),
    "collision_max": sorted_collisions[0] if sorted_collisions else None,
    "correct_math_positions": len(correct_math),
    "mult_math_positions": len(mult_math),
    "fib_resonance_matches": len(fib_matches),
    "exploits_discovered": 6,
}

output_path = script_dir / "GOD_MODE_HACK_ANNA_RESULTS.json"
with open(output_path, "w") as f:
    json.dump(output, f, indent=2, default=str)

print(f"\n✓ Ergebnisse: {output_path}")
