#!/usr/bin/env python3
"""
Reads JSON content files and injects generated HTML into research.html
between BEGIN/END marker pairs:

  <!-- BEGIN:research-cards-generated -->   active research area cards
  <!-- BEGIN:teaching-generated -->         course cards from teaching.json
  <!-- BEGIN:previous-research-generated --> inactive area cards

Run from the repo root.
"""

import html
import json
import re
from pathlib import Path

RESEARCH_AREAS_JSON = Path("content/research_areas/research_areas.json")
TEACHING_JSON       = Path("content/teaching/teaching.json")
RESEARCH_HTML       = Path("research.html")

OVERLAY = "linear-gradient(rgba(24,52,70,0.4),rgba(24,52,70,0.4))"

CARDS_RE    = re.compile(r"<!-- BEGIN:research-cards-generated -->.*?<!-- END:research-cards-generated -->",       re.DOTALL)
TEACHING_RE = re.compile(r"<!-- BEGIN:teaching-generated -->.*?<!-- END:teaching-generated -->",                   re.DOTALL)
PREVIOUS_RE = re.compile(r"<!-- BEGIN:previous-research-generated -->.*?<!-- END:previous-research-generated -->", re.DOTALL)


def h(text: str) -> str:
    return html.escape(str(text))


# ── Research area cards ───────────────────────────────────────────────────────

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


# ── Teaching cards ────────────────────────────────────────────────────────────

def build_teaching_card(course: dict) -> str:
    quarter_tags = "".join(
        f'<span class="tag">{h(q)}</span>'
        for q in course.get("quarters", [])
    )
    quarters_html = f'        <div class="tags" style="margin:.4rem 0 .6rem">{quarter_tags}</div>\n' if quarter_tags else ""

    link_html = ""
    if course.get("link"):
        link_html = (
            f'\n          <a href="{course["link"]}" target="_blank" rel="noopener" '
            f'style="font-size:.875rem;font-weight:600;color:var(--cerulean);'
            f'text-decoration:none;display:inline-flex;align-items:center;gap:.3rem;margin-top:.75rem">'
            f'View course &rarr;</a>'
        )

    return (
        f'      <div class="card card-body">\n'
        f'        <p style="font-size:.75rem;font-weight:700;letter-spacing:.06em;'
        f'text-transform:uppercase;color:var(--cerulean);margin-bottom:.25rem">'
        f'{h(course.get("course_code", ""))}</p>\n'
        f'        <h4 class="text-deep-space">{h(course.get("name", ""))}</h4>\n'
        f'{quarters_html}'
        f'        <p style="font-size:.875rem">{h(course.get("description", ""))}</p>'
        f'{link_html}\n'
        f'      </div>'
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    areas   = json.loads(RESEARCH_AREAS_JSON.read_text())
    courses = json.loads(TEACHING_JSON.read_text()) if TEACHING_JSON.exists() else []
    page    = RESEARCH_HTML.read_text()

    active   = [a for a in areas if a.get("active")]
    inactive = [a for a in areas if not a.get("active")]

    # Active research cards
    cards_html = "\n".join(build_active_card(a) for a in active)
    page = CARDS_RE.sub(
        f"<!-- BEGIN:research-cards-generated -->\n{cards_html}\n<!-- END:research-cards-generated -->",
        page
    )
    print(f"  OK    research cards — {len(active)} area(s)")

    # Teaching cards
    if courses:
        teaching_cards = "\n".join(build_teaching_card(c) for c in courses)
        teaching_block = (
            f'    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));'
            f'gap:1.5rem;margin-top:1.5rem">\n'
            f'{teaching_cards}\n'
            f'    </div>'
        )
    else:
        teaching_block = '    <p style="color:var(--gray-500);font-style:italic">Coming soon.</p>'

    page = TEACHING_RE.sub(
        f"<!-- BEGIN:teaching-generated -->\n{teaching_block}\n<!-- END:teaching-generated -->",
        page
    )
    print(f"  OK    teaching — {len(courses)} course(s)")

    # Previous research
    if inactive:
        prev_cards = "\n".join(build_previous_card(a) for a in inactive)
        prev_block = (
            f'    <div style="margin-top:4rem">\n'
            f'      <h2 class="people-section-title">Previous Research</h2>\n'
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
