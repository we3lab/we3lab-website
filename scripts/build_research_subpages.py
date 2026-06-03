#!/usr/bin/env python3
"""
Generates a sub-page for each active research area listed in
content/research_areas/research_areas.json.

Page structure:
  - Site header + nav
  - Page banner  (name as h1, description as subtitle)
  - Main content:
      Research Overview  (from area["overview"], between BEGIN/END:overview-generated)
      Projects           (placeholder)
      Publications       (placeholder)
  - Footer

If the page already exists and contains the overview markers, only the
overview block is updated — other content is left untouched.

Run from the repo root.
"""

import html
import json
import re
from pathlib import Path

RESEARCH_AREAS_JSON = Path("content/research_areas/research_areas.json")

OVERVIEW_RE = re.compile(
    r"<!-- BEGIN:overview-generated -->.*?<!-- END:overview-generated -->",
    re.DOTALL,
)

NAV_DROPDOWN = """\
          <ul class="dropdown-content">
            <li><a href="../research/separations.html">Separations</a></li>
            <li><a href="../research/energyflexibility.html">Water-Energy Flexibility</a></li>
            <li><a href="../research/infrastructureplanning.html">Systems Planning</a></li>
            <li><a href="../research/waterenergyfoodpolicies.html">WEF Policies</a></li>
            <li class="dropdown-divider"></li>
            <li><a href="../research/dissertations.html">Past Dissertations</a></li>
          </ul>"""


def h(text: str) -> str:
    return html.escape(str(text))


def build_overview_block(area: dict) -> str:
    paras = "\n".join(
        f'    <p style="max-width:760px">{h(p)}</p>'
        for p in area.get("overview", [])
    )
    if not paras:
        paras = '    <p style="color:var(--gray-500);font-style:italic">Overview coming soon.</p>'
    return (
        f"<!-- BEGIN:overview-generated -->\n"
        f"{paras}\n"
        f"<!-- END:overview-generated -->"
    )


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


def build_full_page(area: dict) -> str:
    overview_block  = build_overview_block(area)
    archive_note_html = build_archive_note(area)
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
        <li><a href="../research.html" class="active">What We Do</a></li>
        <li><a href="../why-we-do-it.html">Why We Do It</a></li>
        <li><a href="../contact.html">Contact Us</a></li>
      </ul>
    </div>
  </nav>
</div>

<!-- ── Page Banner ─────────────────────────────────────── -->
<div class="page-banner">
  <div class="container">
    <div class="breadcrumb"><a href="../research.html">What We Do</a> &rsaquo; {h(area["name"])}</div>
    <h1>{h(area["name"])}</h1>
    <p>{h(area["description"])}</p>
  </div>
</div>

<!-- ── Page Content ────────────────────────────────────── -->
<section class="section">
  <div class="container">

{archive_note_html}    <h2 class="text-deep-space">Research Overview</h2>
    <div class="divider" style="margin:1rem 0"></div>
{overview_block}

    <h2 class="text-deep-space" style="margin-top:3rem;margin-bottom:1rem">Projects</h2>
    <p style="color:var(--gray-500);font-style:italic">No projects listed yet.</p>

    <h2 class="text-deep-space" style="margin-top:3rem;margin-bottom:1rem">Publications</h2>
    <p style="color:var(--gray-500);font-style:italic">No publications listed yet.</p>

    <div style="margin-top:3rem">
      <a href="../research.html" class="btn btn-navy">&larr; Back to What We Do</a>
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


def main():
    areas = json.loads(RESEARCH_AREAS_JSON.read_text())

    for area in areas:

        path = Path(area["file"])
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists() and "<!-- BEGIN:overview-generated -->" in path.read_text():
            # Page exists with markers — update only the overview block
            updated = OVERVIEW_RE.sub(build_overview_block(area), path.read_text())
            path.write_text(updated)
            print(f"  UPDATED  {area['file']}  ({area['name']})")
        else:
            # Create the full page
            path.write_text(build_full_page(area))
            print(f"  CREATED  {area['file']}  ({area['name']})")


if __name__ == "__main__":
    main()
