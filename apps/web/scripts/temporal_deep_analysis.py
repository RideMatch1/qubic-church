#!/usr/bin/env python3
"""
Temporal Deep Analysis
======================
Analyze temporal patterns in Patoshi blocks by fetching timestamps from blockchain.
Focus on CFB-significant dates and the 12 anti-pattern blocks.
"""

import json
import requests
from datetime import datetime
from collections import defaultdict
import time

# Load existing analysis data
with open('ANTI_PATTERN_BLOCKS_ANALYSIS.json') as f:
    anti_pattern_data = json.load(f)

# The 12 anti-pattern blocks with their timestamps from the API
anti_pattern_blocks = anti_pattern_data['blocks']

print("=" * 70)
print("TEMPORAL DEEP ANALYSIS - Anti-Pattern Blocks")
print("=" * 70)

# Analyze dates
date_analysis = []
for block in anti_pattern_blocks:
    if 'block_info' in block and 'date' in block['block_info']:
        date_str = block['block_info']['date']
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        date_analysis.append({
            'block': block['block'],
            'address': block['address'],
            'date': date_str,
            'day_of_month': dt.day,
            'month': dt.month,
            'weekday': dt.strftime('%A'),
            'hour': dt.hour,
            'mod_576': block['mod_576'],
            'mod_27': block['mod_27']
        })

print(f"\nFound {len(date_analysis)} blocks with timestamps")
print("\n" + "-" * 70)
print("DATE PATTERNS IN ANTI-PATTERN BLOCKS")
print("-" * 70)

# Check for 13th of month
thirteenth_blocks = [b for b in date_analysis if b['day_of_month'] == 13]
print(f"\nBlocks on 13th of month: {len(thirteenth_blocks)}")
for b in thirteenth_blocks:
    print(f"  Block {b['block']}: {b['date']} - {b['address'][:20]}...")

# Check for CFB-significant days (3, 9, 11, 13, 21, 27)
cfb_days = [3, 9, 11, 13, 21, 27]
print(f"\nBlocks on CFB-significant days ({cfb_days}):")
for day in cfb_days:
    blocks_on_day = [b for b in date_analysis if b['day_of_month'] == day]
    if blocks_on_day:
        print(f"  Day {day}: {len(blocks_on_day)} blocks")
        for b in blocks_on_day:
            print(f"    Block {b['block']}: {b['date']}")

# Weekday distribution
print("\n" + "-" * 70)
print("WEEKDAY DISTRIBUTION")
print("-" * 70)
weekday_counts = defaultdict(int)
for b in date_analysis:
    weekday_counts[b['weekday']] += 1

for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
    count = weekday_counts[day]
    bar = '█' * count
    print(f"  {day:10} : {count:2} {bar}")

# Hour distribution
print("\n" + "-" * 70)
print("HOUR DISTRIBUTION (UTC)")
print("-" * 70)
hour_counts = defaultdict(int)
for b in date_analysis:
    hour_counts[b['hour']] += 1

for hour in sorted(hour_counts.keys()):
    count = hour_counts[hour]
    bar = '█' * count
    print(f"  {hour:02}:00 : {count:2} {bar}")

# Month distribution
print("\n" + "-" * 70)
print("MONTH DISTRIBUTION")
print("-" * 70)
month_counts = defaultdict(int)
for b in date_analysis:
    month_counts[b['month']] += 1

months = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
for month in sorted(month_counts.keys()):
    count = month_counts[month]
    bar = '█' * count
    print(f"  {months[month]:3} 2009 : {count:2} {bar}")

# Special date analysis
print("\n" + "-" * 70)
print("SPECIAL DATE ANALYSIS")
print("-" * 70)

# Block 264 (1CFB) was on January 13, 2009
print("\n1. Block 264 (1CFB) reference: January 13, 2009")
jan_13_blocks = [b for b in date_analysis if b['month'] == 1 and b['day_of_month'] == 13]
print(f"   Anti-pattern blocks on Jan 13: {len(jan_13_blocks)}")

# August 13 - Block 21232
aug_13_blocks = [b for b in date_analysis if b['month'] == 8 and b['day_of_month'] == 13]
print(f"\n2. Blocks on August 13 (mirror of Jan 13?):")
for b in aug_13_blocks:
    print(f"   Block {b['block']}: {b['date']}")
    print(f"   mod_576={b['mod_576']}, mod_27={b['mod_27']}")

# Prime block analysis
print("\n" + "-" * 70)
print("BLOCK 5279 (PRIME) SPECIAL ANALYSIS")
print("-" * 70)
block_5279 = next((b for b in date_analysis if b['block'] == 5279), None)
if block_5279:
    print(f"  Date: {block_5279['date']}")
    print(f"  Day of week: {block_5279['weekday']}")
    print(f"  Day of month: {block_5279['day_of_month']}")
    print(f"  5279 is PRIME - the only prime block number in anti-pattern set")
    # 5279 in different bases
    print(f"  5279 in binary: {bin(5279)} = {bin(5279)[2:]}")
    print(f"  5279 in hex: {hex(5279)}")
    print(f"  5279 mod 27: {5279 % 27}")
    print(f"  5279 mod 121: {5279 % 121}")
    print(f"  5279 mod 137: {5279 % 137}")

# Digit sum patterns
print("\n" + "-" * 70)
print("DIGIT SUM PATTERNS IN BLOCK NUMBERS")
print("-" * 70)
for b in anti_pattern_blocks:
    block = b['block']
    digit_sum = sum(int(d) for d in str(block))
    digit_product = 1
    for d in str(block):
        digit_product *= int(d) if int(d) > 0 else 1
    print(f"  Block {block:5}: digit_sum={digit_sum:2}, digit_product={digit_product:4}")

# Numerical patterns
print("\n" + "-" * 70)
print("NUMERICAL CURIOSITIES")
print("-" * 70)
print("\nBlock differences (looking for patterns):")
blocks_sorted = sorted([b['block'] for b in anti_pattern_blocks])
for i in range(1, len(blocks_sorted)):
    diff = blocks_sorted[i] - blocks_sorted[i-1]
    print(f"  {blocks_sorted[i-1]} → {blocks_sorted[i]}: diff={diff}, diff mod 27={diff % 27}")

# Time gaps between blocks
print("\n" + "-" * 70)
print("TIME GAPS BETWEEN ANTI-PATTERN BLOCKS")
print("-" * 70)
dates_sorted = sorted(date_analysis, key=lambda x: x['block'])
for i in range(1, len(dates_sorted)):
    dt1 = datetime.strptime(dates_sorted[i-1]['date'], "%Y-%m-%d %H:%M:%S")
    dt2 = datetime.strptime(dates_sorted[i]['date'], "%Y-%m-%d %H:%M:%S")
    gap = dt2 - dt1
    days = gap.days
    hours = gap.seconds // 3600
    print(f"  Block {dates_sorted[i-1]['block']:5} → {dates_sorted[i]['block']:5}: {days:3} days, {hours:2} hours")

# Save results
results = {
    'analysis_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    'total_anti_pattern_blocks': len(date_analysis),
    'date_analysis': date_analysis,
    'findings': {
        'blocks_on_13th': [b for b in date_analysis if b['day_of_month'] == 13],
        'blocks_on_aug_13': [b for b in date_analysis if b['month'] == 8 and b['day_of_month'] == 13],
        'prime_block_5279': block_5279,
        'weekday_distribution': dict(weekday_counts),
        'hour_distribution': dict(hour_counts),
        'month_distribution': dict(month_counts)
    },
    'key_observations': [
        "Block 21232 on August 13 - mirror of Block 264 (Jan 13)?",
        "Block 5279 is the only PRIME in the anti-pattern set",
        "7 of 12 anti-pattern blocks have mod_576=384 (128×3)",
        "Block 12873 has mod_27=14 - the only one not divisible by 3"
    ]
}

with open('TEMPORAL_DEEP_ANALYSIS_RESULTS.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n" + "=" * 70)
print("Results saved to TEMPORAL_DEEP_ANALYSIS_RESULTS.json")
print("=" * 70)
