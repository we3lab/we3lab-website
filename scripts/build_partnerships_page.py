#!/usr/bin/env python3
"""
Reads content/partnerships/partnerships.json and injects partner logo grids
into partnerships.html.

Each partner entry:
  {
    "name":    "Partner Name",
    "website": "https://partner.com",
    "logo":    "content/partnerships/logos/partner.png",
    "section": "research"   // or "utility"
  }

Run from the repo root.
"""

import html
import json
import re
from pathlib import Path

PARTNERSHIPS_JSON = Path("content/partnerships/partnerships.json")
PARTNERSHIPS_HTML = Path("partnerships.html")

RESEARCH_RE = re.compile(
    r"<!-- BEGIN:research-partners-generated -->.*?<!-- END:research-partners-generated -->",
    re.DOTALL,
)
UTILITY_RE = re.compile(
    r"<!-- BEGIN:utility-partners-generated -->.*?<!-- END:utility-partners-generated -->",
    re.DOTALL,
)

PLACEHOLDER = '    <p style="color:var(--gray-500);font-style:italic">Content coming soon.</p>'


def h(text: str) -> str:
    return html.escape(str(text))


def build_partner_grid(partners: list) -> str:
    if not partners:
        return PLACEHOLDER

    cards = []
    for p in partners:
        logo = p.get("logo", "").lstrip("/")
        name = p.get("name", "")
        url  = p.get("website", "#")

        if logo and Path(logo).exists():
            inner_html = (
                f'<img src="{h(logo)}" alt="{h(name)}" '
                f'style="max-height:120px;max-width:220px;width:auto;object-fit:contain">'
            )
        else:
            inner_html = (
                f'<div style="height:120px;display:flex;align-items:center;justify-content:center;padding:.5rem">'
                f'<span style="font-size:1.1rem;font-weight:700;color:var(--deep-space);text-align:center;line-height:1.3">{h(name)}</span></div>'
            )

        cards.append(
            f'      <a href="{h(url)}" target="_blank" rel="noopener" '
            f'style="display:flex;align-items:center;justify-content:center;'
            f'padding:.75rem .5rem;border:1px solid var(--gray-200);border-radius:var(--radius);'
            f'text-decoration:none;color:inherit;transition:box-shadow .2s;'
            f'background:var(--white)" '
            f'onmouseover="this.style.boxShadow=\'var(--shadow-md)\'" '
            f'onmouseout="this.style.boxShadow=\'none\'">\n'
            f'        {inner_html}\n'
            f'      </a>'
        )

    grid = "\n".join(cards)
    return (
        f'    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));'
        f'gap:1.5rem;margin-bottom:1rem">\n'
        f'{grid}\n'
        f'    </div>'
    )


def main():
    partners = json.loads(PARTNERSHIPS_JSON.read_text()) if PARTNERSHIPS_JSON.exists() else []

    research = [p for p in partners if p.get("section") == "research"]
    utility  = [p for p in partners if p.get("section") == "utility"]

    page = PARTNERSHIPS_HTML.read_text()

    research_block = build_partner_grid(research)
    page = RESEARCH_RE.sub(
        f"<!-- BEGIN:research-partners-generated -->\n{research_block}\n<!-- END:research-partners-generated -->",
        page,
    )

    utility_block = build_partner_grid(utility)
    page = UTILITY_RE.sub(
        f"<!-- BEGIN:utility-partners-generated -->\n{utility_block}\n<!-- END:utility-partners-generated -->",
        page,
    )

    PARTNERSHIPS_HTML.write_text(page)
    print(f"  OK    partnerships — {len(research)} research, {len(utility)} utility")


if __name__ == "__main__":
    main()
