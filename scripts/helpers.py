"""
Shared helper functions used across all WE3Lab build scripts.

Import what you need:
    from helpers import h, hm, member_slug, initials, find_image, \
                        content_to_img_url, member_display, build_project_card

Image conventions
-----------------
Source images live in content/ and are copied into docs/images/ by the build
scripts so GitHub Pages can serve them. The URL paths used in generated HTML are:

    images/headshots/         ← member headshots
    images/partner_logos/     ← partnership logos
    images/research_area_images/ ← research area photos
"""

import html as _html
import re
from pathlib import Path

# Source directory for member headshot images (read by find_image)
IMAGES_DIR = Path("content/members/headshots")


# ── HTML escaping ─────────────────────────────────────────────────────────────

def h(text: str) -> str:
    """HTML-escape a value for safe insertion into HTML attributes and content."""
    return _html.escape(str(text))


def hm(text: str) -> str:
    """HTML-escape text, converting [label](url) Markdown links to <a> tags.

    Ordinary text is escaped normally; only [text](url) patterns become links
    that open in a new tab.
    """
    parts = re.split(r'(\[[^\]]+\]\([^)]+\))', str(text))
    out = []
    for part in parts:
        m = re.match(r'\[([^\]]+)\]\(([^)]+)\)', part)
        if m:
            out.append(
                f'<a href="{_html.escape(m.group(2))}" target="_blank" rel="noopener">'
                f'{_html.escape(m.group(1))}</a>'
            )
        else:
            out.append(_html.escape(part))
    return ''.join(out)


# ── Name utilities ────────────────────────────────────────────────────────────

def member_slug(name: str) -> str:
    """Convert a member name to a CamelCase URL slug, stripping honorifics.

    Examples:
        'Dr. Foo Bar' → 'FooBar'
        'Jane Smith'  → 'JaneSmith'
    """
    clean = re.sub(r"^Dr\.\s+", "", name, flags=re.IGNORECASE).strip()
    return "".join(w.capitalize() for w in clean.split())


def initials(name: str) -> str:
    """Return two-character uppercase initials (first + last), stripping honorifics.

    Examples:
        'Dr. Jane Smith' → 'JS'
        'Alice'          → 'AL'
    """
    clean = re.sub(r"^Dr\.\s+", "", name, flags=re.IGNORECASE).strip()
    parts = clean.split()
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else parts[0][:2].upper()


# ── Image lookup ──────────────────────────────────────────────────────────────

def find_image(name: str) -> str | None:
    """Return the docs/images/ URL path for a member's headshot, or None if not found.

    Checks both CamelCase and lowercase variants with .png and .jpg extensions
    inside IMAGES_DIR. Returns a URL path suitable for use in HTML src attributes
    (e.g. 'images/headshots/JaneSmith.jpg'), not the filesystem path.
    """
    slug = member_slug(name)
    for ext in ("png", "jpg"):
        for variant in (slug, slug.lower()):
            p = IMAGES_DIR / f"{variant}.{ext}"
            if p.exists():
                return f"images/headshots/{p.name}"
    return None


def content_to_img_url(src: str) -> str:
    """Convert a content/ source image path to its docs/images/ URL equivalent.

    The URL is formed from the image's immediate parent folder name and filename,
    so it works for any image type stored under content/:

        content/research_areas/research_area_images/photo.jpg
            → images/research_area_images/photo.jpg

        content/partnerships/partner_logos/logo.png
            → images/partner_logos/logo.png

    Returns an empty string if src is empty.
    """
    if not src:
        return ""
    p = Path(src)
    return f"images/{p.parent.name}/{p.name}"


# ── Member display chip ───────────────────────────────────────────────────────

def member_display(m: dict, asset_prefix: str = "../",
                   member_link_prefix: str = "../people/") -> str:
    """Render a member as a small chip: circular avatar + name.

    Links to the member's profile page unless the member is an alumnus
    (``m["is_alumni"] == True``), in which case a plain span is returned.

    Args:
        m: Member dict with at least a ``"name"`` key.
        asset_prefix: Path prefix prepended to image ``src`` attributes.
        member_link_prefix: Path prefix prepended to profile page hrefs.
    """
    slug = member_slug(m["name"])
    img  = find_image(m["name"])

    av = (
        f'<div style="width:44px;height:44px;border-radius:50%;overflow:hidden;'
        f'flex-shrink:0;display:flex;align-items:center;justify-content:center;">'
        f'<img src="{asset_prefix}{img}" style="width:100%;height:100%;object-fit:cover" '
        f'alt="{h(m["name"])}"></div>'
        if img else
        f'<div style="width:44px;height:44px;border-radius:50%;overflow:hidden;'
        f'flex-shrink:0;display:flex;align-items:center;justify-content:center;'
        f'background:var(--cerulean);font-size:.8rem;font-weight:700;color:#fff;">'
        f'{initials(m["name"])}</div>'
    )

    name_span = f'<span style="font-weight:600;font-size:.875rem">{h(m["name"])}</span>'

    if m.get("is_alumni"):
        # Alumni have no profile page — render as plain text chip
        return (
            f'<span style="display:inline-flex;align-items:center;gap:.5rem;color:inherit">'
            f'{av}{name_span}</span>'
        )
    return (
        f'<a href="{member_link_prefix}{slug}.html" '
        f'style="display:inline-flex;align-items:center;gap:.5rem;'
        f'text-decoration:none;color:inherit">'
        f'{av}{name_span}</a>'
    )


# ── Project card ──────────────────────────────────────────────────────────────

def build_project_card(project: dict, members_by_netid: dict,
                       asset_prefix: str = "../",
                       member_link_prefix: str = "../people/") -> str:
    """Render a single project as an expandable <details> card.

    The card shows the project title in a <summary> bar. Expanding it reveals:
    team member chips, an overview paragraph, external links, and funders.

    Args:
        project: A project dict from projects.json.
        members_by_netid: Mapping of netID → member dict (active + alumni).
        asset_prefix: Path prefix for avatar image src attributes.
        member_link_prefix: Path prefix for member profile page links.
    """
    summary = (
        f'  <summary>\n'
        f'    <span class="project-expand-title">{h(project["title"])}</span>\n'
        f'  </summary>'
    )

    # Team Members
    team_items = []
    for netid in project.get("team", []):
        m = members_by_netid.get(netid)
        if m:
            team_items.append(member_display(m, asset_prefix, member_link_prefix))
        else:
            team_items.append(f'<span style="font-weight:600;font-size:.875rem">{h(netid)}</span>')

    team_html = ""
    if team_items:
        team_html = (
            f'    <p class="project-section-label">Team Members</p>\n'
            f'    <div style="display:flex;flex-wrap:wrap;gap:.75rem;margin-bottom:1rem">\n'
            f'      ' + "\n      ".join(team_items) + '\n    </div>\n'
        )

    # Overview
    overview_html = (
        f'    <p class="project-section-label">Overview</p>\n'
        f'    <p style="font-size:.9rem;margin-bottom:.75rem">'
        f'{hm(project.get("description", ""))}</p>\n'
    )

    # External links
    links_html = ""
    if project.get("links"):
        link_tags = "".join(
            f'<a href="{lnk["url"]}" target="_blank" rel="noopener">{h(lnk["label"])}</a>'
            for lnk in project["links"] if lnk.get("url")
        )
        if link_tags:
            links_html = (
                f'    <p class="project-section-label">Links</p>\n'
                f'    <div class="project-expand-links">{link_tags}</div>\n'
            )

    # Funding sources
    funding_html = ""
    funders = [f for f in project.get("funding", []) if f]
    if funders:
        items = "".join(f"<li>{h(f)}</li>" for f in funders)
        funding_html = (
            f'    <p class="project-section-label" style="margin-top:.75rem">Supported By</p>\n'
            f'    <ul style="margin:.25rem 0 0 1.1rem;font-size:.875rem;line-height:1.7">'
            f'{items}</ul>\n'
        )

    body = (
        f'  <div class="project-expand-body">\n'
        f'{team_html}'
        f'{overview_html}'
        f'{links_html}'
        f'{funding_html}'
        f'  </div>'
    )
    return f'<details class="project-expand">\n{summary}\n{body}\n</details>'
