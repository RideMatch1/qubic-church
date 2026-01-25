#!/usr/bin/env python3
"""
Extract messages from STRATEGIC NODE positions and their neighborhoods.
Analyzes the Anna Matrix for hidden messages at known strategic coordinates.
"""

import json
import os
from typing import List, Dict, Any, Tuple, Optional

# Strategic nodes with their coordinates (row, col)
STRATEGIC_NODES = {
    "ENTRY": (45, 92),
    "CORE": (6, 33),
    "MEMORY": (21, 21),
    "VISION": (64, 64),
    "EXIT": (82, 39),
    "1CFi": (91, 20),
    "1CFB": (45, 92),
    "VOID": (0, 0)
}

def load_matrix(filepath: str) -> List[List[Any]]:
    """Load the Anna matrix from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)

    # Handle different possible matrix formats
    if isinstance(data, list):
        if len(data) > 0 and isinstance(data[0], list):
            return data  # Already a 2D matrix
        elif len(data) > 0 and isinstance(data[0], dict):
            # Array of row objects
            matrix = []
            for row_data in data:
                if 'values' in row_data:
                    matrix.append(row_data['values'])
                elif 'row' in row_data:
                    matrix.append(row_data['row'])
                else:
                    # Try to extract numeric values
                    row_vals = []
                    for key in sorted(row_data.keys(), key=lambda x: int(x) if x.isdigit() else float('inf')):
                        if key.isdigit():
                            row_vals.append(row_data[key])
                    if row_vals:
                        matrix.append(row_vals)
            return matrix
    elif isinstance(data, dict):
        if 'matrix' in data:
            return data['matrix']
        elif 'data' in data:
            return data['data']
        elif 'rows' in data:
            return data['rows']

    raise ValueError(f"Unknown matrix format: {type(data)}")

def get_value(matrix: List[List[Any]], row: int, col: int) -> Optional[Any]:
    """Safely get a value from the matrix."""
    if 0 <= row < len(matrix) and 0 <= col < len(matrix[row]):
        return matrix[row][col]
    return None

def value_to_ascii(value: Any, as_unsigned: bool = False) -> str:
    """Convert a matrix value to ASCII character if possible."""
    if value is None:
        return ''

    try:
        if isinstance(value, str):
            # If it's already a string, check if it's a hex value
            if value.startswith('0x'):
                num = int(value, 16)
            else:
                try:
                    num = int(value)
                except ValueError:
                    return value  # Return as-is if not a number
        else:
            num = int(value)

        # Convert signed byte to unsigned if needed
        if as_unsigned and num < 0:
            num = num + 256

        # Only convert printable ASCII
        if 32 <= num <= 126:
            return chr(num)
        elif num == 0:
            return ''
        else:
            return f'[{num}]'
    except (ValueError, TypeError):
        return str(value)


def value_to_hex(value: Any) -> str:
    """Convert a matrix value to hex string."""
    if value is None:
        return ''
    try:
        num = int(value)
        # Convert to unsigned byte
        if num < 0:
            num = num + 256
        return f'{num:02x}'
    except (ValueError, TypeError):
        return ''


def values_to_unsigned_bytes(values: List[Any]) -> bytes:
    """Convert a list of values to bytes (unsigned)."""
    result = []
    for v in values:
        if v is not None:
            try:
                num = int(v)
                if num < 0:
                    num = num + 256
                result.append(num & 0xFF)
            except (ValueError, TypeError):
                pass
    return bytes(result)

def extract_node_values(matrix: List[List[Any]]) -> Dict[str, Any]:
    """Extract values at each strategic node."""
    results = {}
    for name, (row, col) in STRATEGIC_NODES.items():
        value = get_value(matrix, row, col)
        unsigned = (int(value) + 256) if value is not None and int(value) < 0 else value
        results[name] = {
            "coordinates": (row, col),
            "value": value,
            "unsigned": unsigned,
            "hex": value_to_hex(value),
            "ascii_signed": value_to_ascii(value, as_unsigned=False),
            "ascii_unsigned": value_to_ascii(value, as_unsigned=True)
        }
    return results

def extract_neighborhood(matrix: List[List[Any]], row: int, col: int) -> List[List[Any]]:
    """Extract 3x3 neighborhood around a position."""
    neighborhood = []
    for dr in [-1, 0, 1]:
        row_vals = []
        for dc in [-1, 0, 1]:
            val = get_value(matrix, row + dr, col + dc)
            row_vals.append(val)
        neighborhood.append(row_vals)
    return neighborhood

def neighborhood_to_ascii(neighborhood: List[List[Any]]) -> Dict[str, str]:
    """Convert 3x3 neighborhood to ASCII in different reading orders."""
    flat = [neighborhood[r][c] for r in range(3) for c in range(3)]

    # Different reading orders
    orders = {
        "row_major": flat,  # Left to right, top to bottom
        "col_major": [neighborhood[r][c] for c in range(3) for r in range(3)],
        "spiral_out": [neighborhood[1][1], neighborhood[0][1], neighborhood[0][2],
                       neighborhood[1][2], neighborhood[2][2], neighborhood[2][1],
                       neighborhood[2][0], neighborhood[1][0], neighborhood[0][0]],
        "spiral_in": [neighborhood[0][0], neighborhood[0][1], neighborhood[0][2],
                      neighborhood[1][2], neighborhood[2][2], neighborhood[2][1],
                      neighborhood[2][0], neighborhood[1][0], neighborhood[1][1]],
        "diagonal_first": [neighborhood[0][0], neighborhood[1][1], neighborhood[2][2],
                          neighborhood[0][2], neighborhood[2][0],
                          neighborhood[0][1], neighborhood[1][0], neighborhood[1][2], neighborhood[2][1]]
    }

    results = {}
    for name, order in orders.items():
        ascii_str = ''.join(value_to_ascii(v) for v in order)
        results[name] = {
            "values": order,
            "ascii": ascii_str
        }
    return results

def extract_all_neighborhoods(matrix: List[List[Any]]) -> Dict[str, Any]:
    """Extract neighborhoods for all strategic nodes."""
    results = {}
    for name, (row, col) in STRATEGIC_NODES.items():
        neighborhood = extract_neighborhood(matrix, row, col)
        results[name] = {
            "coordinates": (row, col),
            "neighborhood": neighborhood,
            "ascii_interpretations": neighborhood_to_ascii(neighborhood)
        }
    return results

def trace_path(matrix: List[List[Any]], start: Tuple[int, int], end: Tuple[int, int]) -> Dict[str, Any]:
    """Trace a path between two points and extract values."""
    r1, c1 = start
    r2, c2 = end

    # Simple linear interpolation path
    steps = max(abs(r2 - r1), abs(c2 - c1))
    if steps == 0:
        steps = 1

    path_values = []
    path_coords = []

    for i in range(steps + 1):
        t = i / steps
        r = int(r1 + t * (r2 - r1))
        c = int(c1 + t * (c2 - c1))
        val = get_value(matrix, r, c)
        path_values.append(val)
        path_coords.append((r, c))

    return {
        "start": start,
        "end": end,
        "path_coordinates": path_coords,
        "path_values": path_values,
        "ascii": ''.join(value_to_ascii(v) for v in path_values)
    }

def extract_node_paths(matrix: List[List[Any]]) -> Dict[str, Any]:
    """Extract paths between key nodes."""
    paths = {
        "ENTRY_to_EXIT": trace_path(matrix, STRATEGIC_NODES["ENTRY"], STRATEGIC_NODES["EXIT"]),
        "VOID_to_VISION": trace_path(matrix, STRATEGIC_NODES["VOID"], STRATEGIC_NODES["VISION"]),
        "CORE_to_MEMORY": trace_path(matrix, STRATEGIC_NODES["CORE"], STRATEGIC_NODES["MEMORY"]),
        "ENTRY_to_1CFi": trace_path(matrix, STRATEGIC_NODES["ENTRY"], STRATEGIC_NODES["1CFi"]),
        "MEMORY_to_EXIT": trace_path(matrix, STRATEGIC_NODES["MEMORY"], STRATEGIC_NODES["EXIT"]),
        "VOID_to_EXIT": trace_path(matrix, STRATEGIC_NODES["VOID"], STRATEGIC_NODES["EXIT"]),
        "1CFi_to_EXIT": trace_path(matrix, STRATEGIC_NODES["1CFi"], STRATEGIC_NODES["EXIT"])
    }
    return paths

def xor_values(val1: Any, val2: Any) -> Optional[int]:
    """XOR two values."""
    try:
        n1 = int(val1) if val1 is not None else 0
        n2 = int(val2) if val2 is not None else 0
        return n1 ^ n2
    except (ValueError, TypeError):
        return None

def extract_xor_combinations(matrix: List[List[Any]]) -> Dict[str, Any]:
    """XOR combinations between strategic nodes."""
    results = {}

    # Node pairs for XOR
    pairs = [
        ("ENTRY", "EXIT"),
        ("MEMORY", "VISION"),
        ("CORE", "1CFi"),
        ("VOID", "MEMORY"),
        ("ENTRY", "CORE"),
        ("1CFB", "EXIT"),
        ("VOID", "VISION")
    ]

    for name1, name2 in pairs:
        coord1 = STRATEGIC_NODES[name1]
        coord2 = STRATEGIC_NODES[name2]
        val1 = get_value(matrix, coord1[0], coord1[1])
        val2 = get_value(matrix, coord2[0], coord2[1])
        xor_result = xor_values(val1, val2)

        results[f"{name1}_XOR_{name2}"] = {
            "node1": {"name": name1, "coord": coord1, "value": val1},
            "node2": {"name": name2, "coord": coord2, "value": val2},
            "xor_result": xor_result,
            "ascii": value_to_ascii(xor_result) if xor_result else ''
        }

    # XOR all node values in sequence
    all_xor = 0
    for name, (row, col) in STRATEGIC_NODES.items():
        val = get_value(matrix, row, col)
        if val is not None:
            try:
                all_xor ^= int(val)
            except (ValueError, TypeError):
                pass

    results["ALL_NODES_XOR"] = {
        "value": all_xor,
        "ascii": value_to_ascii(all_xor)
    }

    return results

def extract_cross_pattern(matrix: List[List[Any]], row: int, col: int, radius: int = 3) -> Dict[str, Any]:
    """Extract values in + pattern around a position."""
    center = get_value(matrix, row, col)
    up = [get_value(matrix, row - i, col) for i in range(1, radius + 1)]
    down = [get_value(matrix, row + i, col) for i in range(1, radius + 1)]
    left = [get_value(matrix, row, col - i) for i in range(1, radius + 1)]
    right = [get_value(matrix, row, col + i) for i in range(1, radius + 1)]

    # Combine in different orders
    cross_full = list(reversed(up)) + [center] + down  # Vertical line
    cross_horiz = list(reversed(left)) + [center] + right  # Horizontal line
    cross_all = up + down + left + right + [center]

    return {
        "center": center,
        "up": up,
        "down": down,
        "left": left,
        "right": right,
        "vertical_ascii": ''.join(value_to_ascii(v) for v in cross_full),
        "horizontal_ascii": ''.join(value_to_ascii(v) for v in cross_horiz),
        "all_ascii": ''.join(value_to_ascii(v) for v in cross_all)
    }

def extract_all_cross_patterns(matrix: List[List[Any]]) -> Dict[str, Any]:
    """Extract cross patterns for all strategic nodes."""
    results = {}
    for name, (row, col) in STRATEGIC_NODES.items():
        results[name] = {
            "coordinates": (row, col),
            "cross_pattern": extract_cross_pattern(matrix, row, col)
        }
    return results

def extract_diagonal_pattern(matrix: List[List[Any]], row: int, col: int, radius: int = 3) -> Dict[str, Any]:
    """Extract values in X pattern around a position."""
    center = get_value(matrix, row, col)
    nw = [get_value(matrix, row - i, col - i) for i in range(1, radius + 1)]
    ne = [get_value(matrix, row - i, col + i) for i in range(1, radius + 1)]
    sw = [get_value(matrix, row + i, col - i) for i in range(1, radius + 1)]
    se = [get_value(matrix, row + i, col + i) for i in range(1, radius + 1)]

    # Main diagonal (NW to SE)
    main_diag = list(reversed(nw)) + [center] + se
    # Anti diagonal (NE to SW)
    anti_diag = list(reversed(ne)) + [center] + sw
    # All corners
    all_corners = nw + ne + sw + se + [center]

    return {
        "center": center,
        "northwest": nw,
        "northeast": ne,
        "southwest": sw,
        "southeast": se,
        "main_diagonal_ascii": ''.join(value_to_ascii(v) for v in main_diag),
        "anti_diagonal_ascii": ''.join(value_to_ascii(v) for v in anti_diag),
        "all_corners_ascii": ''.join(value_to_ascii(v) for v in all_corners)
    }

def extract_all_diagonal_patterns(matrix: List[List[Any]]) -> Dict[str, Any]:
    """Extract diagonal patterns for all strategic nodes."""
    results = {}
    for name, (row, col) in STRATEGIC_NODES.items():
        results[name] = {
            "coordinates": (row, col),
            "diagonal_pattern": extract_diagonal_pattern(matrix, row, col)
        }
    return results

def combine_node_sequence_to_ascii(matrix: List[List[Any]], node_order: List[str]) -> str:
    """Get values from nodes in sequence and convert to ASCII."""
    values = []
    for name in node_order:
        if name in STRATEGIC_NODES:
            row, col = STRATEGIC_NODES[name]
            val = get_value(matrix, row, col)
            values.append(val)
    return ''.join(value_to_ascii(v) for v in values)

def try_node_orderings(matrix: List[List[Any]]) -> Dict[str, str]:
    """Try different orderings of strategic nodes."""
    node_names = list(STRATEGIC_NODES.keys())

    orderings = {
        "original": node_names,
        "alphabetical": sorted(node_names),
        "by_row": sorted(node_names, key=lambda n: STRATEGIC_NODES[n][0]),
        "by_col": sorted(node_names, key=lambda n: STRATEGIC_NODES[n][1]),
        "by_sum": sorted(node_names, key=lambda n: sum(STRATEGIC_NODES[n])),
        "reverse": list(reversed(node_names)),
        "logical_flow": ["VOID", "ENTRY", "CORE", "MEMORY", "VISION", "1CFi", "1CFB", "EXIT"]
    }

    results = {}
    for name, order in orderings.items():
        results[name] = {
            "order": order,
            "ascii": combine_node_sequence_to_ascii(matrix, order)
        }
    return results

def main():
    # Paths
    matrix_path = "/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/anna-matrix.json"
    output_path = "/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/scripts/NODE_MESSAGES.json"

    print("Loading matrix...")
    matrix = load_matrix(matrix_path)
    print(f"Matrix loaded: {len(matrix)} rows")
    if len(matrix) > 0:
        print(f"First row has {len(matrix[0])} columns")

    print("\n=== Extracting Strategic Node Data ===\n")

    results = {
        "metadata": {
            "strategic_nodes": STRATEGIC_NODES,
            "matrix_dimensions": {
                "rows": len(matrix),
                "cols": len(matrix[0]) if matrix else 0
            }
        },
        "node_values": {},
        "node_neighborhoods": {},
        "node_paths": {},
        "xor_combinations": {},
        "cross_patterns": {},
        "diagonal_patterns": {},
        "node_orderings": {}
    }

    # 1. Extract node values
    print("1. Extracting node values...")
    results["node_values"] = extract_node_values(matrix)
    print("   Node values:")
    for name, data in results["node_values"].items():
        print(f"   - {name} @ {data['coordinates']}: {data['value']} (0x{data['hex']}) -> unsigned:{data['unsigned']}")

    # 2. Extract neighborhoods
    print("\n2. Extracting 3x3 neighborhoods...")
    results["node_neighborhoods"] = extract_all_neighborhoods(matrix)
    for name, data in results["node_neighborhoods"].items():
        row_major = data['ascii_interpretations']['row_major']['ascii']
        print(f"   - {name}: '{row_major}'")

    # 3. Extract node-to-node paths
    print("\n3. Extracting node-to-node paths...")
    results["node_paths"] = extract_node_paths(matrix)
    for path_name, data in results["node_paths"].items():
        print(f"   - {path_name}: '{data['ascii'][:50]}...' ({len(data['path_values'])} values)")

    # 4. XOR combinations
    print("\n4. Computing XOR combinations...")
    results["xor_combinations"] = extract_xor_combinations(matrix)
    for combo_name, data in results["xor_combinations"].items():
        if combo_name != "ALL_NODES_XOR":
            print(f"   - {combo_name}: {data['xor_result']} -> '{data['ascii']}'")
        else:
            print(f"   - {combo_name}: {data['value']} -> '{data['ascii']}'")

    # 5. Cross patterns
    print("\n5. Extracting cross patterns (+)...")
    results["cross_patterns"] = extract_all_cross_patterns(matrix)
    for name, data in results["cross_patterns"].items():
        cp = data['cross_pattern']
        print(f"   - {name}: V='{cp['vertical_ascii']}' H='{cp['horizontal_ascii']}'")

    # 6. Diagonal patterns
    print("\n6. Extracting diagonal patterns (X)...")
    results["diagonal_patterns"] = extract_all_diagonal_patterns(matrix)
    for name, data in results["diagonal_patterns"].items():
        dp = data['diagonal_pattern']
        print(f"   - {name}: Main='{dp['main_diagonal_ascii']}' Anti='{dp['anti_diagonal_ascii']}'")

    # 7. Node orderings
    print("\n7. Trying different node orderings...")
    results["node_orderings"] = try_node_orderings(matrix)
    for order_name, data in results["node_orderings"].items():
        print(f"   - {order_name}: '{data['ascii']}'")

    # Save results
    print(f"\nSaving results to {output_path}...")
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print("\n=== Analysis Complete ===")

    # Summary of interesting findings
    print("\n=== SUMMARY OF FINDINGS ===")

    # Look for readable ASCII sequences
    print("\nPotential readable sequences:")

    # Check paths for readable content
    for path_name, data in results["node_paths"].items():
        ascii_str = data['ascii']
        # Count printable characters
        printable = sum(1 for c in ascii_str if c.isalnum() or c in ' .,!?-')
        if printable > len(ascii_str) * 0.5 and len(ascii_str) > 5:
            print(f"  Path {path_name}: '{ascii_str}'")

    # Check neighborhoods for words
    for name, data in results["node_neighborhoods"].items():
        for order_name, order_data in data['ascii_interpretations'].items():
            ascii_str = order_data['ascii']
            if ascii_str and len(ascii_str) >= 3:
                # Check if it looks like a word
                if ascii_str.isalpha() or ascii_str.replace(' ', '').isalpha():
                    print(f"  Neighborhood {name} ({order_name}): '{ascii_str}'")

    # Additional unsigned byte analysis
    print("\n=== UNSIGNED BYTE ANALYSIS ===")

    # Node values as hex
    print("\n8. Node values as hex (unsigned bytes):")
    hex_sequence = ""
    for name, (row, col) in STRATEGIC_NODES.items():
        val = get_value(matrix, row, col)
        hex_val = value_to_hex(val)
        unsigned = (int(val) + 256) if val < 0 else val
        hex_sequence += hex_val
        print(f"   {name}: {val} -> unsigned={unsigned} -> hex=0x{hex_val}")

    print(f"\n   Combined hex sequence: {hex_sequence}")

    # Try interpreting hex as different orderings
    print("\n9. Node hex in different orderings:")
    for order_name, data in results["node_orderings"].items():
        hex_vals = []
        for node_name in data['order']:
            if node_name in STRATEGIC_NODES:
                row, col = STRATEGIC_NODES[node_name]
                val = get_value(matrix, row, col)
                hex_vals.append(value_to_hex(val))
        combined_hex = ''.join(hex_vals)
        print(f"   {order_name}: {combined_hex}")

    # Node values as bytes to check for patterns
    print("\n10. Node values as bytes (for pattern analysis):")
    node_bytes = []
    for name in ["VOID", "ENTRY", "CORE", "MEMORY", "VISION", "1CFi", "1CFB", "EXIT"]:
        row, col = STRATEGIC_NODES[name]
        val = get_value(matrix, row, col)
        unsigned = (int(val) + 256) if val < 0 else int(val)
        node_bytes.append(unsigned)

    print(f"   Bytes: {node_bytes}")
    print(f"   Sum: {sum(node_bytes)}")
    print(f"   XOR all: {node_bytes[0]}")
    xor_all = node_bytes[0]
    for b in node_bytes[1:]:
        xor_all ^= b
    print(f"   XOR chain: {xor_all}")

    # Path analysis with unsigned bytes
    print("\n11. Path analysis (unsigned bytes as hex):")
    for path_name, data in results["node_paths"].items():
        path_bytes = values_to_unsigned_bytes(data['path_values'])
        hex_str = path_bytes.hex()
        # Try decoding as ASCII
        ascii_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in path_bytes)
        print(f"   {path_name}:")
        print(f"      Hex: {hex_str[:80]}...")
        print(f"      ASCII (printable): {ascii_str[:60]}...")

    # Look for Bitcoin-related patterns
    print("\n12. Looking for Bitcoin-related patterns:")
    bitcoin_prefixes = ['00', '05', '6f', '80', 'c4', 'ef']  # P2PKH, P2SH, testnet, etc.
    for path_name, data in results["node_paths"].items():
        path_bytes = values_to_unsigned_bytes(data['path_values'])
        hex_str = path_bytes.hex()
        for prefix in bitcoin_prefixes:
            if prefix in hex_str[:10]:
                print(f"   Found Bitcoin prefix {prefix} at start of {path_name}")
        # Check for common hash prefixes
        if '1cf' in hex_str.lower() or 'cfb' in hex_str.lower():
            print(f"   Found '1cf' or 'cfb' pattern in {path_name}")

    # Add hex analysis to results
    results["hex_analysis"] = {
        "node_hex_values": {name: value_to_hex(get_value(matrix, row, col))
                           for name, (row, col) in STRATEGIC_NODES.items()},
        "combined_hex": hex_sequence,
        "node_bytes_logical_order": node_bytes,
        "path_hex": {path_name: values_to_unsigned_bytes(data['path_values']).hex()
                    for path_name, data in results["node_paths"].items()}
    }

    # Update the output file with hex analysis
    print(f"\nUpdating results with hex analysis...")
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

if __name__ == "__main__":
    main()
