#!/usr/bin/env python3
"""
Reads content/news/news.json and content/research_areas/research_areas.json
and injects generated HTML into index.html between BEGIN/END markers:

  <!-- BEGIN:news-generated -->    news cards in the news strip
  <!-- BEGIN:mission-generated --> mission diamond circles

Mission circles are arranged evenly around a hypothetical circle so that:
  - 4 areas → diamond  (top / right / bottom / left)
  - 3 areas → upward triangle
  - 5 areas → pentagon
  - etc.

Run from the repo root.
"""

import json
import math
import re
import shutil
from pathlib import Path

from helpers import content_to_img_url

NEWS_JSON           = Path("content/news/news.json")
RESEARCH_AREAS_JSON = Path("content/research_areas/research_areas.json")
INDEX_HTML          = Path("docs/index.html")

OVERLAY = "linear-gradient(rgba(255,255,255,.7),rgba(255,255,255,.7))"

NEWS_RE    = re.compile(r"<!-- BEGIN:news-generated -->.*?<!-- END:news-generated -->",       re.DOTALL)
MISSION_RE = re.compile(r"<!-- BEGIN:mission-generated -->.*?<!-- END:mission-generated -->", re.DOTALL)

# Geometry constants (must match .mission-diamond and .mission-circle CSS)
CONTAINER_PX = 500   # .mission-diamond width/height
CIRCLE_PX    = 200   # .mission-circle  width/height
RADIUS       = 150   # px from container center to circle center


# ── Position calculation ──────────────────────────────────────────────────────

def circle_positions(n: int) -> list[tuple[int, int]]:
    """
    Return (top, left) pixel offsets for n circles evenly spaced around a
    hypothetical circle, with the first circle at the 12-o'clock position.
    """
    cx = cy = CONTAINER_PX / 2
    half = CIRCLE_PX / 2
    positions = []
    for i in range(n):
        angle = -math.pi / 2 + (2 * math.pi / n) * i
        top  = round(cy + RADIUS * math.sin(angle) - half)
        left = round(cx + RADIUS * math.cos(angle) - half)
        positions.append((top, left))
    return positions


# ── HTML builders ─────────────────────────────────────────────────────────────

def build_news_card(item: dict) -> str:
    org_html = (
        f'\n          <p style="font-size:.78rem;color:#8c96a3;margin:0">{item["organization"]}</p>'
        if item.get("organization") else ""
    )
    return (
        f'      <div class="card" style="background:#F8F9FA;min-width:240px;width:max-content;'
        f'max-width:380px;flex-shrink:0;scroll-snap-align:start">\n'
        f'        <div class="card-body">\n'
        f'          <span style="font-size:.75rem;color:#1D729B;font-weight:600">{item["date"]}</span>\n'
        f'          <h4 style="color:#183446;margin:.4rem 0 .3rem">\n'
        f'            <a href="{item["link"]}" style="color:inherit;text-decoration:none">{item["headline"]}</a>\n'
        f'          </h4>{org_html}\n'
        f'        </div>\n'
        f'      </div>'
    )


def build_mission_circle(area: dict, top: int, left: int) -> str:
    bg    = f"{OVERLAY}, url('{content_to_img_url(area['image'])}') center/cover no-repeat"
    name  = area["name"].replace("&", "&amp;")
    style = f"top:{top}px;left:{left}px;background:{bg}"
    return (
        f'        <div class="mission-circle" style="{style}">\n'
        f'          <h4 class="text-deep-space">'
        f'<a href="{area["file"]}" style="color:inherit;text-decoration:none">{name}</a>'
        f'</h4>\n'
        f'        </div>'
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    # Copy research area images into docs/images/ so GitHub Pages can serve them
    src = Path("content/research_areas/research_area_images")
    dst = Path("docs/images/research_area_images")
    if src.exists():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)

    html  = INDEX_HTML.read_text()
    items = json.loads(NEWS_JSON.read_text())
    areas = [a for a in json.loads(RESEARCH_AREAS_JSON.read_text()) if a.get("active")]

    # News cards
    cards = "\n".join(build_news_card(item) for item in items)
    html  = NEWS_RE.sub(
        f"<!-- BEGIN:news-generated -->\n{cards}\n<!-- END:news-generated -->", html
    )
    print(f"  OK    news — {len(items)} item(s)")

    # Mission circles with computed positions
    positions = circle_positions(len(areas))
    circles   = "\n".join(
        build_mission_circle(a, top, left)
        for a, (top, left) in zip(areas, positions)
    )
    html = MISSION_RE.sub(
        f"<!-- BEGIN:mission-generated -->\n{circles}\n<!-- END:mission-generated -->", html
    )
    print(f"  OK    mission circles — {len(areas)} area(s) arranged as N={len(areas)} polygon")

    INDEX_HTML.write_text(html)


if __name__ == "__main__":
    main()
