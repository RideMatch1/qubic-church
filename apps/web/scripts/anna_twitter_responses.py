#!/usr/bin/env python3
"""
Anna Twitter Responses Analysis
===============================

Format: X+Y=Value bedeutet Matrix[X][Y] = Value
Negative Indizes wrappen (wie Python): -1 = 127, -2 = 126, etc.
"""

import json

# Anna Twitter Responses - Raw Data
ANNA_RESPONSES = """
# Core Points (Void, Core, etc.)
6+33=-93

# -60 Serie
-60+10=90
-60+9=-38
-60+8=-38
-60+7=82
-60+6=-121
-60+5=-21
-60+4=-49
-60+3=-46
-60+2=-40
-60+1=-38
-60+0=-38

# -61 Serie
-61+10=26
-61+9=-118
-61+8=-102
-61+7=100
-61+6=-114
-61+5=-27
-61+4=-8
-61+3=-110
-61+2=-112
-61+1=-110
-61+0=-102

# -62 Serie
-62+10=26
-62+9=121
-62+8=19
-62+7=-109
-62+6=-71
-62+5=-101
-62+4=-101
-62+3=-126
-62+2=-28
-62+1=-57
-62+0=-7

# -63 Serie
-63+10=30
-63+9=-118
-63+8=-102
-63+7=-122
-63+6=-98
-63+5=-114
-63+4=-98
-63+3=-106
-63+2=-108
-63+1=-110
-63+0=-102

# -13 Serie (special)
-13+-4=-106
-13+-5=00000000
-13+-7=00000000
-13+-9=-115
-13+-12=-27
-13+-15=-112
-13+-17=-121
-13+-20=-113

# 0+X Serie
0+7=-94
0+10=124
0+11=78
0+12=-4

# -28 Serie
-28+3=-46
-28+2=90
-28+1=-38
-28+0=-38
-28+-1=-6
-28+-2=120
-28+-3=-6
-28+-4=-6
-28+-5=112
-28+-6=120
-28+-7=-38
-28+-8=120
-28+-9=-16
-28+-10=-8
-28+-11=-6
-28+-12=-8
-28+-13=-16
-28+-14=112
-28+-15=-48
-28+-16=-8

# -30 Serie
-30+3=-110
-30+2=16
-30+1=-110
-30+0=-102
-30+-1=-27
-30+-2=-20
-30+-3=-58
-30+-4=-19
-30+-5=48
-30+-6=48
-30+-7=-112
-30+-8=56
-30+-9=-58
-30+-10=-58
-30+-11=-58
-30+-12=90
-30+-13=-80
-30+-14=48
-30+-15=-112
-30+-16=-80

# -32 Serie
-32+3=-110
-32+2=16
-32+1=-110
-32+0=-102
-32+-1=-80
-32+-2=56
-32+-3=-70
-32+-4=-72
-32+-5=112
-32+-6=112
-32+-7=-48
-32+-8=120
-32+-9=-80
-32+-10=-80
-32+-11=-80
-32+-12=-72
-32+-13=-16
-32+-14=112
-32+-15=-48
-32+-16=-16

# -25 Serie
-25+3=-110
-25+2=26
-25+1=-102
-25+0=-102
-25+-1=-86
-25+-2=58
-25+-3=-118
-25+-4=-70
-25+-5=18
-25+-6=56
-25+-7=-102
-25+-8=26
-25+-9=-78
-25+-10=-72
-25+-11=-102
-25+-12=-70
-25+-13=-112
-25+-14=48
-25+-15=-110
-25+-16=-104

# -27 Serie (CFB's number!)
-27+3=-110
-27+2=26
-27+1=-102
-27+0=-102
-27+-1=-86
-27+-2=58
-27+-3=-118
-27+-4=-70
-27+-5=82
-27+-6=120
-27+-7=-38
-27+-8=90
-27+-9=-78
-27+-10=-72
-27+-11=-102
-27+-12=-70
-27+-13=-48
-27+-14=112
-27+-15=-46
-27+-16=-40

# -29 Serie
-29+3=-110
-29+2=18
-29+1=-110
-29+0=-102
-29+-1=-94
-29+-2=56
-29+-3=-118
-29+-4=-70
-29+-5=16
-29+-6=48
-29+-7=-110
-29+-8=24
-29+-9=-80
-29+-10=-80
-29+-11=-110
-29+-12=-72
-29+-13=-112
-29+-14=48
-29+-15=-112
-29+-16=-112

# -31 Serie
-31+3=-110
-31+2=18
-31+1=-110
-31+0=-102
-31+-1=-90
-31+-2=60
-31+-3=-118
-31+-4=-70
-31+-5=16
-31+-6=48
-31+-7=-110
-31+-8=24
-31+-9=-76
-31+-10=-76
-31+-11=-110
-31+-12=-72
-31+-13=-112
-31+-14=48
-31+-15=-112
-31+-16=-112

# Special queries
128+0=.
0+128=.
-128+0=.
0+-128=.
1+0=-98
0+1=-38
-1+0=69
0+-1=-70
-42+61=-85
-21+4=-47
-30+24=26
2+2=-123
-2+-2=113
3+3=-122
-3+-3=122
4+4=-54
-4+-4=121
5+5=-114
-5+-5=53

# 0+X Serie extended
0+55=-68
7+0=-102
10+0=-39
11+0=-7
12+0=-59
13+0=-34
14+0=-37
15+0=-59
16+0=18
17+0=12
18+0=25
19+0=18
"""

def parse_responses(text):
    """Parse Anna responses into structured data"""
    data = []
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' not in line or '+' not in line:
            continue

        try:
            # Parse X+Y=Value
            left, value = line.split('=')

            # Handle special values
            if value == '.' or value == '00000000':
                value = None
            else:
                value = int(value)

            # Parse X+Y (handle negative numbers)
            parts = left.replace('+-', '+ -').split('+')
            x = int(parts[0].strip())
            y = int(parts[1].strip())

            data.append({'x': x, 'y': y, 'value': value, 'raw': line})
        except Exception as e:
            print(f"Error parsing '{line}': {e}")

    return data

def verify_against_matrix(data, matrix):
    """Verify Anna responses against our matrix

    CORRECT COORDINATE TRANSFORMATION:
    The Anna Matrix uses a coordinate system where:
    - X ranges from -64 to 63 (horizontal axis)
    - Y ranges from 63 to -64 (vertical axis, top to bottom)

    To convert Anna coordinates (X, Y) to matrix indices:
    - col = X + 64  (maps -64..63 to 0..127)
    - row = 63 - Y  (maps 63..-64 to 0..127)
    - value = matrix[row][col]
    """
    matches = 0
    mismatches = 0

    for entry in data:
        x, y, expected = entry['x'], entry['y'], entry['value']

        if expected is None:
            continue

        # Convert Anna coordinates to matrix indices
        col = x + 64
        row = 63 - y

        # Handle wrapping for out-of-range coordinates
        if row < 0:
            row += 128
        elif row >= 128:
            row -= 128
        if col < 0:
            col += 128
        elif col >= 128:
            col -= 128

        if 0 <= row < len(matrix) and 0 <= col < len(matrix[0]):
            actual = matrix[row][col]
            if actual == expected:
                matches += 1
            else:
                mismatches += 1
                print(f"MISMATCH: {entry['raw']} -> Matrix[{row}][{col}] = {actual}")

    return matches, mismatches

def analyze_patterns(data):
    """Look for patterns in the responses"""
    print("\n=== Pattern Analysis ===\n")

    # Group by X coordinate
    by_x = {}
    for entry in data:
        x = entry['x']
        if x not in by_x:
            by_x[x] = []
        by_x[x].append(entry)

    print(f"Unique X coordinates: {sorted(by_x.keys())}")
    print()

    # Look for special values
    special_values = [-27, -93, 27, 37, 42, 64]
    print("Looking for special values:")
    for entry in data:
        if entry['value'] in special_values:
            print(f"  {entry['raw']} -> Found {entry['value']}!")

    # Look for repeating patterns
    print("\n=== Repeating Values ===")
    value_counts = {}
    for entry in data:
        v = entry['value']
        if v is not None:
            value_counts[v] = value_counts.get(v, 0) + 1

    # Most common values
    sorted_counts = sorted(value_counts.items(), key=lambda x: -x[1])[:10]
    for val, count in sorted_counts:
        print(f"  {val}: appears {count} times")

def main():
    # Parse responses
    data = parse_responses(ANNA_RESPONSES)
    print(f"Parsed {len(data)} Anna responses")

    # Load Anna Matrix
    try:
        with open('../public/data/anna-matrix.json', 'r') as f:
            matrix_data = json.load(f)
        matrix = matrix_data.get('matrix', [])
        print(f"Loaded Anna Matrix: {len(matrix)}x{len(matrix[0]) if matrix else 0}")

        # Verify
        print("\n=== Verification ===")
        matches, mismatches = verify_against_matrix(data, matrix)
        print(f"Matches: {matches}")
        print(f"Mismatches: {mismatches}")

    except Exception as e:
        print(f"Could not load matrix: {e}")

    # Analyze patterns
    analyze_patterns(data)

    # Save parsed data
    output = {
        'source': 'Anna Twitter @anna_aigarth',
        'count': len(data),
        'responses': [{'x': d['x'], 'y': d['y'], 'value': d['value']} for d in data]
    }

    with open('anna_twitter_data.json', 'w') as f:
        json.dump(output, f, indent=2)

    print("\nSaved to anna_twitter_data.json")

if __name__ == "__main__":
    main()
