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

MEAGAN_JSON = Path("content/members/meagan.json")
MEMBERS_JSON = Path("content/members/members.json")
ALUMNI_JSON = Path("content/members/alumni.json")
PEOPLE_HTML = Path("people.html")
IMAGES_DIR = Path("content/members/images")
PEOPLE_DIR = Path("people")

PI_RE = re.compile(r"<!-- BEGIN:pi-generated -->.*?<!-- END:pi-generated -->", re.DOTALL)
PEOPLE_RE = re.compile(r"<!-- BEGIN:people-generated -->.*?<!-- END:people-generated -->", re.DOTALL)

AV_COUNT = 8

ROLE_ORDER = ["postdoc", "phd student", "ms student", "undergrad", "staff", "alumni"]
ROLE_LABELS = {
    "postdoc":    "Postdoctoral Researchers",
    "phd student":"PhD Students",
    "ms student": "MS Students",
    "undergrad":  "Undergraduate Researchers",
    "staff":      "Research Staff",
    "alumni":     "Alumni",
}
ROLE_DISPLAY = {
    "postdoc":    "Postdoctoral Researcher",
    "phd student":"PhD Student",
    "ms student": "MS Student",
    "undergrad":  "Undergraduate Researcher",
    "staff":      "Research Staff",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def h(text: str) -> str:
    return html.escape(str(text))


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
        f'        <p style="font-size:.9rem;color:var(--blk);line-height:1.6;margin-bottom:.75rem">{h(p)}</p>'
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
        <p style="font-size:.85rem;color:#555;margin-top:.4rem;margin-bottom:.75rem">{h(pi['title'])}</p>
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
    place_html = f'        <p class="research-area">{h(a.get("placement", ""))}</p>\n' if a.get("placement") else ""

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
        if key in by_role:
            by_role[key].append(m)

    sections = []
    av_idx = 0

    # Active member sections — alphabetical by last name within each role
    for role in ROLE_ORDER:
        if role == "alumni":
            continue
        group = sorted(by_role.get(role, []), key=lambda m: _last_name(m["name"]))
        if not group:
            continue
        cards = []
        for m in group:
            av = f"av-{(av_idx % AV_COUNT) + 1}"
            av_idx += 1
            cards.append(build_member_card(m, av))
        sections.append(
            f'    <h2 class="people-section-title">{ROLE_LABELS[role]}</h2>\n'
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


def build_contact_section(m: dict, top_offset: str = "0") -> str:
    """Build the Contact sidebar. Returns empty string if nothing to show."""
    link_style = "color:rgba(255,255,255,.85);text-decoration:none;display:flex;align-items:center;gap:.5rem;font-size:.875rem;margin-bottom:.4rem"
    items = []
    netid = m.get("netID", "").strip()
    if netid:
        items.append(
            f'<a href="mailto:{netid}@stanford.edu" style="{link_style}">'
            f'<i class="fa-solid fa-envelope"></i> {netid}@stanford.edu</a>'
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


def build_profile_page(m: dict) -> str:
    role_display = ROLE_DISPLAY.get(m.get("role", "").lower(), m.get("role", "").title())
    bio_text     = m.get("bio", "").strip()
    img_path     = find_image(m["name"])

    bio_html = (
        f'      <p style="color:rgba(255,255,255,.8);font-size:1.1rem;'
        f'line-height:1.6;margin-top:1rem;margin-bottom:0">{h(bio_text)}</p>'
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
        <img src="../assets/logos/WE3_Lab_Logo_white_short.png" alt="WE3 Lab" height="96">
      </a>
      <button class="nav-hamburger" aria-label="Toggle navigation" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
      <ul class="nav-links">
        <li><a href="../index.html">Home</a></li>
        <li><a href="../people.html" class="active">Who We Are</a></li>
        <li><a href="../research.html">What We Do</a></li>
        <li><a href="../why-we-do-it.html">Why We Do It</a></li>
        <li><a href="../contact.html">Contact Us</a></li>
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
    <p style="color:var(--gray-500);font-style:italic">No projects listed yet.</p>

    <h2 class="text-deep-space" style="margin-top:3rem;margin-bottom:1rem">Publications</h2>
    <p style="color:var(--gray-500);font-style:italic">No publications listed yet.</p>

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


def generate_profile_pages(members: list) -> int:
    PEOPLE_DIR.mkdir(exist_ok=True)
    count = 0
    for m in members:
        if m.get("role", "").lower() == "alumni":
            continue
        slug = member_slug(m["name"])
        out = PEOPLE_DIR / f"{slug}.html"
        out.write_text(build_profile_page(m))
        print(f"  OK  people/{slug}.html  ({m['name']})")
        count += 1
    return count


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    pi = json.loads(MEAGAN_JSON.read_text())
    data = json.loads(MEMBERS_JSON.read_text())
    members = data["members"] if isinstance(data, dict) else data
    alumni_data = json.loads(ALUMNI_JSON.read_text())
    alumni = alumni_data["alumni"] if isinstance(alumni_data, dict) else alumni_data

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
    n = generate_profile_pages(members)
    print(f"  OK    {n} new profile page(s) in people/")


if __name__ == "__main__":
    main()
