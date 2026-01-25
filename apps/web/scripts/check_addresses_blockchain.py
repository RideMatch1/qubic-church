#!/usr/bin/env python3
"""
BLOCKCHAIN ADDRESS CHECKER
===========================

Checks if generated mirror addresses have any blockchain activity.
Uses blockchain.info API (no JavaScript needed).
"""

import json
import time
import urllib.request
import urllib.error

def check_address_blockchain(address):
    """
    Check address using blockchain.info API
    Returns: (status, data)
    """
    try:
        url = f"https://blockchain.info/rawaddr/{address}?limit=0"

        # Add headers to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Research Script)'
        }

        req = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())

            return "found", {
                'address': data.get('address'),
                'n_tx': data.get('n_tx', 0),
                'total_received': data.get('total_received', 0),
                'total_sent': data.get('total_sent', 0),
                'final_balance': data.get('final_balance', 0)
            }

    except urllib.error.HTTPError as e:
        if e.code == 404:
            return "not_found", None
        else:
            return "error", f"HTTP {e.code}"

    except Exception as e:
        return "error", str(e)

def check_priority_addresses():
    """Check the most interesting addresses first"""

    print("="*80)
    print("BLOCKCHAIN ADDRESS CHECKER")
    print("="*80)
    print()
    print("Checking high-priority mirror addresses...")
    print()

    # Priority addresses from MIRROR_ANALYSIS_SUMMARY.md
    priority = [
        ("Genesis Mirror Palindrome", "1A1zP1eP5QGefi1aJV8XSuxPtXLs6wrd7y"),
        ("1CFB Mirror Palindrome", "1CFBdvaiZgZPTZEbfU3THHLqPQt9UDhdRy"),
        ("15ubic Mirror Palindrome", "15ubicBBWFnvoZKgE3qy2pSwvPdrL9eDDT"),
        ("Genesis XOR 1CFB", "13Lr1nJCKcfLWEDd6cSdYVrSz7aPcrAVJy"),
        ("Genesis XOR 15ubic", "18xDPqiJd77KWRWSKjU3VhaiJt2ez4w9qZ"),
        ("1CFB XOR 15ubic", "18AJGrqSgFvgecpuSoBRABSW9QhCTA9Uec"),
    ]

    results = []

    for name, address in priority:
        print(f"Checking: {name}")
        print(f"Address:  {address}")

        status, data = check_address_blockchain(address)

        if status == "found":
            print(f"Status:   FOUND ON BLOCKCHAIN")
            print(f"  Transactions: {data['n_tx']}")
            print(f"  Total Received: {data['total_received'] / 100000000:.8f} BTC")
            print(f"  Final Balance: {data['final_balance'] / 100000000:.8f} BTC")

            results.append({
                'name': name,
                'address': address,
                'status': 'found',
                'data': data
            })

        elif status == "not_found":
            print(f"Status:   NOT FOUND (unused address)")

            results.append({
                'name': name,
                'address': address,
                'status': 'not_found',
                'data': None
            })

        else:
            print(f"Status:   ERROR - {data}")

            results.append({
                'name': name,
                'address': address,
                'status': 'error',
                'error': data
            })

        print()

        # Rate limiting - be nice to API
        time.sleep(2)

    # Summary
    print("="*80)
    print("RESULTS SUMMARY")
    print("="*80)
    print()

    found_count = sum(1 for r in results if r['status'] == 'found')
    not_found_count = sum(1 for r in results if r['status'] == 'not_found')
    error_count = sum(1 for r in results if r['status'] == 'error')

    print(f"Total checked:     {len(results)}")
    print(f"Found on chain:    {found_count}")
    print(f"Not found (unused): {not_found_count}")
    print(f"Errors:            {error_count}")
    print()

    if found_count > 0:
        print("ADDRESSES WITH ACTIVITY:")
        print("-"*80)
        for r in results:
            if r['status'] == 'found':
                data = r['data']
                print(f"\n{r['name']}:")
                print(f"  Address: {r['address']}")
                print(f"  Transactions: {data['n_tx']}")
                print(f"  Balance: {data['final_balance'] / 100000000:.8f} BTC")

    # Save results
    with open('blockchain_check_results.json', 'w') as f:
        json.dump({
            'check_date': '2026-01-09',
            'total_checked': len(results),
            'found_count': found_count,
            'not_found_count': not_found_count,
            'results': results
        }, f, indent=2)

    print()
    print("Results saved to: blockchain_check_results.json")

if __name__ == "__main__":
    check_priority_addresses()
