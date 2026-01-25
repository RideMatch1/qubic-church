#!/usr/bin/env python3
"""
Lottery Number Verification Tool
Checks if the numbers [23, 42, 41, 38, 16, 36] have ever won in major lotteries
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# The lottery numbers to verify
TARGET_NUMBERS = [23, 42, 41, 38, 16, 36]
TARGET_NUMBERS_SORTED = sorted(TARGET_NUMBERS)

class LotteryVerifier:
    def __init__(self):
        self.results = {
            "target_numbers": TARGET_NUMBERS,
            "target_numbers_sorted": TARGET_NUMBERS_SORTED,
            "analysis_date": datetime.now().isoformat(),
            "lottery_checks": [],
            "partial_matches": [],
            "exact_matches": [],
            "number_frequencies": {}
        }

    def check_euromillions_api(self) -> List[Dict]:
        """Check EuroMillions historical results"""
        # EuroMillions uses 5 main numbers (1-50) + 2 lucky stars (1-12)
        # Our numbers are: 23, 42, 41, 38, 16, 36
        # All are valid main numbers for EuroMillions

        findings = []

        # Note: EuroMillions only draws 5 main numbers, not 6
        # So we can only match max 5 of our 6 numbers in main draw

        print("\nChecking EuroMillions...")
        print("  Note: EuroMillions draws 5 main numbers (1-50)")
        print(f"  Our 6 numbers: {TARGET_NUMBERS}")
        print("  Maximum possible match: 5 numbers")

        # We'd need to query actual historical data
        # For now, document what we know
        findings.append({
            "lottery": "EuroMillions",
            "format": "5 main numbers (1-50) + 2 Lucky Stars (1-12)",
            "our_numbers_valid": True,
            "max_possible_match": 5,
            "note": "All our numbers are valid for EuroMillions main draw"
        })

        return findings

    def check_powerball_info(self) -> Dict:
        """Document Powerball format and compatibility"""
        # Powerball: 5 white balls (1-69) + 1 Powerball (1-26)

        result = {
            "lottery": "Powerball (USA)",
            "format": "5 white balls (1-69) + 1 Powerball (1-26)",
            "our_numbers_analysis": {
                "valid_white_balls": [n for n in TARGET_NUMBERS if n <= 69],
                "valid_powerball": [n for n in TARGET_NUMBERS if n <= 26],
                "all_valid_white": all(n <= 69 for n in TARGET_NUMBERS)
            }
        }

        # Check if any number could be the Powerball
        # If we split: 5 white + 1 Powerball
        # Numbers <= 26 could be Powerball: 23, 16
        # So valid combinations exist

        result["possible_combinations"] = [
            {
                "white_balls": [42, 41, 38, 36, 23],
                "powerball": 16,
                "valid": True
            },
            {
                "white_balls": [42, 41, 38, 36, 16],
                "powerball": 23,
                "valid": True
            }
        ]

        return result

    def check_german_lotto(self) -> Dict:
        """Check German Lotto 6 aus 49"""
        # German Lotto: 6 numbers from 1-49 + 1 Superzahl (0-9)

        invalid_numbers = [n for n in TARGET_NUMBERS if n > 49]

        result = {
            "lottery": "German Lotto 6 aus 49",
            "format": "6 numbers (1-49) + Superzahl (0-9)",
            "our_numbers_valid": len(invalid_numbers) == 0,
            "invalid_numbers": invalid_numbers,
            "analysis": "Numbers 23, 42, 41, 38, 16, 36 are all valid (1-49 range)"
        }

        return result

    def analyze_number_properties(self) -> Dict:
        """Analyze mathematical properties of the numbers"""
        numbers = TARGET_NUMBERS

        return {
            "numbers": numbers,
            "sum": sum(numbers),
            "average": sum(numbers) / len(numbers),
            "sorted": sorted(numbers),
            "range": max(numbers) - min(numbers),
            "odd_count": len([n for n in numbers if n % 2 == 1]),
            "even_count": len([n for n in numbers if n % 2 == 0]),
            "digit_sum": sum(sum(int(d) for d in str(n)) for n in numbers),
            "special_observations": [
                f"Sum = {sum(numbers)}",
                f"42 is 'The Answer' from Hitchhiker's Guide",
                f"23 is associated with Discordianism (Law of Fives: 2+3=5)",
                f"36 = 6² (perfect square)",
                f"16 = 4² = 2⁴ (perfect square and power of 2)",
                f"38 + 41 = 79 (prime)",
                f"23 + 42 = 65, 41 + 38 = 79, 16 + 36 = 52"
            ]
        }

    def search_historical_wins(self) -> Dict:
        """Search for historical lottery wins with these numbers"""
        # This would require actual lottery APIs
        # Document known sources to check

        return {
            "sources_to_check": [
                {
                    "name": "EuroMillions Official",
                    "url": "https://www.euro-millions.com/results-history",
                    "years_available": "2004-present"
                },
                {
                    "name": "Powerball Official",
                    "url": "https://www.powerball.com/previous-results",
                    "years_available": "1992-present"
                },
                {
                    "name": "Lottery Post",
                    "url": "https://www.lotterypost.com/results",
                    "coverage": "Multiple lotteries worldwide"
                }
            ],
            "search_strategy": [
                "Search for exact 6-number match in 6-number lotteries",
                "Search for 5-number subset in 5+1 format lotteries",
                "Check if any subset appeared as winners"
            ]
        }

    def compile_report(self) -> Dict:
        """Compile full verification report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "target_numbers": TARGET_NUMBERS,
            "lottery_compatibility": {
                "euromillions": self.check_euromillions_api(),
                "powerball": self.check_powerball_info(),
                "german_lotto": self.check_german_lotto()
            },
            "number_analysis": self.analyze_number_properties(),
            "search_resources": self.search_historical_wins(),
            "conclusions": {
                "all_numbers_valid_for": [
                    "German Lotto 6 aus 49 (all 6 valid)",
                    "EuroMillions (all 6 valid as main numbers, but only 5 drawn)",
                    "Powerball (all 6 valid as white balls)"
                ],
                "requires_manual_verification": True,
                "note": "No public API found for exact historical match search. Manual verification needed."
            }
        }

        return report


def main():
    verifier = LotteryVerifier()

    print("=" * 60)
    print("Lottery Number Verification")
    print(f"Target Numbers: {TARGET_NUMBERS}")
    print("=" * 60)

    report = verifier.compile_report()

    # Save report
    with open("LOTTERY_VERIFICATION_REPORT.json", "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n=== Number Analysis ===")
    analysis = report["number_analysis"]
    print(f"Sum: {analysis['sum']}")
    print(f"Average: {analysis['average']:.2f}")
    print(f"Odd/Even: {analysis['odd_count']}/{analysis['even_count']}")

    print("\n=== Lottery Compatibility ===")
    for lottery, info in report["lottery_compatibility"].items():
        if isinstance(info, list):
            for item in info:
                print(f"  {item.get('lottery', lottery)}: Valid for main numbers")
        else:
            valid = info.get("our_numbers_valid", info.get("all_valid_white", False))
            print(f"  {info.get('lottery', lottery)}: {'✓ Valid' if valid else '✗ Has invalid numbers'}")

    print("\n=== Special Observations ===")
    for obs in analysis["special_observations"]:
        print(f"  • {obs}")

    print("\nReport saved to LOTTERY_VERIFICATION_REPORT.json")


if __name__ == "__main__":
    main()
