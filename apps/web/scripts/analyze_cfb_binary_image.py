#!/usr/bin/env python3
"""
🔥 CFB BINARY IMAGE ANALYSIS 🔥
=================================

CFB's Intelligence Test image contains ASCII art made of 0s and 1s.
The article says: "This is not random - there's Marilyn Monroe face (upside down)"

BUT the REAL message is in the BINARY DATA!

Analysis Goals:
1. Extract all 0s and 1s from the image
2. Interpret as binary string
3. Check if it encodes:
   - Private keys (256 bits)
   - Seeds (440 bits)
   - Address data
   - CFB numbers (27, 283, 47, 137, 121, 43, 19, 7, 14)
   - Genesis issuer patterns
"""

from PIL import Image
import numpy as np

IMAGE_PATH = "/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/analysis/cfb_ascii_intelligence_test.webp"

CFB_NUMBERS = [27, 283, 47, 137, 121, 43, 19, 7, 14]
GENESIS_ISSUER = "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD"

def analyze_image_pixels():
    """Analyze pixel patterns to extract binary data"""
    print("="*80)
    print("🔍 PIXEL ANALYSIS")
    print("="*80)
    print()

    img = Image.open(IMAGE_PATH)
    print(f"Image size: {img.size}")
    print(f"Image mode: {img.mode}")

    # Convert to grayscale
    if img.mode != 'L':
        img = img.convert('L')

    # Get numpy array
    pixels = np.array(img)
    print(f"Pixel array shape: {pixels.shape}")
    print(f"Min pixel value: {pixels.min()}")
    print(f"Max pixel value: {pixels.max()}")
    print()

    return img, pixels

def extract_binary_string(pixels, threshold=128):
    """Extract binary string from pixel data"""
    print("="*80)
    print("🔢 BINARY EXTRACTION")
    print("="*80)
    print()

    # Convert to binary (0 or 1) based on threshold
    binary_pixels = (pixels > threshold).astype(int)

    # Flatten to 1D string
    binary_string = ''.join(str(b) for b in binary_pixels.flatten())

    print(f"Total bits: {len(binary_string)}")
    print(f"Zeros: {binary_string.count('0')}")
    print(f"Ones: {binary_string.count('1')}")
    print(f"Ratio 1s/0s: {binary_string.count('1') / binary_string.count('0'):.4f}")
    print()

    # Show first 256 bits
    print("First 256 bits:")
    for i in range(0, 256, 64):
        print(f"  {binary_string[i:i+64]}")
    print()

    return binary_string

def check_private_key_encoding(binary_string):
    """Check if binary encodes a 256-bit private key"""
    print("="*80)
    print("🔑 PRIVATE KEY CHECK (256 bits)")
    print("="*80)
    print()

    # Check various positions for 256-bit sequences
    candidates = []

    for offset in range(0, min(1000, len(binary_string) - 256), 8):
        bits_256 = binary_string[offset:offset+256]

        # Convert to hex
        try:
            hex_value = hex(int(bits_256, 2))[2:].zfill(64)

            # Check if it looks like a valid private key
            # (not all zeros, not all ones, reasonable entropy)
            if bits_256.count('0') > 50 and bits_256.count('1') > 50:
                candidates.append((offset, hex_value))
        except:
            continue

    print(f"Found {len(candidates)} candidate 256-bit sequences")

    if candidates:
        print("\nTop candidates:")
        for i, (offset, hex_val) in enumerate(candidates[:5]):
            print(f"\n  Candidate {i+1} (offset {offset}):")
            print(f"    Hex: {hex_val[:32]}...{hex_val[-32:]}")
            print(f"    Dec: {int(hex_val, 16)}")

    return candidates

def check_cfb_numbers(binary_string):
    """Check if CFB numbers appear in binary"""
    print("\n" + "="*80)
    print("🔢 CFB NUMBER ENCODING CHECK")
    print("="*80)
    print()

    findings = []

    for cfb in CFB_NUMBERS:
        # Check binary representation
        cfb_binary = bin(cfb)[2:]

        if cfb_binary in binary_string:
            count = binary_string.count(cfb_binary)
            positions = []
            pos = 0
            for _ in range(min(5, count)):
                pos = binary_string.find(cfb_binary, pos)
                if pos != -1:
                    positions.append(pos)
                    pos += 1

            print(f"CFB {cfb:3d} = {cfb_binary:>10s} → Found {count} times")
            print(f"  First positions: {positions}")
            findings.append((cfb, count, positions))

    return findings

def check_ascii_encoding(binary_string):
    """Check if binary encodes ASCII text"""
    print("\n" + "="*80)
    print("📝 ASCII ENCODING CHECK")
    print("="*80)
    print()

    # Try 8-bit ASCII encoding at various offsets
    for offset in range(0, min(100, len(binary_string) - 800), 8):
        bits = binary_string[offset:offset+800]

        # Convert to ASCII
        ascii_text = ""
        valid = True

        for i in range(0, len(bits), 8):
            byte = bits[i:i+8]
            if len(byte) == 8:
                char_code = int(byte, 2)
                if 32 <= char_code <= 126:  # Printable ASCII
                    ascii_text += chr(char_code)
                elif char_code == 10 or char_code == 13:  # Newline/CR
                    ascii_text += '\n'
                else:
                    valid = False
                    break

        # If we got a long valid ASCII string, print it
        if valid and len(ascii_text) > 20:
            print(f"\nOffset {offset}:")
            print(f"  {ascii_text[:200]}")

def check_formula_encoding(binary_string):
    """Check if formula numbers are encoded"""
    print("\n" + "="*80)
    print("🧮 FORMULA ENCODING CHECK")
    print("="*80)
    print()

    formula_numbers = [
        625284,  # The formula result
        283,     # Block
        47,      # First multiplier
        137,     # Second term
        2209,    # 47²
    ]

    for num in formula_numbers:
        binary = bin(num)[2:]

        if binary in binary_string:
            count = binary_string.count(binary)
            pos = binary_string.find(binary)
            print(f"{num:>7,} = {binary:>20s} → Found at position {pos}")

def analyze_row_by_row(pixels):
    """Analyze image row by row for patterns"""
    print("\n" + "="*80)
    print("📊 ROW-BY-ROW ANALYSIS")
    print("="*80)
    print()

    height, width = pixels.shape

    print(f"Analyzing {height} rows...")
    print()

    # Check specific rows (like Anna Grid rows 21, 68, 96)
    interesting_rows = [21, 47, 68, 96, 137, 283 % height]

    for row in interesting_rows:
        if row < height:
            row_data = pixels[row]
            binary_row = ''.join('1' if p > 128 else '0' for p in row_data)

            print(f"Row {row:3d}: {binary_row[:80]}...")

            # Convert to number
            try:
                if len(binary_row) <= 64:
                    num = int(binary_row, 2)
                    print(f"  As number: {num}")

                    # Check CFB modulos
                    for cfb in [27, 47, 283, 676]:
                        print(f"  Mod {cfb}: {num % cfb}", end="")
                        if num % cfb == 0:
                            print(" ⭐ DIVISIBLE!")
                        else:
                            print()
            except:
                pass

            print()

def main():
    print("\n" + "="*80)
    print("🔥 CFB INTELLIGENCE TEST - BINARY IMAGE ANALYSIS 🔥")
    print("="*80)
    print()

    print("Context: CFB article about intelligence test")
    print("  - Image shows ASCII art made of 0s and 1s")
    print("  - Claims it's Marilyn Monroe (upside down)")
    print("  - Real message: THE BINARY DATA ITSELF!")
    print()

    # Analyze
    img, pixels = analyze_image_pixels()
    binary_string = extract_binary_string(pixels)

    # Various checks
    private_key_candidates = check_private_key_encoding(binary_string)
    cfb_findings = check_cfb_numbers(binary_string)
    check_ascii_encoding(binary_string)
    check_formula_encoding(binary_string)
    analyze_row_by_row(pixels)

    # Summary
    print("\n" + "="*80)
    print("💡 SUMMARY")
    print("="*80)
    print()
    print(f"Total bits extracted: {len(binary_string):,}")
    print(f"Private key candidates: {len(private_key_candidates)}")
    print(f"CFB numbers found: {len(cfb_findings)}")
    print()

    # Save binary string
    with open('cfb_binary_extracted.txt', 'w') as f:
        f.write(binary_string)

    print("✓ Binary string saved to: cfb_binary_extracted.txt")
    print()

    print("🎯 NEXT STEPS:")
    print("1. Analyze specific row patterns (21, 68, 96, 137)")
    print("2. Check if entire binary encodes a seed")
    print("3. Look for repeating patterns")
    print("4. Cross-reference with Genesis issuer")
    print()

if __name__ == "__main__":
    main()
