# SACCO Management System

A Django project for a SACCO management system. The marked frontend (HTML/CSS/JS)
has been folded into Django templates and static files, served by basic views and
routes, with no business logic built yet.

## Pages

- `/` and `/index.html` — home page
- `/login.html` — login page
- `/staff.html` — staff page
- `/member.html` — member page
- `/account.html` — account page
- `/saving.html` — savings page
- `/loan.html` — loan page
- `/loan-payment.html` — loan-payment page
- `/withdrawal.html` — withdrawal page

## Project layout

- `core/` — Django settings, root `urls.py`, WSGI/ASGI entry points
- `accounts/`, `dashboard/`, `loans/`, `members/`, `savings/`, `staff/`, `withdrawals/` — the Django apps, one per page group
- `templates/` — page templates, namespaced by app, extending `templates/base.html`
- `static/` — CSS, JS and images

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
3. Apply migrations:
   ```
   python manage.py migrate
   ```
4. Run the dev server:
   ```
   python manage.py runserver
   ```
5. Visit `http://127.0.0.1:8000/`.

## Branch workflow

- `main` — active development. Create a feature branch off `main` for your work and open a PR back into it.
- `deployment` — the hosting branch. It is not touched directly; nothing is merged into it from day-to-day feature work.
