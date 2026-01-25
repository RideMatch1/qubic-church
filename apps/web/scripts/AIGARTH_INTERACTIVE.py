#!/usr/bin/env python3
"""
===============================================================================
            🎮 AIGARTH INTERACTIVE CLI 🎮
===============================================================================
Real-time interaction with the Anna neural network.
Type anything and see how the network responds!
"""

import json
import hashlib
import numpy as np
from pathlib import Path
import sys
import time

script_dir = Path(__file__).parent

# Setup
matrix_path = script_dir.parent / "public" / "data" / "anna-matrix.json"
with open(matrix_path) as f:
    data = json.load(f)

def safe_int(v):
    return 0 if isinstance(v, str) else int(v)

matrix = np.array([[safe_int(v) for v in row] for row in data["matrix"]])
ternary_matrix = np.sign(matrix).astype(int)

try:
    from aigarth_it.neuron_cl import AITClNeuron
    neurons = [AITClNeuron(input_weights=ternary_matrix[i].tolist(), input_skew=0) for i in range(128)]
except ImportError:
    print("❌ Aigarth not available. Install with: pip install aigarth-it")
    sys.exit(1)

def bytes_to_trits(data, length=128):
    trits = []
    for byte in data:
        trits.append((byte % 3) - 1)
        trits.append(((byte // 3) % 3) - 1)
        trits.append(((byte // 9) % 3) - 1)
    return (trits + [0] * length)[:length]

def process(input_data):
    if isinstance(input_data, str):
        input_data = hashlib.sha256(input_data.encode()).digest()
    trits = bytes_to_trits(input_data)
    output = []
    for neuron in neurons:
        neuron.state = 0
        neuron.feedforward(trits)
        state, _ = neuron.commit_state()
        output.append(state)
    return output

def get_energy(data):
    return sum(process(data))

def visualize_output(states):
    """Create ASCII visualization of network state."""
    chars = []
    for s in states:
        if s > 50:
            chars.append('█')
        elif s > 25:
            chars.append('▓')
        elif s > 0:
            chars.append('▒')
        elif s > -25:
            chars.append('░')
        elif s > -50:
            chars.append('·')
        else:
            chars.append(' ')
    return ''.join(chars)

def energy_bar(energy, width=40):
    """Create energy bar visualization."""
    # Normalize to -128 to +128 range
    normalized = (energy + 128) / 256
    filled = int(normalized * width)
    bar = '█' * filled + '░' * (width - filled)
    return bar

def classify_energy(energy):
    """Classify energy into categories."""
    if energy > 60:
        return "🔥 EXTREMELY POSITIVE", "red"
    elif energy > 30:
        return "✨ POSITIVE", "yellow"
    elif energy > 0:
        return "➕ SLIGHTLY POSITIVE", "green"
    elif energy > -30:
        return "➖ SLIGHTLY NEGATIVE", "cyan"
    elif energy > -60:
        return "❄️ NEGATIVE", "blue"
    else:
        return "💀 EXTREMELY NEGATIVE", "magenta"

def oracle_answer(question):
    """Get yes/no oracle answer."""
    energy = get_energy(question)
    if energy > 20:
        return "YES", energy
    elif energy < -20:
        return "NO", energy
    else:
        return "UNCERTAIN", energy

def main():
    print("\033[2J\033[H")  # Clear screen
    print("=" * 80)
    print("           🎮 AIGARTH INTERACTIVE CLI 🎮")
    print("=" * 80)
    print("""
    Commands:
      <text>      - Process text through neural network
      /energy     - Show energy of last input
      /compare    - Compare two inputs
      /oracle     - Ask yes/no question
      /find <E>   - Find input with specific energy
      /similar    - Find similar inputs
      /battle     - Energy battle between two inputs
      /stream     - Continuous streaming mode
      /help       - Show this help
      /quit       - Exit

    Type anything to begin...
    """)
    print("-" * 80)

    last_input = None
    last_states = None
    last_energy = None

    while True:
        try:
            user_input = input("\n🧠 > ").strip()

            if not user_input:
                continue

            if user_input == "/quit" or user_input == "/exit":
                print("\n👋 Goodbye!")
                break

            elif user_input == "/help":
                print("""
    Commands:
      <text>      - Process text through neural network
      /energy     - Show energy of last input
      /compare    - Compare two inputs
      /oracle     - Ask yes/no question
      /find <E>   - Find input with specific energy
      /battle     - Energy battle between two inputs
      /stream     - Continuous streaming mode
      /quit       - Exit
                """)

            elif user_input == "/energy":
                if last_energy is not None:
                    print(f"\n  Last input: '{last_input}'")
                    print(f"  Energy: {last_energy}")
                    category, _ = classify_energy(last_energy)
                    print(f"  Category: {category}")
                else:
                    print("  No previous input. Type something first!")

            elif user_input == "/compare":
                print("  Enter first input:")
                inp1 = input("  1> ").strip()
                print("  Enter second input:")
                inp2 = input("  2> ").strip()

                e1 = get_energy(inp1)
                e2 = get_energy(inp2)

                # Calculate similarity
                s1 = process(inp1)
                s2 = process(inp2)
                dot = sum(a*b for a,b in zip(s1, s2))
                n1 = sum(a*a for a in s1) ** 0.5
                n2 = sum(b*b for b in s2) ** 0.5
                sim = (dot / (n1*n2) + 1) / 2 * 100 if n1 and n2 else 0

                print(f"\n  '{inp1}': E={e1}")
                print(f"  '{inp2}': E={e2}")
                print(f"  Similarity: {sim:.1f}%")
                print(f"  Energy difference: {abs(e1-e2)}")

            elif user_input == "/oracle":
                print("  Ask your question:")
                question = input("  ? ").strip()
                answer, energy = oracle_answer(question)
                print(f"\n  Question: '{question}'")
                print(f"  Answer: {answer}")
                print(f"  Confidence (energy): {abs(energy)}")

            elif user_input.startswith("/find"):
                parts = user_input.split()
                if len(parts) > 1:
                    target = int(parts[1])
                else:
                    print("  Target energy:")
                    target = int(input("  E> ").strip())

                print(f"  Searching for inputs with E={target}...")
                found = []
                for i in range(50000):
                    candidate = f"search_{i}"
                    if get_energy(candidate) == target:
                        found.append(candidate)
                        print(f"    Found: '{candidate}'")
                        if len(found) >= 5:
                            break
                if not found:
                    print("    No matches found in 50000 attempts")

            elif user_input == "/battle":
                print("  Enter first combatant:")
                c1 = input("  ⚔️ 1> ").strip()
                print("  Enter second combatant:")
                c2 = input("  ⚔️ 2> ").strip()

                e1 = get_energy(c1)
                e2 = get_energy(c2)

                print(f"\n  ⚔️  ENERGY BATTLE  ⚔️")
                print(f"\n  {c1}")
                print(f"  Energy: {e1}")
                print(f"  {energy_bar(e1)}")
                print(f"\n  VS")
                print(f"\n  {c2}")
                print(f"  Energy: {e2}")
                print(f"  {energy_bar(e2)}")

                if e1 > e2:
                    print(f"\n  🏆 WINNER: '{c1}' (+{e1-e2} energy)")
                elif e2 > e1:
                    print(f"\n  🏆 WINNER: '{c2}' (+{e2-e1} energy)")
                else:
                    print(f"\n  🤝 TIE! Both have E={e1}")

            elif user_input == "/stream":
                print("  Streaming mode. Press Ctrl+C to stop.")
                print("  Type continuously and see energy in real-time:\n")
                buffer = ""
                try:
                    while True:
                        char = sys.stdin.read(1)
                        if char == '\n':
                            if buffer:
                                e = get_energy(buffer)
                                cat, _ = classify_energy(e)
                                print(f"  [{e:+4d}] {cat} | {buffer}")
                            buffer = ""
                        else:
                            buffer += char
                except KeyboardInterrupt:
                    print("\n  Streaming stopped.")

            else:
                # Process the input
                last_input = user_input
                last_states = process(user_input)
                last_energy = sum(last_states)

                category, _ = classify_energy(last_energy)

                print(f"\n  Input: '{user_input}'")
                print(f"  Energy: {last_energy}")
                print(f"  Category: {category}")
                print(f"\n  Neural Pattern:")
                print(f"  {visualize_output(last_states[:64])}")
                print(f"  {visualize_output(last_states[64:])}")
                print(f"\n  {energy_bar(last_energy)}")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    main()
