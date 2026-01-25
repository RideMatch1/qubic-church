#!/usr/bin/env python3
import hashlib
import binascii

def get_hash160(s):
    sha = hashlib.sha256(s.encode() if isinstance(s, str) else s).digest()
    return hashlib.new('ripemd160', sha).hexdigest()

def shift_string(s, n):
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    res = ''
    for char in s:
        if char in alphabet:
            idx = (alphabet.find(char) + n) % 26
            res += alphabet[idx]
        else:
            res += char
    return res

target_1cfb = '7b581609d8f9b74c34f7648c3b79fd8a6848022d'
master_key = 'SKWYEVRXBZNJDNLVMFYP'
acrostic = 'DSXMFCWXKENVGYCVUFLP'

print('--- 🔥 OPERATION CORE ENTRY: HELIX CRACKER 🔥 ---')

# Try shifts -26 to +26
for offset in range(-26, 27):
    # Candidate 1: The Master Key shifted
    c1 = shift_string(master_key, offset)
    
    # Candidate 2: The Acrostic shifted
    c2 = shift_string(acrostic, offset)
    
    # Candidate 3: 4 * 14 structure (like ID 1472)
    frag = shift_string(master_key[:14], offset)
    c3 = frag * 4
    
    for c in [c1, c2, c3]:
        h160 = get_hash160(c)
        if h160 == target_1cfb:
            print(f'🔥 BINGO! MATCH FOUND with Offset {offset}!')
            print(f'Seed: {c}')
            exit()
        
        if h160.startswith('7b'):
             print(f'SIGNIFICANT HIT (121/123 base): {h160[:10]}... | Offset {offset} | Code: {c[:20]}')

print('Phase 1 complete. No immediate match in base shifts.')
