"""
OP_RETURN Message Hunter - Search for Brainwallet hints, puzzles, treasure hunts
"""

import json
import requests
import time

# Keywords that indicate interesting content
INTERESTING_PATTERNS = [
    # Brainwallet related
    "brainwallet", "brain wallet", "private key", "passphrase", "password",
    "phrase", "seed", "mnemonic", "bip39",
    
    # Treasure/Puzzle related
    "treasure", "puzzle", "prize", "reward", "bounty", "challenge",
    "find", "crack", "solve", "decode", "hidden", "secret",
    
    # Direct hints
    "take", "claim", "yours", "free", "gift", "faucet",
    "crypto currency cafe", "good luck", "welcome",
    
    # Suspicious patterns
    "correct horse battery staple",  # XKCD reference
    "satoshi", "nakamoto", "bitcoin",
]

def analyze_op_return_message(hex_data, tx_id, block_height):
    """Analyze an OP_RETURN message and determine if it's interesting."""
    try:
        # Try ASCII decode
        ascii_data = bytes.fromhex(hex_data).decode('ascii', errors='ignore')
        lower_data = ascii_data.lower()
        
        # Check for interesting patterns
        matches = [p for p in INTERESTING_PATTERNS if p.lower() in lower_data]
        
        # Also interesting if it's a long coherent text
        words = ascii_data.split()
        is_long_text = len(words) > 10 and len([w for w in words if len(w) > 3]) > 5
        
        # Check if it looks like a potential brainwallet phrase
        looks_like_phrase = (
            len(words) >= 8 and  # At least 8 words
            all(w.replace(' ','').isalpha() for w in words[:8]) and  # First 8 are letters
            not any(c in ascii_data for c in ['<', '>', '{', '}', 'http'])  # Not HTML/JSON/URL
        )
        
        if matches or is_long_text or looks_like_phrase:
            return {
                "block": block_height,
                "tx_id": tx_id,
                "ascii": ascii_data,
                "matches": matches,
                "looks_like_phrase": looks_like_phrase,
                "score": len(matches) * 10 + (50 if looks_like_phrase else 0) + (10 if is_long_text else 0)
            }
    except:
        pass
    
    return None

def search_tx_for_op_return(tx_id, block_height=None):
    """Search a specific transaction for OP_RETURN outputs."""
    try:
        response = requests.get(f"https://blockstream.info/api/tx/{tx_id}", timeout=10)
        if response.status_code != 200:
            return []
        
        tx_data = response.json()
        if not block_height:
            block_height = tx_data.get('status', {}).get('block_height', 'unknown')
        
        findings = []
        for vout in tx_data.get("vout", []):
            scriptpubkey = vout.get("scriptpubkey", "")
            scriptpubkey_type = vout.get("scriptpubkey_type", "")
            
            if scriptpubkey_type == "op_return" or scriptpubkey.startswith("6a"):
                hex_data = scriptpubkey[4:] if scriptpubkey.startswith("6a") else scriptpubkey  # Skip OP_RETURN opcode
                
                if hex_data:  # Not empty
                    result = analyze_op_return_message(hex_data, tx_id, block_height)
                    if result:
                        findings.append(result)
        
        return findings
    except Exception as e:
        return []

def search_block_range(start, end, description=""):
    """Search a range of blocks for interesting OP_RETURN messages."""
    print(f"\n{'='*70}")
    print(f"🔍 Scanning blocks {start:,}-{end:,}: {description}")
    print(f"{'='*70}")
    
    all_findings = []
    
    for block_height in range(start, end + 1):
        if block_height % 50 == 0:
            print(f"  Block {block_height:,}/{end:,} ... ({len(all_findings)} findings so far)")
        
        try:
            # Get block hash
            response = requests.get(f"https://blockstream.info/api/block-height/{block_height}", timeout=10)
            if response.status_code != 200:
                time.sleep(0.2)
                continue
            
            block_hash = response.text.strip()
            time.sleep(0.15)
            
            # Get block
            response = requests.get(f"https://blockstream.info/api/block/{block_hash}/txids", timeout=10)
            if response.status_code != 200:
                time.sleep(0.2)
                continue
            
            tx_ids = response.json()
            time.sleep(0.15)
            
            # Check each transaction (limit to save time)
            for tx_id in tx_ids[:20]:  # Only first 20 TXs per block
                findings = search_tx_for_op_return(tx_id, block_height)
                all_findings.extend(findings)
                
                if findings:
                    for f in findings:
                        print(f"\n  💎 Block {block_height}, TX: {tx_id[:16]}...")
                        print(f"     Score: {f['score']} | Matches: {f['matches']}")
                        print(f"     Text: {f['ascii'][:150]}")
                        if f['looks_like_phrase']:
                            print(f"     ⚠️  LOOKS LIKE BRAINWALLET PHRASE!")
                
                time.sleep(0.15)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
            break
        except Exception as e:
            time.sleep(0.3)
            continue
    
    return all_findings

def analyze_specific_tx(tx_id):
    """Deep analysis of a specific transaction."""
    print(f"\n{'='*70}")
    print(f"🔍 Analyzing transaction: {tx_id}")
    print(f"{'='*70}\n")
    
    findings = search_tx_for_op_return(tx_id)
    
    if not findings:
        print("❌ No interesting OP_RETURN messages found")
        return
    
    for f in findings:
        print(f"Block: {f['block']}")
        print(f"Score: {f['score']}")
        print(f"Matches: {f['matches']}")
        print(f"Looks like phrase: {f['looks_like_phrase']}")
        print(f"\nFull message:")
        print(f"{f['ascii']}")
        print(f"\n{'-'*70}\n")

if __name__ == "__main__":
    import sys
    
    print("=" * 70)
    print("🔍 OP_RETURN TREASURE HUNTER")
    print("=" * 70)
    print()
    
    if len(sys.argv) > 1:
        # Specific TX or block range
        if len(sys.argv[1]) == 64:  # TX ID
            analyze_specific_tx(sys.argv[1])
        else:
            print("Usage: python op_return_hunter.py <tx_id>")
    else:
        print("MODES:")
        print("  1. Search early blocks (0-5000) - Genesis era")
        print("  2. Search specific block range")
        print("  3. Analyze specific TX: ab37d6ff6c...d3")
        print()
        
        mode = input("Choose mode (1/2/3): ").strip()
        
        if mode == "1":
            findings = search_block_range(0, 5000, "Genesis era - Most likely to have puzzles")
            print(f"\n\n📊 FOUND {len(findings)} interesting messages")
            
            # Sort by score
            findings.sort(key=lambda x: x['score'], reverse=True)
            print("\nTop 10:")
            for i, f in enumerate(findings[:10], 1):
                print(f"\n{i}. Block {f['block']}, TX {f['tx_id'][:16]}... (score: {f['score']})")
                print(f"   {f['ascii'][:100]}")
        
        elif mode == "2":
            start = int(input("Start block: "))
            end = int(input("End block: "))
            findings = search_block_range(start, end)
            print(f"\n\n📊 FOUND {len(findings)} interesting messages")
        
        elif mode == "3":
            tx = input("TX ID: ").strip()
            analyze_specific_tx(tx)
