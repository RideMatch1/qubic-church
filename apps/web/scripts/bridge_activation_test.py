import hashlib

def get_hash160(s):
    if isinstance(s, bytes):
        data = s
    else:
        data = s.encode()
    sha = hashlib.sha256(data).digest()
    return hashlib.new('ripemd160', sha).hexdigest()

TARGET_1CFB = "7b581609d8f9b74c34f7648c3b79fd8a6848022d"

ID0 = "HSISJEJOTMWHNBDGGBTEIYKHQLXBAGCUVTWNKMEHGDWCECFHVAGSTGLBOPKE"
ID20 = "PVARRMXNHNMHECQOOVFESRLVXURDGDBDNPLBLJLLZGCNNRIKBDIQHBEHFPEE"
MASTER_KEY = "SKWYEVRXBZNJDNLVMFYP"

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def shift_str(s, key, direction=1):
    res = ""
    for i in range(len(s)):
        c = s[i]
        k = key[i % len(key)]
        idx = ALPHABET.find(c)
        shift = ALPHABET.find(k)
        if idx == -1:
            res += c
            continue
        new_idx = (idx + direction * shift) % 26
        res += ALPHABET[new_idx]
    return res

def xor_str(s1, s2):
    res = bytearray()
    for i in range(min(len(s1), len(s2))):
        res.append(ord(s1[i]) ^ ord(s2[i]))
    return bytes(res)

candidates = []
# 1. Shifts
candidates.append(("ID20 + MK", shift_str(ID20, MASTER_KEY, 1)))
candidates.append(("ID20 - MK", shift_str(ID20, MASTER_KEY, -1)))
candidates.append(("ID0 + MK", shift_str(ID0, MASTER_KEY, 1)))
candidates.append(("ID0 - MK", shift_str(ID0, MASTER_KEY, -1)))
candidates.append(("ID20 + ID0", shift_str(ID20, ID0, 1)))
candidates.append(("ID20 - ID0", shift_str(ID20, ID0, -1)))

# 2. XORs
candidates.append(("ID20 XOR ID0", xor_str(ID20, ID0)))
candidates.append(("ID20 XOR MK", xor_str(ID20, MASTER_KEY)))

# 3. Concatenations
candidates.append(("ID0+ID20", ID0 + ID20))
candidates.append(("ID20+ID0", ID20 + ID0))
candidates.append(("MK+ID20", MASTER_KEY + ID20))

# 4. Reverse
candidates.append(("ID20 REV", ID20[::-1]))

for name, c in candidates:
    h = get_hash160(c)
    print(f"[{name:15}] -> {h}")
    if h == TARGET_1CFB:
        print("MATCH!")
