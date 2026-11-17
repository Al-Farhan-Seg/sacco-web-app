# Deploying the SACCO app to Render: the full guide

Personal working document. It is listed in `.gitignore` and must never be committed.
Written 2026-11-17 for the project-submission announcement from Mr. Walusimbi Abdulhakim.

**Status of this guide:** nothing below has been applied to the repo yet. Part 4 lists the
exact code changes. Every command and click is written so you can follow it top to bottom.

---

## Part 0. What the teacher wants, and how each item gets done

| # | Teacher's requirement | How we meet it | Where in this guide |
|---|---|---|---|
| 1 | Superuser `admin` / `admin123` | The committed `db.sqlite3` already has a superuser called `admin`, **but its password is not `admin123`**. We reset it and commit the database. | Part 3 |
| 2 | README with project title and all group members | Add a "Group members" section to `README.md` | Part 5 |
| 3 | Commit and push to GitHub | One feature branch, merged into `main`, pushed | Part 6 |
| 4 | Deploy on Render (or Vercel) | Render free web service | Parts 4, 7, 8 |
| 5 | Share the deployed link in the group | `https://<your-service-name>.onrender.com` | Part 9 |

Do them in this order. The deployment (4) needs the code changes, the password reset (1)
and the push (3) to be finished first, because Render builds whatever is on GitHub.

---

## Part 1. How this will work (read once, it explains every step)

### 1.1 What Render does
Render watches your GitHub repo. When you push to the branch it follows (`main`), it:

1. Clones the repo onto a Linux machine.
2. Runs your **Build Command** (installs packages, collects static files, runs migrations).
3. Runs your **Start Command** (starts the web server, `gunicorn`).
4. Gives you a public HTTPS address, `https://<name>.onrender.com`.

### 1.2 Why your app needs small changes first
Right now `core/settings.py` is a development file. On a public server it would fail or be unsafe:

| Problem today | What happens on Render | Fix |
|---|---|---|
| `ALLOWED_HOSTS = []` | Every request returns **400 Bad Request** once `DEBUG` is off | Allow the Render hostname |
| `DEBUG = True` | Leaks code and settings on any error page | Turn it off using an environment variable |
| Hard-coded `SECRET_KEY` in a public repo | Anyone can forge sessions | Read it from an environment variable |
| No static file server | CSS, JS and logo do **not** load (Django only serves static files in `DEBUG`) | Add **WhiteNoise** |
| `runserver` is not for production | Slow, insecure | Use **gunicorn** |
| No `CSRF_TRUSTED_ORIGINS` | Login and sign-up forms fail with **403 CSRF verification failed** on HTTPS | Add your Render URL |

### 1.3 The SQLite question (important, decide knowingly)
Your app uses SQLite, which is a single file (`db.sqlite3`) that is committed to GitHub.

On Render's **free** plan the disk is **ephemeral**: it is wiped every time the service
redeploys **and every time it restarts or wakes up after sleeping**. The consequences:

- Every fresh start gives you the committed demo data again (113 members and so on) and the
  `admin` account. This is **good for a class submission**: the teacher always finds a
  working app and a working admin login.
- Anything created on the live site (new sign-ups, new members, edits) **disappears** at the
  next restart. Do not expect live changes to persist.
- If the teacher signs up a new account, it may vanish after the service sleeps. That is
  expected, not a bug.

**Alternatives, and why we are not using them:**

| Option | Verdict |
|---|---|
| Render free Postgres | Expires after 30 days, needs a second service and extra settings (`dj-database-url`, `psycopg`). Over-engineered for a class demo, and you would have to load the demo data again. |
| Render persistent disk | Paid only. |
| Keep SQLite (recommended) | Zero extra setup, matches README ("Django 6.1 and SQLite only"), demo data always present. |

### 1.4 Why not Vercel
Vercel's file system is **read-only** at runtime and functions are serverless. A Django app on
SQLite cannot write (login sessions need to write to the database), so sign-in would break.
Render is the recommended option in the announcement and is the right one here.

### 1.5 Free plan behaviour you must know
- The service **sleeps after about 15 minutes with no traffic**. The next visit takes
  roughly 30 to 60 seconds to wake it. Open the link yourself a few minutes before the
  teacher is expected to look, and warn the group.
- A free web service does not require a card on Render at the time of writing. If the dashboard
  asks for payment details for a free web service, stop and check the current pricing page.

---

## Part 2. Prerequisites checklist

- [ ] A GitHub account that **owns** `Al-Farhan-Seg/sacco-web-app` (you do; remote is
      `https://github.com/Al-Farhan-Seg/sacco-web-app.git`)
- [ ] A Render account. Sign up at https://render.com using **Sign in with GitHub**. This makes
      connecting the repo one click.
- [ ] Python 3.13 and `pip` working on your machine (`python -V` shows 3.13.6 today)
- [ ] The names of every group member, exactly as the teacher knows them (needed for Part 5)

---

## Part 3. Reset the admin password to `admin123`

The database already contains a user `admin` (superuser, staff, active). Its password is
**not** `admin123` (verified on 2026-11-17: `check_password('admin123')` returned `False`).

Run from the project folder:

```powershell
python manage.py changepassword admin
```

Type `admin123` twice. Django's validators may complain that it is "too common"; the
`changepassword` command **enforces validators**, so use the shell instead, which does not:

```powershell
python manage.py shell -c "from django.contrib.auth.models import User; u=User.objects.get(username='admin'); u.set_password('admin123'); u.is_superuser=True; u.is_staff=True; u.is_active=True; u.save(); print('ok', u.check_password('admin123'))"
```

Expected output: `ok True`.

Then **commit `db.sqlite3`** (Part 6). The live site gets its data from the committed
file, so if you forget to commit it, the live admin password stays the old one.

Security note: `admin` / `admin123` is a publicly guessable credential on a public URL. The
teacher requires it, so use it. Do not put anything real in this database.

---

## Part 4. Code changes needed

Four small edits. Make them on a branch (Part 6).

### 4.1 `requirements.txt`
Currently contains only `Django==6.1`. Make it:

```
Django==6.1
gunicorn==23.0.0
whitenoise==6.9.0
```

(Use the newest versions pip offers if these exact ones are not found; run
`pip install gunicorn whitenoise` locally and `pip freeze | findstr -i "gunicorn whitenoise"`
to read the versions you got, then pin those.)

### 4.2 `core/settings.py`

**a) Imports and secrets, top of file.** Add `import os` under `from pathlib import Path`,
then replace the three development lines:

```python
import os
from pathlib import Path

# ...

# The default key is only for running on your own computer.
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-2y+!ivd-1b&=^^i&c+#2n$qj-tzlp8mm&b$n%r838-^bn1+e1s',
)

# DEBUG is on unless the environment says DEBUG=0 (Render sets it to 0).
DEBUG = os.environ.get('DEBUG', '1') == '1'

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Render sets RENDER_EXTERNAL_HOSTNAME automatically, e.g. sacco-web-app.onrender.com
RENDER_HOST = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_HOST:
    ALLOWED_HOSTS.append(RENDER_HOST)
    CSRF_TRUSTED_ORIGINS = [f'https://{RENDER_HOST}']
    # Render terminates HTTPS in front of the app and forwards this header.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
```

**b) WhiteNoise middleware.** It goes directly **after** `SecurityMiddleware`:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ... rest unchanged
]
```

**c) Static files storage.** Under the existing `STATIC_ROOT` line add:

```python
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage'},
}
```

We use `CompressedStaticFilesStorage`, **not** the `Manifest` variant. The manifest
variant raises an error when a template references a file it did not collect, which
would break pages and the test suite for no benefit in a class project.

`STATIC_URL`, `STATICFILES_DIRS` and `STATIC_ROOT` stay as they are. `staticfiles/` is
already in `.gitignore`, which is correct: Render creates it at build time.

### 4.3 `.gitignore`
Append (it is the answer to "gitignored" in your request):

```
# Personal deployment notes, never committed
render-deployment.md
```

Check it works: `git check-ignore -v render-deployment.md` must print the rule.
`git status` must **not** list the file.

### 4.4 `.python-version` (optional but recommended)
Render picks a default Python version that may be newer or older than 3.13. Django 6.1
needs Python 3.12 or newer. The simplest pin is the **environment variable**
`PYTHON_VERSION=3.13.6` set in the Render dashboard (Part 7). No file needed.

### 4.5 Test the changes locally before pushing

```powershell
pip install -r requirements.txt
python manage.py test                       # all 203 tests must still pass
python manage.py check
```

Now simulate production:

```powershell
$env:DEBUG = "0"
python manage.py collectstatic --noinput
python -m gunicorn core.wsgi          # gunicorn needs Linux/macOS; on Windows use the next line instead
# Windows alternative: python manage.py runserver --insecure
```

Open http://127.0.0.1:8000, confirm:
- the page is styled (CSS loads),
- login with `admin` / `admin123` works,
- `/admin/` loads with the logo and colours,
- a wrong URL shows a plain 404 page without a yellow debug screen.

Then reset the variable: `Remove-Item Env:DEBUG`.

Note: gunicorn does not run on native Windows (it needs `fcntl`). That is fine: Render runs
Linux. Locally use `runserver --insecure` with `DEBUG=0`, as shown above.

---

## Part 5. README: title and group members

The teacher wants "the Project Title and the details of all group members" in
`README.md` in the root. The README already starts with the title, `# SACCO Management System`.
Add this directly under the first paragraph (names to be filled in):

```markdown
## Group members

| No. | Name | Registration number | Student number |
|-----|------|---------------------|----------------|
| 1 | <full name> | <reg no> | <student no> |
| 2 | <full name> | <reg no> | <student no> |

**Live site:** https://<your-service-name>.onrender.com
**Admin login:** `admin` / `admin123`
```

Put in whichever details the teacher asked for (name, registration number, student
number, role). Add the live link after Part 7 is finished and push again.

---

## Part 6. Git: branch, commit, push

Your history uses feature branches merged into `main`. Same pattern here.

```powershell
git switch -c feature/deploy
git add requirements.txt core/settings.py .gitignore README.md db.sqlite3
git status                      # confirm render-deployment.md is NOT listed
git commit -m "Prepare the app for deployment on Render and reset the admin password"
git switch main
git merge feature/deploy
git push origin main
```

Rules:
- Do **not** add any AI attribution line to the commit message (your global rule).
- `render-deployment.md` must not appear in `git status`. If it does, the `.gitignore`
  line is missing or the file was tracked earlier (`git rm --cached render-deployment.md`).
- Open https://github.com/Al-Farhan-Seg/sacco-web-app in a browser afterwards and check
  that the latest commit is there and the README shows the group members.
- Confirm you can push: the README says only the owner pushes. You are the owner.

---

## Part 7. Create the Render web service

1. Go to https://dashboard.render.com and sign in with GitHub.
2. Click **New +** (top right) and choose **Web Service**.
3. Choose **Build and deploy from a Git repository** and click **Next**.
4. If the repo is not listed, click **Configure account** and grant Render access to
   `sacco-web-app` (selecting "Only select repositories" is fine). Then select the repo and
   click **Connect**.
5. Fill the form exactly like this:

| Field | Value |
|---|---|
| Name | `sacco-web-app` (this becomes `sacco-web-app.onrender.com`; if taken, choose another and use that in all later steps) |
| Region | The closest to Uganda that is offered (Frankfurt is usually the nearest) |
| Branch | `main` |
| Root Directory | leave empty |
| Runtime / Language | **Python 3** |
| Build Command | `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate` |
| Start Command | `gunicorn core.wsgi:application` |
| Instance Type | **Free** |

6. Open **Advanced** (or **Environment Variables**) and add:

| Key | Value | Why |
|---|---|---|
| `PYTHON_VERSION` | `3.13.6` | Django 6.1 needs Python 3.12+ |
| `DEBUG` | `0` | Turns off debug pages |
| `SECRET_KEY` | a long random string (see below) | Signs sessions and CSRF tokens |

Generate the secret key locally and paste it:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Do not save this key anywhere in the repo.

7. Leave **Auto-Deploy** on (default: **On Commit**). Every push to `main` redeploys.
8. Click **Create Web Service**.

### What you will see
The page switches to a live **Logs** view:

1. `Cloning from https://github.com/Al-Farhan-Seg/sacco-web-app...`
2. `Installing Python version 3.13.6...`
3. `pip install` output, then `collectstatic` ("X static files copied"), then `Applying ...`
   from `migrate` (or "No migrations to apply", which is correct: the committed database
   is already migrated).
4. `Starting gunicorn` and `Listening at: http://0.0.0.0:10000`
5. `Your service is live` with a green **Live** badge. First deploy takes 3 to 6 minutes.

The URL is shown at the top left, under the service name.

---

## Part 8. Verify the live site (do all of it)

Open `https://sacco-web-app.onrender.com` (use your URL). The first load may take about a
minute.

- [ ] Redirects to the login page, styled correctly (colours, fonts, logo)
- [ ] Log in with `admin` / `admin123`, the dashboard shows **113 members, 12 staff,
      173 accounts** and so on
- [ ] `/admin/` opens and lists the models, with the app's logo and colours
- [ ] `/analytics/` shows the charts
- [ ] Open a records page (Members) and use the search box, e.g. `MEM-007`
- [ ] Add a member through the modal (confirms there is no **CSRF 403** error and the
      database is writable). Remember it will disappear on restart; that is expected.
- [ ] Log out, then try **Sign up** with a throwaway account, then log out again

If you will hand the teacher the admin login, also confirm the **Staff status** and
**Superuser status** boxes are ticked for `admin` in `/admin/auth/user/`.

---

## Part 9. Submit

Post in the group, one message:

```
SACCO Management System: https://sacco-web-app.onrender.com
Admin login: admin / admin123
Repo: https://github.com/Al-Farhan-Seg/sacco-web-app
Note: free hosting sleeps when idle, the first load can take about a minute.
```

Do this only after Parts 3 to 8 are complete. The announcement says every requirement must
be finished before the link is shared.

---

## Part 10. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Build fails: `No matching distribution found for Django==6.1` | Render is using Python older than 3.12 | Set `PYTHON_VERSION=3.13.6` in Environment, then **Manual Deploy > Clear build cache & deploy** |
| `Bad Request (400)` on the site | Host not allowed | Check the URL equals `RENDER_EXTERNAL_HOSTNAME` (shown in Environment, added automatically). Confirm the `ALLOWED_HOSTS` block in 4.2a is deployed |
| Site loads with no styling | WhiteNoise not active, or `collectstatic` did not run | Check the middleware order in 4.2b and that the Build Command contains `collectstatic --noinput` |
| `CSRF verification failed` (403) on login or forms | `CSRF_TRUSTED_ORIGINS` or secure-proxy header missing | Confirm 4.2a is deployed and that you are using `https://` |
| `ModuleNotFoundError: gunicorn` or `whitenoise` | Not in `requirements.txt` | Add them, commit, push |
| `ModuleNotFoundError: No module named 'core.wsgi'`... or `Failed to find attribute 'application'` | Wrong start command | Must be exactly `gunicorn core.wsgi:application` and Root Directory empty |
| Login with `admin123` is rejected on the live site | `db.sqlite3` with the new password was not committed and pushed | `git log -1 --stat -- db.sqlite3` should show a recent commit; if not, redo Part 3 and 6 |
| `unable to open database file` or `attempt to write a readonly database` | Very rare; folder not writable | Check Logs; the repo directory on Render is writable by default. Do not move the DB path |
| Everything was fine, now the data I added is gone | Free disk is ephemeral, service restarted | Expected, see 1.3 |
| Page takes a minute to open | Free instance was asleep | Expected, see 1.5. Open it before the teacher does |
| Deploy "succeeded" but the old version is showing | Browser cache, or the push went to another branch | Hard refresh (Ctrl+F5); confirm Render's Branch is `main` |
| `render-deployment.md` shows up in `git status` | Ignore rule missing or file already tracked | Add the rule, run `git rm --cached render-deployment.md` |

Where to look: Render dashboard, your service, **Logs** (live output) and **Events**
(deploy history). **Manual Deploy** (top right) lets you redeploy a commit or clear the
build cache.

---

## Part 11. After submission

- **Update the live site:** commit and push to `main`; Render redeploys itself in a few
  minutes. Each deploy resets the live database to whatever is committed.
- **Change the demo data:** edit locally, commit `db.sqlite3`, push.
- **Rollback:** Render dashboard, service, **Events**, pick an earlier successful deploy,
  **Rollback**.
- **Stop hosting:** service, **Settings**, scroll to **Delete Web Service**.
- **Rotate `SECRET_KEY`:** change it in Environment. All logged-in sessions end. Harmless.

---

## Part 12. Quick command reference

```powershell
# reset admin password
python manage.py shell -c "from django.contrib.auth.models import User; u=User.objects.get(username='admin'); u.set_password('admin123'); u.save(); print(u.check_password('admin123'))"

# run tests
python manage.py test

# simulate production locally
$env:DEBUG = "0"; python manage.py collectstatic --noinput; python manage.py runserver --insecure

# make a secret key
python -c "import secrets; print(secrets.token_urlsafe(50))"

# prove this file is ignored
git check-ignore -v render-deployment.md
```

Render settings in one place:

```
Build Command : pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
Start Command : gunicorn core.wsgi:application
Env           : PYTHON_VERSION=3.13.6   DEBUG=0   SECRET_KEY=<random>
Plan          : Free
```
