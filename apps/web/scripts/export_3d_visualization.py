#!/usr/bin/env python3
"""
3D VISUALIZATION EXPORT SCRIPT
==============================

Exports bridge data in format suitable for React Three Fiber visualization.

Creates:
- bridges_3d.json: 3D coordinates and connections
- visualization_config.json: Colors, sizes, and styling

Author: qubic-academic-docs
Date: 2026-01-23
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


def get_bridge_color(bridge: Dict[str, Any]) -> str:
    """
    Determine color for a bridge based on its properties.
    """
    # Check for special addresses
    address = bridge.get("bitcoin", {}).get("address", "")

    if address.startswith("1CFB"):
        return "#ff6b00"  # Orange - CFB signature
    elif address.startswith("1CF"):
        return "#ffd700"  # Gold - CF prefix
    elif address.startswith("1CJ"):
        return "#00bfff"  # Deep sky blue
    elif address.startswith("1CH"):
        return "#32cd32"  # Lime green
    else:
        return "#888888"  # Gray - default

    # Check ternary category
    ternary_cat = bridge.get("ternary", {}).get("category", "NEUTRAL")
    if ternary_cat == "POSITIVE":
        return "#00ff88"  # Bright green
    elif ternary_cat == "NEGATIVE":
        return "#ff4488"  # Bright pink/red
    else:
        return "#8888ff"  # Light blue


def get_bridge_size(bridge: Dict[str, Any]) -> float:
    """
    Determine size for a bridge node based on importance.
    """
    address = bridge.get("bitcoin", {}).get("address", "")

    if address.startswith("1CFB"):
        return 2.0  # Largest - CFB signature
    elif address.startswith("1CF"):
        return 1.5  # Large - CF prefix
    elif bridge.get("special"):
        return 1.3  # Medium-large - special
    else:
        return 0.8  # Default size


def compute_3d_position(bridge: Dict[str, Any]) -> List[float]:
    """
    Compute 3D position for visualization.

    Maps:
    - X: column (0-127 -> scaled)
    - Y: offset or row (0-127 -> scaled)
    - Z: layer based on type/category

    Returns:
        [x, y, z] coordinates
    """
    bridge_type = bridge.get("type", "column")

    if bridge_type == "column":
        col = bridge.get("column", 0)
        offset = bridge.get("offset", 0)
        x = (col - 64) * 0.1  # Center and scale
        y = (offset - 64) * 0.1
        z = (col + offset) % 3 * 2.0  # Layer separation
    elif bridge_type == "row":
        row = bridge.get("row", 0)
        offset = bridge.get("offset", 0)
        x = (row - 64) * 0.1
        y = (offset - 64) * 0.1
        z = 3.0 + (row % 3) * 2.0  # Higher layers for rows
    elif bridge_type == "xor_pair":
        col1 = bridge.get("column_1", 0)
        col2 = bridge.get("column_2", 0)
        offset = bridge.get("offset", 0)
        x = ((col1 + col2) / 2 - 64) * 0.1
        y = (offset - 64) * 0.1
        z = 6.0 + (col1 % 3) * 2.0  # Highest layers for XOR pairs
    else:
        x, y, z = 0, 0, 0

    return [round(x, 4), round(y, 4), round(z, 4)]


def create_connection(bridge: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create connection data for the bridge's symmetric partner.
    """
    bridge_type = bridge.get("type", "column")

    if bridge_type == "column":
        symmetric_col = bridge.get("symmetric_column")
        if symmetric_col is not None:
            return {
                "type": "symmetry",
                "from_column": bridge.get("column"),
                "to_column": symmetric_col,
                "relationship": "XOR_PARTNER"
            }
    elif bridge_type == "xor_pair":
        return {
            "type": "xor",
            "columns": [bridge.get("column_1"), bridge.get("column_2")],
            "relationship": "XOR_OPERATION"
        }

    return None


def export_for_three_fiber(bridges: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Export bridge data in format optimized for React Three Fiber.

    Returns:
        Dict ready for JSON export
    """
    nodes = []
    connections = []
    layers = {}

    for bridge in bridges:
        bridge_id = bridge.get("id")
        position = compute_3d_position(bridge)
        color = get_bridge_color(bridge)
        size = get_bridge_size(bridge)

        node = {
            "id": bridge_id,
            "name": bridge.get("name", f"Bridge_{bridge_id}"),
            "type": bridge.get("type", "column"),
            "position": position,
            "color": color,
            "size": size,
            "bitcoin_address": bridge.get("bitcoin", {}).get("address", ""),
            "qubic_identity": bridge.get("qubic_xor", {}).get("identity", ""),
            "ternary_category": bridge.get("ternary", {}).get("category", "NEUTRAL"),
            "special": bridge.get("special"),
            "metadata": {
                "column": bridge.get("column"),
                "row": bridge.get("row"),
                "offset": bridge.get("offset"),
                "hash160_prefix": bridge.get("bitcoin", {}).get("prefix")
            }
        }
        nodes.append(node)

        # Track layers
        z_layer = int(position[2] / 2)
        if z_layer not in layers:
            layers[z_layer] = {"count": 0, "nodes": []}
        layers[z_layer]["count"] += 1
        layers[z_layer]["nodes"].append(bridge_id)

        # Create connections
        conn = create_connection(bridge)
        if conn:
            conn["source_id"] = bridge_id
            connections.append(conn)

    # Create symmetric connections (link pairs)
    symmetric_pairs = []
    column_map = {}
    for node in nodes:
        col = node.get("metadata", {}).get("column")
        if col is not None:
            if col not in column_map:
                column_map[col] = []
            column_map[col].append(node["id"])

    for col, node_ids in column_map.items():
        sym_col = 127 - col
        if sym_col in column_map and sym_col != col:
            for src_id in node_ids:
                for tgt_id in column_map[sym_col]:
                    symmetric_pairs.append({
                        "source": src_id,
                        "target": tgt_id,
                        "type": "symmetric"
                    })

    return {
        "nodes": nodes,
        "connections": connections,
        "symmetric_pairs": symmetric_pairs[:1000],  # Limit for performance
        "layers": {str(k): v for k, v in layers.items()}
    }


def create_visualization_config() -> Dict[str, Any]:
    """
    Create configuration for the 3D visualization.
    """
    return {
        "scene": {
            "background_color": "#0a0a0f",
            "ambient_light": {"intensity": 0.3},
            "point_light": {
                "position": [10, 10, 10],
                "intensity": 1.0
            }
        },
        "camera": {
            "position": [20, 20, 20],
            "fov": 60,
            "near": 0.1,
            "far": 1000
        },
        "colors": {
            "cfb_signature": "#ff6b00",
            "cf_prefix": "#ffd700",
            "positive_ternary": "#00ff88",
            "negative_ternary": "#ff4488",
            "neutral_ternary": "#8888ff",
            "connection_symmetric": "#ffffff40",
            "connection_xor": "#ff880080"
        },
        "sizes": {
            "cfb_signature": 2.0,
            "cf_prefix": 1.5,
            "special": 1.3,
            "default": 0.8
        },
        "animation": {
            "rotation_speed": 0.001,
            "pulse_frequency": 2.0,
            "connection_animation": True
        },
        "interaction": {
            "hover_scale": 1.5,
            "click_zoom": True,
            "tooltip_enabled": True
        },
        "layers": {
            "0": {"name": "Base Layer", "z_offset": 0},
            "1": {"name": "Column Layer 1", "z_offset": 2},
            "2": {"name": "Column Layer 2", "z_offset": 4},
            "3": {"name": "Row Layer 0", "z_offset": 6},
            "4": {"name": "Row Layer 1", "z_offset": 8},
            "5": {"name": "Row Layer 2", "z_offset": 10},
            "6": {"name": "XOR Layer", "z_offset": 12}
        }
    }


def main():
    """Main function."""
    print("=" * 60)
    print("3D VISUALIZATION EXPORT")
    print("=" * 60)

    # Load bridges
    bridges_path = Path(__file__).parent / "COMPLETE_BRIDGE_DATASET.json"
    if not bridges_path.exists():
        print(f"ERROR: Bridge dataset not found: {bridges_path}")
        print("Run COMPLETE_BRIDGE_GENERATOR.py first.")
        return

    print(f"\nLoading bridges from: {bridges_path}")
    with open(bridges_path, 'r') as f:
        data = json.load(f)

    bridges = data.get("bridges", [])
    print(f"Loaded {len(bridges)} bridges")

    # Export for Three Fiber
    print("\nExporting for React Three Fiber...")
    three_fiber_data = export_for_three_fiber(bridges)

    # Create visualization config
    config = create_visualization_config()

    # Save outputs
    output_dir = Path(__file__).parent

    # Main 3D data
    three_fiber_path = output_dir / "bridges_3d.json"
    with open(three_fiber_path, 'w') as f:
        json.dump(three_fiber_data, f, indent=2)

    # Config
    config_path = output_dir / "visualization_config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    # Also save to public/data for web access
    public_data_dir = output_dir.parent / "public" / "data"
    if public_data_dir.exists():
        public_three_fiber = public_data_dir / "bridges_3d.json"
        with open(public_three_fiber, 'w') as f:
            json.dump(three_fiber_data, f, indent=2)
        print(f"Also saved to: {public_three_fiber}")

    # Print summary
    print(f"\n{'=' * 60}")
    print("EXPORT COMPLETE")
    print(f"{'=' * 60}")
    print(f"Nodes: {len(three_fiber_data['nodes'])}")
    print(f"Connections: {len(three_fiber_data['connections'])}")
    print(f"Symmetric pairs: {len(three_fiber_data['symmetric_pairs'])}")
    print(f"Layers: {len(three_fiber_data['layers'])}")
    print(f"\nFiles saved:")
    print(f"  {three_fiber_path}")
    print(f"  {config_path}")


if __name__ == "__main__":
    main()
