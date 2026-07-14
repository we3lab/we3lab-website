# WE3 Lab Website — Content Editing Guide

> **⚠️ Important:** Routine content updates should only be made to files inside the **`content/`** folder. Do not modify HTML files, CSS, JavaScript, or build scripts without permission from the group's Social Media coordinator.

The site is rebuilt automatically by GitHub Actions every Sunday at 6 pm PT. You can also trigger a rebuild manually at any time.

---

## Table of Contents

- [How to trigger a rebuild](#how-to-trigger-a-rebuild)
- [Repo structure](#repo-structure)
- [Adding a group member](#adding-a-group-member)
- [Moving a member to alumni](#moving-a-member-to-alumni)
- [Adding a news item](#adding-a-news-item)
- [Adding a project](#adding-a-project)
- [Adding or updating a publication](#adding-or-updating-a-publication)
- [Adding a partnership](#adding-a-partnership)
- [Modifying a research area](#modifying-a-research-area)
- [Adding a course](#adding-a-course)
- [Adding a dissertation](#adding-a-dissertation)
- [Reference: valid field values](#reference-valid-field-values)
- [Automation summary](#automation-summary)

---

## How to trigger a rebuild

**Option 1 — GitHub Actions (recommended):**
Go to **Actions → Update Site → Run workflow** in the GitHub repository.

**Option 2 — Local:**
Run build scripts from the repo root:

```bash
python3 scripts/build_home_page.py
python3 scripts/build_people_page.py
python3 scripts/build_research_page.py
python3 scripts/build_research_subpages.py
python3 scripts/build_partnerships_page.py
```

---

## Repo structure

```
we3lab-website/
├── content/          ← ALL routine edits go here
│   ├── members/
│   │   ├── members.json              ← member bios and links
│   │   ├── alumni.json               ← alumni links
│   │   ├── meagan.json               ← Meagan's bio and links
│   │   └── headshots/                ← member headshot images
│   ├── projects/
│   │   └── projects.json             ← project descriptions
│   ├── publications/
│   │   └── publications.json         ← publications and presentations (automatically updated but needs to be tagged manually with research areas)
│   ├── research_areas/
│   │   ├── research_areas.json       ← research area descriptions
│   │   └── research_area_images/     ← research area background images
│   ├── partnerships/
│   │   ├── partnerships.json         ← parnter info
│   │   └── partner_logos/            ← partner logos
│   ├── news/
│   │   └── news.json                 ← news titles and links
│   ├── teaching/
│   │   └── teaching.json             ← course descriptions
│   └── dissertations/
│       └── dissertations.json        ← dissertation titles and videos
├── scripts/          ← build scripts (do not edit without permission)
├── docs/             ← built site served by GitHub Pages (do not edit directly)
└── .github/          ← GitHub Actions workflow (do not edit without permission)
```

---

## Adding a group member

### What's manual
- Add a headshot image to `content/members/headshots/`
- Add a JSON entry to `content/members/members.json`

### What's automatic
- Profile page at `people/{FirstLast}.html` is generated on the next build
- The member appears in the people grid on `people.html`
- The member's headshot is copied to `docs/images/headshots/` on each build

### Steps

1. **Add a headshot** to `content/members/headshots/` named `FirstLast.png` (PascalCase, no spaces, no "Dr." — e.g. `JaneSmith.png`). Square crop; 400×400 px is ideal. Accepted formats: `.png`, `.jpg`.

2. **Add an entry** to `content/members/members.json`:

```json
{
  "name": "Jane Smith",
  "netID": "jsmith",
  "email": "jsmith@stanford.edu",
  "role": "phd student",
  // Valid roles: "postdoc" | "phd student" | "ms student" | "undergrad"
  //              "staff" | "staff scientist" | "research engineer"
  "bio": "One or two sentences about Jane's research focus.",
  "scholar_url": "https://scholar.google.com/citations?user=XXXXXXXXX",
  "linkedin": "https://www.linkedin.com/in/janesmith/",
  "website": "",
  "cv": ""
}
```

3. Run `build_people_page.py`.

---

## Moving a member to alumni

### What's manual
- Remove from `members.json`, add to `alumni.json`
- Optionally add a `netID` so the person continues to appear as a team member on project and publication cards

### What's automatic
- Profile page is no longer generated on the next build
- Person moves to the Alumni section on `people.html`
- If `netID` is present, name and headshot still appear on project/publication cards (without a profile link)

### Steps

1. Remove the person's entry from `content/members/members.json`.

2. Add an entry to `content/members/alumni.json`:

```json
{
  "name": "Jane Smith",
  "degree_year": "PhD 2025",
  // Format: "PhD YYYY" | "MS YYYY" | "Postdoc YYYY" | "Co-Term YYYY" | "Visiting MS YYYY"
  "placement": "Assistant Professor, MIT",
  "scholar_url": "https://scholar.google.com/citations?user=XXXXXXXXX",
  "linkedin": "https://www.linkedin.com/in/janesmith/",
  "netID": "jsmith"
  // netID is optional but recommended — enables project/publication linking
}
```

3. Run `build_people_page.py`.

---

## Adding a news item

### What's manual
- Add the entry to `news.json` (most recent first)

### What's automatic
- News strip on the home page is rebuilt on the next build

### Steps

1. Open `content/news/news.json` and prepend a new entry at the top of the array (most recent first):

```json
{
  "date": "June 2026",
  "headline": "Paper accepted at Nature Water",
  "organization": "Nature Portfolio",
  "link": "https://doi.org/10.XXXX/XXXXX"
}
```

2. Run `build_home_page.py`.

---

## Adding a project

### What's manual
- Add the JSON entry to `projects.json`
- Tag `research_areas` and `team` manually

### What's automatic
- Project cards appear on the relevant research area sub-pages and member profile pages on the next build

### Steps

1. Add an entry to `content/projects/projects.json`:

```json
{
  "id": "unique-project-id",
  "title": "Project Title",
  "team": ["netid1", "netid2"],
  // netIDs from members.json and alumni.json
  "description": "Long-form description. Supports [Markdown links](https://example.com).",
  "research_areas": ["separations", "planning"],
  // See "Reference: valid field values" for all options
  "funding": ["NSF Award #XXXXXXX", "Second funder"],
  "links": [
    { "label": "Web Application", "url": "https://example.com" },
    { "label": "GitHub Repository", "url": "https://github.com/we3lab/repo" }
  ]
}
```

2. Run `build_research_subpages.py` and `build_people_page.py`.

---

## Adding or updating a publication

### What's manual
- Adding publications from before 2022, or ones missing from Semantic Scholar
- Tagging `research_areas` on all publications (never done automatically)
- Reviewing auto-tagged `team` assignments for accuracy

### What's automatic
- Publications from 2022 onward are fetched from Semantic Scholar every Sunday and appended to `publications.json`
- `team` is auto-populated for 2022+ publications by matching author names to member/alumni netIDs — review for accuracy before relying on it

### Steps

1. For publications **not** automatically fetched (pre-2022 or missing from Semantic Scholar), add an entry manually to `content/publications/publications.json`:

```json
{
  "title": "Full Publication Title",
  "authors": "Smith, J., Adkins, C., Mauter, M. S.",
  "journal": "Environmental Science & Technology",
  "year": 2025,
  "doi": "10.1021/acs.est.5c00001",
  // DOI only — no "https://doi.org/" prefix
  "research_areas": ["separations"],
  // Must be tagged manually — see "Reference: valid field values"
  "team": ["cadkins"]
  // Auto-populated for 2022+ publications; verify before editing
}
```

2. For any publication (including auto-fetched ones), manually add `research_areas` tags — this is never done automatically.

3. Run `build_research_subpages.py`, `build_people_page.py`, and `build_research_page.py`.

---

## Adding a partnership

### What's manual
- Add logo image to `content/partnerships/partner_logos/`
- Add JSON entry to `partnerships.json`

### What's automatic
- Partner logo grid on the Partnerships page is rebuilt on the next build
- Logos are copied to `docs/images/partner_logos/` on each build

### Steps

1. (Optional) Add a logo image to `content/partnerships/partner_logos/`. Any common image format (`.png`, `.jpg`, `.svg`) is accepted.

2. Add an entry to `content/partnerships/partnerships.json`:

```json
{
  "name": "Partner Organization Name",
  "website": "https://partner.org",
  "logo": "content/partnerships/partner_logos/filename.png",
  // Leave "logo" as "" if no logo is available — name will display instead
  "section": "research"
  // "research" | "utility"
}
```

3. Run `build_partnerships_page.py`.

---

## Modifying a research area

### What's manual
- All fields in `research_areas.json`
- Banner image placed in `content/research_areas/research_area_images/`

### What's automatic
- Research area cards on `research-areas.html` and the home page diamond are rebuilt on the next build
- Research area sub-pages (`research/*.html`) are regenerated automatically

### Steps

1. (If adding a new area) Add a banner image to `content/research_areas/research_area_images/`.

2. Edit the relevant entry in `content/research_areas/research_areas.json` (or add a new one):

```json
{
  "id": "separations",
  // Must be unique; used as a reference key in projects and publications
  "name": "Separations Process Optimization & Technoeconomic Analysis",
  "file": "research/separations.html",
  "active": true,
  // true → appears in main Research grid and home page diamond
  // false → appears in "Previous Research" section with archive note
  "image": "content/research_areas/research_area_images/photo.jpg",
  "description": "Short description shown on research cards.",
  "overview": [
    "First paragraph of the Research Overview section.",
    "Second paragraph (add more strings for more paragraphs)."
  ],
  "archive_note": ""
  // Only shown when active is false — explains why area was archived
}
```

3. Run all build scripts after any change to `research_areas.json`.

---

## Adding a course

### What's manual
- Add the JSON entry to `teaching.json`

### What's automatic
- Teaching page is rebuilt on the next build

### Steps

1. Add an entry to `content/teaching/teaching.json`:

```json
{
  "course_code": "CEE 273X",
  "name": "Course Title",
  "quarters": ["Autumn 2026"],
  // Each string renders as a pill tag; add multiple for multiple offerings
  "description": "Brief course description.",
  "link": "https://navigator.stanford.edu/..."
  // Optional link to course listing or syllabus
}
```

2. Run `build_research_page.py`.

---

## Adding a dissertation

### What's manual
- Add the JSON entry to `dissertations.json`

### What's automatic
- Dissertation strip on `research-areas.html` is rebuilt on the next build; entries are sorted by date automatically

### Steps

1. Add an entry to `content/dissertations/dissertations.json`:

```json
{
  "title": "Full Dissertation Title",
  "name": "Graduate Student Full Name",
  "date": "May 26, 2026",
  // Any readable format: "May 26, 2026" | "June 2026" | etc.
  "link": "https://youtu.be/XXXXXXXXXXX"
  // YouTube URL — video is embedded with a copy-link button
  // Leave "" if no recording is available
}
```

2. Run `build_research_page.py`.

---

## Reference: valid field values

### `research_areas` (used in projects and publications)

| ID | Area name | Status |
|---|---|---|
| `separations` | Separations Process Optimization & Technoeconomic Analysis | Active |
| `flexibility` | Industrial-Energy Flexibility & Grid Integration | Active |
| `planning` | Water & Wastewater Systems Planning | Active |
| `data` | Water-Energy Data & Data Infrastructure | Active |
| `wef` | Water-Energy-Food Policies | Archived |
| `technology` | Water Treatment Technology | Archived |

### `role` (used in members.json)

| Value | Displayed as | Section |
|---|---|---|
| `postdoc` | Postdoctoral Researcher | Postdoctoral Researchers |
| `phd student` | PhD Student | PhD Students |
| `ms student` | MS Student | MS Students |
| `undergrad` | Undergraduate Student | Undergraduate Researchers |
| `staff` | Research Staff | Research Staff |
| `staff scientist` | Staff Scientist | Research Staff |
| `research engineer` | Research Engineer | Research Staff |

### `section` (used in partnerships.json)

| Value | Displayed under |
|---|---|
| `research` | Research Partnerships |
| `utility` | Utility Partnerships |

---

## Automation summary

| Content file | What happens automatically | Script(s) |
|---|---|---|
| `news.json` | Home page news strip rebuilt | `build_home_page.py` |
| `research_areas.json` | Home page diamond + research cards + all sub-pages rebuilt; research area images copied to `docs/images/` | `build_home_page.py`, `build_research_page.py`, `build_research_subpages.py` |
| `teaching.json` | Teaching page rebuilt | `build_research_page.py` |
| `dissertations.json` | Dissertation strip rebuilt | `build_research_page.py` |
| `publications.json` | Publications page + research sub-pages + member profiles rebuilt | `build_research_page.py`, `build_research_subpages.py`, `build_people_page.py` |
| `projects.json` | Research sub-pages + member profiles rebuilt | `build_research_subpages.py`, `build_people_page.py` |
| `members.json` | People page + all profile pages regenerated; headshots copied to `docs/images/` | `build_people_page.py` |
| `alumni.json` | People page rebuilt; alumni appear on project/publication cards if `netID` is present | `build_people_page.py` |
| `meagan.json` | PI section on people page rebuilt | `build_people_page.py` |
| `partnerships.json` | Partnerships page rebuilt; partner logos copied to `docs/images/` | `build_partnerships_page.py` |
| `publications.json` | New publications fetched from Semantic Scholar weekly; `team` auto-tagged for 2022+ entries | GitHub Actions (weekly) |
