import json
from pathlib import Path

# Paths
COMMITTEE_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/executive_committee.json")
GAP_KEYS_JSON = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/matrix_gap_analysis.json")
# Wait, matrix_gap_analysis.json has coords, not keys.
# Let's use legacy_keys_report.md logic or rebuild the list.

def find_committee_shadows():
    print("[*] Auditing Shadow-Side Security: Are Committee Ranges Protected?")
    
    with open(COMMITTEE_JSON, "r") as f:
        committee = json.load(f)
        
    # We need the 185 legacy keys mapping to see which ones are Gap Keys
    # Re-extracting for the audit
    from executive_committee import btc_privkey_to_qubic_seed
    import hashlib
    
    BIN_FILE = Path("/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/horizontal_mining/pos_27_decoded.bin")
    with open(BIN_FILE, "rb") as f:
        data = f.read()
    
    key_size = 32
    num_keys = len(data) // key_size
    
    # Load Gap Coords
    with open(GAP_KEYS_JSON, "r") as f:
        gap_data = json.load(f)
    gap_set = set(tuple(c) for c in gap_data.get("gap_coordinates", []))
    
    gap_keys = []
    for i in range(num_keys):
        key_bytes = data[i*key_size : (i+1)*key_size]
        hex_key = key_bytes.hex()
        seed = btc_privkey_to_qubic_seed(hex_key)
        h = hashlib.sha256(seed.encode('utf-8')).digest()
        coord = (h[0] % 128, h[1] % 128)
        
        if coord in gap_set:
            gap_keys.append(i)
            
    print(f"[+] Isolated {len(gap_keys)} Shadow Keys as 'Gap Access Keys'.")
    
    print("\n[!] COMMITTEE MEMBER SECURITY AUDIT:")
    for name, info in committee.items():
        k_idx = info['key_index']
        status = "🛡️ PROTECTED (GAP KEY)" if k_idx in gap_keys else "🌐 PUBLIC SECTOR"
        print(f"  - {name:7} | Key {k_idx:3} | Status: {status}")

if __name__ == "__main__":
    find_committee_shadows()
