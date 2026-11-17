# Render Deployment and Submission Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Meet the teacher's five submission requirements: superuser `admin`/`admin123`, README with title and group members, everything pushed to GitHub, deployed on Render, link shared.

**Architecture:** Keep Django 6.1 + the committed SQLite demo database. Make `core/settings.py` read production values from environment variables, serve static files with WhiteNoise, run with gunicorn on a Render free web service. The live database is the committed `db.sqlite3` (ephemeral disk: resets to the committed state on every restart).

**Tech Stack:** Django 6.1, gunicorn, whitenoise, Render (free web service), GitHub.

**Spec:** The teacher's announcement (pasted in the conversation of 2026-11-17). Click-by-click detail lives in the gitignored `render-deployment.md` at the repo root.

## Global Constraints

- Superuser username `admin`, password `admin123` (verbatim from the announcement)
- `README.md` in the repo root with the project title and details of all group members
- Host on Render (recommended) or Vercel; this plan uses Render
- Django 6.1 and SQLite only; no new database, no extra frameworks (class project, see README)
- Own CSS only; do not touch the stylesheet
- No AI attribution lines in commit messages (user's global rule)
- `render-deployment.md` stays gitignored and is never committed

## Review Focus

- `DEBUG=0` hides the debug pages: a 404 and a 500 must still render. Test: request a bad URL with `DEBUG=0`.
- Static files must load with `DEBUG=0` (CSS, logo, JS). Test: `collectstatic` then fetch a CSS file.
- Login and modal forms over HTTPS must not return CSRF 403. Test: post a login on the live URL.
- The committed `db.sqlite3` must carry the new admin password. Test: `check_password('admin123')` is `True` on the committed file.
- Local development must keep working with no environment variables set (`DEBUG` defaults on, `localhost` allowed). Test: `python manage.py test` and `runserver` with a clean shell.

---

### Task 1: Admin superuser with the required password

**Files:**
- Modify: `db.sqlite3` (committed demo database)

**Interfaces:**
- Produces: user `admin`, `is_superuser=True`, `is_staff=True`, `is_active=True`, password `admin123`

- [ ] **Step 1: Confirm the current state.** Run `python manage.py shell -c "from django.contrib.auth.models import User; u=User.objects.get(username='admin'); print(u.check_password('admin123'))"`. Expected: `False` (already verified 2026-11-17).
- [ ] **Step 2: Set the password** with `u.set_password('admin123')` in `manage.py shell` (the shell skips the common-password validator that `changepassword` enforces); keep the three flags true.
- [ ] **Step 3: Verify.** Same command as Step 1. Expected: `True`.
- [ ] **Step 4: Commit** `db.sqlite3` together with Task 2 and 3 (one deploy commit, see Task 4).

### Task 2: Production-ready settings and dependencies

**Files:**
- Modify: `requirements.txt`
- Modify: `core/settings.py` (secrets block near the top, `MIDDLEWARE`, static section)

**Interfaces:**
- Consumes: env vars `SECRET_KEY`, `DEBUG` (`'0'` turns debug off), `RENDER_EXTERNAL_HOSTNAME` (set by Render)
- Produces: settings importable with no env vars set (development behaviour unchanged)

- [ ] **Step 1: Add to `requirements.txt`:** `gunicorn`, `whitenoise` (pinned to the versions `pip` installs).
- [ ] **Step 2: In `core/settings.py`** set `SECRET_KEY = os.environ.get('SECRET_KEY', <current dev key>)`, `DEBUG = os.environ.get('DEBUG', '1') == '1'`, `ALLOWED_HOSTS = ['localhost', '127.0.0.1']`; when `RENDER_EXTERNAL_HOSTNAME` is set, append it, set `CSRF_TRUSTED_ORIGINS = [f'https://{host}']`, `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')`, `SESSION_COOKIE_SECURE = True`, `CSRF_COOKIE_SECURE = True`.
- [ ] **Step 3: Insert** `'whitenoise.middleware.WhiteNoiseMiddleware'` directly after `SecurityMiddleware`.
- [ ] **Step 4: Set** `STORAGES['staticfiles']` to `whitenoise.storage.CompressedStaticFilesStorage` (not the Manifest variant: it errors on missing references and would break tests).
- [ ] **Step 5: Run** `pip install -r requirements.txt` then `python manage.py test`. Expected: 203 tests pass.
- [ ] **Step 6: Simulate production:** with `$env:DEBUG="0"`, run `python manage.py collectstatic --noinput` then `python manage.py runserver --insecure`. Expected: styled login page, `admin`/`admin123` logs in, a bad URL gives a plain 404.

### Task 3: README group members and gitignore

**Files:**
- Modify: `README.md` (new "Group members" section under the intro paragraph)
- Modify: `.gitignore` (adds `render-deployment.md`; already done on 2026-11-17)

- [ ] **Step 1: Add** a "Group members" table (name, registration number, student number) and a "Live site" line. Needs the real member details from the owner.
- [ ] **Step 2: Verify** `git check-ignore -v render-deployment.md` prints the rule, and `git status` does not list the file.

### Task 4: Commit and push

**Files:** all of the above.

- [ ] **Step 1:** `git switch -c feature/deploy`, then `git add requirements.txt core/settings.py .gitignore README.md db.sqlite3`.
- [ ] **Step 2:** Commit with a plain message (no attribution lines). Merge into `main`.
- [ ] **Step 3:** `git push origin main`. Expected: latest commit visible on GitHub, including `db.sqlite3` and the README.

### Task 5: Create the Render service

- [ ] **Step 1:** In Render, New + > Web Service, connect `Al-Farhan-Seg/sacco-web-app`, branch `main`, Python 3, Free plan.
- [ ] **Step 2:** Build Command `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`. Start Command `gunicorn core.wsgi:application`.
- [ ] **Step 3:** Environment: `PYTHON_VERSION=3.13.6`, `DEBUG=0`, `SECRET_KEY=<python -c "import secrets; print(secrets.token_urlsafe(50))">`.
- [ ] **Step 4:** Create the service. Expected: logs end with `Listening at: http://0.0.0.0:10000` and a green **Live** badge.

### Task 6: Verify live and submit

- [ ] **Step 1:** On the live URL: styled login, `admin`/`admin123` works, dashboard shows 113 members, `/admin/` and `/analytics/` load, adding a member through the modal succeeds (no CSRF 403).
- [ ] **Step 2:** Put the live URL in the README, commit, push (Render redeploys).
- [ ] **Step 3:** Wake the service by opening it, then post the link in the group.

## Risks

- Free instance sleeps after about 15 minutes idle; first load takes about a minute. Open it before the teacher does.
- Data created on the live site is lost at each restart (ephemeral disk). The committed demo data and `admin` account always return.
- Vercel is not an option: its runtime file system is read-only, so SQLite sessions cannot be written.
