import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import date as _date

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

import anthropic
from flask import Flask, Response, jsonify, render_template, request, send_from_directory, stream_with_context
from flask_cors import CORS

from extract import extract_dream, write_to_graph, build_entity_candidates, _find_active_context_window
from graph import DreamGraph
from prompts import JOURNAL_SYSTEM_PROMPT, EXTRACTION_SYSTEM_PROMPT, TITLE_SYSTEM_PROMPT, QUERY_SYSTEM_PROMPT

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
app = Flask(__name__, template_folder=FRONTEND_DIR)
CORS(app)

_DATA_DIR       = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
_GRAPH_FULL     = os.path.join(_DATA_DIR, "graph.json")
_GRAPH_EMPTY    = os.path.join(_DATA_DIR, "graph_empty.json")
_demo_mode      = False


def _save_graph():
    if not _demo_mode:
        dg.save()


dg = DreamGraph()
try:
    dg.load()
except FileNotFoundError:
    pass

ai = anthropic.Anthropic()
conversation_history: list[dict] = []


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


_SUMMARY_SYSTEM_PROMPT = (
    "You are summarizing a personal life context entry for use in dream analysis. "
    "Write 2-3 sentences that capture the emotional core and key themes. "
    "Focus on what would help a dream analyst understand why this period of life is significant. "
    "Do not include specific names, dates, or minor details. "
    "Return only the summary — no preamble, no explanation."
)


def _generate_lcw_summary(description: str) -> str | None:
    """Call Claude to produce a 2-3 sentence summary of a life context description.
    Returns None if description is too short to summarize."""
    if not description or len(description.strip()) < 50:
        return None
    response = ai.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=200,
        system=_SUMMARY_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": description}],
    )
    return response.content[0].text.strip()


def build_context_block() -> str:
    """Build a formatted context string from all non-archived LifeContextWindow nodes."""
    tiers: dict[str, list[dict]] = {"foreground": [], "background": [], "dormant": []}
    for node_id, attrs in dg.G.nodes(data=True):
        if attrs.get("node_type") != "LifeContextWindow":
            continue
        status = attrs.get("status", "dormant")
        if status not in tiers:
            continue  # skip archived
        tiers[status].append({"id": node_id, **attrs})

    tier_labels = {
        "foreground": "FOREGROUND (consciously active)",
        "background": "BACKGROUND (present but not the loudest thing)",
        "dormant":    "DORMANT (no longer active, but still part of your life)",
    }

    sections = []
    for tier in ("foreground", "background", "dormant"):
        contexts = tiers[tier]
        if not contexts:
            continue
        lines = [f"{tier_labels[tier]}:"]
        for ctx in contexts:
            label = ctx.get("label", "Unnamed")
            text = ctx.get("summary") or (ctx.get("description") or "")[:200] or "(no description)"
            lines.append(f"- {label}: {text}")
        sections.append("\n".join(lines))

    return "\n\n".join(sections)


def build_query_context(dg: DreamGraph) -> str:
    """Serialize pre-aggregated graph analytics for the NL query Claude call."""
    from datetime import timedelta
    today = _date.today()
    cutoff_90  = (today - timedelta(days=90)).isoformat()
    cutoff_180 = (today - timedelta(days=180)).isoformat()

    s = dg.stats()
    lines = [
        "GRAPH OVERVIEW",
        f"  {s['nodes'].get('Dream', 0)} dreams · "
        f"{s['nodes'].get('Symbol', 0)} symbols · "
        f"{s['nodes'].get('Theme', 0)} themes · "
        f"{s['nodes'].get('Character', 0)} characters · "
        f"{s['nodes'].get('LifeContextWindow', 0)} life context windows",
        "",
    ]

    # Symbols — all time
    symbols = dg.get_symbol_frequency()
    lines.append("SYMBOLS — all time (by dream frequency):")
    for sym in symbols[:30]:
        lines.append(f"  [{sym['id']}] \"{sym['name']}\" — {sym['dream_count']} dreams")
    lines.append("")

    # Symbols — last 90 days
    sym_90: dict[str, int] = {}
    for u, v, _, edata in dg.G.edges(data=True, keys=True):
        if edata.get("edge_type") == "contains":
            if dg.G.nodes.get(u, {}).get("date", "") >= cutoff_90:
                sym_90[v] = sym_90.get(v, 0) + 1
    sym_90_sorted = sorted(sym_90.items(), key=lambda x: -x[1])[:20]
    lines.append("SYMBOLS — last 90 days:")
    for sym_id, count in sym_90_sorted:
        name = dg.G.nodes.get(sym_id, {}).get("name", sym_id)
        lines.append(f"  [{sym_id}] \"{name}\" — {count} dreams")
    if not sym_90_sorted:
        lines.append("  (none in this window)")
    lines.append("")

    # Themes — all time
    themes = dg.get_all_themes()
    lines.append("THEMES — all time:")
    for thm in themes[:30]:
        desc = thm.get("description") or ""
        desc_str = f" — {desc}" if desc else ""
        lines.append(f"  [{thm['id']}] \"{thm['name']}\" — {thm['dream_count']} dreams{desc_str}")
    lines.append("")

    # Themes — last 90 days
    thm_90: dict[str, int] = {}
    for u, v, _, edata in dg.G.edges(data=True, keys=True):
        if edata.get("edge_type") == "expresses":
            if dg.G.nodes.get(u, {}).get("date", "") >= cutoff_90:
                thm_90[v] = thm_90.get(v, 0) + 1
    thm_90_sorted = sorted(thm_90.items(), key=lambda x: -x[1])[:20]
    lines.append("THEMES — last 90 days:")
    for thm_id, count in thm_90_sorted:
        name = dg.G.nodes.get(thm_id, {}).get("name", thm_id)
        lines.append(f"  [{thm_id}] \"{name}\" — {count} dreams")
    if not thm_90_sorted:
        lines.append("  (none in this window)")
    lines.append("")

    # Characters — all time
    char_dreams: dict[str, set] = {}
    for u, v, _, edata in dg.G.edges(data=True, keys=True):
        if edata.get("edge_type") == "features":
            char_dreams.setdefault(v, set()).add(u)
    chars_sorted = sorted(char_dreams.items(), key=lambda x: -len(x[1]))[:20]
    lines.append("CHARACTERS — all time:")
    for char_id, dreams in chars_sorted:
        name = dg.G.nodes.get(char_id, {}).get("name", char_id)
        lines.append(f"  [{char_id}] \"{name}\" — {len(dreams)} dreams")
    if not chars_sorted:
        lines.append("  (none recorded)")
    lines.append("")

    # Life context windows with per-window breakdowns
    lcws = dg.get_all_life_context_windows()
    lines.append("LIFE CONTEXT WINDOWS:")
    for lcw in lcws:
        lcw_id = lcw["id"]
        label  = lcw.get("label", lcw_id)
        status = lcw.get("status", "dormant")
        start  = lcw.get("start_date", "?")

        lcw_dream_ids: set[str] = set()
        for u, v, _, edata in dg.G.edges(data=True, keys=True):
            if edata.get("edge_type") == "occurred_during" and v == lcw_id:
                lcw_dream_ids.add(u)

        thm_in_lcw: dict[str, int] = {}
        for u, v, _, edata in dg.G.edges(data=True, keys=True):
            if edata.get("edge_type") == "expresses" and u in lcw_dream_ids:
                thm_in_lcw[v] = thm_in_lcw.get(v, 0) + 1
        top_thms = sorted(thm_in_lcw.items(), key=lambda x: -x[1])[:3]
        thm_str = ", ".join(
            f"\"{dg.G.nodes.get(t, {}).get('name', t)}\" ×{c}" for t, c in top_thms
        ) or "none"

        sym_in_lcw: dict[str, int] = {}
        for u, v, _, edata in dg.G.edges(data=True, keys=True):
            if edata.get("edge_type") == "contains" and u in lcw_dream_ids:
                sym_in_lcw[v] = sym_in_lcw.get(v, 0) + 1
        top_syms = sorted(sym_in_lcw.items(), key=lambda x: -x[1])[:3]
        sym_str = ", ".join(
            f"\"{dg.G.nodes.get(s, {}).get('name', s)}\" ×{c}" for s, c in top_syms
        ) or "none"

        lines.append(
            f"  [{lcw_id}] \"{label}\" ({status}, from {start}) — {len(lcw_dream_ids)} dreams"
        )
        lines.append(f"    Top themes: {thm_str}")
        lines.append(f"    Top symbols: {sym_str}")
    lines.append("")

    # Dream index — last 180 days
    lines.append("DREAM INDEX — last 180 days:")
    dream_index = [
        (attrs.get("date", ""), n)
        for n, attrs in dg.G.nodes(data=True)
        if attrs.get("node_type") == "Dream" and attrs.get("date", "") >= cutoff_180
    ]
    dream_index.sort(reverse=True)
    for date, node_id in dream_index:
        lines.append(f"  [{node_id}] {date}")
    if not dream_index:
        lines.append("  (no dreams in this window)")

    return "\n".join(lines)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/journal.html")
def journal():
    return render_template("journal.html")


@app.route("/dashboard.html")
def dashboard():
    return send_from_directory(FRONTEND_DIR, "dashboard.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "message is required"}), 400

    conversation_history.append({"role": "user", "content": message})

    system_prompt = JOURNAL_SYSTEM_PROMPT(build_context_block())

    def generate():
        full_reply = []
        with ai.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=system_prompt,
            messages=conversation_history,
        ) as stream:
            for text in stream.text_stream:
                full_reply.append(text)
                yield f"data: {json.dumps({'delta': text})}\n\n"

        conversation_history.append({"role": "assistant", "content": "".join(full_reply)})
        yield f"data: {json.dumps({'done': True})}\n\n"

    return Response(
        stream_with_context(generate()),
        content_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/api/extract", methods=["POST"])
def api_extract():
    """
    Run Claude extraction on the current conversation.
    Does NOT write to graph — that happens on /api/confirm.
    Returns extracted data + divergence info for the review card.
    """
    if not conversation_history:
        return jsonify({"error": "No conversation in progress"}), 400

    data = request.json or {}
    dream_date = data.get("date") or _date.today().isoformat()
    context_block = build_context_block()
    candidates_block = build_entity_candidates(dg)
    history_snapshot = list(conversation_history)

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_extract = executor.submit(extract_dream, history_snapshot, dream_date, context_block, candidates_block)
        future_title   = executor.submit(_generate_dream_title, history_snapshot)
        extracted      = future_extract.result()
        suggested_title = ""
        try:
            suggested_title = future_title.result()
        except Exception as e:
            print(f"Title generation failed (non-fatal): {e}")

    print("\n" + "=" * 60)
    print("EXTRACTION RESULT")
    print("=" * 60)
    print(json.dumps(extracted, indent=2))
    print("=" * 60 + "\n")

    divergence = _detect_divergence(extracted, dg, dream_date)

    return jsonify({
        "extracted": extracted,
        "date": dream_date,
        "divergence": divergence,
        "suggested_title": suggested_title,
    })


@app.route("/api/confirm", methods=["POST"])
def api_confirm():
    """Write the reviewed (and possibly user-edited) extraction to the graph."""
    data = request.json or {}
    extracted = data.get("extracted")
    dream_date = data.get("date") or _date.today().isoformat()

    if not extracted:
        return jsonify({"error": "extracted data is required"}), 400

    dream_id = write_to_graph(extracted, dg, dream_date)
    _save_graph()

    print(f"\nWritten to graph as: {dream_id}")
    print(f"Graph stats: {json.dumps(dg.stats(), indent=2)}\n")

    conversation_history.clear()
    return jsonify({"dream_id": dream_id, "stats": dg.stats()})


@app.route("/api/discard", methods=["POST"])
def api_discard():
    """Discard the current conversation without saving anything."""
    conversation_history.clear()
    return jsonify({"status": "discarded"})


@app.route("/api/context", methods=["GET"])
def get_context():
    """Return all foreground LifeContextWindow nodes."""
    foreground = [
        {"id": node_id, **attrs}
        for node_id, attrs in dg.G.nodes(data=True)
        if attrs.get("node_type") == "LifeContextWindow"
        and attrs.get("status") == "foreground"
    ]
    return jsonify(foreground)


@app.route("/api/life-context-windows", methods=["POST"])
def create_life_context_window():
    """Create a new LifeContextWindow node."""
    data = request.json or {}
    label = (data.get("label") or "").strip()
    if not label:
        return jsonify({"error": "label is required"}), 400

    start_date  = data.get("start_date") or None
    description = (data.get("description") or "").strip() or None
    status = data.get("status") or "foreground"
    if status not in {"foreground", "background", "dormant", "archived"}:
        return jsonify({"error": "invalid status"}), 400

    slug_base = _slug(label[:24])
    lcw_id = f"lcw_{slug_base}"
    # If a node with that id already exists, append a counter
    counter = 1
    base_id = lcw_id
    while lcw_id in dg.G:
        lcw_id = f"{base_id}_{counter}"
        counter += 1

    summary = None
    try:
        summary = _generate_lcw_summary(description)
    except Exception as e:
        print(f"LCW summary generation failed (non-fatal): {e}")

    dg.add_life_context_window(
        lcw_id,
        label=label,
        start_date=start_date,
        description=description,
        summary=summary,
        status=status,
    )
    _save_graph()

    node_attrs = dict(dg.G.nodes[lcw_id])
    print(f"\nNew LCW node '{lcw_id}' attributes after save:")
    for k, v in node_attrs.items():
        print(f"  {k}: {v!r}")
    print()

    return jsonify({
        "id": lcw_id,
        "label": label,
        "start_date": start_date,
        "description": description,
        "summary": summary,
        "status": status,
    }), 201


@app.route("/api/life-context-windows/<lcw_id>/status", methods=["PUT"])
def update_life_context_status(lcw_id):
    """Update the status of a LifeContextWindow node."""
    data = request.json or {}
    status = (data.get("status") or "").strip()
    if status not in {"foreground", "background", "dormant", "archived"}:
        return jsonify({"error": "status must be one of: foreground, background, dormant, archived"}), 400
    try:
        found = dg.update_life_context_status(lcw_id, status)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    if not found:
        return jsonify({"error": "not found"}), 404
    _save_graph()
    return jsonify({"id": lcw_id, "status": status})


@app.route("/api/life-context-windows/<lcw_id>", methods=["PUT"])
def update_life_context_window(lcw_id):
    """Update a LifeContextWindow node's label, start_date, description, and status."""
    if lcw_id not in dg.G:
        return jsonify({"error": "not found"}), 404
    if dg.G.nodes[lcw_id].get("node_type") != "LifeContextWindow":
        return jsonify({"error": "not a LifeContextWindow"}), 400

    data = request.json or {}
    label = (data.get("label") or "").strip()
    if not label:
        return jsonify({"error": "label is required"}), 400

    status = data.get("status") or dg.G.nodes[lcw_id].get("status", "foreground")
    if status not in {"foreground", "background", "dormant", "archived"}:
        return jsonify({"error": "invalid status"}), 400

    description = (data.get("description") or "").strip() or None
    start_date  = data.get("start_date") or None

    old_description = dg.G.nodes[lcw_id].get("description")

    dg.G.nodes[lcw_id]["label"]       = label
    dg.G.nodes[lcw_id]["status"]      = status
    dg.G.nodes[lcw_id]["description"] = description
    dg.G.nodes[lcw_id]["start_date"]  = start_date

    if description != old_description:
        try:
            summary = _generate_lcw_summary(description)
            dg.G.nodes[lcw_id]["summary"] = summary
        except Exception as e:
            print(f"LCW summary re-generation failed (non-fatal): {e}")

    _save_graph()
    node = dict(dg.G.nodes[lcw_id])
    return jsonify({
        "id":          lcw_id,
        "label":       node.get("label"),
        "start_date":  node.get("start_date"),
        "description": node.get("description"),
        "summary":     node.get("summary"),
        "status":      node.get("status"),
    })


@app.route("/api/stats")
def get_stats():
    from datetime import date as _dt, timedelta
    today = _dt.today()
    first_of_month = today.replace(day=1)
    last_month_end = first_of_month - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)
    cutoff_90 = (today - timedelta(days=90)).isoformat()

    dreams_this_month = 0
    dreams_last_month = 0
    total_dreams = 0
    for _, attrs in dg.G.nodes(data=True):
        if attrs.get("node_type") != "Dream":
            continue
        total_dreams += 1
        d = attrs.get("date", "")
        if d >= first_of_month.isoformat():
            dreams_this_month += 1
        if last_month_start.isoformat() <= d <= last_month_end.isoformat():
            dreams_last_month += 1

    theme_counts_90: dict[str, int] = {}
    for u, v, _, edata in dg.G.edges(data=True, keys=True):
        if edata.get("edge_type") == "expresses":
            dream_date = dg.G.nodes.get(u, {}).get("date", "")
            if dream_date >= cutoff_90:
                theme_counts_90[v] = theme_counts_90.get(v, 0) + 1

    top_theme_90 = None
    if theme_counts_90:
        top_id = max(theme_counts_90, key=theme_counts_90.get)
        top_theme_90 = {
            "name": dg.G.nodes.get(top_id, {}).get("name", top_id),
            "count": theme_counts_90[top_id],
        }

    symbol_counts: dict[str, int] = {}
    for _, v, _, edata in dg.G.edges(data=True, keys=True):
        if edata.get("edge_type") == "contains":
            symbol_counts[v] = symbol_counts.get(v, 0) + 1

    top_symbol = None
    if symbol_counts:
        top_id = max(symbol_counts, key=symbol_counts.get)
        top_symbol = {
            "name": dg.G.nodes.get(top_id, {}).get("name", top_id),
            "count": symbol_counts[top_id],
        }

    return jsonify({
        "dreams_this_month": dreams_this_month,
        "dreams_last_month": dreams_last_month,
        "top_theme_90_days": top_theme_90,
        "top_symbol_all_time": top_symbol,
        "total_dreams": total_dreams,
    })


@app.route("/api/query", methods=["POST"])
def api_query():
    data = request.json or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "question is required"}), 400

    context = build_query_context(dg)
    response = ai.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=600,
        system=QUERY_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"<graph_data>\n{context}\n</graph_data>\n\nQuestion: {question}",
        }],
    )

    raw = response.content[0].text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    return jsonify(json.loads(raw))


@app.route("/api/dreams")
def get_dreams():
    return jsonify(dg.get_all_dreams())


@app.route("/api/symbols/frequency")
def get_symbol_frequency():
    return jsonify(dg.get_symbol_frequency())


@app.route("/api/themes")
def get_themes():
    return jsonify(dg.get_all_themes())


@app.route("/api/life-context-windows")
def get_life_context_windows():
    return jsonify(dg.get_all_life_context_windows())


@app.route("/api/recurring-series")
def get_recurring_series():
    return jsonify(dg.get_recurring_series())


@app.route("/api/dreams/filter")
def filter_dreams():
    return jsonify(dg.filter_dreams(
        theme=request.args.get("theme"),
        context_window=request.args.get("context_window"),
        start_date=request.args.get("start_date"),
        end_date=request.args.get("end_date"),
        series=request.args.get("series"),
    ))


def _generate_dream_title(conversation_history: list[dict]) -> str:
    """One-shot title generation directly from the conversation transcript."""
    transcript = "\n".join(
        f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
        for m in conversation_history
    )
    response = ai.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=60,
        system=TITLE_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": transcript}],
    )
    return response.content[0].text.strip().strip('"').strip("'")


def _graph_label(node_type: str, attrs: dict) -> str:
    if node_type == "Dream":
        return attrs.get("date", "?")
    if node_type == "LifeContextWindow":
        return attrs.get("label", "?")
    if node_type == "BodySensation":
        desc = attrs.get("description", "")
        return desc[:40] + "…" if len(desc) > 40 else desc
    return attrs.get("name", "?")


@app.route("/api/demo/toggle", methods=["POST"])
def api_demo_toggle():
    global _demo_mode, dg
    _demo_mode = not _demo_mode
    path = _GRAPH_EMPTY if _demo_mode else _GRAPH_FULL
    dg = DreamGraph()
    try:
        dg.load(path)
    except FileNotFoundError:
        pass
    return jsonify({"demo_mode": _demo_mode})


@app.route("/api/graph")
def get_graph():
    nodes = []
    for node_id, attrs in dg.G.nodes(data=True):
        ntype = attrs.get("node_type", "Unknown")
        props = {}
        for k, v in attrs.items():
            if k == "node_type":
                continue
            props[k] = v
        nodes.append({
            "id": node_id,
            "label": _graph_label(ntype, attrs),
            "type": ntype,
            "properties": props,
        })

    links = [
        {"source": u, "target": v, "type": edata.get("edge_type", k)}
        for u, v, k, edata in dg.G.edges(data=True, keys=True)
    ]
    return jsonify({"nodes": nodes, "links": links})


# ── Helpers ───────────────────────────────────────────────────────────────────

def _detect_divergence(extracted: dict, dg: DreamGraph, date: str) -> dict | None:
    """
    Check whether any extracted themes are new to the current LCW.
    Only fires if the LCW already has established patterns (activates edges).
    Returns a dict with new_themes and context_label, or None.
    """
    lcw_id = _find_active_context_window(dg, date)
    if not lcw_id:
        return None

    # Gather theme names already activated in this context
    activated_names: set[str] = set()
    for u, v, k, d in dg.G.edges(data=True, keys=True):
        if u == lcw_id and d.get("edge_type") == "activates":
            name = dg.G.nodes[v].get("name", "").lower()
            activated_names.add(name)

    # Don't flag if context has no established patterns yet
    if not activated_names:
        return None

    new_themes = [
        t["name"]
        for t in extracted.get("themes", [])
        if t["name"].lower() not in activated_names
    ]
    if not new_themes:
        return None

    return {
        "new_themes": new_themes,
        "context_label": dg.G.nodes[lcw_id].get("label", "your current context"),
    }


if __name__ == "__main__":
    app.run(debug=True, port=5001)
