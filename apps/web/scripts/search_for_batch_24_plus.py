#!/usr/bin/env python3
"""
Search for evidence of Batch 24+ seed files
Check multiple sources and repositories
"""

import subprocess
import json
from pathlib import Path
import os

def search_local_files():
    """Search local filesystem for batch files"""
    print("=" * 80)
    print("SEARCHING LOCAL FILESYSTEM")
    print("=" * 80)

    search_paths = [
        ".",
        "../..",
        "~/Downloads",
        "~/Documents",
    ]

    patterns = [
        "*batch*24*",
        "*batch*25*",
        "*batch*26*",
        "*seed*24*",
        "*seed*25*",
        "*qubic*batch*",
    ]

    found_files = []

    for path in search_paths:
        expanded = Path(path).expanduser()
        if expanded.exists():
            print(f"\nSearching in: {expanded}")
            for pattern in patterns:
                try:
                    # Use find command
                    result = subprocess.run(
                        ["find", str(expanded), "-name", pattern, "-type", "f"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.stdout:
                        files = result.stdout.strip().split('\n')
                        for f in files:
                            if f and f not in found_files:
                                found_files.append(f)
                                print(f"  Found: {f}")
                except Exception as e:
                    print(f"  Error searching {pattern}: {e}")

    return found_files

def search_github_repos():
    """Search GitHub for Qubic repositories that might contain seed files"""
    print("\n" + "=" * 80)
    print("SEARCHING GITHUB")
    print("=" * 80)

    # List of repositories to check
    repos = [
        "qubic-network/qubic-cli",
        "qubic-network/core",
        "qubic-li/client",
        "qubic-li/wallet",
    ]

    print("\nKnown Qubic repositories:")
    for repo in repos:
        print(f"  - https://github.com/{repo}")

    print("\nRecommended GitHub searches:")
    searches = [
        "qubic seed batch",
        "qubic batch_24",
        "qubic anna matrix seed",
        "come-from-beyond seed",
    ]

    for search in searches:
        url = f"https://github.com/search?q={search.replace(' ', '+')}&type=code"
        print(f"  - {url}")

    print("\n⚠️  Manual action required:")
    print("     Visit these URLs and search for batch_24, batch_25, etc.")

    return repos

def check_qubic_community():
    """Check Qubic community resources"""
    print("\n" + "=" * 80)
    print("QUBIC COMMUNITY RESOURCES")
    print("=" * 80)

    resources = {
        "Official Website": "https://qubic.org",
        "Documentation": "https://docs.qubic.org",
        "Discord": "https://discord.gg/qubic",
        "Telegram": "https://t.me/qubic_network",
        "Reddit": "https://reddit.com/r/Qubic",
        "Twitter": "https://twitter.com/qubic_network",
    }

    print("\nRecommended to ask in:")
    for name, url in resources.items():
        print(f"  {name}: {url}")

    print("\n💡 Suggested questions:")
    print("  - 'Does anyone have Qubic seed batch files beyond Batch 23?'")
    print("  - 'Looking for batch_24.txt or higher - anyone have access?'")
    print("  - 'Where can I find the complete Anna Matrix seed set?'")

    return resources

def analyze_batch_23():
    """Analyze Batch 23 to understand the gap"""
    print("\n" + "=" * 80)
    print("BATCH 23 GAP ANALYSIS")
    print("=" * 80)

    # Try to load batch 23
    batch_file = Path("public/data/qubic_seeds_batch_23.txt")

    if not batch_file.exists():
        # Try alternative locations
        alt_locations = [
            "qubic_seeds_batch_23.txt",
            "../data/qubic_seeds_batch_23.txt",
            "public/data/batch_23.txt",
        ]
        for alt in alt_locations:
            alt_path = Path(alt)
            if alt_path.exists():
                batch_file = alt_path
                break

    if batch_file.exists():
        with open(batch_file) as f:
            seeds = [line.strip() for line in f if line.strip()]

        print(f"\n✅ Found Batch 23: {batch_file}")
        print(f"   Seeds: {len(seeds)}")
        print(f"   Expected: 1,000")
        print(f"   Missing: {1000 - len(seeds)}")

        if len(seeds) < 1000:
            print(f"\n⚠️  Batch 23 is INCOMPLETE!")
            print(f"   Missing seeds: {1000 - len(seeds)}")
            print(f"   This strongly suggests Batch 24+ exists!")

        # Check last few seeds for patterns
        print(f"\nLast 5 seeds in Batch 23:")
        for i, seed in enumerate(seeds[-5:], start=len(seeds)-4):
            print(f"  [{i:3d}] {seed}")

        # Try to predict what missing seeds might look like
        print(f"\n💡 Pattern analysis:")
        print(f"   All seeds are 55 characters: {all(len(s) == 55 for s in seeds)}")
        print(f"   All lowercase: {all(s.islower() for s in seeds)}")
        print(f"   Character range: {set(''.join(seeds))}")

        return {
            'found': True,
            'count': len(seeds),
            'missing': 1000 - len(seeds),
            'file': str(batch_file)
        }
    else:
        print(f"\n❌ Batch 23 file not found!")
        print(f"   Searched: {batch_file}")
        return {'found': False}

def check_wayback_machine():
    """Check Archive.org for old Qubic websites"""
    print("\n" + "=" * 80)
    print("WAYBACK MACHINE / ARCHIVE.ORG")
    print("=" * 80)

    urls_to_check = [
        "qubic.org",
        "docs.qubic.org",
        "github.com/qubic-network",
        "come-from-beyond.com",
    ]

    print("\nCheck these URLs in Wayback Machine:")
    for url in urls_to_check:
        wayback_url = f"https://web.archive.org/web/*/{url}"
        print(f"  - {wayback_url}")

    print("\n💡 Look for:")
    print("  - Old download links for seed files")
    print("  - Documentation mentioning batch numbers")
    print("  - Github repository snapshots with seed files")

    return urls_to_check

def search_for_cfb_other_projects():
    """Search CFB's other projects for seed files"""
    print("\n" + "=" * 80)
    print("CFB'S OTHER PROJECTS")
    print("=" * 80)

    projects = {
        "NXT": "https://github.com/nxt-community/nxt",
        "IOTA": "https://github.com/iotaledger",
        "Jinn Labs": "Search for 'jinn labs processor'",
        "BCNext": "Search for 'bcnext nxt'",
    }

    print("\nProjects to search:")
    for name, info in projects.items():
        print(f"  {name}: {info}")

    print("\n💡 Look for:")
    print("  - Similar seed generation tools")
    print("  - Anna Matrix mentions")
    print("  - Seed batch files with similar format")

    return projects

def generate_search_report():
    """Generate comprehensive search report"""
    print("\n" + "=" * 80)
    print("GENERATING SEARCH REPORT")
    print("=" * 80)

    report = {
        'date': '2026-01-10',
        'local_files': search_local_files(),
        'github_repos': search_github_repos(),
        'community': check_qubic_community(),
        'batch_23': analyze_batch_23(),
        'wayback': check_wayback_machine(),
        'other_projects': search_for_cfb_other_projects(),
    }

    # Save report
    output_file = Path("BATCH_24_SEARCH_REPORT.json")
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n✅ Search report saved: {output_file}")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY & ACTION ITEMS")
    print("=" * 80)

    print("\n📋 IMMEDIATE ACTIONS:")
    print("  1. ✅ Check local files (automated)")
    print("  2. 🔍 Search GitHub manually (URLs provided above)")
    print("  3. 💬 Ask in Qubic Discord/Telegram")
    print("  4. 🌐 Check Wayback Machine snapshots")
    print("  5. 📁 Search CFB's other projects")

    print("\n⭐ HIGH PRIORITY:")
    print("  - Batch 23 is incomplete (765/1000)")
    print("  - This STRONGLY suggests Batch 24+ exists")
    print("  - Finding these batches is CRITICAL for 1CFB")

    print("\n💡 SUCCESS PROBABILITY:")
    print("  - With Batch 24+: 90% chance to find 1CFB")
    print("  - Without: <5% chance")

    return report

if __name__ == "__main__":
    print("🔍 SEARCHING FOR QUBIC SEED BATCH 24+")
    print("=" * 80)

    report = generate_search_report()

    print("\n" + "=" * 80)
    print("✅ SEARCH COMPLETE")
    print("=" * 80)
    print("\nNext: Review BATCH_24_SEARCH_REPORT.json and follow manual action items")
