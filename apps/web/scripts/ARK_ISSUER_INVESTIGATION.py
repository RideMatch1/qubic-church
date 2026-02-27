#!/usr/bin/env python3
"""
ARK Token Issuer Investigation
Check token distribution and issuer holdings
"""

import json
import sys

# ARK Token Info
ARK_ISSUER = "ARKMGCWFYEHJFAVSGKEXVWBGGXZAVLZNBDNBZEXTQBKLKRPEYPEIEKFHUPNG"
TOTAL_SUPPLY = 2028
AVAILABLE_ON_MARKET = 426
DISTRIBUTED = 1602

print("="*80)
print("ARK TOKEN DISTRIBUTION ANALYSIS")
print("="*80)

print(f"\n📊 BASIC STATS:")
print(f"   Total Supply:        {TOTAL_SUPPLY}")
print(f"   On Market:           {AVAILABLE_ON_MARKET} ({AVAILABLE_ON_MARKET/TOTAL_SUPPLY*100:.1f}%)")
print(f"   Distributed/Held:    {DISTRIBUTED} ({DISTRIBUTED/TOTAL_SUPPLY*100:.1f}%)")

print(f"\n🔍 CRITICAL QUESTIONS:")
print(f"   1. How many ARK does the ISSUER still hold?")
print(f"   2. How many unique holders exist?")
print(f"   3. Is this a fair distribution or issuer-controlled?")

print(f"\n⚠️  RED FLAGS TO CHECK:")
print(f"   - If issuer holds >50% of distributed tokens → SCAM")
print(f"   - If <10 unique holders → FAKE distribution")
print(f"   - If issuer = only seller on orderbook → RUG PULL risk")

print(f"\n💡 TO INVESTIGATE:")
print(f"   - Query Qubic RPC for issuer balance")
print(f"   - Check transaction history of ARK token")
print(f"   - Analyze holder distribution")
print(f"   - Compare to POCC/HASV distribution patterns")

print(f"\n🎯 MATHEMATICAL PROPERTIES OF 426:")
print(f"   426 = 2 × 3 × 71")
print(f"   426 + 1602 = 2028 ✓")
print(f"   426 / 26 = {426/26:.2f}")
print(f"   426 mod 676 = {426 % 676}")
print(f"   426 mod 121 = {426 % 121}")

print(f"\n🎯 MATHEMATICAL PROPERTIES OF 1602:")
print(f"   1602 = 2 × 3² × 89")
print(f"   1602 / 26 = {1602/26:.2f}")
print(f"   1602 mod 676 = {1602 % 676}")
print(f"   1602 mod 121 = {1602 % 121}")
print(f"   1602 / 676 = {1602/676:.4f}")

# Check if these numbers have special meaning
print(f"\n🔬 SPECIAL NUMBER ANALYSIS:")

# 426 analysis
if 426 % 6 == 0:
    print(f"   ✓ 426 divisible by 6")
if 426 % 71 == 0:
    print(f"   ✓ 426 = 6 × 71")

# 1602 analysis
if 1602 % 801 == 0:
    print(f"   ✓ 1602 = 2 × 801")
if 1602 % 267 == 0:
    print(f"   ✓ 1602 = 6 × 267")

# Ratio analysis
ratio = DISTRIBUTED / AVAILABLE_ON_MARKET
print(f"\n📐 DISTRIBUTION RATIO:")
print(f"   Distributed/Available = {ratio:.4f}")
print(f"   Available/Distributed = {1/ratio:.4f}")
print(f"   Golden ratio φ = 1.618...")
print(f"   Difference from φ: {abs(ratio - 1.618):.4f}")

if abs(ratio - 1.618) < 0.1:
    print(f"   ⚠️  RATIO CLOSE TO GOLDEN RATIO!")

# Check against 676
print(f"\n🎲 RELATIONSHIP TO 676:")
print(f"   426 = 676 × {426/676:.4f}")
print(f"   1602 = 676 × {1602/676:.4f}")
print(f"   2028 = 676 × {2028/676:.1f} = 676 × 3 ✓")

print(f"\n" + "="*80)
print("RECOMMENDATION:")
print("="*80)
print("""
⚠️  DO NOT BUY until you verify:

1. Issuer's current ARK holdings
2. Number of unique holders
3. Whether the 1,602 distributed tokens are:
   a) Held by issuer (RED FLAG)
   b) In issuer's other wallets (RED FLAG)
   c) Genuinely distributed to others (GOOD)

🔴 IF issuer holds >1,000 ARK → DEFINITE SCAM
🟡 IF 10-50 unique holders → Possibly legitimate
🟢 IF >100 unique holders AND issuer has <500 → More trustworthy

Current price: $0.52/token × 200 = $104
- This is AFFORDABLE risk
- BUT: Zero liquidity means you can't exit easily

NEXT STEP: Query Qubic RPC to get real distribution data
""")

print("="*80)
