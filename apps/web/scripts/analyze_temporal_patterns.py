#!/usr/bin/env python3
"""
Temporal Pattern Analysis
=========================

Analyze date patterns in Patoshi blocks:
- 13th of month occurrences
- Day of week distribution
- Special dates (CFB birthdays, holidays, etc.)
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

def main():
    script_dir = Path(__file__).parent
    data_path = script_dir.parent / "public" / "data" / "patoshi-addresses.json"

    with open(data_path, 'r') as f:
        data = json.load(f)

    records = data.get('records', data)
    print(f"Analyzing {len(records)} Patoshi blocks for temporal patterns...\n")

    # Parse timestamps
    blocks_by_day = defaultdict(list)
    blocks_by_weekday = defaultdict(list)
    blocks_by_month = defaultdict(list)
    blocks_by_13th = []
    blocks_by_date = defaultdict(list)

    special_dates = {
        "2009-01-03": "Bitcoin Genesis",
        "2009-01-09": "Bitcoin 0.1 release",
        "2009-01-12": "First Bitcoin TX (Hal Finney)",
        "2009-01-13": "Block 264 (1CFB!)",
        "2009-10-05": "First BTC exchange rate",
    }

    # CFB numbers to check for dates
    cfb_days = [3, 9, 11, 13, 21, 27]  # ternary/CFB related

    for record in records:
        timestamp = record.get('timestamp', 0)
        block = record.get('blockHeight', 0)

        if timestamp > 0:
            dt = datetime.utcfromtimestamp(timestamp)
            date_str = dt.strftime('%Y-%m-%d')

            blocks_by_day[dt.day].append(block)
            blocks_by_weekday[dt.strftime('%A')].append(block)
            blocks_by_month[dt.month].append(block)
            blocks_by_date[date_str].append(block)

            if dt.day == 13:
                blocks_by_13th.append({
                    "block": block,
                    "date": date_str,
                    "weekday": dt.strftime('%A')
                })

    print("=" * 70)
    print("DAY OF MONTH DISTRIBUTION")
    print("=" * 70)

    day_counts = {day: len(blocks) for day, blocks in blocks_by_day.items()}
    avg_per_day = sum(day_counts.values()) / len(day_counts) if day_counts else 0

    # Highlight CFB-related days
    print(f"\nAverage blocks per day of month: {avg_per_day:.1f}")
    print("\nCFB-related days (3, 9, 11, 13, 21, 27):")
    for day in cfb_days:
        count = day_counts.get(day, 0)
        deviation = ((count / avg_per_day) - 1) * 100 if avg_per_day > 0 else 0
        marker = "**" if abs(deviation) > 10 else ""
        print(f"  Day {day:2d}: {count:4d} blocks ({deviation:+.1f}% from avg) {marker}")

    print("\n" + "=" * 70)
    print("BLOCKS ON THE 13TH OF EACH MONTH")
    print("=" * 70)
    print(f"\nTotal blocks on 13th: {len(blocks_by_13th)}")

    # Group by month
    by_month_13 = defaultdict(list)
    for entry in blocks_by_13th:
        month = entry['date'][5:7]
        by_month_13[month].append(entry)

    for month, entries in sorted(by_month_13.items()):
        print(f"\n{month}:")
        for e in entries[:5]:  # Show first 5
            print(f"  Block {e['block']:5d} - {e['date']} ({e['weekday']})")
        if len(entries) > 5:
            print(f"  ... and {len(entries) - 5} more")

    print("\n" + "=" * 70)
    print("DAY OF WEEK DISTRIBUTION")
    print("=" * 70)

    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    total_blocks = sum(len(blocks) for blocks in blocks_by_weekday.values())

    for day in weekday_order:
        count = len(blocks_by_weekday.get(day, []))
        pct = (count / total_blocks * 100) if total_blocks > 0 else 0
        expected = 100 / 7
        deviation = pct - expected
        print(f"  {day:9s}: {count:5d} blocks ({pct:5.1f}%, {deviation:+.1f}% from expected)")

    print("\n" + "=" * 70)
    print("SPECIAL DATES")
    print("=" * 70)

    for date, desc in special_dates.items():
        blocks = blocks_by_date.get(date, [])
        print(f"\n{date} - {desc}:")
        if blocks:
            print(f"  Patoshi blocks: {len(blocks)}")
            print(f"  Block range: {min(blocks)} - {max(blocks)}")
        else:
            print("  No Patoshi blocks on this date")

    # Find dates with most blocks
    print("\n" + "=" * 70)
    print("DATES WITH MOST PATOSHI BLOCKS")
    print("=" * 70)

    top_dates = sorted(blocks_by_date.items(), key=lambda x: len(x[1]), reverse=True)[:15]
    for date, blocks in top_dates:
        print(f"  {date}: {len(blocks):4d} blocks (range {min(blocks)}-{max(blocks)})")

    # Find dates with suspicious patterns
    print("\n" + "=" * 70)
    print("PATTERN ANALYSIS: 13th vs OTHER DAYS")
    print("=" * 70)

    # Anti-pattern blocks on 13th?
    anti_pattern_blocks = [1115, 2720, 5057, 5279, 11221, 12778, 12873, 13752, 19214, 21232, 22574, 40252]
    anti_on_13th = []

    for entry in blocks_by_13th:
        if entry['block'] in anti_pattern_blocks:
            anti_on_13th.append(entry)

    print(f"\nAnti-pattern blocks on the 13th: {len(anti_on_13th)}")
    for e in anti_on_13th:
        print(f"  Block {e['block']} - {e['date']}")

    # Anomaly blocks on 13th
    anomaly_blocks = [2838, 2966, 3734, 7777, 8094]  # From previous analysis
    anomaly_on_13th = []

    for entry in blocks_by_13th:
        if entry['block'] in anomaly_blocks:
            anomaly_on_13th.append(entry)

    print(f"\nAnomaly blocks (from matrix) on the 13th: {len(anomaly_on_13th)}")
    for e in anomaly_on_13th:
        print(f"  Block {e['block']} - {e['date']}")

    # Save results
    results = {
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_patoshi_blocks": len(records),
        "blocks_on_13th": {
            "count": len(blocks_by_13th),
            "percentage": len(blocks_by_13th) / len(records) * 100 if records else 0,
            "expected_percentage": 1 / 31 * 100,  # ~3.2%
            "blocks": blocks_by_13th[:50]  # First 50
        },
        "cfb_days_analysis": {
            day: {
                "count": day_counts.get(day, 0),
                "deviation_percent": ((day_counts.get(day, 0) / avg_per_day) - 1) * 100 if avg_per_day > 0 else 0
            }
            for day in cfb_days
        },
        "weekday_distribution": {
            day: len(blocks_by_weekday.get(day, []))
            for day in weekday_order
        },
        "anti_pattern_on_13th": anti_on_13th,
        "anomaly_on_13th": anomaly_on_13th
    }

    output_path = script_dir / "TEMPORAL_PATTERNS_ANALYSIS.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n\nResults saved to: {output_path}")

    # Statistical significance
    print("\n" + "=" * 70)
    print("STATISTICAL SIGNIFICANCE")
    print("=" * 70)

    expected_13th = len(records) / 31
    actual_13th = len(blocks_by_13th)
    deviation = (actual_13th - expected_13th) / expected_13th * 100

    print(f"\nBlocks on 13th:")
    print(f"  Expected (1/31 of total): {expected_13th:.1f}")
    print(f"  Actual: {actual_13th}")
    print(f"  Deviation: {deviation:+.1f}%")

    if abs(deviation) > 5:
        print(f"\n  ⚠️ SIGNIFICANT: {deviation:+.1f}% deviation from expected!")
    else:
        print(f"\n  ✓ Within normal range")


if __name__ == "__main__":
    main()
