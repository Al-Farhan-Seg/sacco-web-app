# SACCO Management System

A Django back-office app for one administrator of a SACCO (a savings and loans group).
After logging in, the administrator sees a dashboard of live numbers and manages seven
kinds of records (members, staff, accounts, savings, withdrawals, loans and loan
payments) with Add, Edit and Delete buttons. Forms open in a modal on the same page.

Django 6.1 and SQLite only. The styling is one hand-written stylesheet, with no
Bootstrap or Tailwind. This is a university class project.

## Where the project stands

**The application is built and working.** This repository is now read-only for
contributors: the owner has restricted who can push, so you can clone it, run it and
read it, but changes are made by the owner only.

What is in `main`:

- Login and logout, with every page except the login page locked behind a login.
- A dashboard with eight live number cards (members, staff, accounts, total savings,
  loans issued, loan repayments, still owed, withdrawals) and two recent-activity tables.
- Seven record pages, each with a table, a large **Add** button, and pencil and
  trash icons on every row. Add, Edit and Delete all open in a modal.
- Automatic IDs shown as codes (`MEM-001`, `STF-001`, `ACC-001`, `SAV-001`, `LN-001`,
  `PAY-001`, `WDR-001`). Nobody types an ID.
- Linked data with rules: an account's balance is its opening balance plus its
  savings; a loan's "still owed" is the loan minus its payments; a payment cannot
  exceed what is still owed; deleting a member also deletes their accounts, savings,
  loans and withdrawals.
- A `db.sqlite3` that already contains demo data, so the app has something to show
  the moment it starts.
- 144 automated tests, all passing.

Deliberately left out, to keep it a simple class demo: member or staff logins (there is
one administrator), roles with permissions (a staff "role" is just a label), loan
approval, interest calculation, search and filters, charts, and any REST API.

## Run it and see what is there

You need Python (built and tested on 3.13) and Git.

1. Clone the repository and go into the folder.
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # macOS/Linux
   ```
3. Install the one dependency (Django):
   ```
   pip install -r requirements.txt
   ```
4. Start the server and open `http://127.0.0.1:8000/`:
   ```
   python manage.py runserver
   ```

That is all. The committed `db.sqlite3` already has the tables and the demo data, so
you do **not** need to run `migrate` or `seed`.

### Demo login (throwaway)

| Username | Password |
|---|---|
| `admin` | `sacco-demo-2026` |

This password is for the class demo only. Do not reuse it anywhere.

### What to look at

1. Log in, and look at the dashboard.
2. Open **Members** and click a pencil to edit, the trash to delete (it asks first),
   or **Add member** at the top right.
3. Open **Savings**, **Loans** and **Loan payments** to see how the records link
   together, and compare the dashboard numbers afterwards.
4. Open **Django Admin** (bottom of the sidebar) to see the same data in Django's own
   screens.

### If the data gets messy

Using the app changes `db.sqlite3` on your machine (including a login session). To
put the committed demo data back:

```
git checkout -- db.sqlite3
```

Only for a brand-new empty database: `python manage.py migrate` then
`python manage.py seed`. Do not run `seed --reset` on the committed database; it wipes
everything and renumbers the codes from MEM-061 onward.

## Pages and addresses

Every page except the login page requires a login.

| Page | Address |
|---|---|
| Login | `/login/` |
| Logout (POST, button in the sidebar) | `/logout/` |
| Dashboard | `/` |
| Members | `/members/` |
| Staff | `/staff/` |
| Accounts | `/accounts/` |
| Savings | `/savings/` |
| Withdrawals | `/withdrawals/` |
| Loans | `/loans/` |
| Loan payments | `/loan-payments/` |
| Django Admin | `/admin/` |

Each data page also has `add/`, `<id>/edit/` and `<id>/delete/` addresses under it
(for example `/members/add/`), which return the modal forms.

## Project layout

```
manage.py
core/                 settings, root urls.py, CodedModel, crud.py (shared list/modal views), template filter ugx
members/ staff/ accounts/ savings/ withdrawals/ loans/
                      one app per data area: models.py, forms.py, views.py, urls.py, admin.py, tests.py
                      (loans/ holds both Loan and LoanPayment)
dashboard/            dashboard view, stats.py (the numbers), management/commands/seed.py
templates/            base.html, registration/login.html, partials/ (modal, pagination, sidebar),
                      and one list page per data area (loans/ has loan_list.html and payment_list.html)
static/css/app.css    the only stylesheet
static/js/            modal.js (modal forms) and lucide.min.js (icons)
db.sqlite3            the database, with demo data
```

## Where to read more

| File | What it tells you |
|---|---|
| `BACKEND_DETAIL.md` | How the code works: models, the shared CRUD helpers, the modal flow, and how to add a new data page |
| `docs/superpowers/specs/2026-11-08-sacco-dashboard-design.md` | The design: what we decided and why, the models, the rules, what was left out |
| `docs/superpowers/plans/2026-11-08-sacco-dashboard.md` | The build plan, task by task |
| `PRODUCT.md` | Who the app is for and what it must do |
| `DESIGN.md` | The visual design system as built: palette, type, components |
| `SACCO Script.sql` | The original database script from the first design stage (reference only; the Django models are the source of truth) |

## Running the tests

```
python manage.py test
python manage.py check
```

The tests take a couple of minutes. They use Django's temporary test database and do
not touch `db.sqlite3`.

## Branches and contributing

- `main` is the current, finished state of the project. It is the only branch on the
  remote that matters for reading and running the app.
- `deployment` is the old hosting branch. It is not touched.
- Pushing is restricted to the owner. You can still clone, run, read and fork; if you
  find a problem, tell the owner.

## Known limits

- It uses Django's development settings (`DEBUG = True`, a committed `SECRET_KEY`), so
  it is not ready to be put on the public internet as it stands.
- The Roboto font loads from Google Fonts, so with no internet connection the page
  falls back to a system font. Everything else works offline.
- Deleting a staff record also deletes the savings and loans that staff member handled.
  The delete window warns about this.
