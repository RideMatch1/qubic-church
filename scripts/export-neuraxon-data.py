#!/usr/bin/env python3
"""
Neuraxon Network Data Export Script

Generates 3D network visualization data from Qubic seeds.
Each seed becomes a neuron with ternary state derived from SHA256.
Connections are generated based on seed similarity.

Output: JSON file with nodes, edges, and frame groupings for the frontend.
"""

import json
import hashlib
import math
import random
from pathlib import Path
from typing import List, Dict, Any

# Configuration
NODES_PER_FRAME = 512
CONNECTIONS_PER_NODE = 8  # Average connections per node
SEED_COUNT = None  # None = use all seeds

def sha256_hash(data: str) -> bytes:
    """Compute SHA256 hash of string."""
    return hashlib.sha256(data.encode('utf-8')).digest()

def derive_ternary_state(seed: str) -> int:
    """
    Derive ternary state (-1, 0, +1) from seed using SHA256.
    Uses first byte mod 3 - 1 for ternary mapping.
    """
    h = sha256_hash(seed)
    return (h[0] % 3) - 1

def generate_3d_position(index: int, total: int, frame_index: int) -> List[float]:
    """
    Generate 3D position using spherical distribution.
    Uses golden angle for even distribution on sphere.
    """
    # Golden angle in radians
    phi = math.pi * (3.0 - math.sqrt(5.0))

    # Offset within frame
    i = index % NODES_PER_FRAME
    n = min(NODES_PER_FRAME, total - frame_index * NODES_PER_FRAME)

    # Spherical coordinates with some randomness
    y = 1 - (i / float(n - 1 if n > 1 else 1)) * 2  # -1 to 1
    radius = math.sqrt(1 - y * y)

    theta = phi * i

    # Add layer depth based on node type
    node_type = determine_node_type(index, n)
    depth_offset = 0
    if node_type == 'input':
        depth_offset = -2
    elif node_type == 'output':
        depth_offset = 2

    x = math.cos(theta) * radius * 5
    z = math.sin(theta) * radius * 5 + depth_offset
    y = y * 5

    # Add small random offset for visual interest
    random.seed(index + frame_index * 10000)
    x += random.uniform(-0.3, 0.3)
    y += random.uniform(-0.3, 0.3)
    z += random.uniform(-0.3, 0.3)

    return [round(x, 3), round(y, 3), round(z, 3)]

def determine_node_type(index: int, frame_size: int) -> str:
    """Determine node type based on position in frame."""
    if index < frame_size * 0.15:
        return 'input'
    elif index > frame_size * 0.85:
        return 'output'
    return 'hidden'

def calculate_connection_weight(seed1: str, seed2: str) -> float:
    """
    Calculate connection weight based on seed similarity.
    Uses Jaccard-like similarity on character positions.
    """
    h1 = sha256_hash(seed1)
    h2 = sha256_hash(seed2)

    # XOR bytes and count matching bits
    matching_bits = sum(bin(b1 ^ b2).count('0') - 1 for b1, b2 in zip(h1[:8], h2[:8]))
    max_bits = 8 * 8  # 8 bytes * 8 bits

    similarity = matching_bits / max_bits

    # Add small random variation
    random.seed(hash((seed1, seed2)))
    variation = random.uniform(-0.1, 0.1)

    return round(max(0.1, min(1.0, similarity + variation)), 3)

def determine_connection_type(weight: float) -> str:
    """Determine connection type based on weight."""
    if weight > 0.7:
        return 'fast'
    elif weight > 0.4:
        return 'slow'
    return 'meta'

def generate_edges(nodes: List[Dict], frame_nodes: List[int]) -> List[Dict]:
    """Generate edges for nodes within a frame."""
    edges = []
    node_count = len(frame_nodes)

    for i, node_idx in enumerate(frame_nodes):
        node = nodes[node_idx]

        # Connect to nearby nodes (by index position in frame)
        num_connections = random.randint(4, CONNECTIONS_PER_NODE + 4)

        for _ in range(num_connections):
            # Prefer connections to nearby nodes
            offset = int(random.gauss(0, node_count / 6))
            target_local = (i + offset) % node_count
            target_idx = frame_nodes[target_local]

            if target_idx != node_idx:
                weight = calculate_connection_weight(node['seed'], nodes[target_idx]['seed'])
                edges.append({
                    'source': node_idx,
                    'target': target_idx,
                    'weight': weight,
                    'type': determine_connection_type(weight)
                })

    return edges

def main():
    # Load Qubic seeds
    seeds_path = Path(__file__).parent.parent / 'apps/web/public/data/qubic-seeds.json'

    print(f"Loading seeds from {seeds_path}...")
    with open(seeds_path, 'r') as f:
        seeds_data = json.load(f)

    records = seeds_data['records']
    if SEED_COUNT:
        records = records[:SEED_COUNT]

    total_seeds = len(records)
    print(f"Processing {total_seeds} seeds...")

    # Generate nodes
    nodes = []
    for i, record in enumerate(records):
        frame_index = i // NODES_PER_FRAME

        node = {
            'id': i,
            'type': determine_node_type(i % NODES_PER_FRAME, NODES_PER_FRAME),
            'seed': record['seed'],
            'realId': record['realIdentity'],
            'documentedId': record.get('documentedIdentity', ''),
            'state': derive_ternary_state(record['seed']),
            'position': generate_3d_position(i, total_seeds, frame_index),
            'frame': frame_index
        }
        nodes.append(node)

        if (i + 1) % 5000 == 0:
            print(f"  Processed {i + 1}/{total_seeds} nodes...")

    print(f"Generated {len(nodes)} nodes")

    # Generate frames
    num_frames = math.ceil(total_seeds / NODES_PER_FRAME)
    frames = []
    all_edges = []

    print(f"Generating {num_frames} frames with edges...")

    for frame_idx in range(num_frames):
        start_idx = frame_idx * NODES_PER_FRAME
        end_idx = min(start_idx + NODES_PER_FRAME, total_seeds)
        frame_node_ids = list(range(start_idx, end_idx))

        frames.append({
            'id': frame_idx,
            'label': f'Frame {frame_idx + 1}',
            'nodeIds': frame_node_ids,
            'startId': start_idx,
            'endId': end_idx - 1
        })

        # Generate edges for this frame
        frame_edges = generate_edges(nodes, frame_node_ids)
        all_edges.extend(frame_edges)

        if (frame_idx + 1) % 10 == 0:
            print(f"  Generated edges for frame {frame_idx + 1}/{num_frames}")

    print(f"Generated {len(all_edges)} edges across {num_frames} frames")

    # Calculate statistics
    state_counts = {-1: 0, 0: 0, 1: 0}
    type_counts = {'input': 0, 'hidden': 0, 'output': 0}

    for node in nodes:
        state_counts[node['state']] += 1
        type_counts[node['type']] += 1

    # Build output
    output = {
        'metadata': {
            'totalNodes': len(nodes),
            'totalEdges': len(all_edges),
            'totalFrames': num_frames,
            'nodesPerFrame': NODES_PER_FRAME,
            'stateDistribution': {
                'negative': state_counts[-1],
                'zero': state_counts[0],
                'positive': state_counts[1]
            },
            'typeDistribution': type_counts
        },
        'nodes': nodes,
        'edges': all_edges,
        'frames': frames
    }

    # Write output
    output_path = Path(__file__).parent.parent / 'apps/web/public/data/neuraxon-network.json'

    print(f"\nWriting to {output_path}...")
    with open(output_path, 'w') as f:
        json.dump(output, f)

    # Calculate file size
    file_size = output_path.stat().st_size
    print(f"Output file size: {file_size / 1024 / 1024:.2f} MB")

    print("\nStatistics:")
    print(f"  Nodes: {len(nodes)}")
    print(f"  Edges: {len(all_edges)}")
    print(f"  Frames: {num_frames}")
    print(f"  State distribution: -1={state_counts[-1]}, 0={state_counts[0]}, +1={state_counts[1]}")
    print(f"  Type distribution: input={type_counts['input']}, hidden={type_counts['hidden']}, output={type_counts['output']}")
    print("\nDone!")

if __name__ == '__main__':
    main()
