#!/usr/bin/env python3
"""
CFB MESSAGE SEARCHER
Search through CFB's messages for ARK-related terms
"""

import json
import os
from pathlib import Path
from datetime import datetime

print("="*80)
print("CFB MESSAGE SEARCHER - Looking for ARK connections")
print("="*80)

# Priority search terms
TIER_1_EXACT = [
    "Phase 0",
    "Phase Zero",
    "Verification procedure",
    "stone into the abyss",
    "Initiation",
    "Gates open",
    "Architect",
    "If we exist",
]

TIER_2_CONCEPTS = [
    "abyss",
    "verification",
    "procedure",
    "response",
    "February 11",
    "February 25",
    "March 3",
    "T+7",
    "T+21",
]

TIER_3_NUMBERS = [
    "2028",
    "28.12.3",
    "ARK",
    "GENESIS",
    "EXODUS",
    "trinity",
    "three phases",
    "594",
    "A=",
]

# Check if CFB messages exist
cfb_folder = Path(__file__).parent / "cfb_profile_posts"

if not cfb_folder.exists():
    print(f"\n⚠️  CFB message folder not found at: {cfb_folder}")
    print(f"\nExpected location: {cfb_folder}")
    print(f"\nTo use this script:")
    print(f"   1. Place CFB Discord messages in cfb_profile_posts/")
    print(f"   2. Format: JSON or text files")
    print(f"   3. Run script again")
    print(f"\nOr manually search Discord for these terms:")
    print(f"\nTIER 1 (EXACT PHRASES - HIGH PRIORITY):")
    for term in TIER_1_EXACT:
        print(f"   '{term}'")
    print(f"\nTIER 2 (CONCEPTS):")
    for term in TIER_2_CONCEPTS:
        print(f"   '{term}'")
    print(f"\nTIER 3 (NUMBERS/TOKENS):")
    for term in TIER_3_NUMBERS:
        print(f"   '{term}'")

else:
    print(f"\n✅ Found CFB message folder: {cfb_folder}")

    # Search through files
    files = list(cfb_folder.glob("*.json")) + list(cfb_folder.glob("*.txt"))
    print(f"   Found {len(files)} message files")

    if len(files) == 0:
        print(f"\n⚠️  No message files found in folder")
        print(f"   Please add JSON or TXT files with CFB's messages")
    else:
        all_matches = []

        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')

                # Search for each term
                for tier, terms in [("TIER 1", TIER_1_EXACT),
                                   ("TIER 2", TIER_2_CONCEPTS),
                                   ("TIER 3", TIER_3_NUMBERS)]:
                    for term in terms:
                        if term.lower() in content.lower():
                            # Find context around match
                            idx = content.lower().find(term.lower())
                            start = max(0, idx - 100)
                            end = min(len(content), idx + len(term) + 100)
                            context = content[start:end]

                            all_matches.append({
                                'tier': tier,
                                'term': term,
                                'file': file_path.name,
                                'context': context
                            })
            except Exception as e:
                print(f"   Error reading {file_path.name}: {e}")

        # Display results
        print(f"\n{'='*80}")
        print(f"SEARCH RESULTS")
        print(f"{'='*80}")

        if len(all_matches) == 0:
            print(f"\n❌ No matches found for any search terms")
            print(f"\nThis suggests:")
            print(f"   - CFB hasn't publicly mentioned these phrases")
            print(f"   - OR messages are from wrong time period")
            print(f"   - OR creator is NOT CFB")
        else:
            print(f"\n🎯 Found {len(all_matches)} matches!")

            # Group by tier
            for tier in ["TIER 1", "TIER 2", "TIER 3"]:
                tier_matches = [m for m in all_matches if m['tier'] == tier]
                if tier_matches:
                    print(f"\n{tier} MATCHES: {len(tier_matches)}")
                    for match in tier_matches[:5]:  # Show first 5
                        print(f"\n   Term: '{match['term']}'")
                        print(f"   File: {match['file']}")
                        print(f"   Context: ...{match['context']}...")
                    if len(tier_matches) > 5:
                        print(f"\n   ... and {len(tier_matches) - 5} more matches")

        # Save results
        if all_matches:
            results_file = Path(__file__).parent / "CFB_SEARCH_RESULTS.json"
            with open(results_file, 'w') as f:
                json.dump(all_matches, f, indent=2)
            print(f"\n✅ Full results saved to: {results_file}")

print(f"\n{'='*80}")
print("SEARCH COMPLETE")
print(f"{'='*80}")
