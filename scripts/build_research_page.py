#!/usr/bin/env python3
"""
Reads content/research_areas/research_areas.json and injects research area
cards into research.html between BEGIN/END marker pairs:

  <!-- BEGIN:research-cards-generated -->   active area cards (2-col grid)
  <!-- BEGIN:previous-research-generated --> inactive area cards

Run from the repo root.
"""

import html
import json
import re
from pathlib import Path

RESEARCH_AREAS_JSON = Path("content/research_areas/research_areas.json")
RESEARCH_HTML       = Path("research.html")

OVERLAY = "linear-gradient(rgba(24,52,70,0.4),rgba(24,52,70,0.4))"

CARDS_RE    = re.compile(r"<!-- BEGIN:research-cards-generated -->.*?<!-- END:research-cards-generated -->",       re.DOTALL)
PREVIOUS_RE = re.compile(r"<!-- BEGIN:previous-research-generated -->.*?<!-- END:previous-research-generated -->", re.DOTALL)


def h(text: str) -> str:
    return html.escape(str(text))


def build_active_card(area: dict) -> str:
    img_css = f"background:{OVERLAY}, url('{area['image']}') center/cover no-repeat"
    return (
        f'      <a class="research-card" href="{area["file"]}">\n'
        f'        <div class="research-card-inner">\n'
        f'          <div class="research-card-banner" style="{img_css}"></div>\n'
        f'          <div class="research-card-body">\n'
        f'            <h3>{h(area["name"])}</h3>\n'
        f'            <p>{h(area["description"])}</p>\n'
        f'            <span class="research-card-link">Learn more &rarr;</span>\n'
        f'          </div>\n'
        f'        </div>\n'
        f'      </a>'
    )


def build_previous_card(area: dict) -> str:
    return (
        f'      <a class="research-card" href="{area["file"]}" style="max-width:380px;display:block">\n'
        f'        <div class="research-card-inner" style="opacity:.8">\n'
        f'          <div class="research-card-body">\n'
        f'            <h3>{h(area["name"])}</h3>\n'
        f'            <p>{h(area["description"])}</p>\n'
        f'            <span class="research-card-link" style="color:var(--gray-500)">View archive &rarr;</span>\n'
        f'          </div>\n'
        f'        </div>\n'
        f'      </a>'
    )


def main():
    areas = json.loads(RESEARCH_AREAS_JSON.read_text())
    page  = RESEARCH_HTML.read_text()

    active   = [a for a in areas if a.get("active")]
    inactive = [a for a in areas if not a.get("active")]

    # Active cards
    cards_html = "\n".join(build_active_card(a) for a in active)
    page = CARDS_RE.sub(
        f"<!-- BEGIN:research-cards-generated -->\n{cards_html}\n<!-- END:research-cards-generated -->",
        page
    )
    print(f"  OK    active cards — {len(active)} area(s)")

    # Previous research
    if inactive:
        prev_cards = "\n".join(build_previous_card(a) for a in inactive)
        prev_block = (
            f'    <div style="margin-top:4rem">\n'
            f'      <h2 class="text-deep-space" style="margin-bottom:.5rem">Previous Research</h2>\n'
            f'      <p style="color:var(--gray-500);max-width:640px;margin-bottom:2rem">'
            f'This thrust was the foundation of the lab\'s early work and produced many of our most-cited '
            f'publications. The group has since evolved into our current research directions.</p>\n'
            f'{prev_cards}\n'
            f'    </div>'
        )
    else:
        prev_block = ""

    page = PREVIOUS_RE.sub(
        f"<!-- BEGIN:previous-research-generated -->\n{prev_block}\n<!-- END:previous-research-generated -->",
        page
    )
    print(f"  OK    previous research — {len(inactive)} area(s)")

    RESEARCH_HTML.write_text(page)


if __name__ == "__main__":
    main()
