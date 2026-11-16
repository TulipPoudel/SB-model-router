"""Builds the 20 public-source tasks from the curated UN sources using fixed templates.
Plan (category, difficulty): meeting 8 (3E/3M/2H), research 6 (2/2/2), slides 2 (M,H), extraction 4 (E,M,H,H)."""
from __future__ import annotations
import json
from src.paths import PUBLIC_SOURCES_DIR

PLAN = ([("meeting_summary", d) for d in ["easy"] * 3 + ["medium"] * 3 + ["hard"] * 2]
        + [("research_brief", d) for d in ["easy", "easy", "medium", "medium", "hard", "hard"]]
        + [("slide_outline", "medium"), ("slide_outline", "hard")]
        + [("data_extraction", d) for d in ["easy", "medium", "hard", "hard"]])
RUBRIC = {"meeting_summary": "meeting_v1", "email_draft": "email_v1", "research_brief": "research_v1",
          "slide_outline": "slides_v1", "data_extraction": "extraction_v1"}
FMT = {"meeting_summary": "bullet_points", "research_brief": "brief", "slide_outline": "slide_outline", "data_extraction": "json"}
K = {"easy": 3, "medium": 4, "hard": 99}


def load_sources():
    srcs = [json.load(open(p, encoding="utf-8")) for p in sorted(PUBLIC_SOURCES_DIR.glob("*.json"))]
    if not 8 <= len(srcs) <= 12:
        raise SystemExit(f"Expected 8-12 public sources in {PUBLIC_SOURCES_DIR}, found {len(srcs)}.")
    return srcs


def _header(s):
    return f"Source: {s['title']} ({s.get('symbol', 'no symbol')}), {s['date']}. Speaker: {s.get('speaker', 'n/a')}, {s.get('country_or_org', 'n/a')}.\n\n"


def build_public_tasks():
    srcs = load_sources()
    n, tasks, counters = len(srcs), [], {}
    for i, (cat, diff) in enumerate(PLAN):
        c = counters[(cat, diff)] = counters.get((cat, diff), 0) + 1
        hard_research = cat == "research_brief" and diff == "hard"
        if hard_research:                      # fixed disjoint pairs -> small, well-defined source groups
            pair = [srcs[0], srcs[1]] if c == 1 else [srcs[2], srcs[3]]
        else:
            pair = [srcs[i % n]]
        s = pair[0]
        facts = [f for p in pair for f in p["key_facts"][:K[diff]]]
        if cat == "meeting_summary":
            desc = {"easy": "Summarise the following official statement delivered at a United Nations meeting.",
                    "medium": "Summarise the statement and list the specific commitments or calls for action made by the speaker.",
                    "hard": "Summarise the statement with attribution. Distinguish what the speaker explicitly states from what is only implied, and list any statistics the speaker cites."}[diff]
            reqs = {"easy": ["Write 3 to 4 bullet points", "Name the speaker and the country/organisation", "Only include what is in the text"],
                    "medium": ["Start with a 2-sentence summary", "List each commitment/call for action as its own bullet", "State clearly if no concrete commitment is made", "Do not add information absent from the text"],
                    "hard": ["Maximum 200 words", "Sections: Explicit positions / Implied positions / Statistics cited", "Do not attribute anything to the speaker that is not in the text", "If no statistics are cited, say so"]}[diff]
            inp = _header(s) + s["text"]
            if diff == "hard":
                facts += [f"statistic: {x}" for x in s["fields"].get("statistics") or []]
        elif cat == "research_brief":
            desc = {"easy": "Write a one-paragraph research brief on the priorities stated in the following UN statement.",
                    "medium": "Write a structured research brief on the following UN statement with the sections: Position, Evidence cited, Open questions.",
                    "hard": "Write a research brief comparing the two statements: areas of agreement, differences in emphasis, and what cannot be concluded from these texts alone."}[diff]
            reqs = {"easy": ["80-120 words", "Use only information in the source"],
                    "medium": ["Use the three headings given", "Separate what the speaker says from your inference", "Use only information in the source"],
                    "hard": ["Maximum 250 words", "Sections: Agreement / Differences / Cannot conclude", "Attribute each point to the correct statement", "Use only information in the sources"]}[diff]
            inp = "\n\n".join(f"--- SOURCE {k + 1} ---\n" + _header(p) + p["text"] for k, p in enumerate(pair))
        elif cat == "slide_outline":
            desc = {"medium": "Create a 6-slide briefing outline for policy staff summarising this statement.",
                    "hard": "Create a 5-slide outline for a 5-minute briefing to senior officials based on this statement."}[diff]
            reqs = {"medium": ["Exactly 6 slides", "Title + 2-3 bullets per slide", "A visual recommendation per slide", "Use only information in the source"],
                    "hard": ["Exactly 5 slides", "Max 3 bullets per slide", "Include a visual recommendation and a one-sentence speaker note per slide", "Do not state anything not in the source", "Separate what is stated from what is implied"]}[diff]
            inp = _header(s) + s["text"]
        else:  # data_extraction - header-free: truth is what the excerpt itself states
            keys = {"easy": ["speaker", "country_or_org", "date"],
                    "medium": ["speaker", "country_or_org", "date", "main_topics", "session_or_meeting"],
                    "hard": ["speaker", "country_or_org", "date", "session_or_meeting", "main_topics", "commitments", "statistics"]}[diff]
            desc = "Extract the requested fields from the following UN statement into JSON."
            reqs = [f"Return JSON with keys: {', '.join(keys)}", "Use null if the text does not state a value and [] for an empty list",
                    "Dates in ISO format", "No text outside the JSON"] + (["Do not guess anything not stated in the text"] if diff == "hard" else [])
            inp = s["text"]
            facts = [f"{k}: {json.dumps(s['fields'].get(k), ensure_ascii=False)}" for k in keys]
        tasks.append({"category": cat, "difficulty": diff, "source_type": "public",
                      "source_id": "+".join(p["source_id"] for p in pair), "source_ids": [p["source_id"] for p in pair],
                      "source_group": None, "scenario_family": "un_" + cat, "task_template": f"un_{cat}_{diff}",
                      "task_description": desc, "input": inp, "requirements": reqs, "expected_facts": facts,
                      "output_format": FMT[cat], "rubric_id": RUBRIC[cat],
                      "provenance": [{k: p.get(k) for k in ("source_id", "symbol", "source_url", "date", "speaker",
                                      "country_or_org", "extraction_date", "license_notes", "truncated")} for p in pair]})
    return tasks
