# SACCO Management System

A Django back-office app for one administrator. After logging in, the administrator
sees a dashboard of live numbers and manages seven kinds of records (members, staff,
accounts, savings, withdrawals, loans and loan payments) with Add, Edit and Delete
buttons. Forms open in a modal on the same page. Django 6.1 and SQLite only; the
styling is one hand-written stylesheet.

## Setup

1. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # macOS/Linux
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create the database tables:
   ```
   python manage.py migrate
   ```
4. Fill the database with demo data and create the demo user (replaces any existing records):
   ```
   python manage.py seed --reset
   ```
5. Run the dev server and open `http://127.0.0.1:8000/`:
   ```
   python manage.py runserver
   ```

### Demo login (throwaway)

| Username | Password |
|---|---|
| `admin` | `sacco-demo-2026` |

This password is for the class demo only. Do not reuse it anywhere, and change it
(or remove the user) before any real use.

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
                      and one <app>_list.html per data area
static/css/app.css    the only stylesheet
static/js/            modal.js (modal forms) and lucide.min.js (icons)
docs/                 design spec and build plan
BACKEND_DETAIL.md     how the CRUD pattern works and how to add a page
```

## Running the tests

```
python manage.py test
python manage.py check
```

The tests use Django's temporary test database and do not touch `db.sqlite3`.

## Branches

- `main` is for development. Create a feature branch off `main` and open a PR back into it.
- `deployment` is the hosting branch. It is not touched directly; feature work is not merged into it.
