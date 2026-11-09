---
version: 1
slug: "templates-base-html"
primary_target: "templates/base.html"
related_targets: ["templates/dashboard/index.html"]
---

# Surface brief: SACCO app shell and dashboard

Scope: the whole authenticated app shell (templates/base.html), the dashboard (templates/dashboard/index.html), the seven data list pages, the shared add/edit/delete modals, and the login page. Visitor mode: Operate.

Audience and job: one SACCO administrator at a desk, entering and checking records all day; secondary audience is a lecturer at a class demo. Proof and content: real rows from the database (sample data from a fill script, marked as sample in the README). Constraints: Django templates, one app.css, one small modal.js, Lucide icons, no Bootstrap or Tailwind, palette pinned by the user.

Unresolved decisions: none. Visual world was pinned by the user (palette image 1, Material Dashboard look); no concept roll was run.

## Direction contract

THESIS: A calm administrator's desk, not a marketing page. The one idea is the Material Dashboard shell redrawn in our own CSS: a floating dark sidebar, an off-white page, and rounded white cards with a coloured icon tile standing on the top edge of each number card. It refuses the default template look of a flat grey admin with one blue accent.

OWN-WORLD: Palladian #EEE9DF page, #FBF9F4 cards, Oatmeal #C9C1B1 lines, Abyssal #1B2632 sidebar and text, Blue Fantastic #2C3B4D secondary tiles, Burning Flame #F2A55C for primary buttons and the current page, Truffle Trouble #A35139 only for delete and errors. Light scene: an office desk in daylight. Roboto for UI, tabular figures for money, Lucide line icons at one stroke weight. Soft offset shadows with real blur, 14px card radius, 9px control radius. Recognizable with the content removed by the dark floating rail, the orange current-page pill and the raised icon tiles.

STORY: The administrator logs in and knows the position of the SACCO from eight real numbers, then moves to any of seven record pages in one click, adds or edits in a modal without losing their place, and is asked before anything is deleted.

FIRST VIEWPORT: Dashboard at 1440 wide. Left, a 250px floating dark rail with brand, Dashboard, then the seven pages as one flat icon list, Django Admin at the bottom, then the signed-in user and log out. Right, a top row with the page title and the signed-in user, then two rows of four number cards with raised icon tiles (the largest figure, total savings, is in the first row), then two tables side by side: recent savings and recent loans. The primary action on data pages is a single orange Add button top right of the title row.

FORM: Standard operate shell (side rail, work area, tables, modal dialogs), pinned by the user. Seed key: none, direction pinned by the user without a roll.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
