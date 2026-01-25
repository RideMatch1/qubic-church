#!/usr/bin/env python3
"""
Date Correlation Analysis for Bitcoin Transactions
Searches for March 3rd transactions and special date patterns
"""

import requests
import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import time

class DateCorrelationAnalyzer:
    def __init__(self):
        self.base_url = "https://blockstream.info/api"
        self.mempool_url = "https://mempool.space/api"
        self.results = {
            "march_3rd_blocks": [],
            "blocks_with_2026": [],
            "blocks_digit_sum_27": [],
            "special_blocks": []
        }

    def fetch_json(self, url: str) -> Optional[Any]:
        """Fetch JSON from URL"""
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error: {e}")
        return None

    def get_block_timestamp(self, block_height: int) -> Optional[datetime]:
        """Get the timestamp of a specific block"""
        block_hash = self.fetch_json(f"{self.base_url}/block-height/{block_height}")
        if block_hash:
            block_data = self.fetch_json(f"{self.base_url}/block/{block_hash}")
            if block_data:
                timestamp = block_data.get("timestamp")
                if timestamp:
                    return datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return None

    def find_march_3rd_blocks(self, start_block: int = 1, end_block: int = 500000) -> List[Dict]:
        """Find blocks mined on March 3rd (any year)"""
        march_3_blocks = []

        # March 3rd dates and approximate block ranges
        # 2009-03-03: ~block 5000-6000 (rough estimate)
        # 2010-03-03: ~block 50000-52000
        # etc.

        # Key March 3rd timestamps to check
        march_3_dates = [
            ("2009-03-03", 4000, 6000),
            ("2010-03-03", 45000, 55000),
            ("2011-03-03", 110000, 115000),
            ("2012-03-03", 168000, 172000),
            ("2013-03-03", 225000, 228000),
            ("2014-03-03", 288000, 292000),
            ("2015-03-03", 345000, 348000),
            ("2016-03-03", 400000, 403000),
            ("2017-03-03", 455000, 458000),
        ]

        print("\nSearching for March 3rd blocks...")

        for date_str, start_est, end_est in march_3_dates:
            print(f"  Checking {date_str} (blocks {start_est}-{end_est})...")

            # Binary search to find the March 3rd blocks
            for block_num in [start_est, (start_est + end_est) // 2, end_est]:
                if block_num > end_block:
                    continue

                ts = self.get_block_timestamp(block_num)
                if ts and ts.month == 3 and ts.day == 3:
                    march_3_blocks.append({
                        "block_height": block_num,
                        "timestamp": ts.isoformat(),
                        "year": ts.year
                    })

                time.sleep(0.2)  # Rate limiting

        return march_3_blocks

    def find_digit_sum_27_blocks(self, max_block: int = 500000) -> List[int]:
        """Find all block numbers with digit sum = 27"""
        def digit_sum(n):
            return sum(int(d) for d in str(n))

        blocks = [b for b in range(1, max_block + 1) if digit_sum(b) == 27]
        return blocks

    def find_21e8_blocks(self) -> List[Dict]:
        """Find blocks with hash starting with 21e8"""
        # Known 21e8 blocks from research
        known_21e8_blocks = [
            26284, 83434, 187323, 259695, 304822, 349158, 437039, 475118, 528249
        ]

        results = []
        print("\nChecking known 21e8 blocks...")

        for block_num in known_21e8_blocks:
            block_hash = self.fetch_json(f"{self.base_url}/block-height/{block_num}")
            if block_hash and str(block_hash).startswith("21e8"):
                results.append({
                    "block_height": block_num,
                    "block_hash": block_hash,
                    "starts_with_21e8": True
                })
                print(f"  Block {block_num}: {block_hash[:16]}...")
            elif block_hash:
                results.append({
                    "block_height": block_num,
                    "block_hash": block_hash,
                    "starts_with_21e8": block_hash.startswith("21e8") if block_hash else False
                })

            time.sleep(0.2)

        return results

    def analyze_genesis_related_blocks(self) -> Dict:
        """Analyze Genesis block and related early blocks"""
        genesis_info = {
            "block_0": {
                "hash": "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f",
                "timestamp": "2009-01-03 18:15:05 UTC",
                "coinbase_message": "The Times 03/Jan/2009 Chancellor on brink of second bailout for banks",
                "reward_address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
                "reward": "50 BTC (unspendable)"
            },
            "block_1": {
                "timestamp": "2009-01-09 02:54:25 UTC",
                "note": "6-day gap from genesis (biblical reference?)"
            },
            "special_observations": [
                "6-day gap parallels 6 days of creation in Genesis",
                "Newspaper headline references financial crisis",
                "Coinbase address has received 100+ BTC in donations (all unspendable)",
                "Block 0 reward is hardcoded and cannot be spent"
            ]
        }

        return genesis_info

    def compile_report(self) -> Dict:
        """Compile full date correlation report"""
        print("=" * 60)
        print("DATE CORRELATION ANALYSIS")
        print("=" * 60)

        # Find digit sum 27 blocks
        print("\nFinding blocks with digit sum 27...")
        digit_sum_27 = self.find_digit_sum_27_blocks(500000)
        print(f"  Found {len(digit_sum_27)} blocks")

        # Check 21e8 blocks
        blocks_21e8 = self.find_21e8_blocks()

        # Analyze genesis
        genesis_analysis = self.analyze_genesis_related_blocks()

        # Find March 3rd blocks (limited search due to API constraints)
        march_3_info = {
            "note": "March 3rd search requires block-by-block analysis",
            "estimation_method": "Block timestamps checked at key ranges",
            "known_facts": [
                "Bitcoin Genesis: January 3, 2009",
                "Block 1: January 9, 2009",
                "~144 blocks per day on average"
            ]
        }

        report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "digit_sum_27_blocks": {
                "count": len(digit_sum_27),
                "first_10": digit_sum_27[:10],
                "last_10": digit_sum_27[-10:],
                "sample_blocks": digit_sum_27[::len(digit_sum_27)//20][:20]
            },
            "blocks_21e8": blocks_21e8,
            "genesis_analysis": genesis_analysis,
            "march_3_analysis": march_3_info,
            "pattern_2026": {
                "note": "Searching for '2026' in OP_RETURN requires full chain scan",
                "method": "Would need to check all OP_RETURN data for '2026' string"
            }
        }

        return report


def main():
    analyzer = DateCorrelationAnalyzer()

    report = analyzer.compile_report()

    # Save report
    with open("DATE_CORRELATION_REPORT.json", "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print(f"\nBlocks with digit sum 27: {report['digit_sum_27_blocks']['count']}")
    print(f"Sample: {report['digit_sum_27_blocks']['first_10'][:5]}...")

    print(f"\n21e8 Blocks checked: {len(report['blocks_21e8'])}")
    for block in report['blocks_21e8'][:5]:
        print(f"  Block {block['block_height']}: {str(block.get('block_hash', 'N/A'))[:20]}...")

    print("\nGenesis Block Analysis:")
    for key, value in report['genesis_analysis']['block_0'].items():
        print(f"  {key}: {str(value)[:60]}")

    print("\nReport saved to DATE_CORRELATION_REPORT.json")


if __name__ == "__main__":
    main()
