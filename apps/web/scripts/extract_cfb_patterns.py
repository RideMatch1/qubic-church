#!/usr/bin/env python3
"""
Extract CFB Discord messages showing the SAME patterns as Satoshi
"""

import json
import re

DISCORD_FILE = "/Users/lukashertle/Developer/projects/qubic-mystery-lab/outputs/cfb_discord_direct/cfb_all_messages.jsonl"

def load_discord_messages():
    """Load CFB Discord messages"""
    messages = []
    with open(DISCORD_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                msg = json.loads(line)
                content = msg.get('content', '')
                if content and len(content) > 20:  # Skip very short messages
                    messages.append({
                        'content': content,
                        'timestamp': msg.get('timestamp', ''),
                        'channel': msg.get('channel_name', '')
                    })
            except:
                continue
    return messages

def find_missing_oxford_commas(messages):
    """Find 'A, B and C' patterns (missing Oxford comma)"""
    pattern = r'\b(\w+),\s+(\w+)\s+(and|or)\s+(\w+)\b'
    results = []

    for msg in messages:
        matches = list(re.finditer(pattern, msg['content'], re.IGNORECASE))
        for match in matches:
            results.append({
                'pattern': match.group(0),
                'full_message': msg['content'],
                'timestamp': msg['timestamp'],
                'channel': msg['channel']
            })

    return results

def find_ellipsis(messages):
    """Find ... usage"""
    results = []
    for msg in messages:
        if '...' in msg['content']:
            results.append({
                'message': msg['content'],
                'timestamp': msg['timestamp'],
                'channel': msg['channel']
            })
    return results

def find_short_sentences(messages):
    """Find staccato style: Short. Sentences. Pattern."""
    results = []
    for msg in messages:
        sentences = re.split(r'[.!?]+', msg['content'])
        short_count = sum(1 for s in sentences if 0 < len(s.split()) <= 5)

        # If 3+ short sentences in one message
        if short_count >= 3 and len(msg['content']) < 200:
            results.append({
                'message': msg['content'],
                'timestamp': msg['timestamp'],
                'channel': msg['channel'],
                'short_count': short_count
            })

    return results

def find_question_answer(messages):
    """Find Q? A. patterns"""
    results = []
    for msg in messages:
        if '?' in msg['content']:
            # Check if message has question followed by statement
            parts = msg['content'].split('?')
            if len(parts) >= 2 and len(parts[1].strip()) > 10:
                results.append({
                    'message': msg['content'],
                    'timestamp': msg['timestamp'],
                    'channel': msg['channel']
                })

    return results

def main():
    print("🔍 Extracting CFB patterns from Discord messages...")
    print()

    messages = load_discord_messages()
    print(f"Loaded {len(messages)} messages\n")

    # Pattern 1: Missing Oxford Commas
    print("="*80)
    print("PATTERN 1: Missing Oxford Comma (A, B and C)")
    print("="*80)
    oxford = find_missing_oxford_commas(messages)
    print(f"Found: {len(oxford)} instances\n")

    for i, ex in enumerate(oxford[:10], 1):
        print(f"{i}. PATTERN: {ex['pattern']}")
        print(f"   MESSAGE: {ex['full_message'][:150]}...")
        print(f"   DATE: {ex['timestamp'][:10]}")
        print()

    # Pattern 2: Ellipsis
    print("\n" + "="*80)
    print("PATTERN 2: Ellipsis Usage (...)")
    print("="*80)
    ellipsis = find_ellipsis(messages)
    print(f"Found: {len(ellipsis)} instances\n")

    for i, ex in enumerate(ellipsis[:10], 1):
        print(f"{i}. {ex['message'][:150]}...")
        print(f"   DATE: {ex['timestamp'][:10]}")
        print()

    # Pattern 3: Short sentences
    print("\n" + "="*80)
    print("PATTERN 3: Short Sentence Fragments")
    print("="*80)
    short = find_short_sentences(messages)
    print(f"Found: {len(short)} instances\n")

    for i, ex in enumerate(short[:10], 1):
        print(f"{i}. {ex['message']}")
        print(f"   DATE: {ex['timestamp'][:10]}")
        print()

    # Pattern 4: Question-Answer
    print("\n" + "="*80)
    print("PATTERN 4: Question-Answer Structure")
    print("="*80)
    qa = find_question_answer(messages)
    print(f"Found: {len(qa)} instances\n")

    for i, ex in enumerate(qa[:10], 1):
        print(f"{i}. {ex['message'][:200]}...")
        print(f"   DATE: {ex['timestamp'][:10]}")
        print()

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Missing Oxford Commas: {len(oxford)}")
    print(f"Ellipsis Usage: {len(ellipsis)}")
    print(f"Short Sentences: {len(short)}")
    print(f"Question-Answer: {len(qa)}")
    print()

if __name__ == '__main__':
    main()
