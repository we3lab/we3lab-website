#!/usr/bin/env python3
"""
Builds the people content in people.html from:
  content/members/meagan.json  → <!-- BEGIN/END:pi-generated -->
  content/members/members.json → <!-- BEGIN/END:people-generated -->

Also generates a shell profile page at people/{Slug}.html for every
active (non-alumni) member except Meagan.

Run from the repo root.
"""

import html
import json
import re
from pathlib import Path

MEAGAN_JSON  = Path("content/members/meagan.json")
MEMBERS_JSON = Path("content/members/members.json")
PROJECTS_JSON      = Path("content/projects/projects.json")
PUBLICATIONS_JSON  = Path("content/publications/publications.json")
ALUMNI_JSON = Path("content/members/alumni.json")
PEOPLE_HTML = Path("people.html")
IMAGES_DIR = Path("content/members/images")
PEOPLE_DIR = Path("people")

PI_RE = re.compile(r"<!-- BEGIN:pi-generated -->.*?<!-- END:pi-generated -->", re.DOTALL)
PEOPLE_RE = re.compile(r"<!-- BEGIN:people-generated -->.*?<!-- END:people-generated -->", re.DOTALL)

AV_COUNT = 8

ROLE_ORDER = ["staff", "postdoc", "phd student", "ms student", "undergrad", "alumni"]
ROLE_LABELS = {
    "postdoc":    "Postdoctoral Researchers",
    "phd student":"PhD Students",
    "ms student": "MS Students",
    "undergrad":  "Undergraduate Researchers",
    "staff":      "Research Staff",
    "alumni":     "Alumni",
}
ROLE_DISPLAY = {
    "postdoc":           "Postdoctoral Researcher",
    "phd student":       "PhD Student",
    "ms student":        "MS Student",
    "undergrad":         "Undergraduate Student",
    "staff":             "Research Staff",
    "staff scientist":   "Staff Scientist",
    "research engineer": "Research Engineer",
}

# Maps specific roles to their section group in ROLE_ORDER
ROLE_GROUP = {
    "staff scientist":   "staff",
    "research engineer": "staff",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def h(text: str) -> str:
    return html.escape(str(text))

def hm(text: str) -> str:
    """HTML-escape text, converting [label](url) markdown links to <a> tags."""
    parts = re.split(r'(\[[^\]]+\]\([^)]+\))', str(text))
    out = []
    for part in parts:
        m = re.match(r'\[([^\]]+)\]\(([^)]+)\)', part)
        if m:
            out.append(f'<a href="{html.escape(m.group(2))}" target="_blank" rel="noopener">{html.escape(m.group(1))}</a>')
        else:
            out.append(html.escape(part))
    return ''.join(out)


def member_slug(name: str) -> str:
    """'Dr. Foo Bar' → 'FooBar'"""
    clean = re.sub(r"^Dr\.\s+", "", name, flags=re.IGNORECASE).strip()
    return "".join(w.capitalize() for w in clean.split())


def initials(name: str) -> str:
    clean = re.sub(r"^Dr\.\s+", "", name, flags=re.IGNORECASE).strip()
    parts = clean.split()
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else parts[0][:2].upper()


def find_image(name: str) -> str | None:
    slug = member_slug(name)
    for ext in ("png", "jpg"):
        for variant in (slug, slug.lower()):
            p = IMAGES_DIR / f"{variant}.{ext}"
            if p.exists():
                return str(p)
    return None


def avatar(name: str, av_class: str, size: int = 100, prefix: str = "") -> str:
    """prefix: path prefix to prepend to image src (e.g. '../' for subdir pages)."""
    img = find_image(name)
    style_attr = f' style="width:{size}px;height:{size}px"' if size != 100 else ""
    if img:
        return f'<div class="person-avatar {av_class}"{style_attr}><img src="{prefix}{img}" alt="{h(name)}"></div>'
    return f'<div class="person-avatar {av_class}"{style_attr}>{initials(name)}</div>'


def av_class_for(name: str) -> str:
    """Deterministic avatar colour based on name so it stays consistent across rebuilds."""
    return f"av-{(sum(ord(c) for c in member_slug(name)) % AV_COUNT) + 1}"


def social_links(m: dict) -> str:
    parts = []
    scholar = m.get("scholar_url") or (
        f"https://scholar.google.com/citations?user={m['scholar_id']}"
        if m.get("scholar_id") else ""
    )
    if scholar:
        parts.append(f'<a href="{scholar}" target="_blank" rel="noopener" title="Google Scholar">'
                     f'<i class="fa-brands fa-google-scholar"></i></a>')
    if m.get("linkedin"):
        parts.append(f'<a href="{m["linkedin"]}" target="_blank" rel="noopener" title="LinkedIn">'
                     f'<i class="fa-brands fa-linkedin"></i></a>')
    if m.get("website"):
        parts.append(f'<a href="{m["website"]}" target="_blank" rel="noopener" title="Website"><i class="fa-solid fa-link"></i></a>')
    if m.get("cv"):
        parts.append(f'<a href="{m["cv"]}" target="_blank" rel="noopener">CV</a>')
    return " &middot; ".join(parts)


# ── PI section ────────────────────────────────────────────────────────────────

def build_pi(pi: dict) -> str:
    bio_html = "\n".join(
        f'        <p style="font-size:.9rem;color:var(--blk);line-height:1.6;margin-bottom:.75rem">{hm(p)}</p>'
        for p in pi.get("bio", [])
    )
    edu_items = "\n".join(
        f'            <li>{h(e)}</li>' for e in pi.get("education", [])
    )
    scholar_link = (
        f'<a href="{pi["scholar_url"]}" target="_blank" rel="noopener" title="Google Scholar" '
        f'style="display:inline-flex;align-items:center;opacity:.75;transition:opacity .2s">'
        f'<i class="fa-brands fa-google-scholar" style="font-size:22px"></i></a>'
    ) if pi.get("scholar_url") else ""
    linkedin_link = (
        f'<a href="{pi["linkedin"]}" target="_blank" rel="noopener" title="LinkedIn" '
        f'style="display:inline-flex;align-items:center;opacity:.75;transition:opacity .2s">'
        f'<i class="fa-brands fa-linkedin" style="font-size:22px"></i></a>'
    ) if pi.get("linkedin") else ""
    social = " ".join(filter(None, [scholar_link, linkedin_link]))

    return f"""\
    <div style="display:flex;gap:2rem;align-items:flex-start;margin-bottom:2.5rem">
      <div style="display:flex;flex-direction:column;align-items:center;flex-shrink:0;width:385px">
        <img src="{pi['image']}" alt="{h(pi['name'])}" style="width:385px;height:385px;border-radius:20%;object-fit:cover">
        <div style="margin-top:1rem;width:100%">
          <p style="font-size:.8rem;font-weight:600;color:var(--blk);margin-bottom:.35rem">Education</p>
          <ul style="font-size:.8rem;color:#444;line-height:1.7;margin:0;padding-left:1.1rem">
{edu_items}
          </ul>
        </div>
      </div>
      <div>
        <h4 style="font-size:1.15rem;color:var(--blk);margin-bottom:.25rem">{h(pi['name'])}</h4>
        <div style="display:flex;gap:.6rem;align-items:center;margin-top:.35rem">
          {social}
        </div>
        <p style="font-size:.85rem;color:#555;margin-top:.4rem;margin-bottom:.75rem">{hm(pi['title'])}</p>
{bio_html}
      </div>
    </div>"""


# ── Member cards ──────────────────────────────────────────────────────────────

def build_member_card(m: dict, av_class: str) -> str:
    role = m.get("role", "").lower()
    label = ROLE_DISPLAY.get(role, role.title())
    links = social_links(m)
    slug = member_slug(m["name"])
    links_html = f'        <div class="links">{links}</div>\n' if links else ""

    return (
        f'      <div class="person-card">\n'
        f'        <a href="people/{slug}.html">{avatar(m["name"], av_class)}</a>\n'
        f'        <h4><a href="people/{slug}.html" style="color:inherit;text-decoration:none">{h(m["name"])}</a></h4>\n'
        f'        <div class="role">{label}</div>\n'
        f'{links_html}'
        f'      </div>'
    )


def build_alumni_card(a: dict, av_class: str) -> str:
    parts = []
    if a.get("scholar_url"):
        parts.append(f'<a href="{a["scholar_url"]}" target="_blank" rel="noopener" title="Google Scholar">'
                     f'<i class="fa-brands fa-google-scholar"></i></a>')
    if a.get("linkedin"):
        parts.append(f'<a href="{a["linkedin"]}" target="_blank" rel="noopener" title="LinkedIn">'
                     f'<i class="fa-brands fa-linkedin"></i></a>')
    links_html = f'        <div class="links">{" &middot; ".join(parts)}</div>\n' if parts else ""
    deg_html   = f'        <div class="role">{h(a.get("degree_year", ""))}</div>\n' if a.get("degree_year") else ""
    place_html = f'        <p class="research-area">{hm(a.get("placement", ""))}</p>\n' if a.get("placement") else ""

    return (
        f'      <div class="person-card">\n'
        f'        {avatar(a["name"], av_class)}\n'
        f'        <h4>{h(a["name"])}</h4>\n'
        f'{deg_html}'
        f'{place_html}'
        f'{links_html}'
        f'      </div>'
    )


def _last_name(name: str) -> str:
    clean = re.sub(r"^Dr\.\s+", "", name, flags=re.IGNORECASE).strip()
    return clean.split()[-1].lower()


def _degree_year(a: dict) -> int:
    """Extract the numeric year from a degree_year string like 'PhD 2022'."""
    m = re.search(r"\d{4}", a.get("degree_year", ""))
    return int(m.group()) if m else 0


def build_people(members: list, alumni: list) -> str:
    by_role: dict[str, list] = {r: [] for r in ROLE_ORDER if r != "alumni"}
    for m in members:
        key = m.get("role", "").lower()
        key = ROLE_GROUP.get(key, key)  # map staff scientist / research engineer → staff
        if key in by_role:
            by_role[key].append(m)

    sections = []
    av_idx = 0

    # Active member sections — alphabetical by last name within each role
    # ms student and undergrad are merged into one combined section
    COMBINED = {"ms student", "undergrad"}
    combined_label = "Undergraduate & Master's Students"
    combined_emitted = False

    for role in ROLE_ORDER:
        if role == "alumni":
            continue
        if role in COMBINED:
            if combined_emitted:
                continue
            # Emit combined section for ms student + undergrad together
            group = sorted(
                by_role.get("ms student", []) + by_role.get("undergrad", []),
                key=lambda m: _last_name(m["name"])
            )
            combined_emitted = True
            label = combined_label
        else:
            group = sorted(by_role.get(role, []), key=lambda m: _last_name(m["name"]))
            label = ROLE_LABELS[role]
        if not group:
            continue
        cards = []
        for m in group:
            av = f"av-{(av_idx % AV_COUNT) + 1}"
            av_idx += 1
            cards.append(build_member_card(m, av))
        sections.append(
            f'    <h2 class="people-section-title">{label}</h2>\n'
            f'    <div class="people-grid">\n'
            + "\n".join(cards) + "\n"
            f'    </div>'
        )

    # Alumni section — most recent degree year first
    if alumni:
        sorted_alumni = sorted(alumni, key=_degree_year, reverse=True)
        cards = []
        for a in sorted_alumni:
            av = f"av-{(av_idx % AV_COUNT) + 1}"
            av_idx += 1
            cards.append(build_alumni_card(a, av))
        sections.append(
            f'    <h2 class="people-section-title">{ROLE_LABELS["alumni"]}</h2>\n'
            f'    <div class="people-grid">\n'
            + "\n".join(cards) + "\n"
            f'    </div>'
        )

    return "\n".join(sections)


# ── Profile sub-pages ─────────────────────────────────────────────────────────

NAV_DROPDOWN = """\
          <ul class="dropdown-content">
            <li><a href="../research/separations.html">Separations</a></li>
            <li><a href="../research/energyflexibility.html">Water-Energy Flexibility</a></li>
            <li><a href="../research/infrastructureplanning.html">Systems Planning</a></li>
            <li><a href="../research/waterenergyfoodpolicies.html">WEF Policies</a></li>
            <li class="dropdown-divider"></li>
            <li><a href="../research/dissertations.html">Past Dissertations</a></li>
          </ul>"""


def build_member_projects(netid: str, projects: list, members_by_netid: dict = None) -> str:
    """Return expandable project cards for a member's profile page."""
    if members_by_netid is None:
        members_by_netid = {}
    member_projects = [p for p in projects if netid in p.get("team", [])]
    if not member_projects:
        return '<p style="color:var(--gray-500);font-style:italic">No projects listed yet.</p>'

    cards = []
    for project in member_projects:
        summary = (
            f'  <summary>\n'
            f'    <span class="project-expand-title">{h(project["title"])}</span>\n'
            f'  </summary>'
        )

        # Team Members
        team_items = []
        for tid in project.get("team", []):
            m = members_by_netid.get(tid)
            if not m:
                team_items.append(f'<span style="font-weight:600;font-size:.875rem">{h(tid)}</span>')
                continue
            slug = member_slug(m["name"])
            img = find_image(m["name"])
            av = (
                f'<div class="person-avatar" style="width:44px;height:44px;border-radius:50%;'
                f'font-size:.8rem;flex-shrink:0"><img src="../{img}" alt="{h(m["name"])}"></div>'
                if img else
                f'<div class="person-avatar av-1" style="width:44px;height:44px;border-radius:50%;'
                f'font-size:.8rem;flex-shrink:0">{initials(m["name"])}</div>'
            )
            if m.get("is_alumni"):
                team_items.append(
                    f'<span style="display:flex;align-items:center;gap:.5rem;color:inherit">'
                    f'{av}<span style="font-weight:600;font-size:.875rem">{h(m["name"])}</span></span>'
                )
            else:
                team_items.append(
                    f'<a href="{slug}.html" style="display:flex;align-items:center;gap:.5rem;'
                    f'text-decoration:none;color:inherit">'
                    f'{av}<span style="font-weight:600;font-size:.875rem">{h(m["name"])}</span></a>'
                )
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
            f'    <p style="font-size:.9rem;margin-bottom:.75rem">{hm(project.get("description", ""))}</p>\n'
        )

        # Resources
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

        # Supported By
        funding_html = ""
        funders = [f for f in project.get("funding", []) if f]
        if funders:
            items = "".join(f"<li>{h(f)}</li>" for f in funders)
            funding_html = (
                f'    <p class="project-section-label" style="margin-top:.75rem">Supported By</p>\n'
                f'    <ul style="margin:.25rem 0 0 1.1rem;font-size:.875rem;line-height:1.7">{items}</ul>\n'
            )

        body = (
            f'  <div class="project-expand-body">\n'
            f'{team_html}'
            f'{overview_html}'
            f'{links_html}'
            f'{funding_html}'
            f'  </div>'
        )
        cards.append(f'<details class="project-expand">\n{summary}\n{body}\n</details>')
    return "\n".join(cards)


def build_member_publications(netid: str, publications: list) -> str:
    member_pubs = [p for p in publications if netid in p.get("team", [])]
    if not member_pubs:
        return '<p style="color:var(--gray-500);font-style:italic">No publications listed yet.</p>'
    sorted_pubs = sorted(member_pubs, key=lambda p: p.get("year", 0), reverse=True)
    cards = []
    for pub in sorted_pubs:
        doi  = pub.get("doi", "").strip()
        href = f"https://doi.org/{doi}" if doi else "#"
        doi_span = f'<span>{h(doi)}</span>' if doi else ""
        cards.append(
            f'<li>\n'
            f'  <a href="{href}" target="_blank" rel="noopener" '
            f'style="display:block;color:inherit;text-decoration:none">\n'
            f'    <strong>{h(pub.get("title",""))}</strong>\n'
            f'    {h(pub.get("authors",""))}. <em>{h(pub.get("journal",""))}</em>, {pub.get("year","")}.' 
            f'\n    {doi_span}\n'
            f'  </a>\n'
            f'</li>'
        )
    return '<ul class="publication-list">\n' + "\n".join(cards) + '\n</ul>'


def build_contact_section(m: dict, top_offset: str = "0") -> str:
    """Build the Contact sidebar. Returns empty string if nothing to show."""
    link_style = "color:rgba(255,255,255,.85);text-decoration:none;display:flex;align-items:center;gap:.5rem;font-size:.875rem;margin-bottom:.4rem"
    items = []
    email = m.get("email", "").strip()
    if email:
        items.append(
            f'<a href="mailto:{email}" style="{link_style}">'
            f'<i class="fa-solid fa-envelope"></i> {email}</a>'
        )
    if m.get("scholar_url"):
        items.append(
            f'<a href="{m["scholar_url"]}" target="_blank" rel="noopener" style="{link_style}">'
            f'<i class="fa-brands fa-google-scholar"></i> Google Scholar</a>'
        )
    if m.get("linkedin"):
        items.append(
            f'<a href="{m["linkedin"]}" target="_blank" rel="noopener" style="{link_style}">'
            f'<i class="fa-brands fa-linkedin"></i> LinkedIn</a>'
        )
    if m.get("website"):
        items.append(
            f'<a href="{m["website"]}" target="_blank" rel="noopener" style="{link_style}">'
            f'<i class="fa-solid fa-link"></i> Website</a>'
        )
    if m.get("cv"):
        items.append(
            f'<a href="{m["cv"]}" target="_blank" rel="noopener" style="{link_style}">'
            f'<i class="fa-solid fa-file-lines"></i> CV</a>'
        )
    if not items:
        return ""
    label = '<p style="font-size:.72rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:rgba(255,255,255,.45);margin-bottom:.6rem">Contact</p>'
    return (
        f'    <div style="flex-shrink:0;margin-top:{top_offset}">\n'
        f'      {label}\n      '
        + "\n      ".join(items)
        + "\n    </div>"
    )


def build_profile_page(m: dict, projects: list = None, members_by_netid: dict = None, publications: list = None) -> str:
    if projects is None:
        projects = []
    if members_by_netid is None:
        members_by_netid = {}
    if publications is None:
        publications = []
    role_display = ROLE_DISPLAY.get(m.get("role", "").lower(), m.get("role", "").title())
    bio_text     = m.get("bio", "").strip()
    img_path     = find_image(m["name"])

    bio_html = (
        f'      <p style="color:rgba(255,255,255,.8);font-size:1.1rem;'
        f'line-height:1.6;margin-top:1rem;margin-bottom:0">{hm(bio_text)}</p>'
        if bio_text else
        f'      <p style="color:rgba(255,255,255,.45);font-size:1.05rem;font-style:italic;'
        f'margin-top:1rem;margin-bottom:0">Bio coming soon.</p>'
    )

    contact = build_contact_section(m, top_offset="220px")

    if img_path:
        left_col = f"""\
      <div style="display:flex;align-items:flex-start;gap:1.25rem">
        <img src="../{img_path}" alt="{h(m['name'])}"
             style="width:220px;height:220px;border-radius:50%;object-fit:cover;flex-shrink:0">
        <div style="min-height:220px;display:flex;flex-direction:column;justify-content:center">
          <h1 style="margin-bottom:.2rem">{h(m["name"])}</h1>
          <p style="color:rgba(255,255,255,.75);margin:0">{role_display}</p>
        </div>
      </div>
{bio_html}"""
        banner_content = (
            f'    <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:3rem;margin-top:.5rem">\n'
            f'      <div style="flex:1">\n{left_col}\n      </div>\n'
            + (contact + "\n" if contact else "")
            + "    </div>"
        )
    else:
        left_col = f"""\
    <h1 style="margin-bottom:.2rem;margin-top:.5rem">{h(m["name"])}</h1>
    <p style="color:rgba(255,255,255,.75);margin:0">{role_display}</p>
{bio_html}"""
        no_img_contact = build_contact_section(m, top_offset="0")
        if no_img_contact:
            banner_content = (
                f'    <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:3rem;margin-top:.5rem">\n'
                f'      <div style="flex:1">\n{left_col}\n      </div>\n'
                + no_img_contact + "\n    </div>"
            )
        else:
            banner_content = left_col

    return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{h(m["name"])} — WE3 Lab</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="../assets/css/style.css" />
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" crossorigin="anonymous" />
</head>
<body>

<!-- ── Site Header (Sticky) ────────────────────────────── -->
<div class="site-header">
  <div class="identity-bar">
    <a href="https://www.stanford.edu">Stanford University</a>
  </div>
  <nav class="nav">
    <div class="container">
      <a class="nav-logo" href="../index.html">
        <img src="../assets/logos/WE3_Lab_Logo_white.png" alt="WE3 Lab" height="96">
      </a>
      <button class="nav-hamburger" aria-label="Toggle navigation" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
      <ul class="nav-links">
        <li><a href="../index.html">Home</a></li>
        <li><a href="../people.html" class="active">Who We Are</a></li>
        <li class="dropdown">
          <a href="../research-areas.html">What We Do</a>
          <ul class="dropdown-content">
            <li><a href="../research-areas.html">Research</a></li>
            <li><a href="../teaching.html">Teaching</a></li>
            <li><a href="../publications.html">Publications &amp; Presentations</a></li>
            <li><a href="https://github.com/we3lab" target="_blank" rel="noopener">GitHub Repositories</a></li>
          </ul>
        </li>
        <li><a href="../partnerships.html">Why We Do It</a></li>
        <li><a href="../contact.html">Join Us</a></li>
      </ul>
    </div>
  </nav>
</div>

<!-- ── Page Banner ─────────────────────────────────────── -->
<div class="page-banner">
  <div class="container">
    <div class="breadcrumb"><a href="../people.html">Who We Are</a> &rsaquo; {h(m["name"])}</div>
{banner_content}
  </div>
</div>

<!-- ── Profile Content ─────────────────────────────────── -->
<section class="section">
  <div class="container">

    <h2 class="text-deep-space" style="margin-bottom:1rem">Projects</h2>
{build_member_projects(m.get("netID",""), projects, members_by_netid)}

    <h2 class="text-deep-space" style="margin-top:3rem;margin-bottom:1rem">Publications</h2>
{build_member_publications(m.get("netID",""), publications)}

    <div style="margin-top:3rem">
      <a href="../people.html" class="btn btn-navy">&larr; Back to Who We Are</a>
    </div>
  </div>
</section>

<!-- ── Footer ──────────────────────────────────────────── -->
<footer class="footer-stanford">
  <div class="footer-stanford-inner">
    <div class="footer-stanford-wordmark">
      <a href="https://www.stanford.edu">Stanford<br>University</a>
    </div>
    <div class="footer-stanford-content">
      <nav aria-label="global footer menu">
        <ul class="footer-stanford-links-primary">
          <li><a href="https://www.stanford.edu">Stanford Home</a></li>
          <li><a href="https://visit.stanford.edu/plan/">Maps &amp; Directions</a></li>
          <li><a href="https://www.stanford.edu/search/">Search Stanford</a></li>
          <li><a href="https://emergency.stanford.edu">Emergency Info</a></li>
        </ul>
        <ul class="footer-stanford-links-secondary">
          <li><a href="https://www.stanford.edu/site/terms/">Terms of Use</a></li>
          <li><a href="https://www.stanford.edu/site/privacy/">Privacy</a></li>
          <li><a href="https://uit.stanford.edu/security/copyright-infringement">Copyright</a></li>
          <li><a href="https://adminguide.stanford.edu/chapter-1/subchapter-5/policy-1-5-4">Trademarks</a></li>
          <li><a href="https://studentservices.stanford.edu/more-resources/student-policies/non-academic/non-discrimination">Non-Discrimination</a></li>
          <li><a href="https://www.stanford.edu/site/accessibility">Accessibility</a></li>
        </ul>
      </nav>
      <div class="footer-stanford-copy">&copy; Stanford University.&nbsp; Stanford, California 94305.</div>
    </div>
    <div class="footer-we3-col">
      <img src="../assets/logos/WE3_Lab_Logo_white.png" alt="WE3 Lab" height="96">
      <div class="footer-social">
        <a href="https://www.linkedin.com/company/we3-lab" target="_blank" rel="noopener" title="LinkedIn"><i class="fa-brands fa-linkedin"></i></a>
        <a href="https://scholar.google.com/citations?user=04f-_PIAAAAJ&hl=en&oi=ao" target="_blank" rel="noopener" title="Google Scholar"><i class="fa-brands fa-google-scholar"></i></a>
        <a href="https://github.com/we3lab" target="_blank" rel="noopener" title="GitHub"><i class="fa-brands fa-github"></i></a>
        <a href="mailto:mauter@stanford.edu" title="Email"><i class="fa-solid fa-envelope"></i></a>
      </div>
    </div>
  </div>
</footer>

<script>
  const btn = document.querySelector('.nav-hamburger');
  const links = document.querySelector('.nav-links');
  if (btn && links) {{
    btn.addEventListener('click', () => {{
      links.classList.toggle('open');
      btn.setAttribute('aria-expanded', links.classList.contains('open'));
    }});
  }}
</script>

</body>
</html>
"""


def generate_profile_pages(members: list, projects: list, members_by_netid: dict, publications: list = None) -> int:
    if publications is None:
        publications = []
    PEOPLE_DIR.mkdir(exist_ok=True)
    # Clear all existing profile pages so removed members don't leave stale files
    for stale in PEOPLE_DIR.glob("*.html"):
        stale.unlink()
    count = 0
    for m in members:
        if m.get("role", "").lower() == "alumni":
            continue
        slug = member_slug(m["name"])
        out = PEOPLE_DIR / f"{slug}.html"
        out.write_text(build_profile_page(m, projects, members_by_netid, publications))
        n = sum(1 for p in projects if m.get("netID", "") in p.get("team", []))
        print(f"  OK  people/{slug}.html  ({m['name']}, {n} project(s))")
        count += 1
    return count


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    pi = json.loads(MEAGAN_JSON.read_text())
    data = json.loads(MEMBERS_JSON.read_text())
    members = data["members"] if isinstance(data, dict) else data
    projects      = json.loads(PROJECTS_JSON.read_text()) if PROJECTS_JSON.exists() else []
    publications  = json.loads(PUBLICATIONS_JSON.read_text()) if PUBLICATIONS_JSON.exists() else []
    members_by_netid = {m.get("netID", ""): m for m in members if m.get("netID")}
    alumni_data = json.loads(ALUMNI_JSON.read_text())
    alumni = alumni_data["alumni"] if isinstance(alumni_data, dict) else alumni_data
    for a in alumni:
        nid = a.get("netID", "")
        if nid and nid not in members_by_netid:
            members_by_netid[nid] = {**a, "is_alumni": True}

    page = PEOPLE_HTML.read_text()

    # Inject PI section
    pi_block = f"<!-- BEGIN:pi-generated -->\n{build_pi(pi)}\n<!-- END:pi-generated -->"
    page = PI_RE.sub(pi_block, page)
    print("  OK    PI section (Meagan)")

    # Inject people grid (cards now link to profile pages)
    people_html = build_people(members, alumni)
    people_block = f"<!-- BEGIN:people-generated -->\n{people_html}\n<!-- END:people-generated -->"
    page = PEOPLE_RE.sub(people_block, page)
    print(f"  OK    people grid — {len(members)} member(s)")

    PEOPLE_HTML.write_text(page)

    # Generate profile shell pages
    n = generate_profile_pages(members, projects, members_by_netid, publications)
    print(f"  OK    {n} new profile page(s) in people/")


if __name__ == "__main__":
    main()
