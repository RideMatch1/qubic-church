#!/usr/bin/env python3
"""
BITCOIN HIDDEN MESSAGE EXTRACTOR

Fetches coinbase messages from Bitcoin blocks 0-1000
Identifies pattern followers vs exceptions
Extracts the hidden message

Usage:
    python3 BITCOIN_HIDDEN_MESSAGE_EXTRACTOR.py [--start 0] [--end 1000]
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime
import argparse

# ==============================================================================
# CONFIGURATION
# ==============================================================================

BLOCKCHAIR_API = "https://api.blockchair.com/bitcoin/dashboards/block/{}"
RATE_LIMIT_DELAY = 1.5  # seconds between requests (Blockchair limit)
PROGRESS_FILE = Path(__file__).parent / "bitcoin_extraction_progress.json"
RESULTS_FILE = Path(__file__).parent / "bitcoin_hidden_message_results.json"

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def load_progress():
    """Load previous progress if exists"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {'blocks': {}, 'last_block': -1}

def save_progress(data):
    """Save progress incrementally"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_expected_letter(height):
    """Calculate expected letter based on (height mod 26) pattern"""
    mod = height % 26
    if mod == 0:
        mod = 26  # 0 = Z (26th letter)
    return chr(ord('A') + mod - 1)

def fetch_block(height, retry=3):
    """Fetch block data from Blockchair API with retry logic"""
    for attempt in range(retry):
        try:
            url = BLOCKCHAIR_API.format(height)
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if 'data' in data and str(height) in data['data']:
                    block_data = data['data'][str(height)]['block']

                    # Extract coinbase from transactions
                    if 'transactions' in data['data'][str(height)]:
                        txs = data['data'][str(height)]['transactions']
                        if len(txs) > 0:
                            coinbase_tx = txs[0]  # First tx is coinbase

                            # Try to get coinbase message
                            coinbase_message = ''
                            if 'inputs' in coinbase_tx and len(coinbase_tx['inputs']) > 0:
                                coinbase_input = coinbase_tx['inputs'][0]
                                if 'coinbase_data_hex' in coinbase_input:
                                    hex_data = coinbase_input['coinbase_data_hex']
                                    try:
                                        # Try to decode as ASCII
                                        coinbase_message = bytes.fromhex(hex_data).decode('ascii', errors='ignore')
                                    except:
                                        coinbase_message = hex_data

                    return {
                        'height': height,
                        'timestamp': block_data['time'],
                        'nonce': block_data['nonce'],
                        'hash': block_data['hash'],
                        'coinbase': coinbase_message,
                        'difficulty': block_data.get('difficulty', 1.0),
                    }

            elif response.status_code == 430:
                print(f"   ⚠️  Rate limit hit, waiting 5 seconds...")
                time.sleep(5)
                continue

            else:
                print(f"   ❌ Error {response.status_code} for block {height}")
                return None

        except Exception as e:
            print(f"   ❌ Exception fetching block {height}: {e}")
            if attempt < retry - 1:
                time.sleep(2)
                continue
            return None

    return None

# ==============================================================================
# MAIN EXTRACTION
# ==============================================================================

def extract_hidden_message(start_block=0, end_block=1000):
    """Main extraction function"""

    print("="*80)
    print("BITCOIN HIDDEN MESSAGE EXTRACTOR")
    print("="*80)
    print(f"\nExtracting blocks {start_block} to {end_block}")
    print(f"Rate limit: {RATE_LIMIT_DELAY}s between requests")
    print(f"Estimated time: {((end_block - start_block + 1) * RATE_LIMIT_DELAY / 60):.1f} minutes")
    print("\nStarting extraction...\n")

    # Load previous progress
    progress = load_progress()
    blocks_data = progress['blocks']

    # Track statistics
    total_blocks = end_block - start_block + 1
    fetched = 0
    pattern_followers = []
    exceptions = []

    # Extract blocks
    for height in range(start_block, end_block + 1):
        # Skip if already fetched
        if str(height) in blocks_data:
            fetched += 1
            continue

        # Fetch block
        print(f"[{fetched+1}/{total_blocks}] Fetching block {height}...", end='')

        block = fetch_block(height)

        if block:
            # Get first character of coinbase (the pattern character)
            coinbase_char = block['coinbase'][0] if block['coinbase'] else ''

            # Calculate expected
            expected = get_expected_letter(height)

            # Check if follows pattern
            is_pattern = (coinbase_char.upper() == expected)

            block_info = {
                'height': height,
                'coinbase_char': coinbase_char,
                'coinbase_full': block['coinbase'][:100],  # First 100 chars
                'expected': expected,
                'is_pattern': is_pattern,
                'timestamp': block['timestamp'],
                'nonce': block['nonce'],
                'hash': block['hash'][:16],
            }

            blocks_data[str(height)] = block_info

            if is_pattern:
                pattern_followers.append(height)
                print(f" ✅ '{coinbase_char}' = '{expected}' (pattern)")
            else:
                exceptions.append(height)
                print(f" 🔥 '{coinbase_char}' ≠ '{expected}' (EXCEPTION!)")

            fetched += 1

            # Save progress every 10 blocks
            if fetched % 10 == 0:
                progress['blocks'] = blocks_data
                progress['last_block'] = height
                save_progress(progress)
                print(f"\n   💾 Progress saved ({fetched}/{total_blocks} blocks)")

        else:
            print(f" ❌ Failed to fetch")

        # Rate limiting
        time.sleep(RATE_LIMIT_DELAY)

    # Final save
    progress['blocks'] = blocks_data
    progress['last_block'] = end_block
    save_progress(progress)

    # ==============================================================================
    # ANALYZE RESULTS
    # ==============================================================================

    print("\n" + "="*80)
    print("EXTRACTION COMPLETE - ANALYZING RESULTS")
    print("="*80)

    # Separate into pattern vs exceptions
    pattern_blocks = []
    exception_blocks = []

    for height in range(start_block, end_block + 1):
        if str(height) in blocks_data:
            block = blocks_data[str(height)]
            if block['is_pattern']:
                pattern_blocks.append(block)
            else:
                exception_blocks.append(block)

    print(f"\n📊 STATISTICS:")
    print(f"   Total blocks: {len(blocks_data)}")
    print(f"   Pattern followers: {len(pattern_blocks)} ({len(pattern_blocks)/len(blocks_data)*100:.1f}%)")
    print(f"   Exceptions: {len(exception_blocks)} ({len(exception_blocks)/len(blocks_data)*100:.1f}%)")

    # ==============================================================================
    # EXTRACT HIDDEN MESSAGE
    # ==============================================================================

    print(f"\n{'='*80}")
    print("HIDDEN MESSAGE EXTRACTION")
    print(f"{'='*80}")

    print(f"\n🔥 EXCEPTION BLOCKS ({len(exception_blocks)}):\n")

    exception_chars = []
    exception_chars_nonspace = []

    for i, block in enumerate(exception_blocks[:50]):  # First 50
        char = block['coinbase_char']
        expected = block['expected']
        height = block['height']

        exception_chars.append(char)
        if char and char != ' ':
            exception_chars_nonspace.append(char)

        print(f"   {i+1:3d}. Block {height:5d}: '{char}' (expected '{expected}')")

    if len(exception_blocks) > 50:
        print(f"   ... and {len(exception_blocks) - 50} more")

    # String together the message
    hidden_message = ''.join(exception_chars)
    hidden_message_nonspace = ''.join(exception_chars_nonspace)

    print(f"\n{'='*80}")
    print("THE HIDDEN MESSAGE")
    print(f"{'='*80}")

    print(f"\nRAW MESSAGE (with spaces):")
    print(f"   '{hidden_message[:200]}'")
    if len(hidden_message) > 200:
        print(f"   ... ({len(hidden_message)} total characters)")

    print(f"\nNON-SPACE CHARACTERS ONLY:")
    print(f"   '{hidden_message_nonspace[:200]}'")
    if len(hidden_message_nonspace) > 200:
        print(f"   ... ({len(hidden_message_nonspace)} total characters)")

    # Look for words
    print(f"\n🔍 LOOKING FOR KNOWN WORDS:")
    keywords = ['BITCOIN', 'SATOSHI', 'NAKAMOTO', 'CFB', 'GENESIS',
                'ARCHITECT', 'QUBIC', 'YHVH', 'ANNA']

    message_upper = hidden_message_nonspace.upper()
    for keyword in keywords:
        if keyword in message_upper:
            pos = message_upper.index(keyword)
            print(f"   ✅ FOUND: '{keyword}' at position {pos}")

    # ==============================================================================
    # SAVE RESULTS
    # ==============================================================================

    results = {
        'timestamp': datetime.now().isoformat(),
        'range': {'start': start_block, 'end': end_block},
        'statistics': {
            'total_blocks': len(blocks_data),
            'pattern_followers': len(pattern_blocks),
            'exceptions': len(exception_blocks),
        },
        'pattern_blocks': [b['height'] for b in pattern_blocks],
        'exception_blocks': [
            {
                'height': b['height'],
                'char': b['coinbase_char'],
                'expected': b['expected'],
                'full_coinbase': b['coinbase_full']
            }
            for b in exception_blocks
        ],
        'hidden_message': hidden_message,
        'hidden_message_nonspace': hidden_message_nonspace,
    }

    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*80}")
    print(f"RESULTS SAVED")
    print(f"{'='*80}")
    print(f"\nResults saved to: {RESULTS_FILE}")
    print(f"Progress saved to: {PROGRESS_FILE}")

    print(f"\n{'='*80}")
    print("EXTRACTION COMPLETE!")
    print(f"{'='*80}")

    return results

# ==============================================================================
# CLI
# ==============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract hidden message from Bitcoin blockchain')
    parser.add_argument('--start', type=int, default=0, help='Start block (default: 0)')
    parser.add_argument('--end', type=int, default=1000, help='End block (default: 1000)')
    parser.add_argument('--resume', action='store_true', help='Resume from last saved progress')

    args = parser.parse_args()

    # Check if resuming
    if args.resume:
        progress = load_progress()
        if progress['last_block'] >= 0:
            print(f"Resuming from block {progress['last_block'] + 1}")
            args.start = progress['last_block'] + 1

    # Run extraction
    try:
        results = extract_hidden_message(args.start, args.end)

        print("\n🎉 SUCCESS! The hidden message has been extracted!")
        print(f"\nCheck the results in: {RESULTS_FILE}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Extraction interrupted by user")
        print(f"Progress saved. Resume with: python3 {__file__} --resume")

    except Exception as e:
        print(f"\n❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()
