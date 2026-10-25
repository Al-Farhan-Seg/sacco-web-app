# Backend Guide for the Team

This file tells you what is already in place in the project (which now lives at the
repository root, not in a `backend/` folder) and what each of us still has to build.
The goal is a simple Django project that shows the basics: models, forms, views,
URLs, templates and the admin site.

## What is already done

| Item | State |
|---|---|
| Django project location | The project was moved out of `backend/` and now lives at the repo root. `core/` holds the settings and the main `urls.py` |
| 7 apps | `staff`, `members`, `accounts`, `savings`, `loans`, `withdrawals`, `dashboard` — all at the repo root, one folder each |
| Apps registered | All 7 are listed in `INSTALLED_APPS` in `core/settings.py` |
| Frontend folded in | The marked frontend (HTML/CSS/JS) has been moved into `templates/` and `static/` — see "Templates and static files" below |
| Routes | Every page already has a working URL and a one-line view that renders it (see "URLs and views" below) — you can `runserver` right now and click through every page |
| Database | SQLite (`db.sqlite3`), the Django default. It is not committed to Git |

## What is NOT done (this is the work)

- No models are written. Each app's `models.py` is still empty.
- No forms exist (`forms.py` files haven't been created yet).
- The existing views only render a static page — they don't read or save any data yet.
- No migrations have been run (there's nothing to migrate until models exist).
- Nothing is registered in any `admin.py`.
- There is no login/authentication. The login page is just a static form that doesn't do anything yet.
- The tables of records on every page are still the original hardcoded dummy rows from the frontend design — once a model and view exist, those rows should come from the database instead.

## Folder layout

```
manage.py
core/                   project settings and the main urls.py (this is where every page's route lives for now)
staff/                  app folder — models.py, views.py, admin.py, etc. (no urls.py yet)
members/                app folder
accounts/               app folder
savings/                app folder
loans/                  app folder
withdrawals/            app folder
dashboard/              app folder
templates/
  base.html             shared head + nav that every page extends
  dashboard/index.html
  staff/login.html, staff.html
  members/member.html
  accounts/account.html
  savings/saving.html
  loans/loan.html, loan_payment.html
  withdrawals/withdrawal.html
static/
  css/                  one stylesheet per page, unchanged from the frontend design
  images/images.png
  js/form-validation.js
```

Templates live under one shared `templates/` folder at the root (not inside each app), namespaced by app name to avoid clashes — e.g. `templates/accounts/account.html`. `core/settings.py` points Django at this folder, and each view's `render()` call already uses the right path (e.g. `render(request, 'accounts/account.html')`).

## Routes, right now

For simplicity (and because not everyone on the team is equally comfortable with Django yet), the routes are **all defined in one place, `core/urls.py`**, as plain, literal paths that match the links already in the templates — not split into a `urls.py` per app, and not using Django's `{% url %}` template tag yet. Each route is commented.

| URL | View (already exists) | App |
|---|---|---|
| `/` and `/index.html` | `dashboard_views.index` | dashboard |
| `/login.html` | `staff_views.login_view` | staff |
| `/staff.html` | `staff_views.staff` | staff |
| `/member.html` | `members_views.member` | members |
| `/account.html` | `accounts_views.account` | accounts |
| `/saving.html` | `savings_views.saving` | savings |
| `/loan.html` | `loans_views.loan` | loans |
| `/loan-payment.html` | `loans_views.loan_payment` | loans |
| `/withdrawal.html` | `withdrawals_views.withdrawal` | withdrawals |

Every one of these views currently looks like this and nothing more:

```python
def account(request):
    return render(request, 'accounts/account.html')
```

Your job for your app is to turn this into the real "show a form, save it if submitted, and list the records" view described below — you are editing the *existing* function, not creating a new one, and you do **not** need to touch `core/urls.py` or add a `urls.py` of your own. If later on the team wants proper namespaced URLs and `{% url %}` tags, that's a deliberate follow-up step everyone should agree on together, not something to slip in app-by-app.

## What each app must contain

- **Staff** are the people who work at the SACCO.
- **Members** are the people who save with the SACCO.
- An **account** is a member's bank account.

Ids are text fields typed in the form, like the frontend (`MEM-001`). An arrow means "belongs to" (a `ForeignKey`).

| App | Model | Fields |
|---|---|---|
| `staff` | Staff | staff id, first name, last name, gender, position, role, contact, address |
| `members` | Member | member id, first name, last name, contact, address, email, gender |
| `accounts` | Account | account id, member → Member, account number, type (Savings / Current), balance |
| `savings` | Saving | savings id, member → Member, account → Account, staff → Staff, payment method (Cash / Mobile Money / Bank Transfer), amount, date |
| `loans` | Loan | loan id, member → Member, staff → Staff, loan amount, payment period, payment amount |
| `loans` | LoanPayment | payment id, loan → Loan, amount, date |
| `withdrawals` | Withdrawal | withdraw id, member → Member, amount, date |
| `dashboard` | none | Only a view that reads the other apps |

Staff is a normal model like the others, with no login and no special user setup.

## What a finished view should do

Each page shows a form and a table of records, so **one view per page** does both: if the form is submitted, validate and save it, then (either way) show the table of existing records. Concretely, for an app like `accounts`:

1. Write `Account` in `models.py`.
2. Run `makemigrations` and `migrate`.
3. Create `forms.py` with an `AccountForm(forms.ModelForm)`.
4. In `views.py`, change the existing `account(request)` function so that:
   - on `POST`, it builds the form from `request.POST`, validates it, and saves a new `Account` if valid;
   - either way, it fetches all `Account` rows and passes both the form and the records into the template's context.
5. Update `templates/accounts/account.html` to render `{{ form }}` instead of the hand-typed `<input>` fields, and loop over the real records (`{% for account in accounts %}`) instead of the hardcoded `<tr>` rows.
6. Register `Account` in `admin.py` so it can be managed at `/admin/`.

## Rules

1. When a saving is recorded, add its amount to the account's balance.
2. Register every model in `admin.py`, so data can be edited or deleted at `/admin/`.

That is all. There is no login, no editing or deleting from our pages (use the admin site), no loan approval, no interest and no JavaScript beyond the existing client-side form-validation script.

## How to run the project

```
python manage.py runserver
```

Open http://127.0.0.1:8000/ — every page already loads, with its CSS and the shared nav. After writing or changing any `models.py`, run:

```
python manage.py makemigrations
python manage.py migrate
```

## Steps for every app

1. Write the model in `models.py`.
2. Run `makemigrations` and `migrate`.
3. Create `forms.py` with a `ModelForm` for the model.
4. Update the existing view in `views.py` (form handling plus the record list, as described above). The route in `core/urls.py` already points at it — you don't need to add anything there.
5. Replace the hardcoded form fields and table rows in your template with the real form and the real records from the view's context.
6. Register the model in `admin.py`.

## Who builds what

| Step | Work | Person |
|---|---|---|
| 1 | `staff` and `members` | Person 1 |
| 2 | `accounts` | Person 2 |
| 3 | `savings` | Person 3 |
| 4 | `loans` (Loan and LoanPayment) | Person 2 |
| 5 | `withdrawals` | Person 3 |
| 6 | `dashboard` and the admin site | Person 1 |

Build `staff` and `members` first, because the other apps point to them.

## Git tips

- Pull before you start work, and push when a feature works.
- Work mostly in your own app's folder (`models.py`, `forms.py`, `views.py`, `admin.py`) and your own template, to avoid merge conflicts.
- The shared files are `core/settings.py` and `core/urls.py`, plus `templates/base.html`. Keep changes there small and flag them to the team before pushing, since everyone's pages depend on them.
- Do not commit `db.sqlite3`. Each of us runs `migrate` on our own machine.

## To decide as a team

- Is "payment period" free text or a number of months?
- Does a withdrawal mean the member leaves the SACCO?
- When do we want to move from the current flat, literal routes (`/account.html`, etc., all in `core/urls.py`) to a proper namespaced `urls.py` per app with `{% url %}` tags in the templates? Worth doing once everyone is comfortable with the basics, but not before.
