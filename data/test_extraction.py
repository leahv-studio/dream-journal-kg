"""
Test extraction with the Grand Am dream.

Simulates a short journal conversation, calls Claude, and prints the
structured output. Does NOT write to graph.json — read-only test.

Run from project root:
    python data/test_extraction.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from extract import extract_dream

# Simulated conversation — mirrors the canonical Grand Am narrative
GRAND_AM_CONVERSATION = [
    {
        "role": "user",
        "content": (
            "I was driving the Grand Am from high school — the white one with the "
            "cracked dashboard. I needed to get somewhere important but I couldn't "
            "figure out where I parked, and when I finally found the car the GPS "
            "wouldn't load. I kept circling the same parking structure. I knew I "
            "was late. I never arrived."
        ),
    },
    {
        "role": "assistant",
        "content": (
            "That sounds disorienting. Were there other people in the car or in the "
            "parking structure, or were you alone?"
        ),
    },
    {
        "role": "user",
        "content": (
            "Alone, mostly. There was a woman standing near the entrance watching me "
            "circle but she wasn't helping or saying anything. The car felt cramped "
            "and kind of airless, the way it always did."
        ),
    },
    {
        "role": "assistant",
        "content": "What were you feeling as you kept circling — was there a specific moment the emotion shifted?",
    },
    {
        "role": "user",
        "content": (
            "Anxiety the whole time. And this heavy dread — like whatever I was late "
            "for was critically important and I'd already missed it. It wasn't just "
            "being late, it felt like I'd failed at something permanent."
        ),
    },
    {
        "role": "assistant",
        "content": "Did the parking structure feel like a real place, or was it distorted in some way?",
    },
    {
        "role": "user",
        "content": (
            "Distorted. It kept going — more levels than made sense. I'd think I'd "
            "found the exit and then there was another ramp. Normal structure but "
            "wrong in a way I couldn't name."
        ),
    },
]

if __name__ == "__main__":
    print("Running extraction on Grand Am dream...")
    print("(This makes a live Claude API call)\n")

    result = extract_dream(GRAND_AM_CONVERSATION, "2025-03-15")

    print("=" * 60)
    print("EXTRACTION RESULT")
    print("=" * 60)
    print(json.dumps(result, indent=2))
    print("=" * 60)

    # Quick sanity checks
    d = result.get("dream", {})
    assert d.get("raw_narrative"), "FAIL: raw_narrative is empty"
    assert d.get("emotional_valence") in ("negative", "mixed", "positive", None), "FAIL: invalid valence"
    assert "is_recurring" not in d, "FAIL: is_recurring must not be in extraction output"
    assert "is_novel" not in d, "FAIL: is_novel must not be in extraction output"
    for t in result.get("themes", []):
        assert "source" not in t, "FAIL: source field must not appear in extracted themes"
    print("\nAll checks passed.")
