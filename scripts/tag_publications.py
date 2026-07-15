#!/usr/bin/env python3
"""
Populates the team list on publications from TAG_FROM_YEAR onwards by matching
author strings against members and alumni netIDs.

Only fills team fields that are currently empty — manual edits are preserved.
Research area tagging is done manually in publications.json.

Usage:
    python3 scripts/tag_publications.py
"""

import json
import re
from pathlib import Path

# Paths are relative to the repo root, regardless of where the script is run from
REPO_ROOT         = Path(__file__).parent.parent
PUBLICATIONS_JSON = REPO_ROOT / "content/publications/publications.json"
MEMBERS_JSON      = REPO_ROOT / "content/members/members.json"
ALUMNI_JSON       = REPO_ROOT / "content/members/alumni.json"

TAG_FROM_YEAR = 2022  # only tag publications from this year onwards


# ── Author → netID lookup ─────────────────────────────────────────────────────

def build_author_lookup(members: list, alumni: list) -> dict:
    """Return a dict mapping last_name.lower() → list of (netID, first_initial, full_name).

    Used to match Semantic Scholar author strings like 'M. Mauter' or 'Corisa A Wong'.
    """
    lookup: dict[str, list] = {}
    for person in members + alumni:
        netid = person.get("netID", "")
        if not netid:
            continue
        # Strip honorifics before extracting name parts
        name = re.sub(r"^Dr\.\s+", "", person["name"], flags=re.IGNORECASE).strip()
        parts = name.split()
        if not parts:
            continue
        last          = parts[-1].lower()
        first_initial = parts[0][0].lower()
        lookup.setdefault(last, []).append((netid, first_initial, name))
    return lookup


def match_author(author_str: str, lookup: dict) -> str | None:
    """Match a single author string to a netID using last name + first initial.

    Returns the netID if a unique match is found, or None if ambiguous/absent.
    """
    parts = author_str.strip().split()
    if not parts:
        return None

    last       = parts[-1].lower()
    candidates = lookup.get(last, [])
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0][0]

    # Multiple people with the same last name — disambiguate by first initial
    first_initial = parts[0].rstrip(".").lower()[0] if parts[0] else ""
    for netid, initial, _ in candidates:
        if initial == first_initial:
            return netid

    return None  # still ambiguous after initial check, skip


def match_authors(authors_str: str, lookup: dict) -> list[str]:
    """Split a comma-separated author string and return a list of matched netIDs."""
    netids = []
    seen   = set()
    for author in authors_str.split(","):
        author = author.strip()
        if not author:
            continue
        nid = match_author(author, lookup)
        if nid and nid not in seen:
            netids.append(nid)
            seen.add(nid)
    return netids


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    pubs    = json.loads(PUBLICATIONS_JSON.read_text())
    members = json.loads(MEMBERS_JSON.read_text())
    alumni  = json.loads(ALUMNI_JSON.read_text())

    lookup      = build_author_lookup(members, alumni)
    tagged_team = 0

    for pub in pubs:
        if pub.get("year", 0) < TAG_FROM_YEAR:
            continue

        title = pub.get("title", "")

        # Only auto-fill team if it hasn't been set manually
        if not pub.get("team"):
            team = match_authors(pub.get("authors", ""), lookup)
            if team:
                pub["team"] = team
                tagged_team += 1

        print(
            f"  {pub.get('year')} | {title[:55]:<55} | "
            f"areas={pub.get('research_areas')} | team={pub.get('team')}"
        )

    PUBLICATIONS_JSON.write_text(json.dumps(pubs, indent=2, ensure_ascii=False))
    print(f"\nDone — tagged team on {tagged_team} pub(s).")


if __name__ == "__main__":
    main()
