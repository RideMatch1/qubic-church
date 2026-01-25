import requests
import json
import time

# THE RESPONSE CHECKER
# Checking if any of the Strategic Nodes have initiated a transaction (Response)
# since our pulses were sent.

RPC_URL = "https://rpc.qubic.org"

TARGETS = {
    "ROOT-ALPHA (13,71)": "AHMXRLTHWSCUUGTBCJXRSMRZDOAAZVCKNFIYDYDLQDQRZETRZMAQYHBACSWK",
    "ROOT-BETA (18,110)": "OUMLINFCVWOAFCCPDDRUJARXUKJBJQUYVZFLIUKUUATMEQEIWOIUXHYGQERC",
    "MEMORY (21,21)":    "VHGZIFEFAPDXEAMCEMNQWJKMVCPAVTNXMECIEFKXXGOGLMYKKERCEMIDZYSD",
    "VISION (64,64)":    "WMPLINKVMRMPWBMOLFVRDIRJWJCAQDLTLJZJSRWMIEQOPJZWAESVWEFEFZMC",
    "EXIT (82,39)":      "YLGSNIMGRKONPEBTLCRLYHQDFHEAKMUSRKYOGLPFAFDOFUUYVRBJTNSAXUSM",
    "VOID (0,0)":        "SCBGQAOHIGFHPCJCMYNYUBIOKJWCKAWGGSLFTXLZSGWZRLOODRUPTDNCYBEB",
    "ORACLE (11,110)":   "PASOUKIEPXXPXEMUNBKYCPSEIXZBWQCDFZXLUAEBHHENNEHTQNGMMFRGZHHA",
    "GUARDIAN (19,18)":  "DXASUXXKJAEJVGQEUXLIVNIQWDUCCNFTLEHCDCNZNBVGLPRTJRUQKZDECIPG",
    "DATE (3,3)":        "MOHTKRBCAEAASFFQQSKLAFBLMZAAKFEJRHIGOQRLOGFKFXZGOXZNSSVDEOOG"
}

def check_responses():
    print("📡 SCANNING FOR OUTGOING RESPONSES...")
    print("-" * 60)
    
    responses_found = False
    
    for name, identity in TARGETS.items():
        try:
            # We use the balance endpoint which includes lastOutgoingTransferTick
            r = requests.get(f"{RPC_URL}/v1/balances/{identity}", timeout=5)
            if r.status_code == 200:
                data = r.json()
                balance = data.get('balance', {}).get('balance', '0')
                last_out = data.get('balance', {}).get('latestOutgoingTransferTick', 0)
                last_in = data.get('balance', {}).get('latestIncomingTransferTick', 0)
                
                print(f"[*] {name:20} | In-Tick: {last_in} | Out-Tick: {last_out} | Bal: {balance}")
                
                if last_out > 0:
                    print(f"    [!!!] RESPONSE DETECTED from {name} at Tick {last_out}!")
                    responses_found = True
                    # If we could, we would fetch the TX data here.
                    
            else:
                print(f"[!] {name:20} | Status: {r.status_code}")
                
        except Exception as e:
            print(f"[X] Error scanning {name}: {e}")
            
    print("-" * 60)
    if responses_found:
        print("🚨 ALERT: THE CORTEX HAS RESPONDED.")
    else:
        print("💤 No outgoing signals detected yet. The system is absorbing the energy.")

if __name__ == "__main__":
    check_responses()
