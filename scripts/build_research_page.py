#!/usr/bin/env python3
"""
Reads JSON content files and injects generated HTML into:
  research-areas.html  — research cards + previous research
  teaching.html        — course cards

Run from the repo root.
"""

import json
import re
from pathlib import Path

from helpers import h, hm, content_to_img_url

RESEARCH_AREAS_JSON  = Path("content/research_areas/research_areas.json")
TEACHING_JSON        = Path("content/teaching/teaching.json")
DISSERTATIONS_JSON   = Path("content/dissertations/dissertations.json")
PUBLICATIONS_JSON    = Path("content/publications/publications.json")
RESEARCH_AREAS_HTML  = Path("docs/research-areas.html")
TEACHING_HTML        = Path("docs/teaching.html")
PUBLICATIONS_HTML    = Path("docs/publications.html")

OVERLAY = "linear-gradient(rgba(24,52,70,0.4),rgba(24,52,70,0.4))"

CARDS_RE         = re.compile(r"<!-- BEGIN:research-cards-generated -->.*?<!-- END:research-cards-generated -->",       re.DOTALL)
DISSERTATIONS_RE = re.compile(r"<!-- BEGIN:dissertations-generated -->.*?<!-- END:dissertations-generated -->",       re.DOTALL)
TEACHING_RE = re.compile(r"<!-- BEGIN:teaching-generated -->.*?<!-- END:teaching-generated -->",                   re.DOTALL)
PREVIOUS_RE      = re.compile(r"<!-- BEGIN:previous-research-generated -->.*?<!-- END:previous-research-generated -->", re.DOTALL)
PUBLICATIONS_RE  = re.compile(r"<!-- BEGIN:publications-generated -->.*?<!-- END:publications-generated -->", re.DOTALL)


# ── Research area cards ───────────────────────────────────────────────────────

def build_active_card(area: dict) -> str:
    img_css = f"background:{OVERLAY}, url('{content_to_img_url(area["image"])}') center/cover no-repeat"
    return (
        f'      <a class="research-card" href="{area["file"]}">\n'
        f'        <div class="research-card-inner">\n'
        f'          <div class="research-card-banner" style="{img_css}"></div>\n'
        f'          <div class="research-card-body">\n'
        f'            <h3>{h(area["name"])}</h3>\n'
        f'            <p>{hm(area["description"])}</p>\n'
        f'            <span class="research-card-link">Learn more &rarr;</span>\n'
        f'          </div>\n'
        f'        </div>\n'
        f'      </a>'
    )


def build_previous_card(area: dict) -> str:
    return (
        f'      <a class="research-card" href="{area["file"]}" style="max-width:380px">\n'
        f'        <div class="research-card-inner" style="opacity:.8">\n'
        f'          <div class="research-card-body">\n'
        f'            <h3>{h(area["name"])}</h3>\n'
        f'            <p>{hm(area["description"])}</p>\n'
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
        f'        <p style="font-size:.875rem">{hm(course.get("description", ""))}</p>'
        f'{link_html}\n'
        f'      </div>'
    )


# ── Dissertation cards ────────────────────────────────────────────────────────

def youtube_id(url: str) -> str | None:
    """Extract YouTube video ID from a youtu.be or youtube.com URL."""
    m = re.search(r'(?:youtu\.be/|[?&]v=)([A-Za-z0-9_-]{11})', url or "")
    return m.group(1) if m else None


def build_dissertation_card(d: dict) -> str:
    vid_id = youtube_id(d.get("link", ""))
    link   = d.get("link", "").strip()
    title  = h(d.get("title", ""))
    name   = h(d.get("name", ""))
    date   = h(d.get("date", ""))

    if vid_id:
        embed_url  = f"https://www.youtube.com/embed/{vid_id}"
        copy_js    = (f"navigator.clipboard.writeText('{link}').then(function(){{"
                      f"var b=this;b.innerHTML='<i class=\\'fa-solid fa-check\\'></i>';"
                      f"setTimeout(function(){{b.innerHTML='<i class=\\'fa-solid fa-link\\'></i>';}},1500);}}.bind(this))")
        video_html = (
            f'<div class="dissertation-video-wrap">\n'
            f'          <iframe src="{embed_url}" title="{name}" '
            f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" '
            f'allowfullscreen loading="lazy"></iframe>\n'
            f'          <button class="dissertation-copy-btn" onclick="{copy_js}" title="Copy link">'
            f'<i class="fa-solid fa-link"></i></button>\n'
            f'        </div>'
        )
    else:
        video_html = ('<div class="dissertation-thumb">'
                      '<div class="dissertation-thumb-placeholder">🎓</div></div>')

    title_html = f'<p class="dissertation-title">{title}</p>' if title else ""

    return (
        f'      <div class="dissertation-card">\n'
        f'        {video_html}\n'
        f'        <div class="dissertation-body">\n'
        f'          <p class="dissertation-date">{date}</p>\n'
        f'          <p class="dissertation-name">{name}</p>\n'
        f'          {title_html}\n'
        f'        </div>\n'
        f'      </div>'
    )


# ── Publications page ─────────────────────────────────────────────────────────

def build_publications_page(publications: list) -> str:
    if not publications:
        return '    <p style="color:var(--gray-500);font-style:italic">No publications listed yet.</p>'
    sorted_pubs = sorted(publications, key=lambda p: p.get("year", 0), reverse=True)
    by_year: dict = {}
    for pub in sorted_pubs:
        year = str(pub.get("year", ""))
        by_year.setdefault(year, []).append(pub)
    blocks = []
    for year, pubs in by_year.items():
        items = []
        for pub in pubs:
            doi  = pub.get("doi", "").strip()
            href = f"https://doi.org/{doi}" if doi else "#"
            doi_span = f'<span style="font-size:.8rem;color:var(--gray-500)">{h(doi)}</span>' if doi else ""
            items.append(
                f'  <li style="margin-bottom:1rem">\n'
                f'    <a href="{href}" target="_blank" rel="noopener" style="display:block;color:inherit;text-decoration:none">\n'
                f'      <strong>{h(pub.get("title",""))}</strong><br>\n'
                f'      <span style="font-size:.9rem">{h(pub.get("authors",""))}. <em>{h(pub.get("journal",""))}</em>, {pub.get("year","")}.</span>\n'
                f'      {"<br>" + doi_span if doi_span else ""}\n'
                f'    </a>\n'
                f'  </li>'
            )
        blocks.append(
            f'    <h3 style="color:var(--deep-space);margin:2rem 0 .75rem;padding-bottom:.4rem;border-bottom:2px solid var(--gray-200)">{h(year)}</h3>\n'
            f'    <ul style="list-style:none;padding:0;margin:0">\n'
            + "\n".join(items) +
            f'\n    </ul>'
        )
    return "\n".join(blocks)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    areas         = json.loads(RESEARCH_AREAS_JSON.read_text())
    courses       = json.loads(TEACHING_JSON.read_text()) if TEACHING_JSON.exists() else []
    dissertations = json.loads(DISSERTATIONS_JSON.read_text()) if DISSERTATIONS_JSON.exists() else []
    publications  = json.loads(PUBLICATIONS_JSON.read_text()) if PUBLICATIONS_JSON.exists() else []

    active   = [a for a in areas if a.get("active")]
    inactive = [a for a in areas if not a.get("active")]

    # ── research-areas.html: research cards + previous research ──────────────
    ra_page = RESEARCH_AREAS_HTML.read_text()

    cards_html = "\n".join(build_active_card(a) for a in active)
    ra_page = CARDS_RE.sub(
        f"<!-- BEGIN:research-cards-generated -->\n{cards_html}\n<!-- END:research-cards-generated -->",
        ra_page
    )
    print(f"  OK    research cards — {len(active)} area(s)")

    if inactive:
        prev_cards = "\n".join(build_previous_card(a) for a in inactive)
        prev_block = (
            f'    <div style="margin-top:4rem">\n'
            f'      <h2 class="people-section-title">Previous Research</h2>\n'
            f'      <p style="color:var(--gray-500);max-width:640px;margin-bottom:2rem">'
            f'These thrusts helped lay the foundations of the lab\'s early work and produced many of our most-cited '
            f'publications. The group has since evolved into our current research directions.</p>\n'
            f'      <div style="display:flex;gap:1.5rem;flex-wrap:wrap">\n'
            f'{prev_cards}\n'
            f'      </div>\n'
            f'    </div>'
        )
    else:
        prev_block = ""

    ra_page = PREVIOUS_RE.sub(
        f"<!-- BEGIN:previous-research-generated -->\n{prev_block}\n<!-- END:previous-research-generated -->",
        ra_page
    )
    print(f"  OK    previous research — {len(inactive)} area(s)")

    # Dissertations strip
    if dissertations:
        from datetime import datetime

        def parse_date(d):
            raw = d.get("date", "")
            for fmt in ("%B %d, %Y", "%B %Y", "%Y-%m-%d", "%Y"):
                try:
                    return datetime.strptime(raw.strip(), fmt)
                except ValueError:
                    continue
            return datetime.min

        sorted_d = sorted(dissertations, key=parse_date, reverse=True)
        d_cards  = "\n".join(build_dissertation_card(d) for d in sorted_d)
    else:
        d_cards = '      <p style="color:var(--gray-500);font-style:italic">Coming soon.</p>'
    RESEARCH_AREAS_HTML.write_text(ra_page)

    # ── teaching.html: course cards ───────────────────────────────────────────
    t_page = TEACHING_HTML.read_text()

    if courses:
        teaching_block = "\n".join(build_teaching_card(c) for c in courses)
    else:
        teaching_block = '      <p style="color:var(--gray-500);font-style:italic">Coming soon.</p>'

    t_page = TEACHING_RE.sub(
        f"<!-- BEGIN:teaching-generated -->\n{teaching_block}\n<!-- END:teaching-generated -->",
        t_page
    )
    print(f"  OK    teaching — {len(courses)} course(s)")

    TEACHING_HTML.write_text(t_page)

    # ── publications.html: dissertations + publications ───────────────────────
    p_page = PUBLICATIONS_HTML.read_text()

    p_page = DISSERTATIONS_RE.sub(
        f"<!-- BEGIN:dissertations-generated -->\n{d_cards}\n<!-- END:dissertations-generated -->",
        p_page
    )
    print(f"  OK    dissertations — {len(dissertations)} entry(ies)")

    pub_block = build_publications_page(publications)
    p_page = PUBLICATIONS_RE.sub(
        f"<!-- BEGIN:publications-generated -->\n{pub_block}\n<!-- END:publications-generated -->",
        p_page
    )
    PUBLICATIONS_HTML.write_text(p_page)
    print(f"  OK    publications — {len(publications)} entry(ies)")


if __name__ == "__main__":
    main()
