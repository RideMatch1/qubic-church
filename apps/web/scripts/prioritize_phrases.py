"""
Prioritize brainwallet phrases - put interesting/rare ones first, skip obvious ones
"""

from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PHRASES_FILE = SCRIPT_DIR / "brainwallet_phrases.txt"
OUTPUT_FILE = SCRIPT_DIR / "brainwallet_phrases_prioritized.txt"

# Define priority categories
SKIP_PATTERNS = [
    # Standard passwords - guaranteed empty
    "password", "123456", "12345678", "qwerty", "abc123", "monkey",
    "letmein", "trustno1", "dragon", "baseball", "iloveyou", "master",
    "sunshine", "ashley", "michael", "shadow", "123123", "654321",
    "superman", "qazwsx", "football", "admin", "login", "welcome",
    "solo", "princess", "starwars", "passw0rd", "hello123", "charlie",
    "donald", "password1", "password123",
    # Keyboard patterns
    "qwertyuiop", "asdfghjkl", "zxcvbnm", "qweasdzxc", "1qaz2wsx",
    "qwerty123", "asdf1234", "zaq1xsw2",
    # Trivial
    "test", "testing", "temp", "tmp", "pass", "passwd",
    "a", "b", "c", "x", "y", "z", "aa", "aaa", "aaaa",
    # Simple words (too obvious)
    "bitcoin", "satoshi", "crypto", "money", "secret", "god", "love",
    "hate", "death", "life", "freedom", "power", "truth", "fuck", "shit",
    "hell", "damn", "jesus", "allah", "buddha",
    # Simple numbers
    "0", "1", "2", "12", "13", "21", "42", "69", "420", "666", "1337",
]

HIGH_PRIORITY_KEYWORDS = [
    # Qubic/CFB specific
    "qubic", "come from beyond", "cfb", "sergey ivancheglo", "jinn",
    "ternary", "trinary", "curl", "abra", "nxt", "iota",
    # Bitcoin genesis/historical
    "the times", "chancellor", "bailout", "genesis block", "satoshi nakamoto",
    # Philosophy (longer quotes)
    "unexamined life", "step twice", "god is dead", "does not kill us",
    "existence precedes", "condemned to be free", "know nothing",
    "to be is to be perceived", "hell is other people", "whereof",
    # Bible verses (specific, longer)
    "in the beginning god created", "let there be light", "lord is my shepherd",
    "valley of the shadow of death", "thy rod and thy staff", "blessed are",
    "sermon on the mount", "love thy neighbor", "prodigal son",
    "good samaritan", "thou shalt not", "alpha and omega",
    # Literature (specific quotes)
    "to be or not to be", "all the world", "what light through yonder",
    "tomorrow and tomorrow", "something wicked", "call me ishmael",
    "it was the best of times", "pride and prejudice", "sense and sensibility",
    # Lorem Ipsum (VERY rare)
    "lorem ipsum", "dolor sit amet", "consectetur adipisicing",
    # Scientific
    "e equals mc squared", "schrodinger", "heisenberg", "fibonacci",
    "golden ratio", "mersenne", "fermat",
]

def categorize_phrase(phrase: str) -> int:
    """Return priority: 1=HIGH, 2=MEDIUM, 3=LOW, 999=SKIP"""
    phrase_lower = phrase.lower().strip()
    
    # Skip obvious ones
    if phrase_lower in [p.lower() for p in SKIP_PATTERNS]:
        return 999
    
    # Skip simple numbers (but keep interesting ones like 21000000)
    if phrase_lower.isdigit() and len(phrase_lower) <= 4:
        return 999
    
    # High priority - rare/specific
    for keyword in HIGH_PRIORITY_KEYWORDS:
        if keyword.lower() in phrase_lower:
            return 1
    
    # Long phrases are usually more interesting
    if len(phrase) > 50:
        return 1
    
    # Medium priority - moderate length, not too obvious
    if len(phrase) > 15:
        return 2
    
    # Low priority - short, simple
    return 3

def main():
    print("🔄 Analyzing and prioritizing phrases...")
    
    # Load phrases
    with open(PHRASES_FILE) as f:
        lines = f.readlines()
    
    # Categorize
    high_priority = []
    medium_priority = []
    low_priority = []
    skipped = []
    comments = []
    
    for line in lines:
        stripped = line.strip()
        
        # Keep comments and empty lines
        if not stripped or stripped.startswith("#"):
            comments.append(line)
            continue
        
        priority = categorize_phrase(stripped)
        
        if priority == 1:
            high_priority.append(stripped)
        elif priority == 2:
            medium_priority.append(stripped)
        elif priority == 3:
            low_priority.append(stripped)
        else:  # 999 = skip
            skipped.append(stripped)
    
    print(f"✅ Categorized:")
    print(f"   HIGH priority:   {len(high_priority)} phrases (rare/interesting)")
    print(f"   MEDIUM priority: {len(medium_priority)} phrases")
    print(f"   LOW priority:    {len(low_priority)} phrases")
    print(f"   SKIPPED:         {len(skipped)} phrases (too obvious/empty)")
    
    # Write prioritized file
    with open(OUTPUT_FILE, "w") as f:
        f.write("# ============================================================\n")
        f.write("# PRIORITIZED Brainwallet Phrases\n")
        f.write("# Order: HIGH → MEDIUM → LOW (skipped obvious ones)\n")
        f.write("# ============================================================\n\n")
        
        f.write("# --- HIGH PRIORITY: Rare/Specific/Long phrases ---\n")
        for p in sorted(high_priority):
            f.write(f"{p}\n")
        
        f.write("\n# --- MEDIUM PRIORITY: Moderate complexity ---\n")
        for p in sorted(medium_priority):
            f.write(f"{p}\n")
        
        f.write("\n# --- LOW PRIORITY: Simple/Short phrases ---\n")
        for p in sorted(low_priority):
            f.write(f"{p}\n")
        
        f.write("\n# --- SKIPPED (uncomment to scan): Standard passwords ---\n")
        for p in sorted(skipped):
            f.write(f"# {p}\n")
    
    print(f"\n💾 Saved to: {OUTPUT_FILE}")
    print(f"📊 Total active phrases: {len(high_priority) + len(medium_priority) + len(low_priority)}")
    print(f"⏭️  Skipped {len(skipped)} obvious phrases")

if __name__ == "__main__":
    main()
