
import json

def get_shift(doc_char, real_char):
    return (ord(real_char) - ord(doc_char)) % 26

with open("/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/public/data/qubic-seeds.json") as f:
    data = json.load(f)
    records = {r["id"]: r for r in data["records"]}

# Sync Path Seed IDs from the doc
sync_ids = [10641, 7922, 1472, 13652, 1383, 7089, 5492, 1302, 8504, 5747, 54, 11193, 3322, 10476, 16408, 297, 7760, 1320, 13176, 1049]

shifts = []
for sid in sync_ids:
    r = records[sid]
    # Check the first char of doc and real
    doc = r["documentedIdentity"]
    real = r["realIdentity"]
    shift = get_shift(doc[0], real[0])
    shifts.append(shift)

print("Shifts:", shifts)
print("Chars:", "".join(chr(ord('A') + s) for s in shifts))

# Node 0
r0 = records[0]
doc0 = r0["documentedIdentity"]
real0 = r0["realIdentity"]
shifts0 = [get_shift(doc0[i], real0[i]) for i in range(len(doc0))]
print("Node 0 Shifts:", shifts0[:20])
print("Node 0 Chars:", "".join(chr(ord('A') + s) for s in shifts0[:20]))
