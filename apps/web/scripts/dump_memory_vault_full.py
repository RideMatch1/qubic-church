#!/usr/bin/env python3
"""
MEMORY VAULT FULL DATA DUMP
===========================

Extracts and analyzes all data from the Memory Vault at coordinates (21,21)
in the Anna Matrix, including neighboring cells and various decodings.

Memory Vault Details:
- Qubic ID: VHGZIFEFAPDXEAMCEMNQWJKMVCPAVTNXMECIEFKXXGOGLMYKKERCEMIDZYSD
- Seed: xsasnghzffaxrpopeetcdlylfwawscysteapaasyqyxdnrtqtwloljd
- Private Key: be7e69448a7e66b9ada36eee0c5a8810f2adec55e7110108e51793bf4682628b
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Bitcoin key generation imports
try:
    from ecdsa import SigningKey, SECP256k1
    import base58
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("Warning: ecdsa/base58 not available. Bitcoin key derivation will be skipped.")

# File paths
MATRIX_FILE = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/matrix_cartography.json")
OUTPUT_FILE = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/MEMORY_VAULT_FULL_DUMP.json")

# Memory Vault constants
MEMORY_VAULT = {
    "qubic_id": "VHGZIFEFAPDXEAMCEMNQWJKMVCPAVTNXMECIEFKXXGOGLMYKKERCEMIDZYSD",
    "seed": "xsasnghzffaxrpopeetcdlylfwawscysteapaasyqyxdnrtqtwloljd",
    "private_key": "be7e69448a7e66b9ada36eee0c5a8810f2adec55e7110108e51793bf4682628b",
    "coordinates": (21, 21)
}

# XOR constants for analysis
XOR_CONSTANTS = [27, 121, 19, 137, 283]

# ISA Symbol mapping
ISA_SYMBOLS = "=><+%^#:|&"


class MemoryVaultAnalyzer:
    """Comprehensive Memory Vault data extractor and analyzer."""

    def __init__(self):
        self.matrix: Dict[str, str] = {}
        self.results: Dict[str, Any] = {
            "metadata": {
                "analysis_date": datetime.now().isoformat(),
                "memory_vault": MEMORY_VAULT,
                "matrix_file": str(MATRIX_FILE)
            },
            "primary_cell": {},
            "neighboring_cells": [],
            "xor_analysis": {},
            "correlations": {},
            "bitcoin_derivations": {},
            "decoded_outputs": {}
        }

    def load_matrix(self) -> bool:
        """Load the Anna Matrix from JSON file."""
        print("=" * 80)
        print("LOADING ANNA MATRIX")
        print("=" * 80)

        try:
            with open(MATRIX_FILE, "r") as f:
                self.matrix = json.load(f)
            print(f"Loaded matrix with {len(self.matrix)} entries")
            return True
        except Exception as e:
            print(f"ERROR: Failed to load matrix: {e}")
            return False

    def get_cell(self, row: int, col: int) -> Optional[str]:
        """Get hex value at specific coordinates."""
        key = f"{row},{col}"
        return self.matrix.get(key)

    def hex_to_bytes(self, hex_str: str) -> bytes:
        """Convert hex string to bytes."""
        return bytes.fromhex(hex_str)

    def decode_as_utf8(self, data: bytes) -> str:
        """Attempt UTF-8 decoding."""
        try:
            # Try direct decoding
            decoded = data.decode('utf-8', errors='ignore')
            # Filter to printable characters
            printable = ''.join(c for c in decoded if c.isprintable() or c in '\n\r\t')
            return printable if printable else "[No valid UTF-8]"
        except Exception:
            return "[UTF-8 decode failed]"

    def decode_as_isa(self, data: bytes) -> str:
        """Decode bytes as ISA symbols."""
        return "".join([ISA_SYMBOLS[b % len(ISA_SYMBOLS)] for b in data])

    def decode_as_qubic_seed(self, data: bytes) -> str:
        """
        Attempt to decode as Qubic seed format (55 lowercase letters a-z).
        Uses modulo 26 mapping.
        """
        seed_chars = []
        for b in data:
            char_index = b % 26
            seed_chars.append(chr(ord('a') + char_index))
        return ''.join(seed_chars[:55])

    def derive_bitcoin_key(self, hex_key: str) -> Dict[str, Any]:
        """Derive Bitcoin private key and address from hex data."""
        if not CRYPTO_AVAILABLE:
            return {"error": "Crypto libraries not available"}

        try:
            # Ensure we have 32 bytes (64 hex chars)
            if len(hex_key) != 64:
                # Hash to get 32 bytes
                private_key_bytes = hashlib.sha256(bytes.fromhex(hex_key)).digest()
            else:
                private_key_bytes = bytes.fromhex(hex_key)

            # Create ECDSA private key
            sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
            vk = sk.get_verifying_key()

            # Uncompressed public key
            public_key_uncompressed = b'\x04' + vk.to_string()

            # Compressed public key
            x = vk.to_string()[:32]
            y = vk.to_string()[32:]
            prefix = b'\x02' if int.from_bytes(y, 'big') % 2 == 0 else b'\x03'
            public_key_compressed = prefix + x

            # Hash160 (uncompressed)
            sha256_hash = hashlib.sha256(public_key_uncompressed).digest()
            ripemd160 = hashlib.new('ripemd160')
            ripemd160.update(sha256_hash)
            hash160_uncompressed = ripemd160.digest()

            # Hash160 (compressed)
            sha256_hash_c = hashlib.sha256(public_key_compressed).digest()
            ripemd160_c = hashlib.new('ripemd160')
            ripemd160_c.update(sha256_hash_c)
            hash160_compressed = ripemd160_c.digest()

            # Bitcoin address (uncompressed)
            versioned = b'\x00' + hash160_uncompressed
            checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
            address_uncompressed = base58.b58encode(versioned + checksum).decode('utf-8')

            # Bitcoin address (compressed)
            versioned_c = b'\x00' + hash160_compressed
            checksum_c = hashlib.sha256(hashlib.sha256(versioned_c).digest()).digest()[:4]
            address_compressed = base58.b58encode(versioned_c + checksum_c).decode('utf-8')

            # WIF (uncompressed)
            extended = b'\x80' + private_key_bytes
            wif_checksum = hashlib.sha256(hashlib.sha256(extended).digest()).digest()[:4]
            wif_uncompressed = base58.b58encode(extended + wif_checksum).decode('utf-8')

            # WIF (compressed)
            extended_c = b'\x80' + private_key_bytes + b'\x01'
            wif_checksum_c = hashlib.sha256(hashlib.sha256(extended_c).digest()).digest()[:4]
            wif_compressed = base58.b58encode(extended_c + wif_checksum_c).decode('utf-8')

            return {
                "private_key_hex": private_key_bytes.hex(),
                "wif_uncompressed": wif_uncompressed,
                "wif_compressed": wif_compressed,
                "address_uncompressed": address_uncompressed,
                "address_compressed": address_compressed,
                "public_key_uncompressed": public_key_uncompressed.hex(),
                "public_key_compressed": public_key_compressed.hex(),
                "hash160_uncompressed": hash160_uncompressed.hex(),
                "hash160_compressed": hash160_compressed.hex()
            }
        except Exception as e:
            return {"error": str(e)}

    def xor_with_constant(self, data: bytes, constant: int) -> bytes:
        """XOR all bytes with a constant value."""
        return bytes([b ^ (constant % 256) for b in data])

    def xor_with_key(self, data: bytes, key: bytes) -> bytes:
        """XOR data with a key (cyclic)."""
        return bytes([d ^ key[i % len(key)] for i, d in enumerate(data)])

    def analyze_primary_cell(self):
        """Analyze the primary Memory Vault cell at (21,21)."""
        print("\n" + "=" * 80)
        print("ANALYZING PRIMARY CELL (21, 21)")
        print("=" * 80)

        row, col = MEMORY_VAULT["coordinates"]
        hex_value = self.get_cell(row, col)

        if not hex_value:
            print(f"ERROR: No data at coordinates ({row}, {col})")
            self.results["primary_cell"] = {"error": "No data found"}
            return

        print(f"\nCoordinates: ({row}, {col})")
        print(f"Hex Value: {hex_value}")
        print(f"Length: {len(hex_value)} hex chars = {len(hex_value) // 2} bytes")

        raw_bytes = self.hex_to_bytes(hex_value)

        # Store primary cell data
        self.results["primary_cell"] = {
            "coordinates": {"row": row, "col": col},
            "hex": hex_value,
            "length_hex": len(hex_value),
            "length_bytes": len(hex_value) // 2,
            "raw_bytes": list(raw_bytes),
            "decodings": {}
        }

        # Decode as raw bytes
        print(f"\n[1] RAW BYTES:")
        print(f"    First 16: {list(raw_bytes[:16])}")
        print(f"    Last 16:  {list(raw_bytes[-16:])}")

        # Decode as UTF-8
        utf8_decoded = self.decode_as_utf8(raw_bytes)
        print(f"\n[2] UTF-8 DECODE:")
        print(f"    {utf8_decoded[:80] if len(utf8_decoded) > 0 else '[Empty]'}...")
        self.results["primary_cell"]["decodings"]["utf8"] = utf8_decoded

        # Decode as ISA symbols
        isa_decoded = self.decode_as_isa(raw_bytes)
        print(f"\n[3] ISA SYMBOLS (=><+%^#:|&):")
        print(f"    {isa_decoded}")
        self.results["primary_cell"]["decodings"]["isa"] = isa_decoded

        # Decode as Qubic seed
        qubic_seed = self.decode_as_qubic_seed(raw_bytes)
        print(f"\n[4] QUBIC SEED FORMAT (55-char):")
        print(f"    {qubic_seed}")
        self.results["primary_cell"]["decodings"]["qubic_seed"] = qubic_seed

        # Derive Bitcoin key
        print(f"\n[5] BITCOIN KEY DERIVATION:")
        btc_data = self.derive_bitcoin_key(hex_value)
        if "error" not in btc_data:
            print(f"    Private Key (hex): {btc_data['private_key_hex']}")
            print(f"    WIF (compressed):  {btc_data['wif_compressed']}")
            print(f"    Address (comp):    {btc_data['address_compressed']}")
            print(f"    Address (uncomp):  {btc_data['address_uncompressed']}")
        else:
            print(f"    Error: {btc_data['error']}")
        self.results["primary_cell"]["decodings"]["bitcoin"] = btc_data

    def analyze_neighbors(self):
        """Analyze all neighboring cells (20,20) to (22,22)."""
        print("\n" + "=" * 80)
        print("ANALYZING NEIGHBORING CELLS (20,20) to (22,22)")
        print("=" * 80)

        neighbors = []
        primary_row, primary_col = MEMORY_VAULT["coordinates"]

        for row in range(primary_row - 1, primary_row + 2):
            for col in range(primary_col - 1, primary_col + 2):
                if row == primary_row and col == primary_col:
                    continue  # Skip primary cell

                hex_value = self.get_cell(row, col)
                if not hex_value:
                    print(f"\n({row}, {col}): [NO DATA]")
                    continue

                raw_bytes = self.hex_to_bytes(hex_value)
                isa_decoded = self.decode_as_isa(raw_bytes)
                qubic_seed = self.decode_as_qubic_seed(raw_bytes)
                btc_data = self.derive_bitcoin_key(hex_value)

                neighbor_data = {
                    "coordinates": {"row": row, "col": col},
                    "hex": hex_value,
                    "decodings": {
                        "isa": isa_decoded,
                        "qubic_seed": qubic_seed,
                        "bitcoin": btc_data
                    }
                }
                neighbors.append(neighbor_data)

                print(f"\n({row}, {col}):")
                print(f"    Hex: {hex_value[:32]}...")
                print(f"    ISA: {isa_decoded[:40]}...")
                if "error" not in btc_data:
                    print(f"    BTC: {btc_data['address_compressed']}")

        self.results["neighboring_cells"] = neighbors

    def perform_xor_analysis(self):
        """XOR primary cell data with known constants."""
        print("\n" + "=" * 80)
        print("XOR ANALYSIS WITH KNOWN CONSTANTS")
        print("=" * 80)

        primary_hex = self.results["primary_cell"].get("hex")
        if not primary_hex:
            print("ERROR: No primary cell data for XOR analysis")
            return

        primary_bytes = self.hex_to_bytes(primary_hex)
        xor_results = {}

        for constant in XOR_CONSTANTS:
            xored = self.xor_with_constant(primary_bytes, constant)
            xored_hex = xored.hex()
            isa_decoded = self.decode_as_isa(xored)
            utf8_decoded = self.decode_as_utf8(xored)
            qubic_seed = self.decode_as_qubic_seed(xored)
            btc_data = self.derive_bitcoin_key(xored_hex)

            xor_results[str(constant)] = {
                "constant": constant,
                "result_hex": xored_hex,
                "decodings": {
                    "isa": isa_decoded,
                    "utf8": utf8_decoded,
                    "qubic_seed": qubic_seed,
                    "bitcoin": btc_data
                }
            }

            print(f"\nXOR with {constant}:")
            print(f"    Result Hex: {xored_hex[:32]}...")
            print(f"    ISA: {isa_decoded[:40]}...")
            print(f"    UTF-8: {utf8_decoded[:40] if utf8_decoded else '[None]'}...")
            if "error" not in btc_data:
                print(f"    BTC: {btc_data['address_compressed']}")

        # Also XOR with the Memory Vault private key
        print("\n--- XOR with Memory Vault Private Key ---")
        vault_key_bytes = self.hex_to_bytes(MEMORY_VAULT["private_key"])
        xored_with_key = self.xor_with_key(primary_bytes, vault_key_bytes)
        xored_hex = xored_with_key.hex()
        btc_data = self.derive_bitcoin_key(xored_hex)

        xor_results["memory_vault_key"] = {
            "key_hex": MEMORY_VAULT["private_key"],
            "result_hex": xored_hex,
            "decodings": {
                "isa": self.decode_as_isa(xored_with_key),
                "qubic_seed": self.decode_as_qubic_seed(xored_with_key),
                "bitcoin": btc_data
            }
        }

        print(f"    Result Hex: {xored_hex[:32]}...")
        if "error" not in btc_data:
            print(f"    BTC: {btc_data['address_compressed']}")

        self.results["xor_analysis"] = xor_results

    def find_correlations(self):
        """Find correlations between Memory Vault data and matrix."""
        print("\n" + "=" * 80)
        print("CORRELATION ANALYSIS")
        print("=" * 80)

        correlations = {
            "position_significance": {},
            "pattern_matches": [],
            "mathematical_properties": {}
        }

        row, col = MEMORY_VAULT["coordinates"]

        # Position significance
        correlations["position_significance"] = {
            "row": row,
            "col": col,
            "sum": row + col,
            "product": row * col,
            "difference": abs(row - col),
            "is_diagonal": row == col,
            "mod_27": (row * col) % 27,
            "mod_121": (row * col) % 121,
            "mod_19": (row * col) % 19,
            "mod_137": (row * col) % 137
        }

        print("\nPosition Mathematical Properties:")
        for key, value in correlations["position_significance"].items():
            print(f"    {key}: {value}")

        # Check if primary cell hex appears elsewhere
        primary_hex = self.results["primary_cell"].get("hex", "")
        matches = []
        for coord, hex_val in self.matrix.items():
            if hex_val == primary_hex and coord != f"{row},{col}":
                matches.append(coord)

        correlations["pattern_matches"] = matches
        if matches:
            print(f"\nFound {len(matches)} duplicate hex values at: {matches}")
        else:
            print("\nNo duplicate hex values found (primary cell is unique)")

        # Hash relationships
        primary_bytes = self.hex_to_bytes(primary_hex)
        sha256_hash = hashlib.sha256(primary_bytes).hexdigest()
        md5_hash = hashlib.md5(primary_bytes).hexdigest()

        correlations["mathematical_properties"]["sha256"] = sha256_hash
        correlations["mathematical_properties"]["md5"] = md5_hash
        correlations["mathematical_properties"]["byte_sum"] = sum(primary_bytes)
        correlations["mathematical_properties"]["byte_xor_fold"] = self._xor_fold(primary_bytes)

        print(f"\nHash Properties:")
        print(f"    SHA256: {sha256_hash}")
        print(f"    MD5:    {md5_hash}")
        print(f"    Byte Sum: {sum(primary_bytes)}")
        print(f"    XOR Fold: {correlations['mathematical_properties']['byte_xor_fold']}")

        self.results["correlations"] = correlations

    def _xor_fold(self, data: bytes) -> str:
        """XOR fold all bytes to get a single value."""
        result = 0
        for b in data:
            result ^= b
        return f"{result} (0x{result:02x})"

    def generate_all_bitcoin_derivations(self):
        """Generate Bitcoin keys from various interpretations of the data."""
        print("\n" + "=" * 80)
        print("ALL BITCOIN DERIVATIONS")
        print("=" * 80)

        derivations = {}
        primary_hex = self.results["primary_cell"].get("hex", "")
        vault_seed = MEMORY_VAULT["seed"]
        vault_key = MEMORY_VAULT["private_key"]

        methods = [
            ("direct_hex", primary_hex),
            ("sha256_of_hex", hashlib.sha256(bytes.fromhex(primary_hex)).hexdigest()),
            ("sha256_of_seed", hashlib.sha256(vault_seed.encode()).hexdigest()),
            ("vault_private_key", vault_key),
            ("double_sha256", hashlib.sha256(hashlib.sha256(bytes.fromhex(primary_hex)).digest()).hexdigest()),
        ]

        for method_name, hex_input in methods:
            print(f"\n{method_name}:")
            btc_data = self.derive_bitcoin_key(hex_input)
            derivations[method_name] = {
                "input_hex": hex_input,
                "bitcoin_data": btc_data
            }

            if "error" not in btc_data:
                print(f"    Input: {hex_input[:32]}...")
                print(f"    Address (comp): {btc_data['address_compressed']}")
                print(f"    Address (uncomp): {btc_data['address_uncompressed']}")
            else:
                print(f"    Error: {btc_data['error']}")

        self.results["bitcoin_derivations"] = derivations

    def save_results(self):
        """Save comprehensive results to JSON file."""
        print("\n" + "=" * 80)
        print("SAVING RESULTS")
        print("=" * 80)

        try:
            with open(OUTPUT_FILE, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            print(f"Results saved to: {OUTPUT_FILE}")
            print(f"File size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")
        except Exception as e:
            print(f"ERROR saving results: {e}")

    def run_full_analysis(self):
        """Execute the complete Memory Vault analysis."""
        print("\n")
        print("*" * 80)
        print("*  MEMORY VAULT FULL DATA DUMP                                                *")
        print("*  Coordinates: (21, 21) in Anna Matrix                                       *")
        print("*  Qubic ID: VHGZIFEFAPDXEAMCEMNQWJKMVCPAVTNXMECIEFKXXGOGLMYKKERCEMIDZYSD     *")
        print("*" * 80)

        if not self.load_matrix():
            return False

        self.analyze_primary_cell()
        self.analyze_neighbors()
        self.perform_xor_analysis()
        self.find_correlations()
        self.generate_all_bitcoin_derivations()
        self.save_results()

        self.print_summary()
        return True

    def print_summary(self):
        """Print analysis summary."""
        print("\n" + "=" * 80)
        print("ANALYSIS SUMMARY")
        print("=" * 80)

        primary = self.results["primary_cell"]
        neighbors = self.results["neighboring_cells"]
        xor = self.results["xor_analysis"]

        print(f"\nPrimary Cell (21,21):")
        print(f"    Hex: {primary.get('hex', 'N/A')}")

        if primary.get("decodings", {}).get("bitcoin"):
            btc = primary["decodings"]["bitcoin"]
            if "error" not in btc:
                print(f"    Bitcoin Address: {btc.get('address_compressed', 'N/A')}")

        print(f"\nNeighboring Cells Analyzed: {len(neighbors)}")

        print(f"\nXOR Transformations Tested: {len(xor)}")

        if primary.get("decodings", {}).get("isa"):
            print(f"\nISA Bytecode: {primary['decodings']['isa']}")

        if primary.get("decodings", {}).get("qubic_seed"):
            print(f"\nDerived Qubic Seed: {primary['decodings']['qubic_seed']}")

        print("\n" + "=" * 80)
        print("MEMORY VAULT DUMP COMPLETE")
        print("=" * 80)


def main():
    """Main execution entry point."""
    analyzer = MemoryVaultAnalyzer()
    success = analyzer.run_full_analysis()

    if success:
        print("\nAnalysis completed successfully.")
        print(f"Results saved to: {OUTPUT_FILE}")
    else:
        print("\nAnalysis failed. Check error messages above.")

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
