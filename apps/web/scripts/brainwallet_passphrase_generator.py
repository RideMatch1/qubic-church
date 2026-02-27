"""
Brainwallet Passphrase Generator - Academic Security Research

Demonstrates why brainwallets based on memorable phrases are insecure:
Attackers apply systematic mutations to known quotes, phrases, and common
strings to generate candidate passphrases at scale.

This module implements the mutation strategies documented in:
  - Castellucci, R. (2013). "Cracking Cryptocurrency Brainwallets"
  - Vasek, M. et al. (2016). "The Bitcoin Brain Drain"

Usage:
  python brainwallet_passphrase_generator.py

  Or import as module:
    from brainwallet_passphrase_generator import generate_mutations
    for variant in generate_mutations("To be or not to be"):
        print(variant)
"""

from __future__ import annotations

import itertools
import re
from typing import Iterator


# --- Mutation strategies ---
# Each strategy represents a known attack vector against passphrase-based keys.

# Common substitutions attackers try (leet-speak and keyboard patterns)
LEET_MAP: dict[str, list[str]] = {
    "a": ["@", "4"],
    "e": ["3"],
    "i": ["1", "!"],
    "o": ["0"],
    "s": ["$", "5"],
    "t": ["7"],
    "l": ["1"],
}

# Suffixes commonly appended by users trying to "strengthen" passphrases
COMMON_SUFFIXES = [
    "",  # original
    "1", "12", "123", "1234",
    "!", "!!", "!!!", "?",
    ".", "..", "...",
    "#", "$", "*",
    "2024", "2025", "2026",
    "btc", "BTC", "bitcoin", "Bitcoin",
]

# Prefixes sometimes prepended
COMMON_PREFIXES = [
    "",  # original
    "the ", "The ",
    "my ", "My ",
]


def _normalize_whitespace(phrase: str) -> Iterator[str]:
    """
    Strategy: Whitespace normalization.

    Users may store passphrases with inconsistent spacing.
    Attackers try all common whitespace variants.
    """
    stripped = phrase.strip()
    yield stripped

    # No spaces at all
    no_spaces = stripped.replace(" ", "")
    if no_spaces != stripped:
        yield no_spaces

    # Single spaces (normalize multiple spaces)
    single_spaced = re.sub(r"\s+", " ", stripped)
    if single_spaced != stripped:
        yield single_spaced

    # Underscores instead of spaces
    yield stripped.replace(" ", "_")

    # Hyphens instead of spaces
    yield stripped.replace(" ", "-")


def _case_variants(phrase: str) -> Iterator[str]:
    """
    Strategy: Case manipulation.

    Users apply predictable casing patterns.
    """
    yield phrase
    yield phrase.lower()
    yield phrase.upper()
    yield phrase.capitalize()
    yield phrase.title()
    # First letter lowercase, rest unchanged
    if len(phrase) > 0:
        yield phrase[0].lower() + phrase[1:]


def _suffix_variants(phrase: str) -> Iterator[str]:
    """
    Strategy: Common suffix appending.

    Users often append numbers or symbols thinking it adds security.
    """
    for suffix in COMMON_SUFFIXES:
        yield phrase + suffix


def _prefix_variants(phrase: str) -> Iterator[str]:
    """
    Strategy: Common prefix prepending.
    """
    for prefix in COMMON_PREFIXES:
        yield prefix + phrase


def _punctuation_variants(phrase: str) -> Iterator[str]:
    """
    Strategy: Punctuation removal/modification.

    Quotes often include punctuation that users may or may not include.
    """
    yield phrase

    # Remove all punctuation
    no_punct = re.sub(r"[^\w\s]", "", phrase)
    if no_punct != phrase:
        yield no_punct

    # Remove only trailing punctuation
    stripped = phrase.rstrip(".,!?;:'\"")
    if stripped != phrase:
        yield stripped


def _leet_speak(phrase: str) -> Iterator[str]:
    """
    Strategy: Leet-speak substitutions.

    Basic character substitutions that users often apply.
    Only single-character substitutions to keep the search space manageable.
    """
    lower = phrase.lower()
    yield lower  # base for leet

    # Apply each leet substitution individually
    for char, replacements in LEET_MAP.items():
        if char in lower:
            for replacement in replacements:
                yield lower.replace(char, replacement)


def generate_mutations(phrase: str) -> list[str]:
    """
    Generate all passphrase mutations for a given input phrase.

    Applies multiple mutation strategies and deduplicates results.
    Returns a deterministic list of unique candidate passphrases.
    """
    candidates: set[str] = set()

    # Layer 1: Whitespace normalization
    for ws_variant in _normalize_whitespace(phrase):
        # Layer 2: Case variants
        for case_variant in _case_variants(ws_variant):
            # Layer 3: Punctuation variants
            for punct_variant in _punctuation_variants(case_variant):
                candidates.add(punct_variant)

                # Layer 4: Suffixes (only on base forms to limit explosion)
                for suffix_variant in _suffix_variants(punct_variant):
                    candidates.add(suffix_variant)

    # Layer 5: Leet-speak (applied to original phrase only, to limit size)
    for leet_variant in _leet_speak(phrase):
        candidates.add(leet_variant)

    # Layer 6: Prefix variants (on original and lowercase)
    for prefix_variant in _prefix_variants(phrase):
        candidates.add(prefix_variant)
    for prefix_variant in _prefix_variants(phrase.lower()):
        candidates.add(prefix_variant)

    # Sort for deterministic output
    return sorted(candidates)


# --- Demo ---

EXAMPLE_QUOTES = [
    "To be or not to be",
    "I think therefore I am",
    "Let there be light",
    "In the beginning",
    "Knowledge is power",
]


def main() -> None:
    print("=" * 64)
    print("Brainwallet Passphrase Mutation Generator")
    print("Academic Security Research Tool")
    print("=" * 64)

    for quote in EXAMPLE_QUOTES:
        mutations = generate_mutations(quote)
        print(f"\nSource: \"{quote}\"")
        print(f"  Mutations generated: {len(mutations)}")
        print(f"  Sample variants:")
        # Show first 10 as examples
        for i, variant in enumerate(mutations[:10]):
            print(f"    [{i+1:>2}] \"{variant}\"")
        if len(mutations) > 10:
            print(f"    ... and {len(mutations) - 10} more")

    # Summary statistics
    print("\n" + "=" * 64)
    print("Summary:")
    print(f"  Quotes processed:    {len(EXAMPLE_QUOTES)}")
    total = sum(len(generate_mutations(q)) for q in EXAMPLE_QUOTES)
    print(f"  Total passphrases:   {total}")
    avg = total / len(EXAMPLE_QUOTES)
    print(f"  Average per quote:   {avg:.0f}")
    print("=" * 64)
    print()
    print("This demonstrates why memorable phrases are weak keys:")
    print("A small set of quotes expands into hundreds of candidates,")
    print("each derivable and testable in microseconds via SHA-256.")


if __name__ == "__main__":
    main()
