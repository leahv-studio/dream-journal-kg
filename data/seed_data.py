"""
seed_data.py — Loads 10+ dream entries into the knowledge graph and saves to data/graph.json.

Run from the project root:
    python data/seed_data.py

Or from the data/ directory:
    python seed_data.py
"""

import os
import sys

# Allow importing graph.py from backend/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from graph import DreamGraph

dg = DreamGraph()


# ── Life Context Windows ─────────────────────────────────────────────────────

dg.add_life_context_window(
    "lcw_job_search",
    label="Active job search + grad school applications",
    start_date="2024-09-01",
    end_date="2025-01-15",
    description=(
        "I was laid off in late August and spent the fall applying to jobs and finishing "
        "my grad school applications simultaneously. The financial pressure was constant — "
        "I was burning through savings and every rejection letter hit harder than it should have. "
        "There was a specific kind of shame in being unemployed while also trying to present "
        "myself as competent enough for a grad program. It ended when I got the offer in January."
    ),
    summary=(
        "A period defined by financial precarity and compounding identity stress — simultaneously "
        "unemployed and applying to a graduate program, forcing the person to perform competence "
        "while feeling acutely exposed. Shame and legitimacy anxiety were central, with every "
        "rejection amplified by the underlying fear of not belonging."
    ),
    status="archived",
)

dg.add_life_context_window(
    "lcw_new_role",
    label="New job + proving myself + program coursework",
    start_date="2025-01-16",
    description=(
        "Started the new role in January — excited but deeply aware that I don't fully know "
        "what I'm doing yet. The learning curve is steep and I catch myself second-guessing "
        "things I'd have been confident about a year ago. Grad school is running in parallel "
        "and the deadlines don't care that I'm also onboarding. I keep waiting to feel "
        "like I belong in both places."
    ),
    summary=(
        "A high-demand period of simultaneous transitions — new professional role and active "
        "graduate coursework running in parallel, with no room for either to slow down. "
        "The dominant emotional register is imposter syndrome: a persistent sense of not yet "
        "belonging in either space, and waiting for the feeling of legitimacy that hasn't arrived."
    ),
    status="foreground",
)


# ── Characters ───────────────────────────────────────────────────────────────

dg.add_character("char_mom", "Mom",
                 character_type="real_current",
                 symbolic_role="Safety, home, and unresolved expectations")

dg.add_character("char_dad", "Dad",
                 character_type="real_current",
                 symbolic_role="Authority and standards")

dg.add_character("char_old_boss", "Former boss",
                 character_type="real_historical",
                 symbolic_role="Institutional judgment and legitimacy")

dg.add_character("char_stranger_woman", "Unnamed woman",
                 character_type="constructed",
                 symbolic_role="Unknown self or guide figure")

dg.add_character("char_classmate", "Unnamed classmate",
                 character_type="constructed",
                 symbolic_role="Peer comparison, competence anxiety")


# ── Symbols ──────────────────────────────────────────────────────────────────

dg.add_symbol("sym_car", "Car / driving",
              category="object",
              symbolic_note="Navigation, autonomy, forward momentum — frequent failure site")

dg.add_symbol("sym_keys", "Lost keys",
              category="object",
              symbolic_note="Access, readiness, the thing that lets you go")

dg.add_symbol("sym_phone", "Phone that won't work",
              category="object",
              symbolic_note="Failed communication, isolation, can't reach who I need")

dg.add_symbol("sym_door", "Door that won't open",
              category="object",
              symbolic_note="Blocked passage, locked out of something wanted")

dg.add_symbol("sym_water", "Rising water",
              category="sensory",
              symbolic_note="Overwhelm, the unconscious, something spreading beyond control")

dg.add_symbol("sym_backpack", "Overfull backpack",
              category="object",
              symbolic_note="Accumulated burden, too many obligations to carry")

dg.add_symbol("sym_stairs", "Infinite or wrong stairs",
              category="action",
              symbolic_note="Effort without arrival, recursive striving")

dg.add_symbol("sym_mirror", "Mirror showing wrong reflection",
              category="object",
              symbolic_note="Identity discontinuity, self not recognizable")

dg.add_symbol("sym_wrong_slides", "Wrong presentation slides",
              category="object",
              symbolic_note="Unpreparedness exposed publicly; legitimacy crisis")

dg.add_symbol("sym_grand_am", "The Grand Am",
              category="object",
              symbolic_note="Specific car from adolescence — navigation failure, autonomy")


# ── Settings ─────────────────────────────────────────────────────────────────

dg.add_setting("set_childhood_home", "Childhood home",
               familiarity="distorted",
               real_or_constructed="composite",
               symbolic_note="Anchor of origin; always slightly wrong in dreams")

dg.add_setting("set_duplex", "The duplex (way bigger inside)",
               familiarity="distorted",
               real_or_constructed="composite",
               symbolic_note="Former apartment; always contains undiscovered rooms — psychic space")

dg.add_setting("set_grand_am_interior", "Grand Am interior",
               familiarity="known",
               real_or_constructed="real",
               symbolic_note="Cramped, specific, charged with adolescent memory")

dg.add_setting("set_school_exam_room", "Unknown school / exam room",
               familiarity="unfamiliar",
               real_or_constructed="constructed",
               symbolic_note="Site of evaluation and exposure")

dg.add_setting("set_workplace", "Office / workplace",
               familiarity="distorted",
               real_or_constructed="composite",
               symbolic_note="Current or past job, usually distorted or wrong")

dg.add_setting("set_basement", "Flooded basement",
               familiarity="known",
               real_or_constructed="composite",
               symbolic_note="Depths, the unconscious filling up")

dg.add_setting("set_parking_structure", "Multi-level parking structure",
               familiarity="unfamiliar",
               real_or_constructed="constructed",
               symbolic_note="Navigation maze; can't find the car or the exit")


# ── Emotions ─────────────────────────────────────────────────────────────────

dg.add_emotion("emo_anxiety", "Anxiety", valence="negative", confidence="stated")
dg.add_emotion("emo_dread", "Dread", valence="negative", confidence="stated")
dg.add_emotion("emo_shame", "Shame", valence="negative", confidence="stated")
dg.add_emotion("emo_confusion", "Confusion", valence="ambiguous", confidence="stated")
dg.add_emotion("emo_wonder", "Wonder", valence="positive", confidence="stated")
dg.add_emotion("emo_relief", "Relief", valence="positive", confidence="stated")
dg.add_emotion("emo_fear", "Fear", valence="negative", confidence="stated")
dg.add_emotion("emo_grief", "Grief", valence="negative", confidence="inferred")
dg.add_emotion("emo_urgency", "Urgency", valence="negative", confidence="stated")


# ── Themes ───────────────────────────────────────────────────────────────────

dg.add_theme("thm_navigation_failure", "Navigation failure",
             description="Can't get where I'm going — wrong turns, broken vehicles, lost exits",
             source="user")

dg.add_theme("thm_legitimacy_anxiety", "Legitimacy anxiety",
             description="Fear of being exposed as unqualified, unprepared, or not belonging",
             source="user")

dg.add_theme("thm_home_belonging", "Home / belonging",
             description="Questions of where home is and whether I belong there",
             source="user")

dg.add_theme("thm_control_loss", "Loss of control",
             description="Systems, tools, or situations failing when needed most",
             source="llm")

dg.add_theme("thm_transformation", "Transformation / discovery",
             description="Finding new space, capacity, or self — often surprising",
             source="llm")

dg.add_theme("thm_isolation", "Isolation / failed connection",
             description="Unable to reach people or be reached; communication breakdown",
             source="user")


# ── Body Sensations ──────────────────────────────────────────────────────────

dg.add_body_sensation("bs_falling", "Sudden falling sensation at sleep onset",
                      location="whole body", quality="movement", confidence="stated")

dg.add_body_sensation("bs_chest_pressure", "Heavy pressure on chest",
                      location="chest", quality="pressure", confidence="stated")

dg.add_body_sensation("bs_legs_wont_move", "Legs won't move or move too slowly",
                      location="legs", quality="other", confidence="stated")


# ── Dreams ───────────────────────────────────────────────────────────────────

# 1. Grand Am (canonical demo entry)
dg.add_dream(
    "dream_grand_am",
    date="2025-03-15",
    raw_narrative=(
        "I'm driving the Grand Am from high school — the white one with the cracked "
        "dashboard. I need to get somewhere important but I can't figure out where I "
        "parked, and when I finally find the car the GPS won't load. I keep circling "
        "the same parking structure. I know I'm late. I never arrive."
    ),
    emotional_valence="negative",
    intensity=4,
    visual_quality="normal",
    notable_color=None,
    lucid=False,
)

# 2. Duplex #1 (first entry in recurring series)
dg.add_dream(
    "dream_duplex_1",
    date="2024-10-03",
    raw_narrative=(
        "I'm back in the old duplex on Aldrich. I go through a door I thought was a "
        "closet and there's an entire extra wing — three more rooms, high ceilings, "
        "windows I've never seen. The apartment is way bigger than it ever was. "
        "I feel amazed but also anxious, like I've been missing something obvious."
    ),
    emotional_valence="mixed",
    intensity=3,
    visual_quality="bright",
    is_recurring=True,
    recurring_series_name="My duplex is way bigger and more messed up than I realized",
    status="active",
    lucid=False,
)

# 3. Duplex #2
dg.add_dream(
    "dream_duplex_2",
    date="2025-01-08",
    raw_narrative=(
        "The duplex again. This time there's a basement I didn't know about. "
        "Water is coming in slowly. The new rooms are there but they feel unstable, "
        "like the floors might give. Mom is somewhere in the house but I can't find her."
    ),
    emotional_valence="negative",
    intensity=4,
    visual_quality="dark",
    is_recurring=True,
    recurring_series_name="My duplex is way bigger and more messed up than I realized",
    status="active",
    lucid=False,
)

# 4. Exam I didn't study for
dg.add_dream(
    "dream_exam_unprepared",
    date="2025-02-20",
    raw_narrative=(
        "I'm sitting in an exam room — big lecture hall, fluorescent lights. "
        "The test is already being handed out and I realize I never attended the class. "
        "I don't even know what subject this is. My former boss is proctoring. "
        "I can't leave."
    ),
    emotional_valence="negative",
    intensity=5,
    visual_quality="washed_out",
    lucid=False,
)

# 5. Phone won't work
dg.add_dream(
    "dream_phone_wont_work",
    date="2024-11-14",
    raw_narrative=(
        "I need to call mom urgently. My phone keeps opening the wrong apps, "
        "the screen distorts, the number won't dial. I try for what feels like "
        "hours. I never get through."
    ),
    emotional_valence="negative",
    intensity=3,
    visual_quality="normal",
    lucid=False,
)

# 6. Childhood home — rooms wrong
dg.add_dream(
    "dream_childhood_home_wrong",
    date="2024-09-22",
    raw_narrative=(
        "I'm back in the house I grew up in, but the layout is wrong. "
        "My bedroom is where the kitchen should be. Dad is there, sitting at "
        "a table that doesn't fit the space. He's proud of me about something "
        "I haven't done yet."
    ),
    emotional_valence="mixed",
    intensity=2,
    visual_quality="normal",
    lucid=False,
)

# 7. Water rising in basement
dg.add_dream(
    "dream_water_basement",
    date="2025-03-02",
    raw_narrative=(
        "There's a basement I need to get to but water is already up to my knees. "
        "I know something important is down there. The water is cold and keeps rising. "
        "I don't go in."
    ),
    emotional_valence="negative",
    intensity=4,
    visual_quality="dark",
    notable_color="grey-green",
    lucid=False,
)

# 8. Lost car keys before something important
dg.add_dream(
    "dream_lost_keys",
    date="2025-01-29",
    raw_narrative=(
        "I have a job interview in 20 minutes. I cannot find my keys anywhere. "
        "I search every pocket, every drawer, the same places over and over. "
        "A stranger woman watches me search. She seems unsurprised."
    ),
    emotional_valence="negative",
    intensity=5,
    visual_quality="normal",
    lucid=False,
)

# 9. Wrong slides in presentation
dg.add_dream(
    "dream_wrong_slides",
    date="2025-02-05",
    raw_narrative=(
        "I'm presenting to a room of people — maybe twenty of them. "
        "My slides are someone else's entirely. I try to improvise but "
        "I don't know the material. A classmate in the front row takes notes. "
        "I keep talking."
    ),
    emotional_valence="negative",
    intensity=4,
    visual_quality="washed_out",
    lucid=False,
)

# 10. Infinite stairs
dg.add_dream(
    "dream_infinite_stairs",
    date="2024-12-18",
    raw_narrative=(
        "I'm climbing stairs in a building that keeps adding floors. "
        "The door I need is always one more flight up. My backpack is unbearably heavy. "
        "I don't stop climbing."
    ),
    emotional_valence="negative",
    intensity=3,
    visual_quality="dark",
    lucid=False,
)

# 11. Mirror / wrong reflection
dg.add_dream(
    "dream_mirror",
    date="2025-03-28",
    raw_narrative=(
        "I'm in a bathroom I don't recognize. I look in the mirror and the person "
        "looking back is me but from a different time — younger, or older, I can't tell. "
        "She mouths something I can't hear. I feel the falling sensation and wake up."
    ),
    emotional_valence="mixed",
    intensity=3,
    visual_quality="vivid",
    is_novel=True,
    lucid=False,
)


# ── Edges: Dream → LifeContextWindow ────────────────────────────────────────

dg.add_occurred_during("dream_duplex_1",             "lcw_job_search")
dg.add_occurred_during("dream_phone_wont_work",      "lcw_job_search")
dg.add_occurred_during("dream_childhood_home_wrong", "lcw_job_search")
dg.add_occurred_during("dream_duplex_2",             "lcw_new_role")
dg.add_occurred_during("dream_exam_unprepared",      "lcw_new_role")
dg.add_occurred_during("dream_lost_keys",            "lcw_new_role")
dg.add_occurred_during("dream_wrong_slides",         "lcw_new_role")
dg.add_occurred_during("dream_infinite_stairs",      "lcw_job_search")
dg.add_occurred_during("dream_grand_am",             "lcw_new_role")
dg.add_occurred_during("dream_water_basement",       "lcw_new_role")
dg.add_occurred_during("dream_mirror",               "lcw_new_role")


# ── Edges: Dream → Symbol ────────────────────────────────────────────────────

dg.add_contains("dream_grand_am",             "sym_grand_am",    prominence="central")
dg.add_contains("dream_grand_am",             "sym_car",         prominence="central")
dg.add_contains("dream_grand_am",             "sym_keys",        prominence="present")

dg.add_contains("dream_duplex_1",             "sym_door",        prominence="central")
dg.add_contains("dream_duplex_2",             "sym_door",        prominence="present")
dg.add_contains("dream_duplex_2",             "sym_water",       prominence="central")

dg.add_contains("dream_phone_wont_work",      "sym_phone",       prominence="central")

dg.add_contains("dream_lost_keys",            "sym_keys",        prominence="central")
dg.add_contains("dream_lost_keys",            "sym_car",         prominence="present")

dg.add_contains("dream_wrong_slides",         "sym_wrong_slides", prominence="central")

dg.add_contains("dream_infinite_stairs",      "sym_stairs",      prominence="central")
dg.add_contains("dream_infinite_stairs",      "sym_backpack",    prominence="present")

dg.add_contains("dream_water_basement",       "sym_water",       prominence="central")
dg.add_contains("dream_water_basement",       "sym_door",        prominence="background")

dg.add_contains("dream_exam_unprepared",      "sym_backpack",    prominence="background")

dg.add_contains("dream_mirror",               "sym_mirror",      prominence="central")

dg.add_contains("dream_childhood_home_wrong", "sym_door",        prominence="background")


# ── Edges: Dream → Character ─────────────────────────────────────────────────

dg.add_features("dream_grand_am",             "char_stranger_woman", role="observer")
dg.add_features("dream_duplex_2",             "char_mom",             role="passive")
dg.add_features("dream_exam_unprepared",      "char_old_boss",        role="active")
dg.add_features("dream_phone_wont_work",      "char_mom",             role="passive")
dg.add_features("dream_childhood_home_wrong", "char_dad",             role="passive")
dg.add_features("dream_lost_keys",            "char_stranger_woman",  role="observer")
dg.add_features("dream_wrong_slides",         "char_classmate",       role="observer")


# ── Edges: Dream → Setting ───────────────────────────────────────────────────

dg.add_takes_place_in("dream_grand_am",             "set_grand_am_interior",  distortion_level="intact")
dg.add_takes_place_in("dream_grand_am",             "set_parking_structure",  distortion_level="distorted")
dg.add_takes_place_in("dream_duplex_1",             "set_duplex",             distortion_level="distorted")
dg.add_takes_place_in("dream_duplex_2",             "set_duplex",             distortion_level="distorted")
dg.add_takes_place_in("dream_duplex_2",             "set_basement",           distortion_level="intact")
dg.add_takes_place_in("dream_exam_unprepared",      "set_school_exam_room",   distortion_level="intact")
dg.add_takes_place_in("dream_childhood_home_wrong", "set_childhood_home",     distortion_level="distorted")
dg.add_takes_place_in("dream_water_basement",       "set_basement",           distortion_level="intact")
dg.add_takes_place_in("dream_wrong_slides",         "set_workplace",          distortion_level="distorted")
dg.add_takes_place_in("dream_infinite_stairs",      "set_workplace",          distortion_level="distorted")
dg.add_takes_place_in("dream_lost_keys",            "set_childhood_home",     distortion_level="distorted")


# ── Edges: Dream → Emotion ───────────────────────────────────────────────────

dg.add_evoked("dream_grand_am",             "emo_anxiety",  anchor="can't find exit", confidence="stated")
dg.add_evoked("dream_grand_am",             "emo_urgency",  anchor="late for something important", confidence="stated")
dg.add_evoked("dream_duplex_1",             "emo_wonder",   anchor="discovering new rooms", confidence="stated")
dg.add_evoked("dream_duplex_1",             "emo_anxiety",  anchor="having missed this space", confidence="stated")
dg.add_evoked("dream_duplex_2",             "emo_dread",    anchor="rising water", confidence="stated")
dg.add_evoked("dream_duplex_2",             "emo_grief",    anchor="can't find mom", confidence="inferred")
dg.add_evoked("dream_exam_unprepared",      "emo_shame",    anchor="former boss watching", confidence="stated")
dg.add_evoked("dream_exam_unprepared",      "emo_dread",    anchor="can't leave room", confidence="stated")
dg.add_evoked("dream_phone_wont_work",      "emo_anxiety",  anchor="can't reach mom", confidence="stated")
dg.add_evoked("dream_phone_wont_work",      "emo_fear",     anchor="isolation", confidence="inferred")
dg.add_evoked("dream_childhood_home_wrong", "emo_confusion", anchor="rooms in wrong places", confidence="stated")
dg.add_evoked("dream_water_basement",       "emo_dread",    anchor="water keeps rising", confidence="stated")
dg.add_evoked("dream_lost_keys",            "emo_anxiety",  anchor="late for interview", confidence="stated")
dg.add_evoked("dream_lost_keys",            "emo_shame",    anchor="stranger watching", confidence="inferred")
dg.add_evoked("dream_wrong_slides",         "emo_shame",    anchor="exposed as unprepared", confidence="stated")
dg.add_evoked("dream_infinite_stairs",      "emo_urgency",  anchor="door always one flight higher", confidence="stated")
dg.add_evoked("dream_mirror",               "emo_wonder",   anchor="other self in mirror", confidence="stated")
dg.add_evoked("dream_mirror",               "emo_fear",     anchor="falling sensation", confidence="stated")


# ── Edges: Dream → Theme ─────────────────────────────────────────────────────

dg.add_expresses("dream_grand_am",             "thm_navigation_failure",  source="user", strength="strong")
dg.add_expresses("dream_grand_am",             "thm_control_loss",        source="llm",  strength="moderate")
dg.add_expresses("dream_duplex_1",             "thm_home_belonging",      source="user", strength="strong")
dg.add_expresses("dream_duplex_1",             "thm_transformation",      source="llm",  strength="moderate")
dg.add_expresses("dream_duplex_2",             "thm_home_belonging",      source="user", strength="strong")
dg.add_expresses("dream_duplex_2",             "thm_control_loss",        source="llm",  strength="strong")
dg.add_expresses("dream_exam_unprepared",      "thm_legitimacy_anxiety",  source="user", strength="strong")
dg.add_expresses("dream_exam_unprepared",      "thm_control_loss",        source="llm",  strength="strong")
dg.add_expresses("dream_phone_wont_work",      "thm_isolation",           source="user", strength="strong")
dg.add_expresses("dream_phone_wont_work",      "thm_control_loss",        source="llm",  strength="moderate")
dg.add_expresses("dream_childhood_home_wrong", "thm_home_belonging",      source="user", strength="moderate")
dg.add_expresses("dream_water_basement",       "thm_control_loss",        source="llm",  strength="strong")
dg.add_expresses("dream_lost_keys",            "thm_navigation_failure",  source="user", strength="strong")
dg.add_expresses("dream_lost_keys",            "thm_legitimacy_anxiety",  source="user", strength="moderate")
dg.add_expresses("dream_wrong_slides",         "thm_legitimacy_anxiety",  source="user", strength="strong")
dg.add_expresses("dream_wrong_slides",         "thm_control_loss",        source="llm",  strength="moderate")
dg.add_expresses("dream_infinite_stairs",      "thm_navigation_failure",  source="user", strength="moderate")
dg.add_expresses("dream_infinite_stairs",      "thm_control_loss",        source="llm",  strength="moderate")
dg.add_expresses("dream_mirror",               "thm_transformation",      source="llm",  strength="strong")


# ── Edges: Dream → BodySensation ─────────────────────────────────────────────

dg.add_includes_sensation("dream_mirror",        "bs_falling")
dg.add_includes_sensation("dream_duplex_2",      "bs_chest_pressure")
dg.add_includes_sensation("dream_infinite_stairs", "bs_legs_wont_move")


# ── Edges: Symbol → Theme ────────────────────────────────────────────────────

dg.add_contributes_to("sym_car",         "thm_navigation_failure")
dg.add_contributes_to("sym_grand_am",    "thm_navigation_failure")
dg.add_contributes_to("sym_keys",        "thm_navigation_failure")
dg.add_contributes_to("sym_keys",        "thm_legitimacy_anxiety")
dg.add_contributes_to("sym_phone",       "thm_isolation")
dg.add_contributes_to("sym_door",        "thm_home_belonging")
dg.add_contributes_to("sym_door",        "thm_control_loss")
dg.add_contributes_to("sym_water",       "thm_control_loss")
dg.add_contributes_to("sym_stairs",      "thm_navigation_failure")
dg.add_contributes_to("sym_backpack",    "thm_control_loss")
dg.add_contributes_to("sym_wrong_slides","thm_legitimacy_anxiety")
dg.add_contributes_to("sym_mirror",      "thm_transformation")


# ── Edges: Character → Theme ─────────────────────────────────────────────────

dg.add_associated_with("char_old_boss",        "thm_legitimacy_anxiety")
dg.add_associated_with("char_mom",             "thm_home_belonging")
dg.add_associated_with("char_mom",             "thm_isolation")
dg.add_associated_with("char_dad",             "thm_legitimacy_anxiety")
dg.add_associated_with("char_classmate",       "thm_legitimacy_anxiety")
dg.add_associated_with("char_stranger_woman",  "thm_transformation")


# ── Edges: Character → Symbol ────────────────────────────────────────────────

dg.add_represents("char_old_boss",       "sym_wrong_slides")
dg.add_represents("char_stranger_woman", "sym_mirror")


# ── Edges: Setting → Theme ───────────────────────────────────────────────────

dg.add_evokes("set_parking_structure",  "thm_navigation_failure")
dg.add_evokes("set_grand_am_interior",  "thm_navigation_failure")
dg.add_evokes("set_duplex",             "thm_home_belonging")
dg.add_evokes("set_duplex",             "thm_transformation")
dg.add_evokes("set_childhood_home",     "thm_home_belonging")
dg.add_evokes("set_school_exam_room",   "thm_legitimacy_anxiety")
dg.add_evokes("set_workplace",          "thm_legitimacy_anxiety")
dg.add_evokes("set_basement",           "thm_control_loss")


# ── Edges: Theme → Theme ─────────────────────────────────────────────────────

dg.add_related_to("thm_navigation_failure", "thm_legitimacy_anxiety",
                  relationship_type="reinforces")
dg.add_related_to("thm_legitimacy_anxiety", "thm_control_loss",
                  relationship_type="reinforces")
dg.add_related_to("thm_control_loss",       "thm_transformation",
                  relationship_type="evolves_into")
dg.add_related_to("thm_home_belonging",     "thm_isolation",
                  relationship_type="contrasts")


# ── Edges: Dream → Dream (recurs_as, user-asserted) ──────────────────────────

dg.add_recurs_as("dream_duplex_1", "dream_duplex_2")


# ── Auto-calculated edges ─────────────────────────────────────────────────────

dg.recalculate_derived_edges()


# ── Save ──────────────────────────────────────────────────────────────────────

dg.save()
print("Graph saved.")
print()

stats = dg.stats()
print("Node counts:")
for node_type, count in sorted(stats["nodes"].items()):
    print(f"  {node_type}: {count}")

print()
print("Edge counts:")
for edge_type, count in sorted(stats["edges"].items()):
    print(f"  {edge_type}: {count}")

print()
print("All dreams (sorted by date):")
for dream in dg.get_all_dreams():
    print(f"  [{dream['date']}] {dream['id']} — {dream.get('emotional_valence', 'n/a')}, intensity {dream.get('intensity', 'n/a')}")
