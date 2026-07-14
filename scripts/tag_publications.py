#!/usr/bin/env python3
"""
For publications from TAG_FROM_YEAR onwards, infers research_areas from the
title and populates the team list by matching authors against members/alumni.

Only fills fields that are currently empty — manual edits are preserved.

Usage:
    python3 scripts/tag_publications.py
"""

import json
import re
from pathlib import Path

PUBLICATIONS_JSON = Path("content/publications/publications.json")
MEMBERS_JSON      = Path("content/members/members.json")
ALUMNI_JSON       = Path("content/members/alumni.json")

TAG_FROM_YEAR = 2022  # only tag publications from this year onwards


# ── Research area keyword rules ───────────────────────────────────────────────
# Each entry maps an area ID to a list of keywords (case-insensitive).
# A paper is tagged to an area if ANY keyword appears in its title.

AREA_KEYWORDS = {
    "separations": [
        "desalin", "membrane", "osmosis", "brine", "concentrate", "separation",
        "nanofiltration", "ultrafiltration", "electrodialysis", "technoeconomic",
        "mineral extract", "salt", "evaporation", "distillation", "ion exchange",
        "crystalliz", "brackish", "seawater", "reverse osmosis",
    ],
    "flexibility": [
        "flexib", "demand response", "load shift", "load-shift", "grid integrat",
        "grid-integrat", "electricity price", "carbon emission", "greenhouse",
        "emission reduct", "dispatch", "curtailment", "energy storage",
        "wastewater treatment plant", "wwtp", "data center",
    ],
    "planning": [
        "planning", "infrastructure", "capacity expansion", "water supply",
        "drought", "stochastic", "uncertainty", "portfolio", "siting",
        "watershed", "nutrient remov", "water reuse", "non-traditional water",
        "alternative water", "groundwater", "permitting", "adaptive",
    ],
    "data": [
        "data infrastructure", "ontology", "schema", "digital twin", "dataset",
        "machine learning", "artificial intelligence", "pypes", "acquirium",
        "data management", "data platform", "knowledge graph",
    ],
    "wef": [
        "water-energy-food", "water energy food", "wef nexus", "food security",
        "agricultural water", "food system", "agri-environ", "crop water",
        "food-energy-water", "nexus", "irrigation",
    ],
    "technology": [
        "advanced oxidation", "disinfection byproduct", "chlorin", "ozon",
        "ultraviolet", "photolysis", "radical", "dbp", "trihalomethane",
        "haloacetic", "bromide", "bromate", "aop ", "fouling", "grafted",
        "zwitterion", "polyethersulfone", "ultrafiltration membrane",
        "membrane transport", "membrane fouling", "membrane permeab",
        "infrared microscop", "nusselt", "heat transfer",
    ],
}


def infer_research_areas(title: str) -> list[str]:
    t = title.lower()
    areas = []
    for area, keywords in AREA_KEYWORDS.items():
        if any(kw in t for kw in keywords):
            areas.append(area)
    return areas


# ── Author → netID lookup ─────────────────────────────────────────────────────

def build_author_lookup(members: list, alumni: list) -> dict:
    """
    Returns a dict mapping last_name.lower() → list of (netID, first_initial, full_name).
    Used to match S2 author strings like 'M. Mauter' or 'Corisa A Wong'.
    """
    lookup: dict[str, list] = {}
    for person in members + alumni:
        netid = person.get("netID", "")
        if not netid:
            continue
        # Strip honorifics
        name = re.sub(r"^Dr\.\s+", "", person["name"], flags=re.IGNORECASE).strip()
        parts = name.split()
        if not parts:
            continue
        last  = parts[-1].lower()
        first_initial = parts[0][0].lower() if parts else ""
        lookup.setdefault(last, []).append((netid, first_initial, name))
    return lookup


def match_author(author_str: str, lookup: dict) -> str | None:
    """
    Try to match an author string (e.g. 'M. Zaniolo' or 'Corisa A Wong')
    to a netID using last-name + optional first-initial disambiguation.
    Returns netID or None.
    """
    parts = author_str.strip().split()
    if not parts:
        return None

    last  = parts[-1].lower()
    candidates = lookup.get(last, [])
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0][0]

    # Disambiguate by first initial
    first_initial = parts[0].rstrip(".").lower()[0] if parts[0] else ""
    for netid, initial, _ in candidates:
        if initial == first_initial:
            return netid

    return None  # ambiguous, skip


def match_authors(authors_str: str, lookup: dict) -> list[str]:
    """Split a comma-separated author string and return matched netIDs."""
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

    lookup  = build_author_lookup(members, alumni)

    tagged_team = 0

    for pub in pubs:
        year = pub.get("year", 0)
        if year < TAG_FROM_YEAR:
            continue

        title = pub.get("title", "")

        # Match team only if currently empty
        if not pub.get("team"):
            authors_str = pub.get("authors", "")
            team = match_authors(authors_str, lookup)
            if team:
                pub["team"] = team
                tagged_team += 1

        print(
            f"  {year} | {title[:55]:<55} | "
            f"areas={pub.get('research_areas')} | team={pub.get('team')}"
        )

    PUBLICATIONS_JSON.write_text(json.dumps(pubs, indent=2, ensure_ascii=False))
    print(f"\nDone — tagged team on {tagged_team} pub(s).")


if __name__ == "__main__":
    main()
