# Backend Guide for the Team

This file tells you what is already scaffolded in `backend/` and what each of us has to build. The goal is a simple Django project that shows the basics: models, forms, views, URLs, templates and the admin site.

## What is already done

| Item | State |
|---|---|
| Django project | `backend/core/` holds the settings and the main `urls.py` |
| 7 apps | Created with `startapp`: `staff`, `members`, `accounts`, `savings`, `loans`, `withdrawals`, `dashboard` |
| Apps registered | All 7 are listed in `INSTALLED_APPS` in `core/settings.py` |
| Templates | Empty page files, one per frontend page (see the layout below) |
| Database | SQLite (`db.sqlite3`), the Django default. It is not committed to Git |

## What is NOT done (this is the work)

- No models, forms, views or URLs are written. Each app's `models.py` and `views.py` are still empty.
- `core/urls.py` only has `/admin/`. No page is connected yet.
- The template files are empty. The HTML is in `frontend/`, and it has to be moved in.
- No migrations have been run.

## Folder layout

```
backend/
  manage.py
  core/                 project settings and main urls.py
  staff/                templates/staff/staff.html
  members/              templates/members/member.html
  accounts/             templates/accounts/account.html
  savings/              templates/savings/saving.html
  loans/                templates/loans/loan.html, loan_payment.html
  withdrawals/          templates/withdrawals/withdrawal.html
  dashboard/            templates/dashboard/index.html
frontend/               the original HTML and CSS, to copy from
```

Pages follow one rule: `<app>/templates/<app>/page.html`. Django finds them automatically.

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

## URLs and views

Each page shows a form and a table of records, so **one view per page** does both: if the form is sent, save it, then show the table.

| URL | View | What it does | App |
|---|---|---|---|
| `/` | `index` | Home page with totals and recent activity | dashboard |
| `/staff/` | `staff_page` | Register staff, list staff | staff |
| `/members/` | `member_page` | Register member, list members | members |
| `/accounts/` | `account_page` | Open account, list accounts | accounts |
| `/savings/` | `saving_page` | Record deposit, list deposits | savings |
| `/loans/` | `loan_page` | Record loan, list loans | loans |
| `/loan-payments/` | `loan_payment_page` | Record payment, list payments | loans |
| `/withdrawals/` | `withdrawal_page` | Record withdrawal, list withdrawals | withdrawals |

## Rules

1. When a saving is recorded, add its amount to the account's balance.
2. Register every model in `admin.py`, so data can be edited or deleted at `/admin/`.

That is all. There is no login, no editing or deleting from our pages (use the admin site), no loan approval, no interest and no JavaScript.

## How to run the project

```
cd backend
python manage.py runserver
```

Open http://127.0.0.1:8000/. After changing any `models.py`, run:

```
python manage.py makemigrations
python manage.py migrate
```

## Steps for every app

1. Write the model in `models.py`.
2. Run `makemigrations` and `migrate`.
3. Create `forms.py` with a `ModelForm` for the model.
4. Write the view in `views.py` (form plus list, as described above).
5. Create `urls.py` in the app, and include it from `core/urls.py`.
6. Copy the HTML from `frontend/` into the template, and use the form and records from the view.
7. Register the model in `admin.py`.

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
- Work only in your own app's folder, to avoid merge conflicts.
- The shared files are `core/settings.py` and `core/urls.py`. Keep changes there small: one line per app.
- Do not commit `db.sqlite3`. Each of us runs `migrate` on our own machine.

## To decide as a team

- Is "payment period" free text or a number of months?
- Does a withdrawal mean the member leaves the SACCO?
