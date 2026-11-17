# Lesson: "Why is my deployed app empty?" (Django + Render + SQLite vs Postgres)

> **Who this is for:** me, as a junior dev, now and later.
> **What it is:** a worked case study from the RealEstate-Management-System class project (Nov 17, 2026). It covers what broke, how we found the cause, how we fixed it, and the habits worth keeping.
> **Not specific to one project.** The same trap applies to any app that works locally and shows nothing after deployment, including the SACCO app.

---

## 1. The one-paragraph summary

The app worked locally with real data (98 clients, 20 leases, 57 payments). The live site at Render showed **an empty database**. Nothing was "broken". The live app was talking to a **different database** than the one on the laptop. Locally Django used the `db.sqlite3` file. On Render the config said "use a brand-new Postgres database", and nobody ever put data into it. We fixed it by making the app use the committed `db.sqlite3` everywhere, then removed the leftover code that no longer applied.

**The core lesson:** *"It works on my machine" almost always means "my machine has state (data, env vars, files) the server doesn't have."* When a deployed app behaves differently, first ask **which database, which config and which files is it really using?** Don't start by suspecting the code.

---

## 2. Vocabulary you need first

| Term | Plain meaning |
|---|---|
| **Schema** | The *shape* of the database: tables and columns. `migrate` creates this. |
| **Data** | The *rows* inside the tables. `migrate` does **not** create these. |
| **Migration** | A script Django runs to build or change the schema. |
| **Fixture** | A JSON file of rows that `loaddata` can insert into a database. |
| **Seed** | Putting starting data into a database. |
| **Environment variable** | A setting supplied from outside the code (e.g. `DATABASE_URL`). It differs per machine. |
| **Ephemeral disk** | Files written while the app runs are thrown away on every deploy or restart. |
| **Blueprint (`render.yaml`)** | A file that tells Render which services and databases to create. |
| **Fast-forward pull** | A `git pull` that just moves your branch forward with no merge. |

The key point: **`migrate` builds empty tables. An "empty app" after a successful deploy is exactly what a working `migrate` with no seeding looks like.** There is no error, which is why it's confusing.

---

## 3. What happened (timeline)

| Commit | What it did | Why it matters |
|---|---|---|
| `af9bd96` Prepare Django project for Render deployment | Added `render.yaml`, `build.sh`, `settings.py` changes | Created a **separate Postgres DB** and told Django to use it via `DATABASE_URL` |
| `7e354c5` Create production Django superuser | Added `createsuperuser --noinput \|\| true` to `build.sh` | One-off workaround to get an admin login on the empty DB |
| `ed07ca5` Add production superuser creation command | Replaced it with a custom management command | Same goal, safer version |
| `15f1d9e` Remove temporary superuser creation command | Removed the **call** from `build.sh` | The command's **file stayed** in the repo, so it became dead code |
| `05f5b8f` | Our fix: switched to committed SQLite | Solved the empty-site problem |
| `dd4d59f` | Removed dead code and unused packages | Cleanup |

The three superuser commits are a **symptom**. People kept patching around "the live DB is empty" (creating just one admin user) instead of asking why it was empty.

---

## 4. Root cause, step by step

```
LOCAL                                   RENDER
-----                                   ------
settings.py -> db.sqlite3  (has data)   settings.py -> reads DATABASE_URL
                                                      |
                                                      v
                                        Postgres "realestate-db"  (brand new, EMPTY)
                                        db.sqlite3 in the repo is never opened
```

Three facts combined to cause it:

1. **`render.yaml` created a separate Postgres database** and injected its address as `DATABASE_URL`.
2. **`settings.py` said:** "if `DATABASE_URL` exists, use it; otherwise fall back to `db.sqlite3`." On Render it exists, so SQLite was ignored. The fallback only applied locally.
3. **`build.sh` only ran `migrate`.** It creates tables but never inserts rows. No fixture or seed step existed.

Result: a perfect, working, completely empty app.

---

## 5. How we investigated (the method, reusable anywhere)

We followed the *systematic debugging* rule: **find the root cause before you change anything.**

**Step 1: Read the config that decides behaviour, not just the code.**
We read `render.yaml`, `build.sh`, `requirements.txt` and the database section of `settings.py`. The bug was in the *wiring*, not in any view or model.

**Step 2: Check the git history for clues.**
`git log --oneline --all` showed the three "superuser" commits. A pile of workaround commits around one symptom tells you the real problem is upstream.

**Step 3: Verify claims instead of trusting them.**
The briefing said the superuser command was "removed from the repo". When we looked, **the file was still there**; only its call in `build.sh` had been removed. It also said `seed_demo` could re-seed the data, but it needs a `names.json` file that isn't committed, so it couldn't run on Render. *Assumptions from a previous investigation were partly wrong. Always re-check.*

**Step 4: Notice your own checkout is stale.**
`render.yaml` didn't exist locally. The cause: local `main` was **4 commits behind** `origin/main`. Fix: read the remote versions with `git show origin/main:<file>` before pulling, then `git pull --ff-only`.

**Step 5: Count the data on both sides.**
We counted rows in the local DB and in the *committed* copy (`git show HEAD:db.sqlite3`). This showed the committed DB had the right data and the right accounts, while the working copy had extra local test changes. That mattered a lot for the next step.

**Step 6: Say what you can't verify.**
We couldn't know whether the admin user existed on the live Postgres without database access (Render dashboard, then the database, then Connect; or `render psql`). Say "can't tell" instead of guessing.

---

## 6. The fix, step by step

**Decision:** use the committed `db.sqlite3` instead of Postgres. For a class project that must show the same data every time, this is simpler.

1. **`git pull --ff-only`** to get the deployment files.
2. **`settings.py`:** replaced the `dj_database_url.config(...)` call with a plain SQLite setting:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': BASE_DIR / 'db.sqlite3',
       }
   }
   ```
   We used a plain setting rather than keeping the fallback on purpose. If a leftover `DATABASE_URL` still exists on the Render service, it can no longer silently send the app back to Postgres.
3. **`settings.py`:** removed the rule that crashed startup when `DATABASE_URL` was missing.
4. **`render.yaml`:** deleted the `databases:` block and the `DATABASE_URL` variable.
5. **`README.md`:** updated the deploy section so the docs match reality.
6. **Verified:** `manage.py check` passed locally *and* with Render-like env vars (`RENDER=1`, `SECRET_KEY=...`).
7. **Committed only the files we meant to**, not the modified `db.sqlite3`.
8. **Cleanup commit:** deleted the dead `create_render_superuser.py` and removed `psycopg2-binary` and `dj-database-url` from `requirements.txt`, then re-ran `check`.

We skipped the fixture approach we first proposed. With a committed database, the data already ships with the repo, and a fixture would be a second copy to keep in sync.

---

## 7. Mistakes and what each one teaches

These are framed as process lessons, not blame. Every one of them is easy to make.

### 7.1 Changing the database in production without a data plan
Switching to a new Postgres DB meant the data had to be moved somewhere. Nobody planned that.
**Rule:** before changing where data lives, write down *how the data gets there.*

### 7.2 Patching the symptom three times
Three commits tried to get an admin login working on an empty DB.
**Rule:** if you've made two workaround commits for the same symptom, stop and ask what's upstream. (This is the "3 failed fixes means question the design" rule.)

### 7.3 Hiding failures with `|| true`
`createsuperuser --noinput || true` swallows errors. If the needed `DJANGO_SUPERUSER_*` variables were never set, the command fails and the build says "success."
**Rule:** `|| true` makes failures invisible. If you must use it, log *why*. Prefer a command that is safe to run twice (idempotent) instead.

### 7.4 "Removing" code by removing its call, not the code
The command's call left `build.sh`, but the file stayed. Dead code confuses the next reader, who thinks it's still used.
**Rule:** when you remove a feature, search for every reference (`grep -rn name .`) and delete the definition too.

### 7.5 Trusting a summary instead of the source
Two claims in the briefing were wrong or incomplete (see Step 3 above).
**Rule:** treat other people's summaries, including an AI's or your own from yesterday, as leads to verify.

### 7.6 Working on a stale branch
Local `main` was 4 commits behind, so the key files were invisible.
**Rule:** run `git fetch` and `git status` first. `git log HEAD..origin/main` shows what you're missing.

### 7.7 My own slip: a test that touched the real database
When testing the fixture, I set `DATABASE_URL` to point at a scratch file. But the local `settings.py` was the *old* version that ignores `DATABASE_URL`, so `migrate` and `loaddata` ran against the **real `db.sqlite3`**. It did no harm, because the fixture was an export of that same data, and I re-counted rows afterwards. It could have gone badly.
**Rules:**
- A safety variable only works if the code actually reads it. **Confirm the test target before running anything that writes.**
- Check that the scratch file got created. Mine never appeared, and that was the warning sign.
- Back up first (`cp db.sqlite3 db.backup`) when a command writes to data you care about.

### 7.8 A tracked file that is also in `.gitignore`
`db.sqlite3` is listed in `.gitignore` but is tracked in git anyway. Ignoring only applies to *untracked* files, so changes still show as modified (`M`) and can be committed by accident with `git add .`.
**Rule:** when a file is both tracked and ignored, always stage files by name, and decide deliberately whether it should be tracked at all.

---

## 8. Postgres vs committed SQLite on a free host

| | Committed SQLite | Render free Postgres |
|---|---|---|
| Starts with your data | **Yes**, it's in the repo | No, starts empty unless you seed it |
| Data added on the live site | **Lost** on every deploy or restart (ephemeral disk) | Kept |
| Extra setup | None | Provisioning, `DATABASE_URL`, seeding |
| Expiry | None | Free tier databases expire (about 30 days at the time of writing; **verify current terms**) |
| Good for | Demos and class projects that must always look the same | Real apps where users create data |

**Rule of thumb:** SQLite committed to git is fine for a read-mostly demo. The moment users should be able to *save* things that stay, you need a real hosted database **plus** a plan to seed and back it up.

---

## 9. Reusable checklist: "works locally, empty or broken when deployed"

1. **Which database is the live app really using?** Look at `DATABASES`, `DATABASE_URL` and the host's dashboard.
2. **Is the data in that database, or only the schema?** `migrate` gives tables, not rows.
3. **Which environment variables differ** between local and production?
4. **What does the build/start script actually run?** Read `build.sh` or the Procfile line by line.
5. **Is the disk ephemeral?** Will files written at runtime survive a restart?
6. **Is your checkout current?** `git fetch`, then compare with `origin/main`.
7. **Read the history** for repeated workaround commits.
8. **Verify, don't assume**, then change **one thing at a time**.
9. **Test against a throwaway target** and confirm it's really the target.
10. **Commit the files you meant to, by name**, and re-check `git status`.

---

## 10. Commands worth remembering

```bash
# See what a file looks like on the remote without changing your checkout
git show origin/main:path/to/file

# See commits you're missing / ahead by
git fetch && git log --oneline HEAD..origin/main

# Safe pull: refuses to create a merge commit
git pull --ff-only

# What the committed copy of a file looks like (to compare with your working copy)
git show HEAD:db.sqlite3 > /tmp/committed.sqlite3

# Find every reference before deleting something
grep -rn "create_render_superuser" .

# Delete a file AND stage the deletion (then `git add <that path>` will fail, since it's already staged)
git rm path/to/file

# Django: confirm the project loads, including with production-like env vars
python manage.py check
RENDER=1 SECRET_KEY=x RENDER_EXTERNAL_HOSTNAME=app.onrender.com python manage.py check

# Export rows to a fixture / load them back (useful when you DO use Postgres)
python manage.py dumpdata clients employees --indent 2 -o seed.json
python manage.py loaddata seed.json   # overwrites rows with the same primary key!
```

A `loaddata` gotcha: it **overwrites** by primary key, so running it on every deploy would wipe edits made on the live site. Guard it so it only runs when the database is empty.

---

## 11. Things to try so it sticks

- In a scratch project, deploy to Render **with** Postgres and seed it with a `loaddata` guard that runs only when the table is empty.
- Write a one-line "data plan" in the README of your next project: *where does production data come from, and how do I back it up?*
- Search an old project for `|| true` and ask what it's hiding.
- Next time something "works on my machine," run the checklist in section 9 before opening the code.
