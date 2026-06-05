#!/usr/bin/env python3
"""
Generates a sub-page for each research area listed in
content/research_areas/research_areas.json.

Pulls project cards from content/projects/projects.json, filtered by area id.
Always regenerates pages fully so projects stay current.

Run from the repo root.
"""

import html
import json
import re
from pathlib import Path

RESEARCH_AREAS_JSON = Path("content/research_areas/research_areas.json")
PROJECTS_JSON        = Path("content/projects/projects.json")
PUBLICATIONS_JSON    = Path("content/publications/publications.json")
MEMBERS_JSON        = Path("content/members/members.json")
IMAGES_DIR          = Path("content/members/images")


def h(text: str) -> str:
    return html.escape(str(text))


def member_slug(name: str) -> str:
    clean = re.sub(r"^Dr\.\s+", "", name, flags=re.IGNORECASE).strip()
    return "".join(w.capitalize() for w in clean.split())


def initials(name: str) -> str:
    clean = re.sub(r"^Dr\.\s+", "", name, flags=re.IGNORECASE).strip()
    parts = clean.split()
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else parts[0][:2].upper()


def find_headshot(name: str) -> str | None:
    slug = member_slug(name)
    for ext in ("png", "jpg"):
        for variant in (slug, slug.lower()):
            p = IMAGES_DIR / f"{variant}.{ext}"
            if p.exists():
                return str(p)
    return None


# ── Project card builder ──────────────────────────────────────────────────────

def member_display(m: dict, asset_prefix: str, member_link_prefix: str) -> str:
    slug = member_slug(m["name"])
    hs   = find_headshot(m["name"])
    av   = (
        f'<div style="width:44px;height:44px;border-radius:50%;overflow:hidden;flex-shrink:0;display:flex;align-items:center;justify-content:center;">'
        f'<img src="{asset_prefix}{hs}" style="width:100%;height:100%;object-fit:cover" alt="{h(m["name"])}"></div>'
        if hs else
        f'<div style="width:44px;height:44px;border-radius:50%;overflow:hidden;flex-shrink:0;display:flex;align-items:center;justify-content:center;background:var(--cerulean);font-size:.8rem;font-weight:700;color:#fff;">'
        f'{initials(m["name"])}</div>'
    )
    return (
        f'<a href="{member_link_prefix}{slug}.html" '
        f'style="display:inline-flex;align-items:center;gap:.5rem;text-decoration:none;color:inherit">'
        f'{av}<span style="font-weight:600;font-size:.875rem">{h(m["name"])}</span></a>'
    )


def build_project_card(project: dict, members_by_netid: dict,
                       asset_prefix: str = "../",
                       member_link_prefix: str = "../people/") -> str:
    # Thumbnail image in summary
    img_path = project.get("image", "").lstrip("/")
    img_html = (
        f'<img src="{asset_prefix}{img_path}" '
        f'style="width:64px;height:48px;object-fit:cover;border-radius:4px;flex-shrink:0" alt="">'
        if img_path else ""
    )
    summary = (
        f'  <summary>\n    {img_html}\n'
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
        f'    <p style="font-size:.9rem;margin-bottom:.75rem">{h(project.get("description", ""))}</p>\n'
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
    return f'<details class="project-expand">\n{summary}\n{body}\n</details>'



def build_pub_card(pub: dict) -> str:
    doi  = pub.get("doi", "").strip()
    href = f"https://doi.org/{doi}" if doi else "#"
    doi_span = f'<span>{h(doi)}</span>' if doi else ""
    return (
        f'<li>\n'
        f'  <a href="{href}" target="_blank" rel="noopener" '
        f'style="display:block;color:inherit;text-decoration:none">\n'
        f'    <strong>{h(pub.get("title",""))}</strong>\n'
        f'    {h(pub.get("authors",""))}. <em>{h(pub.get("journal",""))}</em>, {pub.get("year","")}.'
        f'\n    {doi_span}\n'
        f'  </a>\n'
        f'</li>'
    )


def build_publications_section(area_id: str, publications: list) -> str:
    area_pubs = [p for p in publications
                 if area_id in p.get("research_areas", [])]
    if not area_pubs:
        return '    <p style="color:var(--gray-500);font-style:italic">No publications listed yet.</p>'
    sorted_pubs = sorted(area_pubs, key=lambda p: p.get("year", 0), reverse=True)
    cards = "\n    ".join(build_pub_card(p) for p in sorted_pubs)
    return f'    <ul class="publication-list">\n    {cards}\n    </ul>'


def build_projects_section(area_id: str, projects: list, members_by_netid: dict) -> str:
    area_projects = [p for p in projects if area_id in p.get("research_areas", [])]
    if not area_projects:
        return '    <p style="color:var(--gray-500);font-style:italic">No projects listed yet.</p>'
    cards = "\n    ".join(
        build_project_card(p, members_by_netid,
                           asset_prefix="../",
                           member_link_prefix="../people/")
        for p in area_projects
    )
    return f"    {cards}"


# ── Overview + archive note ───────────────────────────────────────────────────

def build_overview_block(area: dict) -> str:
    paras = "\n".join(
        f'    <p style="max-width:760px">{h(p)}</p>'
        for p in area.get("overview", [])
    )
    if not paras:
        paras = '    <p style="color:var(--gray-500);font-style:italic">Overview coming soon.</p>'
    return paras


def build_archive_note(area: dict) -> str:
    note = area.get("archive_note", "").strip()
    if not note:
        return ""
    return (
        f'    <div style="background:#fff8e1;border-left:4px solid #f9a825;'
        f'border-radius:var(--radius);padding:1rem 1.25rem;margin-bottom:2rem">\n'
        f'      <p style="margin:0;font-size:.9rem;color:#5d4037">'
        f'<strong>Archive note:</strong> {h(note)}</p>\n'
        f'    </div>\n'
    )


# ── Page template ─────────────────────────────────────────────────────────────

def build_full_page(area: dict, projects: list, members_by_netid: dict, publications: list = None) -> str:
    if publications is None:
        publications = []
    overview          = build_overview_block(area)
    archive_note      = build_archive_note(area)
    projects_html     = build_projects_section(area["id"], projects, members_by_netid)
    publications_html = build_publications_section(area["id"], publications)

    return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{h(area["name"])} — WE3 Lab</title>
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
        <li><a href="../people.html">Who We Are</a></li>
        <li class="dropdown">
          <a href="../work.html" class="active">What We Do</a>
          <ul class="dropdown-content">
            <li><a href="../research-areas.html">Research</a></li>
            <li><a href="../teaching.html">Teaching</a></li>
          </ul>
        </li>
        <li><a href="../stories.html">Why We Do It</a></li>
        <li><a href="../contact.html">Contact Us</a></li>
      </ul>
    </div>
  </nav>
</div>

<!-- ── Page Banner ─────────────────────────────────────── -->
<div class="page-banner">
  <div class="container">
    <div class="breadcrumb"><a href="../work.html">What We Do</a> &rsaquo; {h(area["name"])}</div>
    <h1>{h(area["name"])}</h1>
    <p>{h(area["description"])}</p>
  </div>
</div>

<!-- ── Page Content ────────────────────────────────────── -->
<section class="section">
  <div class="container">

{archive_note}    <h2 class="text-deep-space">Research Overview</h2>
    <div class="divider" style="margin:1rem 0"></div>
<!-- BEGIN:overview-generated -->
{overview}
<!-- END:overview-generated -->

    <h2 class="text-deep-space" style="margin-top:3rem;margin-bottom:1rem">Projects</h2>
{projects_html}

    <h2 class="text-deep-space" style="margin-top:3rem;margin-bottom:1rem">Publications</h2>
{publications_html}

    <div style="margin-top:3rem">
      <a href="../work.html" class="btn btn-navy">&larr; Back to What We Do</a>
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


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    areas    = json.loads(RESEARCH_AREAS_JSON.read_text())
    projects      = json.loads(PROJECTS_JSON.read_text()) if PROJECTS_JSON.exists() else []
    publications  = json.loads(PUBLICATIONS_JSON.read_text()) if PUBLICATIONS_JSON.exists() else []
    members  = json.loads(MEMBERS_JSON.read_text())
    raw      = members["members"] if isinstance(members, dict) else members
    members_by_netid = {m.get("netID", ""): m for m in raw if m.get("netID")}

    for area in areas:
        path = Path(area["file"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(build_full_page(area, projects, members_by_netid, publications))
        n = sum(1 for p in projects if area["id"] in p.get("research_areas", []))
        print(f"  OK  {area['file']}  ({n} project(s))")


if __name__ == "__main__":
    main()
