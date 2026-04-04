import json
import os
from itertools import combinations

import networkx as nx
from networkx.readwrite import json_graph

GRAPH_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "graph.json")
)


class DreamGraph:
    def __init__(self):
        self.G = nx.MultiDiGraph()

    # ── Persistence ──────────────────────────────────────────────────────────

    def save(self, path=None):
        path = path or GRAPH_PATH
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = json_graph.node_link_data(self.G)
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def load(self, path=None):
        path = path or GRAPH_PATH
        with open(path) as f:
            data = json.load(f)
        self.G = json_graph.node_link_graph(data, directed=True, multigraph=True)

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _add_node(self, node_id, node_type, **attrs):
        # Only store non-None attrs so nulls remain meaningful by absence
        clean = {k: v for k, v in attrs.items() if v is not None}
        self.G.add_node(node_id, node_type=node_type, **clean)

    def _add_edge(self, u, v, edge_type, **attrs):
        clean = {k: v for k, v in attrs.items() if v is not None}
        self.G.add_edge(u, v, key=edge_type, edge_type=edge_type, **clean)

    # ── Node types ───────────────────────────────────────────────────────────

    def add_dream(self, id, date, raw_narrative=None, emotional_valence=None,
                  intensity=None, visual_quality=None, notable_color=None,
                  language=None, is_recurring=None, recurring_series_name=None,
                  status=None, is_novel=None, age_range=None, lucid=None):
        self._add_node(id, "Dream",
                       date=date, raw_narrative=raw_narrative,
                       emotional_valence=emotional_valence, intensity=intensity,
                       visual_quality=visual_quality, notable_color=notable_color,
                       language=language, is_recurring=is_recurring,
                       recurring_series_name=recurring_series_name, status=status,
                       is_novel=is_novel, age_range=age_range, lucid=lucid)

    def add_character(self, id, name, character_type=None, symbolic_role=None,
                      language_spoken=None):
        self._add_node(id, "Character",
                       name=name, character_type=character_type,
                       symbolic_role=symbolic_role, language_spoken=language_spoken)

    def add_symbol(self, id, name, category=None, symbolic_note=None):
        self._add_node(id, "Symbol",
                       name=name, category=category, symbolic_note=symbolic_note)

    def add_setting(self, id, name, familiarity=None, real_or_constructed=None,
                    symbolic_note=None):
        self._add_node(id, "Setting",
                       name=name, familiarity=familiarity,
                       real_or_constructed=real_or_constructed,
                       symbolic_note=symbolic_note)

    def add_emotion(self, id, name, valence=None, confidence=None):
        self._add_node(id, "Emotion",
                       name=name, valence=valence, confidence=confidence)

    def add_theme(self, id, name, description=None, source=None):
        self._add_node(id, "Theme",
                       name=name, description=description, source=source)

    def add_life_context_window(self, id, label, start_date, end_date=None,
                                stressors=None, life_phase=None):
        self._add_node(id, "LifeContextWindow",
                       label=label, start_date=start_date, end_date=end_date,
                       stressors=stressors, life_phase=life_phase)

    def add_body_sensation(self, id, description, location=None, quality=None,
                           confidence=None):
        self._add_node(id, "BodySensation",
                       description=description, location=location,
                       quality=quality, confidence=confidence)

    # ── Asserted edges ───────────────────────────────────────────────────────

    def add_occurred_during(self, dream_id, lcw_id):
        self._add_edge(dream_id, lcw_id, "occurred_during")

    def add_contains(self, dream_id, symbol_id, prominence=None):
        self._add_edge(dream_id, symbol_id, "contains", prominence=prominence)

    def add_features(self, dream_id, char_id, role=None):
        self._add_edge(dream_id, char_id, "features", role=role)

    def add_takes_place_in(self, dream_id, setting_id, distortion_level=None):
        self._add_edge(dream_id, setting_id, "takes_place_in",
                       distortion_level=distortion_level)

    def add_evoked(self, dream_id, emotion_id, anchor=None, confidence=None):
        self._add_edge(dream_id, emotion_id, "evoked",
                       anchor=anchor, confidence=confidence)

    def add_expresses(self, dream_id, theme_id, source=None, strength=None):
        self._add_edge(dream_id, theme_id, "expresses",
                       source=source, strength=strength)

    def add_includes_sensation(self, dream_id, sensation_id):
        self._add_edge(dream_id, sensation_id, "includes_sensation")

    def add_contributes_to(self, symbol_id, theme_id):
        self._add_edge(symbol_id, theme_id, "contributes_to")

    def add_associated_with(self, char_id, theme_id):
        self._add_edge(char_id, theme_id, "associated_with")

    def add_represents(self, char_id, symbol_id):
        self._add_edge(char_id, symbol_id, "represents")

    def add_evokes(self, setting_id, theme_id):
        self._add_edge(setting_id, theme_id, "evokes")

    def add_related_to(self, theme_id1, theme_id2, relationship_type=None):
        self._add_edge(theme_id1, theme_id2, "related_to",
                       relationship_type=relationship_type)

    def add_recurs_as(self, dream_id1, dream_id2):
        self._add_edge(dream_id1, dream_id2, "recurs_as", source="user_asserted")

    # ── Auto-calculated edges ────────────────────────────────────────────────

    def recalculate_co_occurs_with(self):
        """Rebuild co_occurs_with edges from Dream→Symbol connections."""
        edges_to_remove = [
            (u, v, k)
            for u, v, k, d in self.G.edges(data=True, keys=True)
            if d.get("edge_type") == "co_occurs_with"
        ]
        for u, v, k in edges_to_remove:
            self.G.remove_edge(u, v, key=k)

        dream_symbols: dict[str, list[str]] = {}
        for u, v, k, d in self.G.edges(data=True, keys=True):
            if d.get("edge_type") == "contains":
                dream_symbols.setdefault(u, []).append(v)

        counts: dict[tuple[str, str], int] = {}
        for symbols in dream_symbols.values():
            for a, b in combinations(sorted(symbols), 2):
                counts[(a, b)] = counts.get((a, b), 0) + 1

        for (a, b), freq in counts.items():
            self.G.add_edge(a, b, key="co_occurs_with",
                            edge_type="co_occurs_with", frequency=freq)

    def recalculate_activates(self):
        """Rebuild activates edges from LifeContextWindow←Dream→Theme chains."""
        edges_to_remove = [
            (u, v, k)
            for u, v, k, d in self.G.edges(data=True, keys=True)
            if d.get("edge_type") == "activates"
        ]
        for u, v, k in edges_to_remove:
            self.G.remove_edge(u, v, key=k)

        dream_lcw: dict[str, str] = {}
        for u, v, k, d in self.G.edges(data=True, keys=True):
            if d.get("edge_type") == "occurred_during":
                dream_lcw[u] = v

        counts: dict[tuple[str, str], int] = {}
        for u, v, k, d in self.G.edges(data=True, keys=True):
            if d.get("edge_type") == "expresses":
                lcw = dream_lcw.get(u)
                if lcw:
                    counts[(lcw, v)] = counts.get((lcw, v), 0) + 1

        for (lcw, theme), freq in counts.items():
            self.G.add_edge(lcw, theme, key="activates",
                            edge_type="activates", frequency=freq)

    def recalculate_derived_edges(self):
        self.recalculate_co_occurs_with()
        self.recalculate_activates()

    # ── Queries ──────────────────────────────────────────────────────────────

    def get_all_dreams(self) -> list[dict]:
        """Return all Dream nodes sorted by date."""
        return sorted(
            [{"id": n, **attrs}
             for n, attrs in self.G.nodes(data=True)
             if attrs.get("node_type") == "Dream"],
            key=lambda d: d.get("date", "")
        )

    def get_node(self, node_id) -> dict | None:
        if node_id not in self.G:
            return None
        return {"id": node_id, **self.G.nodes[node_id]}

    def stats(self) -> dict:
        node_counts: dict[str, int] = {}
        for _, attrs in self.G.nodes(data=True):
            t = attrs.get("node_type", "unknown")
            node_counts[t] = node_counts.get(t, 0) + 1

        edge_counts: dict[str, int] = {}
        for _, _, d in self.G.edges(data=True):
            t = d.get("edge_type", "unknown")
            edge_counts[t] = edge_counts.get(t, 0) + 1

        return {"nodes": node_counts, "edges": edge_counts}
