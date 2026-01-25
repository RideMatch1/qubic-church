#!/usr/bin/env python3
"""
Find CFB = Satoshi patterns using CFB's OWN methodology from 2026-01-08:
1. Comma patterns: "A, B C" (missing second comma)
2. Ellipsis usage: "..." frequency
3. Sentence fragments
4. Question-answer structure
"""

import re
import json
from collections import Counter

# CFB's own patterns to look for
PATTERNS = {
    'missing_comma': r'\b([A-Z][a-z]+),\s+([a-z]+)\s+([a-z]+)\b',  # A, B C
    'ellipsis': r'\.\.\.+',  # ... usage
    'sentence_fragment': r'\.\s+[A-Z][^.]{10,40}\.\s+[A-Z]',  # Short. Sentences. Pattern.
    'question_answer': r'\?\s*[A-Z][^?]+\b(Because|Answer|Yes|No)\b',  # Q? Answer...
    'inline_math': r'\b\w+\s*=\s*\w+\s*[\+\-\*/]\s*\w+',  # x = y + z
}

def analyze_text(text, label="Text"):
    """Analyze text for CFB's signature patterns"""
    results = {
        'label': label,
        'patterns': {},
        'examples': {}
    }

    for pattern_name, pattern_regex in PATTERNS.items():
        matches = list(re.finditer(pattern_regex, text, re.MULTILINE))
        results['patterns'][pattern_name] = len(matches)

        # Get first 3 examples with context
        examples = []
        for match in matches[:3]:
            start = max(0, match.start() - 60)
            end = min(len(text), match.end() + 60)
            context = text[start:end].replace('\n', ' ').strip()
            examples.append(context)

        results['examples'][pattern_name] = examples

    # Additional stats
    results['word_count'] = len(text.split())
    results['avg_sentence_length'] = len(text.split()) / max(1, text.count('.'))
    results['questions'] = text.count('?')
    results['exclamations'] = text.count('!')

    return results

def compare_patterns(results1, results2):
    """Compare two analysis results"""
    print(f"\n{'='*80}")
    print(f"COMPARISON: {results1['label']} vs {results2['label']}")
    print(f"{'='*80}\n")

    print(f"📊 PATTERN FREQUENCIES:\n")

    for pattern_name in PATTERNS.keys():
        count1 = results1['patterns'][pattern_name]
        count2 = results2['patterns'][pattern_name]

        # Normalize by word count
        norm1 = count1 / max(1, results1['word_count'] / 1000)
        norm2 = count2 / max(1, results2['word_count'] / 1000)

        similarity = 100 - abs(norm1 - norm2) / max(norm1, norm2, 1) * 100 if max(norm1, norm2) > 0 else 0

        print(f"  {pattern_name}:")
        print(f"    {results1['label']}: {count1} ({norm1:.2f} per 1k words)")
        print(f"    {results2['label']}: {count2} ({norm2:.2f} per 1k words)")
        print(f"    Similarity: {similarity:.1f}%")
        print()

def show_examples(results, pattern_name):
    """Show example matches for a pattern"""
    examples = results['examples'].get(pattern_name, [])
    if not examples:
        return

    print(f"\n{'='*80}")
    print(f"EXAMPLES: {pattern_name} in {results['label']}")
    print(f"{'='*80}\n")

    for i, example in enumerate(examples, 1):
        print(f"{i}. ...{example}...")
        print()

# Test texts (we'll load real ones from files)
CFB_SAMPLE = """
I'm saying with high chance it was same person who wrote content of Valis blog and Amadues site
Why I paid attention? I collected Spelunker text style stats when was looking for his other accounts on the Internet.
Complex sentences on both sites have the same mistake: omitting second comma in sentences having A, B, C. structure. The both write it as A, B C.
For me: style match = same person behind. and that's spelunker
"""

SATOSHI_SAMPLE = """
The Times 03/Jan/2009 Chancellor on brink of second bailout for banks.
A purely peer-to-peer version of electronic cash would allow online payments to be sent directly from one party to another without going through a financial institution.
The proof-of-work involves scanning for a value that when hashed, such as with SHA-256, the hash begins with a number of zero bits.
We define an electronic coin as a chain of digital signatures. Each owner transfers the coin to the next by digitally signing a hash of the previous transaction and the public key of the next owner.
"""

if __name__ == '__main__':
    print("🔍 CFB = SATOSHI PATTERN ANALYSIS")
    print("Using CFB's own methodology from 2026-01-08\n")

    # Analyze samples
    cfb_results = analyze_text(CFB_SAMPLE, "CFB (Discord 2026)")
    satoshi_results = analyze_text(SATOSHI_SAMPLE, "Satoshi (2009)")

    # Compare
    compare_patterns(cfb_results, satoshi_results)

    # Show examples
    for pattern in ['missing_comma', 'ellipsis', 'inline_math']:
        show_examples(cfb_results, pattern)
        show_examples(satoshi_results, pattern)

    print("\n" + "="*80)
    print("✅ Analysis complete! Run with real file paths for full comparison.")
    print("="*80)
