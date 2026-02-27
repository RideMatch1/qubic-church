"""
Automated OP_RETURN Scanner & Brainwallet Tester
Finds OP_RETURN messages with brainwallet hints and tests them automatically
"""

import json
import requests
import time
import hashlib
from ecdsa import SECP256k1, SigningKey

def sha256(data):
    return hashlib.sha256(data).digest()

def hash160(data):
    return hashlib.new('ripemd160', sha256(data)).digest()

def base58encode(payload):
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    n = int.from_bytes(payload, 'big')
    result = []
    while n > 0:
        n, remainder = divmod(n, 58)
        result.append(alphabet[remainder])
    for byte in payload:
        if byte == 0: result.append('1')
        else: break
    return ''.join(reversed(result))

def base58check_encode(version, payload):
    versioned = version + payload
    return base58encode(versioned + sha256(sha256(versioned))[:4])

def phrase_to_address(phrase):
    """Convert phrase to Bitcoin address."""
    try:
        priv = sha256(phrase.encode('utf-8'))
        sk = SigningKey.from_string(priv, curve=SECP256k1)
        vk = sk.get_verifying_key()
        pub_c = (b'\x02' if vk.pubkey.point.y() % 2 == 0 else b'\x03') + vk.pubkey.point.x().to_bytes(32, 'big')
        addr = base58check_encode(b'\x00', hash160(pub_c))
        return addr, priv.hex()
    except:
        return None, None

def check_address_balance(address):
    """Check if address has balance or history."""
    try:
        response = requests.get(f"https://blockstream.info/api/address/{address}", timeout=10)
        if response.status_code != 200:
            return None
        
        data = response.json()
        cs = data.get('chain_stats', {})
        
        return {
            "tx_count": cs.get('tx_count', 0),
            "received": cs.get('funded_txo_sum', 0),
            "balance": cs.get('funded_txo_sum', 0) - cs.get('spent_txo_sum', 0)
        }
    except:
        return None

def extract_phrases_from_text(text):
    """Extract potential brainwallet phrases from text."""
    phrases = []
    
    # Whole text
    if len(text) > 10:
        phrases.append(text.strip())
    
    # Lines
    lines = text.split('\n')
    for line in lines:
        clean = line.strip()
        if len(clean) > 10:
            phrases.append(clean)
    
    # Look for sentences
    import re
    sentences = re.split(r'[.!?]+', text)
    for sent in sentences:
        clean = sent.strip()
        if len(clean.split()) >= 5:  # At least 5 words
            phrases.append(clean)
    
    return list(set(phrases))

def scan_block_for_op_returns(block_height):
    """Scan a single block for OP_RETURN messages."""
    findings = []
    
    try:
        # Get block hash
        response = requests.get(f"https://blockstream.info/api/block-height/{block_height}", timeout=10)
        if response.status_code != 200:
            return findings
        
        block_hash = response.text.strip()
        time.sleep(0.2)
        
        # Get TXs
        response = requests.get(f"https://blockstream.info/api/block/{block_hash}/txids", timeout=10)
        if response.status_code != 200:
            return findings
        
        tx_ids = response.json()
        time.sleep(0.2)
        
        # Check each TX (limit to first 10 for speed)
        for tx_id in tx_ids[:10]:
            try:
                response = requests.get(f"https://blockstream.info/api/tx/{tx_id}", timeout=10)
                if response.status_code != 200:
                    continue
                
                tx_data = response.json()
                time.sleep(0.2)
                
                # Look for OP_RETURN
                for vout in tx_data.get("vout", []):
                    scriptpubkey = vout.get("scriptpubkey", "")
                    scriptpubkey_type = vout.get("scriptpubkey_type", "")
                    
                    if scriptpubkey_type == "op_return" or scriptpubkey.startswith("6a"):
                        hex_data = scriptpubkey[4:] if len(scriptpubkey) > 4 else scriptpubkey
                        
                        if hex_data:
                            try:
                                ascii_text = bytes.fromhex(hex_data).decode('ascii', errors='ignore')
                                
                                # Filter: must look like text
                                if len(ascii_text) > 20 and any(c.isalpha() for c in ascii_text):
                                    findings.append({
                                        "block": block_height,
                                        "tx_id": tx_id,
                                        "text": ascii_text
                                    })
                            except:
                                pass
            except:
                continue
    except:
        pass
    
    return findings

def auto_scan_and_test(start_block, end_block, output_file="op_return_results.json"):
    """Scan blocks and test found phrases automatically."""
    print("=" * 70)
    print("🤖 AUTOMATED OP_RETURN SCANNER & BRAINWALLET TESTER")
    print("=" * 70)
    print(f"Scanning blocks {start_block:,} to {end_block:,}")
    print(f"This will find OP_RETURN messages and test them as brainwallets")
    print("=" * 70)
    
    all_results = []
    tested_phrases = set()
    
    for block in range(start_block, end_block + 1):
        if block % 100 == 0:
            print(f"\n📍 Block {block:,}/{end_block:,} ... ({len(tested_phrases)} phrases tested)")
        
        findings = scan_block_for_op_returns(block)
        
        for finding in findings:
            text = finding['text']
            phrases = extract_phrases_from_text(text)
            
            print(f"\n  💬 Block {block}: Found OP_RETURN message")
            print(f"     Text: {text[:80]}...")
            print(f"     Testing {len(phrases)} variations...")
            
            for phrase in phrases:
                if phrase in tested_phrases:
                    continue
                
                tested_phrases.add(phrase)
                
                addr, privkey = phrase_to_address(phrase)
                if not addr:
                    continue
                
                time.sleep(0.3)  # Rate limit
                balance_info = check_address_balance(addr)
                
                if balance_info and balance_info['tx_count'] > 0:
                    result = {
                        "block": block,
                        "tx_id": finding['tx_id'],
                        "phrase": phrase,
                        "address": addr,
                        "private_key": privkey,
                        "tx_count": balance_info['tx_count'],
                        "total_received_sat": balance_info['received'],
                        "current_balance_sat": balance_info['balance']
                    }
                    
                    all_results.append(result)
                    
                    print(f"\n     🎯 HIT! '{phrase[:40]}'")
                    print(f"        Address: {addr}")
                    print(f"        TXs: {balance_info['tx_count']}")
                    print(f"        Received: {balance_info['received']/1e8:.8f} BTC")
                    print(f"        Balance: {balance_info['balance']/1e8:.8f} BTC")
                    
                    if balance_info['balance'] > 0:
                        print(f"        💰💰💰 HAS BALANCE! 💰💰💰")
    
    # Save results
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n\n{'='*70}")
    print(f"📊 SCAN COMPLETE")
    print(f"{'='*70}")
    print(f"Tested phrases: {len(tested_phrases)}")
    print(f"Hits (used addresses): {len(all_results)}")
    print(f"Results saved to: {output_file}")
    
    if all_results:
        with_balance = [r for r in all_results if r['current_balance_sat'] > 0]
        if with_balance:
            print(f"\n💰 JACKPOT! {len(with_balance)} addresses with current balance:")
            for r in with_balance:
                print(f"   {r['address']}: {r['current_balance_sat']/1e8:.8f} BTC")
                print(f"   Phrase: {r['phrase']}")
                print(f"   Private Key: {r['private_key']}")
        else:
            print(f"\n⚠️  All {len(all_results)} found addresses were already swept (balance = 0)")
    else:
        print("\n❌ No hits found - all messages were either invalid or never used")
    
    return all_results

if __name__ == "__main__":
    print("\n🚀 Starting automated scan...")
    print("This will take a while (rate-limited to avoid API bans)")
    print()
    
    # Scan early interesting blocks
    # These are most likely to contain treasure hunts
    results = auto_scan_and_test(
        start_block=0,
        end_block=1000,  # First 1000 blocks
        output_file="apps/web/scripts/op_return_treasures.json"
    )
