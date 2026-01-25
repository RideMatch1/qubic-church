#!/usr/bin/env python3
"""
🔥 CFB ARTICLES MASTER ANALYSIS 🔥
====================================

Systematische Analyse aller 12 CFB Medium-Artikel für:
1. CFB numbers (27, 283, 47, 137, 121, 43, 19, 7, 14)
2. Formula patterns (625284 = 283 × 47² + 137)
3. Mathematical encoding
4. Hidden messages (wie Intelligence Test)
5. Genesis/Qubic connections
6. Reward hints
7. Trinary logic references
8. Paracosm concepts
9. Neural network patterns
10. Cross-article connections

USAGE:
    python3 analyze_cfb_articles.py
"""

import os
import re
import json
from collections import Counter, defaultdict
import hashlib

ARTICLES_DIR = "/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/analysis/cfb_articles/raw/"
OUTPUT_DIR = "/Users/lukashertle/Developer/projects/qubic-academic-docs/apps/web/analysis/cfb_articles/analyzed/"

CFB_NUMBERS = [27, 283, 47, 137, 121, 43, 19, 7, 14, 676, 625284]
FORMULA_COMPONENTS = [283, 47, 137, 2209, 625284]

EXPECTED_ARTICLES = [
    "01_neuronal_transistor",
    "02_amaaaaa",
    "03_main_goal_neural_network",
    "04_qubic_ai_unboxed",
    "05_ai_seeking_god",
    "06_brain_eating",
    "07_the_perspective",
    "08_paracosm_platform",
    "09_jinn_trinary_processor",
    "10_paracosm_manifesto",
    "11_decentralized_vs_distributed",
    "12_nihilator_manifests_self",
]

# Keywords to search
KEYWORDS = {
    'genesis': ['genesis', 'beginning', 'origin', 'start'],
    'qubic': ['qubic', 'quorum', 'quantum'],
    'bitcoin': ['bitcoin', 'btc', 'satoshi', 'blockchain', 'block'],
    'reward': ['reward', 'prize', 'bounty', 'claim'],
    'trinary': ['trinary', 'ternary', 'three', 'tri'],
    'anna': ['anna', 'grid', 'matrix', '128'],
    'computor': ['computor', 'compute', 'consensus', '676'],
    'cfb': ['come', 'beyond', 'sergey', 'ivancheglo'],
    'iota': ['iota', 'tangle'],
    'jinn': ['jinn', 'processor'],
    'paracosm': ['paracosm', 'universe', 'world'],
    'nihilator': ['nihilator', 'nihil', 'nothing'],
    'intelligence': ['intelligence', 'ai', 'agi', 'asi'],
    'pattern': ['pattern', 'structure', 'sequence'],
    'random': ['random', 'entropy', 'chaos'],
}

def check_completeness():
    """Check if all 12 articles are present"""
    print("="*80)
    print("📋 COMPLETENESS CHECK")
    print("="*80)
    print()

    if not os.path.exists(ARTICLES_DIR):
        print(f"❌ Directory not found: {ARTICLES_DIR}")
        print()
        print("Please create the directory and add articles!")
        return False

    files = os.listdir(ARTICLES_DIR)
    found_articles = [f for f in files if f.endswith(('.txt', '.md'))]

    print(f"Expected: {len(EXPECTED_ARTICLES)} articles")
    print(f"Found: {len(found_articles)} files")
    print()

    if len(found_articles) == 0:
        print("❌ NO ARTICLES FOUND!")
        print()
        print("Please add articles to:")
        print(f"  {ARTICLES_DIR}")
        return False

    # Check each expected article
    missing = []
    for expected in EXPECTED_ARTICLES:
        found = any(expected in f for f in found_articles)
        status = "✓" if found else "✗"
        print(f"  {status} {expected}")
        if not found:
            missing.append(expected)

    print()

    if missing:
        print(f"⚠️  Missing {len(missing)} articles:")
        for m in missing:
            print(f"    - {m}")
        print()
        return False
    else:
        print("✅ ALL ARTICLES PRESENT!")
        print()
        return True

def load_article(filepath):
    """Load article text"""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def extract_numbers(text):
    """Extract all numbers from text"""
    # Find all numbers (including decimals and commas)
    numbers = re.findall(r'\b\d+(?:,\d+)*(?:\.\d+)?\b', text)
    # Clean and convert
    cleaned = []
    for num in numbers:
        try:
            cleaned.append(int(num.replace(',', '')))
        except:
            pass
    return cleaned

def find_cfb_numbers(text):
    """Find CFB numbers in text"""
    findings = {}

    for cfb in CFB_NUMBERS:
        # As word boundary number
        pattern = rf'\b{cfb}\b'
        matches = re.findall(pattern, text)

        if matches:
            # Find contexts
            contexts = []
            for match in re.finditer(pattern, text):
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]
                contexts.append(context.strip())

            findings[cfb] = {
                'count': len(matches),
                'contexts': contexts[:5]  # First 5
            }

    return findings

def find_keywords(text):
    """Find all keywords in text"""
    findings = defaultdict(list)

    text_lower = text.lower()

    for category, keywords in KEYWORDS.items():
        for keyword in keywords:
            pattern = rf'\b{keyword}\w*\b'
            matches = re.findall(pattern, text_lower, re.IGNORECASE)

            if matches:
                findings[category].extend(matches)

    # Count unique occurrences
    result = {}
    for category, matches in findings.items():
        counter = Counter(matches)
        result[category] = {
            'total': len(matches),
            'unique': len(counter),
            'top': counter.most_common(5)
        }

    return result

def analyze_structure(text):
    """Analyze text structure"""
    lines = text.split('\n')

    # Count different elements
    headers = [l for l in lines if l.startswith('#')]
    quotes = [l for l in lines if l.startswith('>')]
    code_blocks = re.findall(r'```[\s\S]*?```', text)

    # Word stats
    words = text.split()
    sentences = re.split(r'[.!?]+', text)

    return {
        'total_chars': len(text),
        'total_lines': len(lines),
        'total_words': len(words),
        'total_sentences': len([s for s in sentences if s.strip()]),
        'headers': len(headers),
        'quotes': len(quotes),
        'code_blocks': len(code_blocks),
        'avg_words_per_sentence': len(words) / max(1, len([s for s in sentences if s.strip()])),
    }

def find_formulas(text):
    """Find mathematical formulas"""
    formulas = []

    # Pattern: number = expression
    pattern = r'(\d+(?:,\d+)*)\s*=\s*([^\n]+)'
    matches = re.findall(pattern, text)

    for match in matches:
        lhs = match[0].replace(',', '')
        rhs = match[1].strip()

        # Check if contains CFB numbers
        contains_cfb = any(str(cfb) in rhs for cfb in CFB_NUMBERS)

        formulas.append({
            'lhs': lhs,
            'rhs': rhs,
            'contains_cfb': contains_cfb
        })

    return formulas

def analyze_lists(text):
    """Analyze lists (like Owl, Pigeon example)"""
    # Find bulleted/numbered lists
    lists = []

    # Pattern: lines that start with bullet or number
    lines = text.split('\n')
    current_list = []

    for line in lines:
        stripped = line.strip()

        # Check if list item
        if stripped.startswith(('-', '*', '•')) or re.match(r'^\d+\.', stripped):
            item = re.sub(r'^[-*•\d\.]\s*', '', stripped)
            current_list.append(item)
        else:
            if current_list and len(current_list) >= 3:
                # Analyze this list
                lists.append(analyze_list_pattern(current_list))
            current_list = []

    return [l for l in lists if l]  # Filter empty

def analyze_list_pattern(items):
    """Analyze a single list for patterns"""
    # Extract first letters
    first_letters = [item[0].upper() for item in items if item]

    # Convert to numbers (A=1, B=2, ...)
    letter_values = [ord(c) - ord('A') + 1 for c in first_letters if c.isalpha()]

    return {
        'items': items[:10],  # First 10
        'count': len(items),
        'first_letters': ''.join(first_letters),
        'letter_sum': sum(letter_values),
        'letter_sum_mod_27': sum(letter_values) % 27 if letter_values else None,
        'letter_sum_mod_47': sum(letter_values) % 47 if letter_values else None,
    }

def analyze_article(filename, text):
    """Complete analysis of single article"""
    print(f"\n{'='*80}")
    print(f"📄 ANALYZING: {filename}")
    print(f"{'='*80}\n")

    analysis = {
        'filename': filename,
        'structure': analyze_structure(text),
        'cfb_numbers': find_cfb_numbers(text),
        'keywords': find_keywords(text),
        'formulas': find_formulas(text),
        'lists': analyze_lists(text),
        'all_numbers': Counter(extract_numbers(text)),
    }

    # Print summary
    print(f"📊 Structure:")
    print(f"  Words: {analysis['structure']['total_words']:,}")
    print(f"  Lines: {analysis['structure']['total_lines']:,}")
    print(f"  Sentences: {analysis['structure']['total_sentences']:,}")
    print()

    if analysis['cfb_numbers']:
        print(f"🔢 CFB Numbers Found:")
        for cfb, data in sorted(analysis['cfb_numbers'].items()):
            print(f"  {cfb}: {data['count']} times")
            if data['contexts']:
                print(f"    Context: ...{data['contexts'][0]}...")
        print()

    if analysis['formulas']:
        print(f"🧮 Formulas Found: {len(analysis['formulas'])}")
        for formula in analysis['formulas'][:3]:
            print(f"  {formula['lhs']} = {formula['rhs'][:50]}...")
        print()

    if analysis['lists']:
        print(f"📋 Lists Found: {len(analysis['lists'])}")
        for lst in analysis['lists'][:2]:
            print(f"  {lst['count']} items, letters: {lst['first_letters']}, sum: {lst['letter_sum']}")
        print()

    # Top keywords
    if analysis['keywords']:
        print(f"🔍 Top Keyword Categories:")
        for cat, data in sorted(analysis['keywords'].items(), key=lambda x: x[1]['total'], reverse=True)[:5]:
            print(f"  {cat}: {data['total']} occurrences")
        print()

    return analysis

def cross_reference_analysis(all_analyses):
    """Find connections between articles"""
    print(f"\n{'='*80}")
    print(f"🔗 CROSS-REFERENCE ANALYSIS")
    print(f"{'='*80}\n")

    # Which articles mention CFB numbers most?
    cfb_counts = {}
    for analysis in all_analyses:
        total = sum(data['count'] for data in analysis['cfb_numbers'].values())
        cfb_counts[analysis['filename']] = total

    print("Articles by CFB number mentions:")
    for filename, count in sorted(cfb_counts.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  {filename}: {count} mentions")
    print()

    # Which keywords appear across multiple articles?
    keyword_articles = defaultdict(set)
    for analysis in all_analyses:
        for category in analysis['keywords']:
            keyword_articles[category].add(analysis['filename'])

    print("Keywords appearing in multiple articles:")
    for category, articles in sorted(keyword_articles.items(), key=lambda x: len(x[1]), reverse=True):
        if len(articles) >= 3:
            print(f"  {category}: {len(articles)} articles")
    print()

def generate_master_index(all_analyses):
    """Generate master index document"""
    print(f"\n{'='*80}")
    print(f"📚 GENERATING MASTER INDEX")
    print(f"{'='*80}\n")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Save detailed JSON
    json_path = os.path.join(OUTPUT_DIR, "master_analysis.json")
    with open(json_path, 'w') as f:
        json.dump(all_analyses, f, indent=2, default=str)

    print(f"✓ Saved detailed analysis: {json_path}")

    # Create markdown summary
    md_path = os.path.join(OUTPUT_DIR, "MASTER_INDEX.md")

    with open(md_path, 'w') as f:
        f.write("# 🔥 CFB ARTICLES - MASTER INDEX 🔥\n\n")
        f.write(f"**Total Articles Analyzed**: {len(all_analyses)}\n\n")
        f.write("---\n\n")

        for analysis in all_analyses:
            f.write(f"## {analysis['filename']}\n\n")
            f.write(f"**Words**: {analysis['structure']['total_words']:,}\n")
            f.write(f"**Lines**: {analysis['structure']['total_lines']:,}\n\n")

            if analysis['cfb_numbers']:
                f.write("**CFB Numbers**:\n")
                for cfb, data in sorted(analysis['cfb_numbers'].items()):
                    f.write(f"- {cfb}: {data['count']} mentions\n")
                f.write("\n")

            if analysis['keywords']:
                f.write("**Top Keywords**:\n")
                for cat, data in sorted(analysis['keywords'].items(), key=lambda x: x[1]['total'], reverse=True)[:5]:
                    f.write(f"- {cat}: {data['total']} times\n")
                f.write("\n")

            f.write("---\n\n")

    print(f"✓ Saved master index: {md_path}")
    print()

def main():
    print("\n" + "="*80)
    print("🔥 CFB ARTICLES MASTER ANALYSIS 🔥")
    print("="*80)
    print()

    # Check completeness
    if not check_completeness():
        print("❌ Cannot proceed without all articles!")
        print()
        print("📖 See: analysis/cfb_articles/ARTIKEL_BESCHAFFUNG_ANLEITUNG.md")
        return

    # Load and analyze all articles
    all_analyses = []

    for filename in sorted(os.listdir(ARTICLES_DIR)):
        if not filename.endswith(('.txt', '.md')):
            continue

        filepath = os.path.join(ARTICLES_DIR, filename)
        text = load_article(filepath)

        analysis = analyze_article(filename, text)
        all_analyses.append(analysis)

    # Cross-reference
    cross_reference_analysis(all_analyses)

    # Generate master index
    generate_master_index(all_analyses)

    print("="*80)
    print("✅ ANALYSIS COMPLETE!")
    print("="*80)
    print()
    print("📊 Results saved to:")
    print(f"  {OUTPUT_DIR}")
    print()

if __name__ == "__main__":
    main()
