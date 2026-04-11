"""
extract.py — Claude-powered extraction and graph writing.

Two public functions:
  extract_dream(conversation_history, date) -> dict
      Sends the conversation to Claude and returns structured JSON.

  write_to_graph(extracted, dg, date) -> str
      Writes the extracted nodes and edges to the DreamGraph.
      Returns the new dream node ID.
"""

import json
import os
import re

import anthropic
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

from graph import DreamGraph
from prompts import EXTRACTION_SYSTEM_PROMPT

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from environment


# ── Helpers ──────────────────────────────────────────────────────────────────

def _slug(text: str) -> str:
    """Turn a display name into a lowercase underscore-separated ID fragment."""
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def _find_node_by_name(dg: DreamGraph, node_type: str, name: str) -> str | None:
    """Return an existing node ID if a node of that type with that name exists."""
    for node_id, attrs in dg.G.nodes(data=True):
        if attrs.get("node_type") == node_type:
            if attrs.get("name", "").lower() == name.lower():
                return node_id
    return None


def _unique_id(dg: DreamGraph, base: str) -> str:
    """Return base if unused; otherwise return base_2, base_3, etc."""
    if base not in dg.G:
        return base
    i = 2
    while f"{base}_{i}" in dg.G:
        i += 1
    return f"{base}_{i}"


def _find_active_context_window(dg: DreamGraph, date: str) -> str | None:
    """Return the LifeContextWindow whose date range covers the given date."""
    for node_id, attrs in dg.G.nodes(data=True):
        if attrs.get("node_type") != "LifeContextWindow":
            continue
        start = attrs.get("start_date", "")
        end = attrs.get("end_date")  # None means still active
        if start <= date and (end is None or date <= end):
            return node_id
    return None


# ── Extraction ────────────────────────────────────────────────────────────────

def extract_dream(conversation_history: list[dict], date: str) -> dict:
    """
    Send the full conversation to Claude for structured extraction.

    conversation_history: list of {"role": "user"|"assistant", "content": "..."}
    date: ISO date string YYYY-MM-DD for this dream entry

    Returns the parsed extraction dict.
    """
    transcript = "\n".join(
        f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
        for m in conversation_history
    )

    user_message = (
        f"<conversation>\n{transcript}\n</conversation>\n\n"
        f"Date of dream: {date}\n\n"
        "Extract the structured data from this dream journal conversation."
    )

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=EXTRACTION_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw = response.content[0].text.strip()

    # Strip markdown code fences if Claude wrapped the output
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    return json.loads(raw)


# ── Graph writing ─────────────────────────────────────────────────────────────

def write_to_graph(extracted: dict, dg: DreamGraph, date: str) -> str:
    """
    Write extracted nodes and edges to the graph.
    Deduplicates Characters, Symbols, Settings, Emotions, and Themes by name.
    Returns the new dream node ID.
    """

    # ── Dream ─────────────────────────────────────────────────────────────────
    dream_id = _unique_id(dg, f"dream_{_slug(date)}")
    d = extracted["dream"]
    dg.add_dream(
        dream_id,
        date=date,
        raw_narrative=d.get("raw_narrative"),
        emotional_valence=d.get("emotional_valence"),
        intensity=d.get("intensity"),
        visual_quality=d.get("visual_quality"),
        notable_color=d.get("notable_color"),
        lucid=d.get("lucid"),
        title=d.get("title"),
    )

    # ── Characters ────────────────────────────────────────────────────────────
    for c in extracted.get("characters", []):
        char_id = _find_node_by_name(dg, "Character", c["name"])
        if char_id is None:
            char_id = _unique_id(dg, f"char_{_slug(c['name'])}")
            dg.add_character(
                char_id,
                name=c["name"],
                character_type=c.get("character_type"),
                symbolic_role=c.get("symbolic_role"),
            )
        dg.add_features(dream_id, char_id, role=c.get("role_in_dream"))

    # ── Symbols ───────────────────────────────────────────────────────────────
    for s in extracted.get("symbols", []):
        sym_id = _find_node_by_name(dg, "Symbol", s["name"])
        if sym_id is None:
            sym_id = _unique_id(dg, f"sym_{_slug(s['name'])}")
            dg.add_symbol(
                sym_id,
                name=s["name"],
                category=s.get("category"),
                symbolic_note=s.get("symbolic_note"),
            )
        dg.add_contains(dream_id, sym_id, prominence=s.get("prominence"))

    # ── Settings ──────────────────────────────────────────────────────────────
    for st in extracted.get("settings", []):
        set_id = _find_node_by_name(dg, "Setting", st["name"])
        if set_id is None:
            set_id = _unique_id(dg, f"set_{_slug(st['name'])}")
            dg.add_setting(
                set_id,
                name=st["name"],
                familiarity=st.get("familiarity"),
                real_or_constructed=st.get("real_or_constructed"),
                symbolic_note=st.get("symbolic_note"),
            )
        dg.add_takes_place_in(dream_id, set_id, distortion_level=st.get("distortion_level"))

    # ── Emotions ──────────────────────────────────────────────────────────────
    for e in extracted.get("emotions", []):
        emo_id = _find_node_by_name(dg, "Emotion", e["name"])
        if emo_id is None:
            emo_id = _unique_id(dg, f"emo_{_slug(e['name'])}")
            dg.add_emotion(
                emo_id,
                name=e["name"],
                valence=e.get("valence"),
                confidence=e.get("confidence"),
            )
        dg.add_evoked(
            dream_id, emo_id,
            anchor=e.get("anchor"),
            confidence=e.get("confidence"),
        )

    # ── Themes ────────────────────────────────────────────────────────────────
    for t in extracted.get("themes", []):
        thm_id = _find_node_by_name(dg, "Theme", t["name"])
        if thm_id is None:
            thm_id = _unique_id(dg, f"thm_{_slug(t['name'])}")
            dg.add_theme(
                thm_id,
                name=t["name"],
                description=t.get("description"),
                source="llm",
            )
        dg.add_expresses(dream_id, thm_id, source="llm", strength=t.get("strength"))

    # ── Body Sensations ───────────────────────────────────────────────────────
    for i, bs in enumerate(extracted.get("body_sensations", [])):
        bs_id = _unique_id(dg, f"bs_{dream_id}_{i}")
        dg.add_body_sensation(
            bs_id,
            description=bs["description"],
            location=bs.get("location"),
            quality=bs.get("quality"),
            confidence=bs.get("confidence"),
        )
        dg.add_includes_sensation(dream_id, bs_id)

    # ── occurred_during ───────────────────────────────────────────────────────
    lcw_id = _find_active_context_window(dg, date)
    if lcw_id:
        dg.add_occurred_during(dream_id, lcw_id)

    # ── Rebuild auto-calculated edges ─────────────────────────────────────────
    dg.recalculate_derived_edges()

    return dream_id
