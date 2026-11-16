"""Downloads/reads the sources listed in data/public_sources_manifest.yaml and stores them with provenance."""
from __future__ import annotations
import json, re
from datetime import date
import requests, yaml
from bs4 import BeautifulSoup
from src.paths import PUBLIC_MANIFEST, PUBLIC_SOURCES_DIR, ROOT

REQUIRED = ["source_id", "title", "date", "license_notes", "key_facts", "fields"]


def _clean(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["script", "style", "nav", "header", "footer"]):
        t.decompose()
    return re.sub(r"\s+\n", "\n", re.sub(r"[ \t]+", " ", soup.get_text("\n"))).strip()


def fetch_public():
    man = yaml.safe_load(PUBLIC_MANIFEST.read_text()) or {}
    srcs = man.get("sources") or []
    if not srcs:
        raise SystemExit(f"No sources in {PUBLIC_MANIFEST}. Fill it in (see comments), or use `build-data --synthetic-only`.")
    PUBLIC_SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    for s in srcs:
        miss = [k for k in REQUIRED if not s.get(k)]
        if miss:
            raise SystemExit(f"{s.get('source_id')}: missing {miss}")
        if len(s["key_facts"]) < 4:
            raise SystemExit(f"{s['source_id']}: write at least 4 key_facts")
        if s.get("local_file"):
            raw = (ROOT / s["local_file"]).read_text(encoding="utf-8")
            url = s.get("url") or f"local:{s['local_file']}"
        else:
            r = requests.get(s["url"], timeout=60, headers={"User-Agent": "springbase-router-research/1.0"})
            r.raise_for_status()
            raw, url = _clean(r.text), s["url"]
        words = raw.split()
        if len(words) < 150:
            raise SystemExit(f"{s['source_id']}: excerpt file looks empty or too short ({len(words)} words)")
        mx = int(s.get("max_words", 700))
        rec = {**s, "source_url": url, "extraction_date": date.today().isoformat(),
               "truncated": len(words) > mx, "original_word_count": len(words), "text": " ".join(words[:mx])}
        (PUBLIC_SOURCES_DIR / f"{s['source_id']}.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False))
        print(f"saved {s['source_id']} ({min(len(words), mx)} words, truncated={rec['truncated']})")
