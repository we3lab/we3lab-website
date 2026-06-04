# WE3 Lab Website — Editing Guide

All routine content updates are made by editing JSON files in the `content/` folder and running the build scripts. The site is rebuilt automatically by GitHub Actions every Sunday at 6 pm PT, or you can trigger it manually.

---

## Table of Contents

- [Triggering a rebuild manually](#triggering-a-rebuild-manually)
- [Site structure overview](#site-structure-overview)
- [Content folder overview](#content-folder-overview)
- [Adding a new group member](#adding-a-new-group-member)
- [Moving a group member to alumni](#moving-a-group-member-to-alumni)
- [Adding a news item](#adding-a-news-item)
- [Adding a project](#adding-a-project)
- [Adding a publication](#adding-a-publication)
- [Modifying a research area](#modifying-a-research-area)
- [Adding a course](#adding-a-course)
- [Adding a dissertation](#adding-a-dissertation)
- [How the automation works](#how-the-automation-works)

---

## Triggering a rebuild manually

**Option 1 — GitHub Actions:** Go to **Actions → Update Site → Run workflow** in the GitHub repository.

**Option 2 — Local:** Run all build scripts from the repo root:

```bash
python3 scripts/build_home_page.py
python3 scripts/build_research_page.py
python3 scripts/build_research_subpages.py
python3 scripts/build_people_page.py
```

---

## Site structure overview

| Page | URL | Description |
|---|---|---|
| Home | `index.html` | Landing page with lab mission, research areas, and news strip |
| Who We Are | `people.html` | Lab members grid; links to individual profile pages |
| Member profiles | `people/{Name}.html` | Auto-generated profile pages |
| What We Do | `work.html` | Landing page with Research and Teaching boxes |
| Research | `research-areas.html` | Research areas, Previous Research, Dissertations strip |
| Research sub-pages | `research/{area}.html` | Per-area page with overview, projects, publications |
| Teaching | `teaching.html` | Course cards |
| Why We Do It | `stories.html` | Lab stories page |
| Contact | `contact.html` | Contact form and info |

---

## Content folder overview

All content you manually edit lives in `content/`:

| File | Controls |
|---|---|
| `content/members/members.json` | Active lab members (all roles except alumni) |
| `content/members/meagan.json` | PI profile — bio, education, title, links |
| `content/members/alumni.json` | Alumni |
| `content/members/images/` | Member headshots |
| `content/news/news.json` | Front-page news strip |
| `content/projects/projects.json` | Lab projects |
| `content/publications/publications.json` | Lab publications |
| `content/research_areas/research_areas.json` | Research areas (name, description, overview, image) |
| `content/research_areas/` (images) | Research area banner images |
| `content/teaching/teaching.json` | Courses taught by group |
| `content/dissertations/dissertations.json` | dissertation defenses |

---

## Adding a new group member

1. Add a headshot to `content/members/images/` named `{FirstLast}.png` (PascalCase, no spaces, no "Dr." — e.g. `JaneSmith.png`). Crop to a square; 400×400 px is ideal.

2. Add an entry to `content/members/members.json`:

```json
{
  "name": "Jane Smith",
  "netID": "jsmith",
  "email": "jsmith@stanford.edu",
  "role": "phd student",
  "bio": "One or two sentences about Jane's research focus.",
  "research_areas": ["separations", "infrastructure planning"],
  "scholar_url": "https://scholar.google.com/citations?user=XXXXXXXXX",
  "linkedin": "https://www.linkedin.com/in/janesmith/",
  "website": "",
  "cv": ""
}
```

**Valid roles:** `postdoc` · `phd student` · `ms student` · `undergrad` · `staff`

**Valid `research_areas` IDs** (must match `id` fields in `research_areas.json`):
`separations` · `energy flexibility` · `infrastructure planning` · `water energy food policies`

3. Run `build_people_page.py`. This regenerates `people.html` and creates a profile page at `people/JaneSmith.html`.

---

## Moving a group member to alumni

1. Remove the person's entry from `content/members/members.json`.
2. Add an entry to `content/members/alumni.json`:

```json
{
  "name": "Jane Smith",
  "degree_year": "PhD 2025",
  "placement": "Assistant Professor, MIT",
  "scholar_url": "https://scholar.google.com/citations?user=XXXXXXXXX",
  "linkedin": "https://www.linkedin.com/in/janesmith/"
}
```

3. Run `build_people_page.py`. The person will move from the active members grid to the Alumni section, and their profile page will no longer be generated.

---

## Adding a news item

Edit `content/news/news.json` and prepend a new entry (most recent first):

```json
{
  "date": "June 2026",
  "headline": "Paper accepted at Nature Water",
  "organization": "Nature Portfolio",
  "link": "https://doi.org/10.XXXX/XXXXX"
}
```

Run `build_home_page.py` to update the front page news strip.

---

## Adding a project

1. (Optional) Add a project image to `content/projects/images/`.

2. Add an entry to `content/projects/projects.json`:

```json
{
  "id": "unique-project-id",
  "title": "Project Title",
  "team": ["netid1", "netid2"],
  "description": "Long-form description of the project.",
  "research_areas": ["separations", "infrastructure planning"],
  "image": "content/projects/images/myproject.jpg",
  "funding": ["NSF CBET Award #XXXXXXX"],
  "links": [
    { "label": "Web Application", "url": "https://example.com" },
    { "label": "GitHub", "url": "https://github.com/we3lab/repo" }
  ]
}
```

- `team`: list of `netID` values from `members.json` — headshots and profile links are resolved automatically.
- `research_areas`: list of area `id` values from `research_areas.json` — determines which research sub-pages show this project.
- `funding`: list of funding source strings displayed as a bulleted "Supported By" list.

3. Run `build_research_subpages.py` and `build_people_page.py`.

---

## Adding a publication

Add an entry to `content/publications/publications.json`:

```json
{
  "title": "Full Publication Title",
  "authors": "Smith, J., Adkins, C., & Mauter, M. S.",
  "journal": "Environmental Science & Technology",
  "year": 2025,
  "doi": "10.1021/acs.est.5c00001",
  "research_areas": ["separations"],
  "team": ["cadkins"]
}
```

- `doi`: DOI without the `https://doi.org/` prefix. Used to build the clickable link on the card.
- `research_areas`: list of area `id` values — determines which research sub-pages list this publication.
- `team`: list of `netID` values — determines which member profile pages list this publication.

Run `build_research_subpages.py` and `build_people_page.py`.

---

## Modifying a research area

Edit `content/research_areas/research_areas.json`. Each entry has:

```json
{
  "id": "separations",
  "name": "Separations Process Modeling & Design",
  "label": "Separations",
  "file": "research/separations.html",
  "active": true,
  "image": "content/research_areas/reverse_osmosis.jpg",
  "description": "Short description shown on cards.",
  "overview": [
    "First paragraph of the Research Overview section.",
    "Second paragraph."
  ],
  "archive_note": ""
}
```

- `active: true` — area appears in the main Research grid and the home page diamond.
- `active: false` — area appears in the "Previous Research" section with an archive note box.
- `archive_note` — message shown in the amber warning box on inactive area pages.
- `label` — short name used in the "What We Do" nav dropdown.

To add a **new** research area:
1. Add an entry to `research_areas.json` with a unique `id` and a `file` path (e.g. `research/newarea.html`).
2. Place a banner image in `content/research_areas/`.
3. Run `build_research_page.py` (updates the Research page) and `build_research_subpages.py` (creates the sub-page).
4. Add "What We Do" nav dropdown entries to all HTML files and build script templates — search for `research-areas.html` to find all locations.

Run all build scripts after any change to `research_areas.json`.

---

## Adding a course

Add an entry to `content/teaching/teaching.json`:

```json
{
  "course_code": "CEE 273X",
  "name": "Course Title",
  "quarters": ["Autumn 2026"],
  "description": "Brief course description.",
  "link": "https://explorecourses.stanford.edu/..."
}
```

- `quarters`: array of strings — each renders as a pill tag on the card.
- `link`: optional URL to the course listing or syllabus.

Run `build_research_page.py` to update the Teaching page.

---

## Adding a dissertation

Add an entry to `content/dissertations/dissertations.json`:

```json
{
  "title": "Full Dissertation Title",
  "name": "Graduate Student Full Name",
  "date": "May 26, 2026",
  "link": "https://youtu.be/XXXXXXXXXXX"
}
```

- `title`: full dissertation title. Can be left empty (`""`) if not yet available.
- `name`: graduate's full name as it should appear on the card.
- `date`: defense date in any readable format — `"May 26, 2026"`, `"June 2026"`, etc. Entries are sorted most-recent-first automatically.
- `link`: YouTube URL of the defense recording (upload as **Unlisted**). The video will be embedded directly on the page with a copy-link button. Leave empty (`""`) if no recording is available.

Run `build_research_page.py` to update the Dissertations strip on the Research page.

---

## How the automation works

| Content file | Pages rebuilt | Script |
|---|---|---|
| `content/news/news.json` | `index.html` | `build_home_page.py` |
| `content/research_areas/research_areas.json` | `index.html`, `research-areas.html`, `teaching.html` | `build_home_page.py`, `build_research_page.py` |
| `content/teaching/teaching.json` | `teaching.html` | `build_research_page.py` |
| `content/dissertations/dissertations.json` | `research-areas.html` | `build_research_page.py` |
| `content/research_areas/research_areas.json` | `research/*.html` sub-pages | `build_research_subpages.py` |
| `content/projects/projects.json` | `research/*.html`, `people/*.html` | `build_research_subpages.py`, `build_people_page.py` |
| `content/publications/publications.json` | `research/*.html`, `people/*.html` | `build_research_subpages.py`, `build_people_page.py` |
| `content/members/members.json` | `people.html`, `people/*.html` | `build_people_page.py` |
| `content/members/alumni.json` | `people.html` | `build_people_page.py` |
| `content/members/meagan.json` | `people.html` | `build_people_page.py` |
