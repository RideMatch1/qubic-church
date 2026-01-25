# AIGARTH PRAKTISCHER NUTZUNGSLEITFADEN

**Version:** 1.0
**Datum:** 2026-01-24
**Basierend auf:** Qubic Paper 2018, aigarth-it Bibliothek, Qubic Core Source Code

---

## Teil I: WAS IST AIGARTH?

### Definition
Aigarth (AI Intelligent Tissue) ist ein **ternäres neuronales Netzwerk**, das:
- Auf **Circle-Topologie** basiert (Neuronen in einem Ring angeordnet)
- **Ternäre Werte** (-1, 0, +1) statt binärer verwendet
- **Tick-basiert** arbeitet (läuft bis Konvergenz)
- **Evolutionär trainiert** wird (Mutation + Selektion)
- Für **Hypercomputation** ausgelegt ist (Super-Turing-Complete Tasks)

### Architektur-Übersicht

```
┌─────────────────────────────────────────────────────────────────┐
│                    AIGARTH KREIS-TOPOLOGIE                       │
│                                                                  │
│           Input Neuronen         Output Neuronen                │
│               │                       │                          │
│     ┌─────────▼─────────┬─────────────▼─────────┐               │
│     │    [I₀]──[I₁]──[I₂]──[O₀]──[O₁]──[O₂]    │               │
│     │      ↑              ↑        ↑           │               │
│     │      │    ← CIRCLE →│        │           │               │
│     │      └──────────────┴────────┘           │               │
│     │                                          │               │
│     │  Jedes Neuron ist mit N Nachbarn         │               │
│     │  in beide Richtungen verbunden           │               │
│     └──────────────────────────────────────────┘               │
│                                                                  │
│  TICK-LOOP:                                                      │
│  1. Sammle Nachbar-Zustände                                      │
│  2. Berechne gewichtete Summe                                    │
│  3. Clamp zu ternär (-1, 0, +1)                                  │
│  4. Wiederhole bis Konvergenz                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Teil II: TERNÄRES ENCODING

### Die toTenaryBits Funktion

Dies ist das Herzstück der Qubic/Aigarth Kommunikation:

```python
def to_ternary_bits(number: int, bit_count: int) -> List[int]:
    """
    Konvertiert eine Zahl zu ternären Bits.

    REGEL: Bit 0 → -1, Bit 1 → +1

    Beispiel: 5 = 0b101
    → [+1, -1, +1, -1, -1, -1, -1, -1]  (für 8 bits)
    """
    bits = []
    for i in range(bit_count):
        bit_value = (number >> i) & 1
        bits.append(-1 if bit_value == 0 else 1)
    return bits
```

### Encoding Beispiele

| Dezimal | Binär | Ternär Encoding |
|---------|-------|-----------------|
| 0 | 00000000 | [-1,-1,-1,-1,-1,-1,-1,-1] |
| 1 | 00000001 | [+1,-1,-1,-1,-1,-1,-1,-1] |
| 5 | 00000101 | [+1,-1,+1,-1,-1,-1,-1,-1] |
| 42 | 00101010 | [-1,+1,-1,+1,-1,+1,-1,-1] |
| 127 | 01111111 | [+1,+1,+1,+1,+1,+1,+1,-1] |
| 255 | 11111111 | [+1,+1,+1,+1,+1,+1,+1,+1] |

### Text zu Ternär

```python
def text_to_ternary(text: str) -> List[int]:
    """Konvertiert Text zu ternären Bits."""
    bits = []
    for char in text.encode('utf-8'):
        bits.extend(to_ternary_bits(char, 8))
    return bits

# Beispiel: "cfb" →
# 'c' = 99  → [+1,+1,-1,-1,-1,+1,+1,-1]
# 'f' = 102 → [-1,+1,+1,-1,-1,+1,+1,-1]
# 'b' = 98  → [-1,+1,-1,-1,-1,+1,+1,-1]
```

---

## Teil III: DIE ANNA MATRIX ALS GEWICHTE

### Matrix-Struktur

Die Anna Matrix (128×128) enthält signed bytes (-128 bis +127):

```
┌─────────────────────────────────────────────────────────────────┐
│                    ANNA MATRIX (128×128)                         │
│                                                                  │
│  ┌───┬───┬───┬───┬───┬───┬─────────────────────────┬───┬───┐    │
│  │-68│-82│-27│-82│-6 │-82│  ...  ...  ...  ...     │ 62│ 67│ r=0│
│  ├───┼───┼───┼───┼───┼───┼─────────────────────────┼───┼───┤    │
│  │-67│-61│-92│-61│-123│-48│ ...  ...  ...  ...     │ 61│ 66│ r=1│
│  ├───┼───┼───┼───┼───┼───┼─────────────────────────┼───┼───┤    │
│  │...│...│...│...│...│...│ ...  ...  ...  ...     │...│...│    │
│  ├───┼───┼───┼───┼───┼───┼─────────────────────────┼───┼───┤    │
│  │ 66│ 60│ 91│ 60│122│ 47│ ...  ...  ...  ...     │-68│-67│ r=127│
│  └───┴───┴───┴───┴───┴───┴─────────────────────────┴───┴───┘    │
│    c=0 c=1 c=2 c=3 c=4 c=5                          c=126 c=127  │
│                                                                  │
│  EIGENSCHAFTEN:                                                  │
│  • 99.58% Punkt-Symmetrie: matrix[r][c] + matrix[127-r][127-c] = -1│
│  • 26 "Dark Cells" (Wert 0)                                      │
│  • 8186 negative, 8172 positive Werte                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Matrix als Neuronale Gewichte Interpretation

**Hypothese:** Jede Zeile/Spalte der Matrix könnte Synapsen-Gewichte für Aigarth-Neuronen darstellen.

```python
def matrix_to_weights(matrix, row_idx):
    """
    Konvertiert eine Matrix-Zeile zu ternären Gewichten.

    Die signed bytes (-128 bis +127) werden zu ternär geclamped:
    - Werte > 0 → +1
    - Werte = 0 → 0
    - Werte < 0 → -1
    """
    return [
        1 if v > 0 else (-1 if v < 0 else 0)
        for v in matrix[row_idx]
    ]
```

---

## Teil IV: DER TICK-LOOP ALGORITHMUS

### Offizieller Algorithmus (aus aigarth-it)

```python
def feedforward(self, feed):
    """
    Der ECHTE Aigarth Feedforward-Algorithmus.
    Läuft MEHRERE TICKS bis Konvergenz!
    """
    # 1. Alle Neuronen auf 0 zurücksetzen
    for n in self._circle:
        n.state = 0

    # 2. Input-Werte an Input-Neuronen zuweisen
    for i, value in enumerate(feed):
        self._neurons_i[i].state = value

    # 3. TICK-LOOP (das Kernstück!)
    for tick in range(self.ff_cycle_cap):  # Bis zu 1,000,000 Ticks!

        # 3a. Berechne nächsten Zustand für alle Neuronen
        for i, n in enumerate(self._circle):
            n_feed = self.get_neuron_feed(i)  # Nachbar-Zustände
            n.feedforward(n_feed)              # Gewichtete Summe → Clamp

        # 3b. Commit alle Zustände (atomar)
        any_changed = False
        for n in self._circle:
            n_state, changed = n.commit_state()
            if changed:
                any_changed = True

        # 3c. ABBRUCHBEDINGUNGEN

        # Bedingung 1: Alle Output-Neuronen non-zero → FERTIG
        if all(n.state != 0 for n in self._neurons_o):
            break

        # Bedingung 2: Keine Änderungen → KONVERGENZ
        if not any_changed:
            break

        # Bedingung 3: Max Ticks erreicht → TIMEOUT

    # 4. Output extrahieren
    return tuple([n.state for n in self._neurons_o])
```

### Neuron Feedforward

```python
def feedforward(self, feed):
    """
    Einzelnes Neuron: Gewichtete Summe → Ternäres Clamping
    """
    # Gewichtete Summe der Inputs
    total = sum(f * w for f, w in zip(feed, self.input_weights))

    # Ternäres Clamping
    if total > 0:
        self._state_next = 1
    elif total < 0:
        self._state_next = -1
    else:
        self._state_next = 0

    return self._state_next
```

---

## Teil V: PRAKTISCHE ANWENDUNGEN

### 1. Matrix-Koordinaten Abfragen (Anna Bot)

Der Anna Bot (@QubicAigarth auf Twitter) akzeptiert Koordinaten-Queries:

```
Format: <row>+<column>

Beispiel: "6+33"
Antwort: Collision Value at [6,33] = 26
```

### 2. GENESIS Token Monitoring

```python
# GENESIS Token Adresse
address = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"

# POCC Prefix Dekodierung
P = 15  # 16. Buchstabe
O = 14  # 15. Buchstabe
C = 2   # 3. Buchstabe
C = 2   # 3. Buchstabe
POCC_SUM = 15 + 14 + 2 + 2 = 33

# Matrix Lookup
matrix[6][33] = 26

# Verbindung zu Qubic
26² = 676 = Qubic Computors
```

### 3. Lokale Aigarth-Instanz Erstellen

```python
from aigarth_it import AigarthITUCl

# Erstelle Aigarth Netzwerk
itu = AigarthITUCl(
    itu_group="test",
    input_bitwidth=64,   # 64 Input-Neuronen
    output_bitwidth=64   # 64 Output-Neuronen
)

# Input vorbereiten (ternäre Bits)
input_data = text_to_ternary("cfb")

# Feedforward (mit Tick-Loop!)
output, stats = itu.feedforward(tuple(input_data))

print(f"Ticks: {stats.tick_count}")
print(f"Abbruchgrund: {stats.end_reason}")
print(f"Output: {output}")
```

### 4. Evolutionäres Training

```python
# Training durch Mutation
for episode in range(1000):
    # Mutation: Ein zufälliges Gewicht ändern
    itu.mutate(
        training_episode=episode,
        training_season="season_1"
    )

    # Evaluieren
    output, stats = itu.feedforward(test_input)

    # Fitness berechnen
    fitness = calculate_fitness(output, expected_output)

    # Nur die besten behalten (Selektion)
    if fitness > best_fitness:
        best_itu = itu.copy()
```

---

## Teil VI: DIE XOR-NACHRICHT

### AI.MEG.GOU Entschlüsselung

Die Matrix enthält eine versteckte Nachricht, die durch XOR von Spalten 30 und 97 sichtbar wird:

```python
# XOR der Spalten 30 und 97
message = []
for row in range(128):
    xor_value = matrix[row][30] ^ matrix[row][97]
    message.append(chr(xor_value) if 32 <= xor_value <= 126 else '?')

# Ergebnis enthält: "AI.MEG.GOU" und weitere kodierte Daten
```

### Was bedeutet AI.MEG.GOU?

| Teil | Interpretation |
|------|----------------|
| AI | Artificial Intelligence |
| MEG | Meg = 10⁶ (Mega) oder "Megabyte" |
| GOU | Government of Universe? Gödel? Unknown |

Zusammen: **AIGARTH Signatur** in der Matrix.

---

## Teil VII: TIME-LOCK MECHANISMUS

### März 3, 2026

```
Bitcoin Genesis:     03.01.2009
Time-Lock Datum:     03.03.2026
Differenz:           6,267 Tage

6267 = 3 × 2089 (2089 ist Primzahl)
6267 mod 127 = 52
6267 mod 128 = 123
```

### Countdown

```python
from datetime import datetime

bitcoin_genesis = datetime(2009, 1, 3)
timelock_date = datetime(2026, 3, 3)
today = datetime.now()

days_remaining = (timelock_date - today).days
# Aktuell: 38 Tage (Stand: 24.01.2026)
```

### Was passiert am 03.03.2026?

**Hypothesen:**
1. **Aigarth Activation** - Das System wird "live" geschaltet
2. **Schlüssel-Freigabe** - Ein kryptographischer Schlüssel wird verfügbar
3. **Message Reveal** - Eine versteckte Nachricht wird entschlüsselbar
4. **Nichts** - Es ist nur eine mathematische Curiosität

---

## Teil VIII: HISTORISCHER KONTEXT

### Timeline

```
1998    CFB beginnt ternäre Computerforschung
        └── Ursprung der Jinn/Aigarth Vision

2008    Bitcoin Whitepaper
        └── Satoshi Nakamoto publiziert
        └── "15ubicBBW..." = QUBIC (QWERTY Substitution)

2009    Bitcoin Genesis
        └── 03. Januar 2009
        └── Block 576 enthält 0x1b Byte (= 27)

2013    NXT Genesis (CFB)
        └── Curve25519, 121665 Konstante
        └── 121 = 11² erscheint in Anna Matrix

2015    IOTA (CFB)
        └── Balanced Ternary
        └── Tangle-Architektur

2018    Qubic Paper
        └── "before focusing on the matrix"
        └── Aigarth als Hypercomputer beschrieben

2024    Qubic Mainnet
        └── 676 Computors = 26²
        └── 17. April 2024

2026    TIME-LOCK
        └── 03. März 2026
        └── 6267 Tage seit Bitcoin Genesis
```

### CFB's Vermächtnis

Sergey Ivancheglo (Come-From-Beyond) hat über 20 Jahre an diesem System gearbeitet:
- **NXT** (2013) - Proof-of-Stake Pionier
- **IOTA** (2015) - Ternär, Tangle
- **Qubic** (2018-2024) - Aigarth, 676 Computors
- **Anna Matrix** - Das "Buch" das gelesen werden kann

---

## Teil IX: SYSTEM-FÄHIGKEITEN

### Was kann Aigarth (theoretisch)?

1. **Hypercomputation**
   - Super-Turing-Complete Tasks
   - Σ⁰₁ und Π⁰₁ Formeln berechenbar
   - Random Oracle Computer

2. **Distributed AI**
   - 676 Computors als verteiltes neuronales Netz
   - Quorum-basierte Consensus (2/3)
   - Fehlertolerant durch Redundanz

3. **IoT Swarm Intelligence**
   - Autonome Fahrzeug-Netzwerke
   - Schwarm-Koordination
   - Dezentrale Entscheidungsfindung

4. **Kryptographische Primitive**
   - Zufallszahlen-Orakel
   - Signatur-Verifizierung
   - Zeit-basierte Freischaltung

### Aktuelle Limitierungen

1. **Kein öffentlicher Aigarth-Zugang** - Das Netz ist nicht direkt querybar
2. **Unbekanntes Training** - Die Gewichte sind möglicherweise vortrainiert
3. **Fehlende Dokumentation** - Vieles ist Reverse-Engineering

---

## Teil X: PRAKTISCHE EXPERIMENTE

### Experiment 1: Matrix-Symmetrie Verifizieren

```python
import json

with open('anna-matrix.json') as f:
    data = json.load(f)
    matrix = data['matrix']

symmetric_count = 0
for r in range(128):
    for c in range(128):
        val1 = matrix[r][c]
        val2 = matrix[127-r][127-c]
        if val1 + val2 == -1:
            symmetric_count += 1

print(f"Symmetrische Paare: {symmetric_count} / 16384")
# Ergebnis: 16316 / 16384 = 99.58%
```

### Experiment 2: Dark Cells Finden

```python
dark_cells = []
for r in range(128):
    for c in range(128):
        if matrix[r][c] == 0:
            dark_cells.append((r, c))

print(f"Dark Cells: {len(dark_cells)}")
# Ergebnis: 26 Zellen mit Wert 0
```

### Experiment 3: XOR-Nachricht Extrahieren

```python
xor_result = []
for r in range(128):
    xor = matrix[r][30] ^ matrix[r][97]
    xor_result.append(chr(xor) if 32 <= xor <= 126 else '.')

print(''.join(xor_result))
# Enthält: AI.MEG.GOU
```

---

## Teil XI: ZUSAMMENFASSUNG

### Das System in einem Satz

**Aigarth ist ein ternäres, evolutionär trainiertes, verteiltes neuronales Netzwerk, das auf der Anna Matrix basiert und Hypercomputation ermöglichen soll.**

### Schlüsselerkenntnisse

| Aspekt | Erkenntnis |
|--------|-----------|
| **Encoding** | 0→-1, 1→+1 (toTenaryBits) |
| **Topologie** | Circle (Ring von Neuronen) |
| **Algorithmus** | Multi-Tick Feedforward bis Konvergenz |
| **Training** | Evolutionär (Mutation + Selektion) |
| **Matrix** | 128×128 mit 99.58% Punkt-Symmetrie |
| **Computors** | 676 = 26² |
| **Time-Lock** | 03.03.2026 (38 Tage) |

### Offene Fragen

1. Wie kommuniziert man direkt mit Aigarth?
2. Was sind die korrekten Netzwerk-Parameter?
3. Was passiert am Time-Lock Datum?
4. Wie wurde die Matrix trainiert/generiert?

---

## ANHANG: CODE-SNIPPETS

### A. Vollständiger Ternär-Encoder

```python
def to_ternary_bits(number: int, bit_count: int) -> list:
    return [(-1 if ((number >> i) & 1) == 0 else 1) for i in range(bit_count)]

def from_ternary_bits(bits: list) -> int:
    result = 0
    for i, bit in enumerate(bits):
        if bit > 0:
            result |= (1 << i)
    return result
```

### B. Matrix Loader

```python
import json

def load_anna_matrix(path: str):
    with open(path) as f:
        data = json.load(f)
    return data['matrix']
```

### C. Minimaler Aigarth Simulator

```python
class SimpleAigarth:
    def __init__(self, weights):
        self.weights = weights

    def feedforward(self, inputs, max_ticks=1000):
        state = [0] * len(self.weights)
        for tick in range(max_ticks):
            next_state = []
            for i in range(len(state)):
                total = sum(inputs[j] * self.weights[i][j] for j in range(len(inputs)))
                next_state.append(1 if total > 0 else (-1 if total < 0 else 0))
            if next_state == state:
                break
            state = next_state
        return state
```

---

**DEEPER. FASTER. HIGHER. DIVINE.**

*37 Tage bis Time-Lock: 03. März 2026*

---

*Dokumentiert am 2026-01-24*
*Basierend auf: Qubic Paper 2018, aigarth-it Library, Qubic Core Source*
