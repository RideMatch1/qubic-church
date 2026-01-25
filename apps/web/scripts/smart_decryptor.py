import subprocess
import os

# SMART DECRYPTOR
# Attempts to force-open the extracted artifact using likely keys and ciphers.

ARTIFACTS = [
    "/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/candidate_A.der",
    "/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/candidate_B.der"
]
KEYS = [
    "SKWIKENGRZNXRPLXWRHP", # The Master Key
    "1CFBdvaiZgZPTZERqnezAtDQJuGHKoHSzg", # Start Address
    "1CFiVYy5wuys6zAbvGGYpE2xh1NopsoHbi", # End Address
    "POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD", # Genesis
    "POCC",
    "SKWIKEN",
    "CFB",
    "Satoshi",
    "137",
    "26",
    "16777216",
    "vfr4923f",
    "QUBIC"
]

CIPHERS = [
    "aes-256-cbc",
    "aes-128-cbc",
    "des3",
    "rc4",
    "bf" # Blowfish
]

def try_decrypt():
    print("🔓 STARTING BRUTEFORCE DECRYPTION...")
    
    for ARTIFACT in ARTIFACTS:
        print(f"\n[+] Testing Artifact: {os.path.basename(ARTIFACT)}")
        if not os.path.exists(ARTIFACT):
            print("x Artifact not found.")
            continue

    success = False
    
    # METHOD 1: PKCS#12 / PKCS#8 Container
    print("[-] Testing as PKCS Container...")
    for key in KEYS:
        # Try PKCS8
        cmd = ["openssl", "pkcs8", "-inform", "DER", "-in", ARTIFACT, "-passin", f"pass:{key}"]
        try:
            res = subprocess.run(cmd, capture_output=True, timeout=1)
            if res.returncode == 0:
                print(f"[!] SUCCESS: Decrypted via PKCS8 with key '{key}'")
                print(res.stdout)
                success = True
                break
        except Exception: pass
        
        # Try PKCS12
        cmd = ["openssl", "pkcs12", "-in", ARTIFACT, "-passin", f"pass:{key}", "-nokeys", "-nomacver"]
        try:
            res = subprocess.run(cmd, capture_output=True, timeout=1)
            if res.returncode == 0:
                print(f"[!] SUCCESS: Decrypted via PKCS12 with key '{key}'")
                return
        except Exception: pass

        if success: continue

    # METHOD 2: Raw Cipher Stream
    print("[-] Testing as Raw Ciphertext...")
    for cipher in CIPHERS:
        for key in KEYS:
            # OpenSSL enc -d
            cmd = ["openssl", "enc", "-d", f"-{cipher}", "-in", ARTIFACT, "-pass", f"pass:{key}"]
            try:
                res = subprocess.run(cmd, capture_output=True, timeout=1)
                if res.returncode == 0:
                    # Check for text or readability
                    out = res.stdout
                    try:
                        text = out.decode('utf-8')
                        if text.isprintable() and len(text) > 5:
                            print(f"[!] POSSIBLE MATCH: {cipher} with key '{key}'")
                            print(f"    Output: {text[:50]}...")
                    except:
                        # Check for JSON or XML chars
                        if b"{" in out or b"<" in out:
                             print(f"[!] BINARY MATCH: {cipher} with key '{key}' (Contains structure)")
                             
            except Exception: pass

    print("[*] Bruteforce Complete.")

if __name__ == "__main__":
    try_decrypt()
