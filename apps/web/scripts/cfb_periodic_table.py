#!/usr/bin/env python3
"""
CFB Puzzle - Periodic Table Decoding
====================================

Testing if the numbers are atomic numbers!
"""

PUZZLE = [45, 92, 3, 77, 14, 58, 29, 81, 6, 33, 70, 48, 95, 22, 61, 9, 84, 37, 50, 16, 73, 28, 85, 41, 96, 7, 62, 19, 74, 30, 87, 43, 98, 5, 60, 15, 72, 27, 82, 39]

# Periodic table: atomic number -> (symbol, name)
ELEMENTS = {
    1: ("H", "Hydrogen"), 2: ("He", "Helium"), 3: ("Li", "Lithium"),
    4: ("Be", "Beryllium"), 5: ("B", "Boron"), 6: ("C", "Carbon"),
    7: ("N", "Nitrogen"), 8: ("O", "Oxygen"), 9: ("F", "Fluorine"),
    10: ("Ne", "Neon"), 11: ("Na", "Sodium"), 12: ("Mg", "Magnesium"),
    13: ("Al", "Aluminum"), 14: ("Si", "Silicon"), 15: ("P", "Phosphorus"),
    16: ("S", "Sulfur"), 17: ("Cl", "Chlorine"), 18: ("Ar", "Argon"),
    19: ("K", "Potassium"), 20: ("Ca", "Calcium"), 21: ("Sc", "Scandium"),
    22: ("Ti", "Titanium"), 23: ("V", "Vanadium"), 24: ("Cr", "Chromium"),
    25: ("Mn", "Manganese"), 26: ("Fe", "Iron"), 27: ("Co", "Cobalt"),
    28: ("Ni", "Nickel"), 29: ("Cu", "Copper"), 30: ("Zn", "Zinc"),
    31: ("Ga", "Gallium"), 32: ("Ge", "Germanium"), 33: ("As", "Arsenic"),
    34: ("Se", "Selenium"), 35: ("Br", "Bromine"), 36: ("Kr", "Krypton"),
    37: ("Rb", "Rubidium"), 38: ("Sr", "Strontium"), 39: ("Y", "Yttrium"),
    40: ("Zr", "Zirconium"), 41: ("Nb", "Niobium"), 42: ("Mo", "Molybdenum"),
    43: ("Tc", "Technetium"), 44: ("Ru", "Ruthenium"), 45: ("Rh", "Rhodium"),
    46: ("Pd", "Palladium"), 47: ("Ag", "Silver"), 48: ("Cd", "Cadmium"),
    49: ("In", "Indium"), 50: ("Sn", "Tin"), 51: ("Sb", "Antimony"),
    52: ("Te", "Tellurium"), 53: ("I", "Iodine"), 54: ("Xe", "Xenon"),
    55: ("Cs", "Cesium"), 56: ("Ba", "Barium"), 57: ("La", "Lanthanum"),
    58: ("Ce", "Cerium"), 59: ("Pr", "Praseodymium"), 60: ("Nd", "Neodymium"),
    61: ("Pm", "Promethium"), 62: ("Sm", "Samarium"), 63: ("Eu", "Europium"),
    64: ("Gd", "Gadolinium"), 65: ("Tb", "Terbium"), 66: ("Dy", "Dysprosium"),
    67: ("Ho", "Holmium"), 68: ("Er", "Erbium"), 69: ("Tm", "Thulium"),
    70: ("Yb", "Ytterbium"), 71: ("Lu", "Lutetium"), 72: ("Hf", "Hafnium"),
    73: ("Ta", "Tantalum"), 74: ("W", "Tungsten"), 75: ("Re", "Rhenium"),
    76: ("Os", "Osmium"), 77: ("Ir", "Iridium"), 78: ("Pt", "Platinum"),
    79: ("Au", "Gold"), 80: ("Hg", "Mercury"), 81: ("Tl", "Thallium"),
    82: ("Pb", "Lead"), 83: ("Bi", "Bismuth"), 84: ("Po", "Polonium"),
    85: ("At", "Astatine"), 86: ("Rn", "Radon"), 87: ("Fr", "Francium"),
    88: ("Ra", "Radium"), 89: ("Ac", "Actinium"), 90: ("Th", "Thorium"),
    91: ("Pa", "Protactinium"), 92: ("U", "Uranium"), 93: ("Np", "Neptunium"),
    94: ("Pu", "Plutonium"), 95: ("Am", "Americium"), 96: ("Cm", "Curium"),
    97: ("Bk", "Berkelium"), 98: ("Cf", "Californium"), 99: ("Es", "Einsteinium"),
    100: ("Fm", "Fermium"),
}

def decode_as_elements():
    print("=" * 70)
    print("CFB PUZZLE - PERIODIC TABLE DECODING")
    print("=" * 70)

    print("\nDecoding sequence as atomic numbers:\n")

    symbols = []
    first_letters = []
    names = []

    for i, num in enumerate(PUZZLE):
        if num in ELEMENTS:
            sym, name = ELEMENTS[num]
            symbols.append(sym)
            first_letters.append(sym[0])
            names.append(name)
            print(f"{i+1:2d}. {num:3d} = {sym:2s} ({name})")
        else:
            symbols.append("??")
            first_letters.append("?")
            names.append("Unknown")
            print(f"{i+1:2d}. {num:3d} = ?? (Unknown element)")

    print("\n" + "=" * 70)
    print("DECODED MESSAGES")
    print("=" * 70)

    # Element symbols concatenated
    symbol_str = ''.join(symbols)
    print(f"\nElement symbols: {symbol_str}")

    # First letters only
    first_str = ''.join(first_letters)
    print(f"First letters:   {first_str}")

    # Look for meaningful patterns
    print("\n" + "=" * 70)
    print("PATTERN ANALYSIS")
    print("=" * 70)

    # Split into groups
    print(f"\nGrouped by 10:")
    for i in range(0, len(symbols), 10):
        group = ''.join(symbols[i:i+10])
        print(f"  {i//10 + 1}: {group}")

    # Check for words
    print("\nLooking for words in symbol sequence...")

    # Common chemistry/crypto words to look for
    possible_words = [
        'AU', 'AG', 'CU', 'FE', 'PB', 'HG',  # Metal symbols
        'CO', 'NI', 'CF', 'AM',  # Other elements
        'U', 'TH', 'PU',  # Radioactive
    ]

    for word in possible_words:
        if word in symbol_str:
            pos = symbol_str.index(word)
            print(f"  Found '{word}' at position {pos}")

    # The message
    print("\n" + "=" * 70)
    print("THE MESSAGE")
    print("=" * 70)

    print(f"\nFull element sequence:")
    print(symbol_str)

    print(f"\nReadable attempt (adding spaces based on element boundaries):")
    readable = ' '.join(symbols)
    print(readable)

    # Special elements
    print("\n" + "=" * 70)
    print("SPECIAL ELEMENTS IN SEQUENCE")
    print("=" * 70)

    special = [
        (27, "Co", "Cobalt - CFB's favorite number 27!"),
        (79, "Au", "Gold - if present"),
        (47, "Ag", "Silver - if present"),
        (6, "C", "Carbon - basis of life"),
        (92, "U", "Uranium - radioactive"),
    ]

    for num, sym, desc in special:
        if num in PUZZLE:
            pos = PUZZLE.index(num)
            print(f"  {num} ({sym}) at position {pos}: {desc}")

    # Try reading as acronym
    print("\n" + "=" * 70)
    print("POSSIBLE MEANINGS")
    print("=" * 70)

    print("""
The element symbols spell out:
Rh U Li Ir Si Ce Cu Tl C As Yb Cd Am Ti Pm F Po Rb Sn S Ta Ni At Nb Cm N Sm K W Zn Fr Tc Cf B Nd P Hf Co Pb Y

Notable patterns:
- U (Uranium) at position 2
- C (Carbon) at position 9
- Co (Cobalt) at position 38 (number 27!)
- Cf (Californium) at position 34

Could this be:
1. A chemical formula?
2. An encoded message using element symbols?
3. A reference to something specific?

First letters: R U L I S C C T C A Y C A T P F P R S S T N A N C N S K W Z F T C B N P H C P Y
""")


def analyze_radioactive():
    """Check for radioactive elements"""
    print("\n" + "=" * 70)
    print("RADIOACTIVE ELEMENTS")
    print("=" * 70)

    radioactive = [43, 61, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98]
    found = [(n, ELEMENTS[n][0]) for n in PUZZLE if n in radioactive]

    print(f"Radioactive elements in sequence: {found}")
    print(f"Count: {len(found)}")


def main():
    decode_as_elements()
    analyze_radioactive()

    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print("""
🧪 ELEMENT DECODING RESULT:

Symbols: RhULiIrSiCeCuTlCAsYbCdAmTiPmFPoRbSnSTaNiAtNbCmNSmKWZnFrTcCfBNdPHfCoPbY

Key observations:
1. 27 = Cobalt (Co) - CFB's signature number!
2. Multiple radioactive elements (U, Am, Po, Tc, Cf, etc.)
3. 92 = Uranium at position 2
4. 98 = Californium at position 33

This could be:
- A chemistry puzzle
- An encoded message
- A reference to nuclear/radioactive themes
- Simply testing if Grok recognizes periodic table
""")


if __name__ == "__main__":
    main()
