#!/usr/bin/env python3
"""
CHECK 1CFB ADDRESSES ON BLOCKCHAIN

Check all 25 1CFB addresses for:
- Balance
- Transaction count
- First/last transaction dates
- Connected addresses
"""

import json
import time
import urllib.request
import urllib.error
from pathlib import Path

def load_1cfb_addresses():
    """Load the analyzed 1CFB addresses"""
    analysis_file = Path("1CFB_COMPLETE_ANALYSIS.json")

    if not analysis_file.exists():
        print("❌ Analysis file not found. Run analyze_all_1cfb_addresses.py first!")
        return None

    with open(analysis_file) as f:
        data = json.load(f)

    return data

def check_address_blockchain(address):
    """Check a single address on blockchain (using blockchain.info API)"""
    try:
        url = f"https://blockchain.info/rawaddr/{address}?limit=0"

        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read())

        return {
            'address': address,
            'balance': data.get('final_balance', 0) / 100000000,  # Convert satoshis to BTC
            'total_received': data.get('total_received', 0) / 100000000,
            'total_sent': data.get('total_sent', 0) / 100000000,
            'n_tx': data.get('n_tx', 0),
            'error': None,
        }

    except urllib.error.HTTPError as e:
        if e.code == 429:
            return {'address': address, 'error': 'RATE_LIMIT'}
        return {'address': address, 'error': f'HTTP_{e.code}'}

    except Exception as e:
        return {'address': address, 'error': str(e)}

def check_all_addresses_sequential(addresses):
    """Check all addresses with rate limiting"""
    print("=" * 80)
    print("CHECKING ADDRESSES ON BLOCKCHAIN")
    print("=" * 80)
    print("\nNote: This will take ~2-3 minutes due to API rate limits")
    print("Checking with 5 second delay between requests...")

    results = []

    for i, addr_data in enumerate(addresses, 1):
        address = addr_data['address']

        print(f"\n[{i}/{len(addresses)}] Checking: {address}")

        result = check_address_blockchain(address)

        if result['error'] is None:
            balance = result['balance']
            n_tx = result['n_tx']
            total_received = result['total_received']

            status = "💰" if balance > 0 else "📭"
            print(f"  {status} Balance: {balance:.8f} BTC")
            print(f"     Transactions: {n_tx}")
            print(f"     Total received: {total_received:.8f} BTC")

            if balance > 0 or n_tx > 0:
                print(f"  ⭐⭐⭐ ACTIVE ADDRESS!")

        elif result['error'] == 'RATE_LIMIT':
            print(f"  ⚠️  Rate limited, waiting 30 seconds...")
            time.sleep(30)
            result = check_address_blockchain(address)  # Retry

        else:
            print(f"  ❌ Error: {result['error']}")

        results.append({
            **addr_data,
            'blockchain': result,
        })

        # Rate limiting: wait 5 seconds between requests
        if i < len(addresses):
            time.sleep(5)

    return results

def analyze_blockchain_results(results):
    """Analyze the blockchain check results"""
    print("\n" + "=" * 80)
    print("BLOCKCHAIN RESULTS ANALYSIS")
    print("=" * 80)

    # Filter out errors
    valid_results = [r for r in results if r['blockchain']['error'] is None]

    print(f"\nSuccessfully checked: {len(valid_results)}/{len(results)} addresses")

    # Find addresses with balance
    with_balance = [r for r in valid_results if r['blockchain']['balance'] > 0]
    print(f"\nAddresses with balance > 0: {len(with_balance)}")

    if with_balance:
        print("\n⭐⭐⭐ ADDRESSES WITH BALANCE:")
        for r in with_balance:
            print(f"\n  {r['address']}")
            print(f"    Balance: {r['blockchain']['balance']:.8f} BTC")
            print(f"    Total received: {r['blockchain']['total_received']:.8f} BTC")
            print(f"    Transactions: {r['blockchain']['n_tx']}")
            print(f"    Byte sum: {r['byte_sum']:,}")
            print(f"    Method: {r['method']}")

    # Find addresses with transactions
    with_tx = [r for r in valid_results if r['blockchain']['n_tx'] > 0]
    print(f"\nAddresses with transactions: {len(with_tx)}")

    if with_tx:
        print("\n📊 ADDRESSES WITH TRANSACTION HISTORY:")
        for r in sorted(with_tx, key=lambda x: x['blockchain']['n_tx'], reverse=True):
            print(f"\n  {r['address']}")
            print(f"    Transactions: {r['blockchain']['n_tx']}")
            print(f"    Balance: {r['blockchain']['balance']:.8f} BTC")
            print(f"    Total received: {r['blockchain']['total_received']:.8f} BTC")
            print(f"    Total sent: {r['blockchain']['total_sent']:.8f} BTC")

    # Check if best candidate has activity
    print("\n" + "=" * 80)
    print("BEST CANDIDATE STATUS")
    print("=" * 80)

    best_address = "1CFBpdLNULnV1F1frie8rHU9DqwufEiQXU"
    best_result = next((r for r in valid_results if r['address'] == best_address), None)

    if best_result:
        bc = best_result['blockchain']
        print(f"\nAddress: {best_address}")
        print(f"Balance: {bc['balance']:.8f} BTC")
        print(f"Transactions: {bc['n_tx']}")
        print(f"Total received: {bc['total_received']:.8f} BTC")

        if bc['balance'] > 0 or bc['n_tx'] > 0:
            print("\n⭐⭐⭐ BEST CANDIDATE IS ACTIVE!")
        else:
            print("\n💤 Best candidate has no activity")
            print("   → Might need to check other candidates")

    return valid_results, with_balance, with_tx

def save_blockchain_results(results):
    """Save blockchain check results"""
    output_file = Path("1CFB_BLOCKCHAIN_RESULTS.json")

    with open(output_file, 'w') as f:
        json.dump({
            'date': '2026-01-10',
            'total_checked': len(results),
            'results': results,
        }, f, indent=2)

    print(f"\n✅ Results saved: {output_file}")

def main():
    print("🔍 CHECKING 1CFB ADDRESSES ON BLOCKCHAIN")
    print("=" * 80)

    # Load addresses
    analysis_data = load_1cfb_addresses()

    if not analysis_data:
        return

    addresses = analysis_data['all_addresses']

    print(f"\nTotal addresses to check: {len(addresses)}")
    print(f"Best candidate: {analysis_data['best_candidate']['address']}")

    # Check if user wants to proceed
    print("\n⚠️  This will make API calls to blockchain.info")
    print("   It will take ~2-3 minutes with rate limiting")

    response = input("\nProceed? (yes/no): ").strip().lower()

    if response not in ['yes', 'y']:
        print("\n❌ Cancelled")
        print("\nYou can manually check addresses at:")
        print("  https://blockchain.info/address/[ADDRESS]")
        return

    # Check all addresses
    results = check_all_addresses_sequential(addresses)

    # Analyze results
    valid_results, with_balance, with_tx = analyze_blockchain_results(results)

    # Save results
    save_blockchain_results(results)

    print("\n" + "=" * 80)
    print("✅ BLOCKCHAIN CHECK COMPLETE")
    print("=" * 80)

    if with_balance:
        print(f"\n🎉 Found {len(with_balance)} addresses with balance!")
        print(f"   → These are the ACTIVE 1CFB addresses!")
    elif with_tx:
        print(f"\n📊 Found {len(with_tx)} addresses with transaction history")
        print(f"   → These have been used in the past")
    else:
        print("\n💤 No addresses with balance or transactions found")
        print("   → All 1CFB addresses are unused")
        print("   → This is actually INTERESTING - why generate but not use?")

if __name__ == "__main__":
    main()
