#!/usr/bin/env python3
"""
Fetches publications from the Semantic Scholar API for Meagan Mauter and writes
them to content/publications/publications.json, sorted by year (most recent first).

No API key or account required. Free and works in GitHub Actions.

Only includes publications from YEAR_CUTOFF onwards.
Existing entries are kept exactly as-is; only new publications are appended.

Usage:
    python3 scripts/fetch_publications.py

Requires:
    pip install requests
"""

import json
import re
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: run: pip install requests")
    sys.exit(1)

S2_AUTHOR_ID  = "14672527"            # Meagan Mauter on Semantic Scholar
S2_AUTHOR_ID2 = "2253994678"          # split S2 profile under "Meagan S. Mauter"
S2_AUTHOR_QUERY = "Meagan S. Mauter"  # used for auto-lookup if S2_AUTHOR_ID is None
YEAR_CUTOFF  = 2012
OUTPUT_PATH  = Path("content/publications/publications.json")

S2_BASE  = "https://api.semanticscholar.org/graph/v1"
HEADERS  = {"User-Agent": "WE3Lab-website-builder/1.0"}


# ── Helpers ───────────────────────────────────────────────────────────────────

_SMALL = {"a", "an", "the", "and", "but", "or", "for", "nor", "on", "at",
           "to", "by", "in", "of", "up", "as", "is", "it"}

def title_case(s: str) -> str:
    """Title-case a journal name, keeping small words lowercase except at the start."""
    words = s.split()
    return " ".join(
        w if (i > 0 and w.lower() in _SMALL) else w.capitalize()
        for i, w in enumerate(words)
    )

def _norm(title: str) -> str:
    return re.sub(r"\s+", " ", title.lower().strip())


def load_existing() -> dict:
    if not OUTPUT_PATH.exists():
        return {}
    try:
        data = json.loads(OUTPUT_PATH.read_text())
        return {_norm(e.get("title", "")): e for e in data}
    except Exception:
        return {}


def s2_get(path: str, params: dict) -> dict:
    url = S2_BASE + path
    for attempt in range(3):
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=20)
            if resp.status_code == 429:
                wait = 30 * (attempt + 1)
                print(f"  Rate limited — waiting {wait}s...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            print(f"  Request error: {e}")
            time.sleep(5)
    return {}


# ── Author ID lookup ──────────────────────────────────────────────────────────

def find_author_id(query: str) -> str | None:
    data = s2_get("/author/search", {
        "query": query,
        "fields": "name,affiliations,paperCount",
        "limit": 5,
    })
    candidates = data.get("data", [])
    if not candidates:
        print(f"No authors found for: {query!r}")
        return None

    # Prefer Stanford-affiliated candidates with the most papers
    stanford = [
        a for a in candidates
        if any("stanford" in af.lower() for af in a.get("affiliations", []))
    ]
    chosen = max(stanford or candidates, key=lambda a: a.get("paperCount", 0))
    print(f"Found author: {chosen['name']} ({chosen.get('paperCount', '?')} papers, ID: {chosen['authorId']})")
    return chosen["authorId"]


# ── Paper fetch ───────────────────────────────────────────────────────────────

def fetch_all_papers(author_id: str) -> list[dict]:
    fields  = "title,authors,year,journal,publicationVenue,externalIds"
    papers  = []
    offset  = 0
    limit   = 200

    while True:
        data = s2_get(f"/author/{author_id}/papers", {
            "fields": fields,
            "limit":  limit,
            "offset": offset,
        })
        batch = data.get("data", [])
        if not batch:
            break
        papers.extend(batch)
        print(f"  Retrieved {len(papers)} papers so far...")
        if len(batch) < limit:
            break
        offset += limit
        time.sleep(1)

    return papers


def paper_to_entry(p: dict) -> dict:
    title   = (p.get("title") or "").strip()
    authors = ", ".join(a.get("name", "") for a in p.get("authors", []))
    year    = p.get("year") or 0

    journal = ""
    if p.get("journal") and p["journal"].get("name"):
        journal = title_case(p["journal"]["name"])
    elif p.get("publicationVenue") and p["publicationVenue"].get("name"):
        journal = title_case(p["publicationVenue"]["name"])

    doi = (p.get("externalIds") or {}).get("DOI", "") or ""

    return {
        "title":          title,
        "authors":        authors,
        "journal":        journal,
        "year":           year,
        "doi":            doi,
        "research_areas": [],
        "team":           [],
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    global S2_AUTHOR_ID

    if not S2_AUTHOR_ID:
        print(f"Looking up Semantic Scholar ID for: {S2_AUTHOR_QUERY!r}")
        S2_AUTHOR_ID = find_author_id(S2_AUTHOR_QUERY)
        if not S2_AUTHOR_ID:
            print("Could not find author. Set S2_AUTHOR_ID manually at the top of the script.")
            sys.exit(1)

    print(f"\nFetching papers for author {S2_AUTHOR_ID}...")
    raw_papers = fetch_all_papers(S2_AUTHOR_ID)
    print(f"Retrieved {len(raw_papers)} papers from primary profile.")

    if S2_AUTHOR_ID2:
        print(f"Fetching papers from secondary profile {S2_AUTHOR_ID2}...")
        extra = fetch_all_papers(S2_AUTHOR_ID2)
        # Deduplicate by S2 paper ID
        seen_ids = {p.get("paperId") for p in raw_papers}
        new_extra = [p for p in extra if p.get("paperId") not in seen_ids]
        print(f"Found {len(new_extra)} additional paper(s) from secondary profile.")
        raw_papers.extend(new_extra)

    print(f"Total: {len(raw_papers)} papers.")

    existing = load_existing()
    results  = list(existing.values())
    added    = 0

    for p in raw_papers:
        year = p.get("year") or 0
        if year < YEAR_CUTOFF:
            continue

        title = (p.get("title") or "").strip()
        key   = _norm(title)

        if key in existing:
            continue

        entry = paper_to_entry(p)
        results.append(entry)
        existing[key] = entry
        added += 1
        print(f"  + {year} — {title[:70]}")

    results.sort(key=lambda p: (-p["year"], p["title"].lower()))

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nDone — {added} new publication(s) added, {len(results)} total written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
