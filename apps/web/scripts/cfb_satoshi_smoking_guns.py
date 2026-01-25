#!/usr/bin/env python3
"""
🔥 CFB = SATOSHI SMOKING GUNS 🔥
Using CFB's OWN methodology from 2026-01-08

CFB said:
1. "style match = same person behind"
2. "feed texts into chatgpt to verify"
3. "omitting second comma in sentences having A, B, C. structure"

Let's find CONCRETE EXAMPLES.
"""

import json
import re
from pathlib import Path

# Paths
SATOSHI_POSTS = Path("/Users/lukashertle/Developer/projects/qubic-mystery-lab/outputs/bitcointalk_posts/satoshi/posts_with_content.jsonl")
CFB_POSTS = Path("/Users/lukashertle/Developer/projects/qubic-mystery-lab/outputs/bitcointalk_posts/cfb/posts.jsonl")

def load_posts(filepath):
    """Load JSONL posts"""
    posts = []
    if not filepath.exists():
        return posts

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                posts.append(json.loads(line))
            except:
                continue
    return posts

def find_comma_patterns(text):
    """
    Find CFB's specific pattern: "A, B C" (missing second comma)
    Looking for sentences like: "Bitcoin, Qubic and Ethereum" (should be "Bitcoin, Qubic, and Ethereum")
    """
    patterns = []

    # Pattern 1: word, word and word (missing Oxford comma)
    pattern1 = r'\b(\w+),\s+(\w+)\s+(and|or)\s+(\w+)\b'
    for match in re.finditer(pattern1, text, re.IGNORECASE):
        full = match.group(0)
        context_start = max(0, match.start() - 70)
        context_end = min(len(text), match.end() + 70)
        context = text[context_start:context_end]

        patterns.append({
            'type': 'missing_oxford_comma',
            'pattern': full,
            'context': context.strip()
        })

    # Pattern 2: A, B C. (list with missing comma before last item)
    pattern2 = r'\b([A-Z][a-z]+),\s+([a-z]+)\s+([a-z]+)\.'
    for match in re.finditer(pattern2, text):
        full = match.group(0)
        context_start = max(0, match.start() - 70)
        context_end = min(len(text), match.end() + 70)
        context = text[context_start:context_end]

        patterns.append({
            'type': 'list_missing_comma',
            'pattern': full,
            'context': context.strip()
        })

    return patterns

def find_ellipsis_usage(text):
    """Find ... usage patterns"""
    patterns = []
    for match in re.finditer(r'\.\.\.+', text):
        context_start = max(0, match.start() - 50)
        context_end = min(len(text), match.end() + 50)
        context = text[context_start:context_end]
        patterns.append(context.strip())
    return patterns

def find_sentence_fragments(text):
    """Find short sentence patterns: Short. Sentences. Like. This."""
    # Look for 3+ consecutive short sentences (< 8 words)
    sentences = re.split(r'[.!?]+', text)
    fragments = []

    for i in range(len(sentences) - 2):
        s1 = sentences[i].strip()
        s2 = sentences[i+1].strip()
        s3 = sentences[i+2].strip()

        if s1 and s2 and s3:
            w1 = len(s1.split())
            w2 = len(s2.split())
            w3 = len(s3.split())

            if w1 <= 8 and w2 <= 8 and w3 <= 8:
                fragment = f"{s1}. {s2}. {s3}."
                if len(fragment) < 200:
                    fragments.append(fragment)

    return fragments

def find_question_answer(text):
    """Find Q? A. patterns"""
    patterns = []
    # Pattern: Question? Answer...
    pattern = r'([^.?!]{10,120}\?)\s+([A-Z][^.?!]{10,120}[.!])'
    for match in re.finditer(pattern, text):
        patterns.append({
            'question': match.group(1).strip(),
            'answer': match.group(2).strip()
        })
    return patterns

def analyze_author(posts, author_name):
    """Analyze all posts from an author"""
    print(f"\n{'='*80}")
    print(f"📊 ANALYZING: {author_name}")
    print(f"{'='*80}\n")

    total_text = ""
    post_count = 0

    for post in posts:
        content = post.get('content', '') or post.get('post_content', '')
        if content:
            total_text += content + "\n"
            post_count += 1

    print(f"Posts analyzed: {post_count}")
    print(f"Total characters: {len(total_text):,}")
    print()

    # Find patterns
    print("🔍 PATTERN 1: Missing Comma (CFB's specific test)")
    comma_patterns = find_comma_patterns(total_text)
    print(f"Found: {len(comma_patterns)} instances\n")

    for i, p in enumerate(comma_patterns[:5], 1):
        print(f"  {i}. TYPE: {p['type']}")
        print(f"     PATTERN: {p['pattern']}")
        print(f"     CONTEXT: ...{p['context']}...")
        print()

    print("\n🔍 PATTERN 2: Ellipsis Usage (...)")
    ellipsis = find_ellipsis_usage(total_text)
    print(f"Found: {len(ellipsis)} instances\n")

    for i, e in enumerate(ellipsis[:3], 1):
        print(f"  {i}. ...{e}...")
        print()

    print("\n🔍 PATTERN 3: Sentence Fragments (Short. Punchy. Style.)")
    fragments = find_sentence_fragments(total_text)
    print(f"Found: {len(fragments)} instances\n")

    for i, f in enumerate(fragments[:3], 1):
        print(f"  {i}. {f}")
        print()

    print("\n🔍 PATTERN 4: Question-Answer Structure")
    qa = find_question_answer(total_text)
    print(f"Found: {len(qa)} instances\n")

    for i, q in enumerate(qa[:3], 1):
        print(f"  {i}. Q: {q['question']}")
        print(f"     A: {q['answer']}")
        print()

    return {
        'author': author_name,
        'post_count': post_count,
        'comma_patterns': len(comma_patterns),
        'ellipsis': len(ellipsis),
        'fragments': len(fragments),
        'qa_patterns': len(qa),
        'char_count': len(total_text)
    }

def compare_results(satoshi_stats, cfb_stats):
    """Compare statistics"""
    print(f"\n{'='*80}")
    print("🔥 SIDE-BY-SIDE COMPARISON")
    print(f"{'='*80}\n")

    # Normalize per 10k characters
    def norm(count, chars):
        return (count / chars * 10000) if chars > 0 else 0

    metrics = [
        ('Missing Comma Patterns', 'comma_patterns'),
        ('Ellipsis Usage', 'ellipsis'),
        ('Sentence Fragments', 'fragments'),
        ('Question-Answer', 'qa_patterns')
    ]

    print(f"{'Metric':<30} {'Satoshi':<20} {'CFB':<20} {'Match'}")
    print("-" * 80)

    for name, key in metrics:
        s_count = satoshi_stats[key]
        c_count = cfb_stats[key]

        s_norm = norm(s_count, satoshi_stats['char_count'])
        c_norm = norm(c_count, cfb_stats['char_count'])

        # Calculate similarity
        if s_norm + c_norm > 0:
            similarity = 100 - abs(s_norm - c_norm) / max(s_norm, c_norm) * 100
        else:
            similarity = 0

        match_icon = "✅" if similarity > 70 else "⚠️" if similarity > 50 else "❌"

        print(f"{name:<30} {s_norm:>6.2f}/10k         {c_norm:>6.2f}/10k         {match_icon} {similarity:.0f}%")

    print("\n" + "="*80)
    print("📝 INTERPRETATION")
    print("="*80)
    print()
    print("By CFB's OWN standard from 2026-01-08:")
    print('  "For me: style match = same person behind"')
    print()
    print("If patterns match at >70% similarity → SAME AUTHOR")
    print()

if __name__ == '__main__':
    print("🔥"*40)
    print("CFB = SATOSHI SMOKING GUNS")
    print("Using CFB's Own Methodology (2026-01-08)")
    print("🔥"*40)

    # Load posts
    print("\n📂 Loading data...")
    satoshi_posts = load_posts(SATOSHI_POSTS)
    cfb_posts = load_posts(CFB_POSTS)

    print(f"Satoshi posts: {len(satoshi_posts)}")
    print(f"CFB posts: {len(cfb_posts)}")

    # Analyze
    satoshi_stats = analyze_author(satoshi_posts, "SATOSHI NAKAMOTO")
    cfb_stats = analyze_author(cfb_posts, "COME-FROM-BEYOND (CFB)")

    # Compare
    compare_results(satoshi_stats, cfb_stats)

    print("\n" + "🔥"*40)
    print("✅ ANALYSIS COMPLETE")
    print("🔥"*40)
    print()
    print("CONCLUSION:")
    print("By CFB's own standard ('style match = same person'), if patterns")
    print("match at >70%, we can conclude: CFB = Satoshi")
    print()
