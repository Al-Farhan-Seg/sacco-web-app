# Backend Guide for the Team

This file tells you what is already in place in the project (which now lives at the
repository root, not in a `backend/` folder) and exactly what each of us still has to
build, with real code you can copy and adapt. The goal is a simple Django project that
shows the basics: models, forms, views, URLs, templates and the admin site.

If you are new to Django, read the "How Django fits together" and "Worked example"
sections first — they walk through one full app (`members`) end to end. Every other
app follows the exact same five steps.

## How Django fits together

Every page follows the same path:

```
Browser requests a URL
      ↓
core/urls.py        picks which view handles that URL
      ↓
<app>/views.py       the view function: reads the request, talks to the model,
                      decides what to show
      ↓
<app>/models.py       the database table(s) the view reads/writes
      ↓
<app>/forms.py         (used by the view to validate submitted data)
      ↓
templates/<app>/*.html the view renders this, filling in real data
      ↓
Browser shows the page
```

| Piece | Job | Example here |
|---|---|---|
| **Model** | A database table, written as a Python class | `Member` |
| **Form** | Checks the data typed into an HTML form | `MemberForm` |
| **View** | Python function that handles a page | `member(request)` |
| **URL** | Connects a web address to a view | `/member.html` |
| **Template** | The HTML page, with data filled in | `templates/members/member.html` |
| **Admin** | Auto-built admin screens for a model | registered in `members/admin.py` |

An **app** is a folder that holds one feature: its models, forms, views and admin
registration. (Templates currently live together under the root `templates/` folder
instead of inside each app — see "Folder layout" below.)

## What is already done

| Item | State |
|---|---|
| Django project location | The project was moved out of `backend/` and now lives at the repo root. `core/` holds the settings and the main `urls.py` |
| 7 apps | `staff`, `members`, `accounts`, `savings`, `loans`, `withdrawals`, `dashboard` — all at the repo root, one folder each |
| Apps registered | All 7 are listed in `INSTALLED_APPS` in `core/settings.py` |
| Frontend folded in | The marked frontend (HTML/CSS/JS) has been moved into `templates/` and `static/` — see "Folder layout" below |
| Routes | Every page already has a working URL and a one-line view that renders it (see "Routes, right now" below) — you can `runserver` right now and click through every page |
| Database | SQLite (`db.sqlite3`), the Django default. It is not committed to Git |

## What is NOT done (this is the work)

- No models are written. Each app's `models.py` is still empty (just the boilerplate Django generates).
- No forms exist (`forms.py` files haven't been created in any app yet).
- The existing views only render a static page — they don't read or save any data yet.
- No migrations have been run (there's nothing to migrate until models exist).
- Nothing is registered in any `admin.py`, so `/admin/` currently shows nothing but users/groups.
- There is no login/authentication. The login page is just a static form that doesn't do anything yet.
- The tables of records on every page are still the original hardcoded dummy rows from the frontend design — once a model and view exist, those rows should come from the database instead.

## Folder layout

```
manage.py
core/                   project settings and the main urls.py (every page's route lives here for now)
staff/                  app folder — models.py, views.py, admin.py, etc. (no urls.py yet)
  migrations/
  models.py             empty — your job
  views.py               has login_view() and staff(), both just render() for now
  admin.py               empty — your job
members/                app folder, same shape as staff/
accounts/               app folder, same shape
savings/                app folder, same shape
loans/                  app folder, same shape (two views: loan() and loan_payment())
withdrawals/            app folder, same shape
dashboard/              app folder, same shape (no model — see its own section below)
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

Templates live under one shared `templates/` folder at the root (not inside each app), namespaced by app name to avoid clashes — e.g. `templates/accounts/account.html`. `core/settings.py` already points Django at this folder, and each view's `render()` call already uses the right path (e.g. `render(request, 'accounts/account.html')`). You don't need to change any settings — just edit the template files that already exist.

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

Your job for your app is to turn this into the real "show a form, save it if submitted, and list the records" view, following the worked example below. You are editing the *existing* function, not creating a new one, and you do **not** need to touch `core/urls.py` or add a `urls.py` of your own. If later on the team wants proper namespaced URLs and `{% url %}` tags, that's a deliberate follow-up step everyone should agree on together, not something to slip in app-by-app.

## Worked example: the `members` app, start to finish

This is the exact code to write for `members`. Every other app is the same shape —
jump to "Field specs for every app" afterwards for the field list to use instead.

**1. `members/models.py`** — one class per database table. Field names use
`snake_case` (Python convention) even though the HTML form's `name=` attributes are
`Member_id`, `First_name`, etc. — that's fine, you map between them in the form.

```python
from django.db import models


class Member(models.Model):
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
    ]

    member_id = models.CharField(max_length=20, unique=True, help_text="e.g. MEM-001")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    contact = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    email = models.EmailField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    def __str__(self):
        return f"{self.member_id} - {self.first_name} {self.last_name}"
```

**2. Make and run the migration** (do this every time you add or change a model):

```
python manage.py makemigrations members
python manage.py migrate
```

**3. `members/forms.py`** (new file) — a `ModelForm` builds the HTML `<input>`s for
you from the model, and validates submitted data against it.

```python
from django import forms

from .models import Member


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["member_id", "first_name", "last_name", "contact", "address", "email", "gender"]
```

**4. `members/views.py`** — replace the existing placeholder with this:

```python
from django.shortcuts import render

from .forms import MemberForm
from .models import Member


# Shows the member registration page
def member(request):
    if request.method == "POST":
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            form = MemberForm()  # show a blank form again after a successful save
    else:
        form = MemberForm()

    members = Member.objects.all().order_by("-id")

    return render(request, "members/member.html", {
        "form": form,
        "members": members,
    })
```

**5. `templates/members/member.html`** — swap the hand-typed fields and hardcoded
table rows for the real form and real data. Everything else in the file (the header,
nav, page title) stays exactly as it is — you're only touching the `<form>` and the
`<table>`.

Before (hardcoded, what's in the file today):

```html
<form action="">
  <label for="Member_id">Member id</label>
  <input type="text" id="Member_id" name="Member_id" placeholder="MEM-001">
  ...
  <button type="submit">Register Member</button>
</form>
```

After (driven by the form and the model):

```html
<form method="post">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit">Register Member</button>
</form>
```

`{% csrf_token %}` is required on every form that submits with `method="post"` —
Django will reject the submission without it. `{{ form.as_p }}` renders every field
from `MemberForm` wrapped in a `<p>` each; it won't look identical to the original
hand-styled inputs, and that's expected — once this works, whoever owns the CSS can
restyle the auto-generated fields (or use `{{ form.member_id }}`,
`{{ form.first_name }}`, etc. individually to control the markup, matching the
original field-by-field layout exactly). Getting the data flowing correctly comes
first; polishing the exact HTML is a fast follow.

And the table:

```html
<table>
  <thead>
    <tr>
      <th>Member ID</th>
      <th>First Name</th>
      <th>Last Name</th>
      <th>Contact</th>
      <th>Address</th>
      <th>Email</th>
      <th>Gender</th>
    </tr>
  </thead>
  <tbody>
    {% for member in members %}
    <tr>
      <td>{{ member.member_id }}</td>
      <td>{{ member.first_name }}</td>
      <td>{{ member.last_name }}</td>
      <td>{{ member.contact }}</td>
      <td>{{ member.address }}</td>
      <td>{{ member.email }}</td>
      <td>{{ member.get_gender_display }}</td>
    </tr>
    {% empty %}
    <tr><td colspan="7">No members yet.</td></tr>
    {% endfor %}
  </tbody>
</table>
```

(`get_gender_display` is a free method Django gives you on any field with `choices`
— it prints "Male"/"Female" instead of the raw stored "M"/"F".)

**6. `members/admin.py`** — register the model so it shows up at `/admin/`:

```python
from django.contrib import admin

from .models import Member

admin.site.register(Member)
```

That's a whole app, done. Run `python manage.py createsuperuser` once (any app) if
you want to log into `/admin/` to inspect the data you're saving.

## Field specs for every app

Use the same five steps as above for each app, with these fields. Money fields use
`DecimalField(max_digits=12, decimal_places=2)` (never `FloatField` for money —
floats lose precision). Date fields use `DateField()`. IDs are
`CharField(max_length=20, unique=True)`, matching the frontend's typed IDs like
`MEM-001`. A `ForeignKey` means "this row points at a row in another app's model" —
import the other app's model to use it.

### `staff` — `Staff`

| Field | Type |
|---|---|
| `staff_id` | `CharField(max_length=20, unique=True)` |
| `first_name` | `CharField(max_length=100)` |
| `last_name` | `CharField(max_length=100)` |
| `gender` | `CharField(max_length=1, choices=[("M","Male"),("F","Female")])` |
| `position` | `CharField(max_length=100)` |
| `role` | `CharField(max_length=100)` (e.g. "Admin", "User" — matches the dummy data in `staff.html`) |
| `contact` | `CharField(max_length=20)` |
| `address` | `CharField(max_length=255)` |

The `login.html` page has no model behind it yet — there's no login system built.
For now, leave `login_view` as a plain `render()`; building real authentication
(Django's `User`/`AbstractUser`, `LoginView`) is a separate, later decision for the
whole team (see "To decide as a team").

### `members` — `Member`

Already fully specified in the worked example above.

### `accounts` — `Account`

| Field | Type |
|---|---|
| `account_id` | `CharField(max_length=20, unique=True)` |
| `member` | `models.ForeignKey("members.Member", on_delete=models.CASCADE)` |
| `account_number` | `CharField(max_length=20)` (the form field is numeric, but keep it a CharField — leading zeros and formatting are easier this way) |
| `account_type` | `CharField(max_length=10, choices=[("Savings","Savings"),("Current","Current")])` |
| `balance` | `DecimalField(max_digits=12, decimal_places=2, default=0)` |

`on_delete=models.CASCADE` means: if the linked `Member` is deleted, delete this
`Account` too. That's the right default for every `ForeignKey` in this project unless
we decide otherwise as a team.

### `savings` — `Saving`

| Field | Type |
|---|---|
| `savings_id` | `CharField(max_length=20, unique=True)` |
| `member` | `ForeignKey("members.Member", on_delete=models.CASCADE)` |
| `account` | `ForeignKey("accounts.Account", on_delete=models.CASCADE)` |
| `staff` | `ForeignKey("staff.Staff", on_delete=models.CASCADE)` |
| `payment_method` | `CharField(max_length=10, choices=[("Cash","Cash"),("Mobile","Mobile Money"),("Bank","Bank Transfer")])` |
| `amount` | `DecimalField(max_digits=12, decimal_places=2)` |
| `date` | `DateField()` |

**Rule to implement here:** when a `Saving` is saved, add its `amount` to the linked
`Account`'s `balance`. The simplest place to do this is right in the view, after
`form.save()`:

```python
if form.is_valid():
    saving = form.save()
    saving.account.balance += saving.amount
    saving.account.save()
    form = SavingForm()
```

### `loans` — `Loan` and `LoanPayment`

Two models in one app — `loans/models.py` has both classes.

**`Loan`**

| Field | Type |
|---|---|
| `loan_id` | `CharField(max_length=20, unique=True)` |
| `member` | `ForeignKey("members.Member", on_delete=models.CASCADE)` |
| `staff` | `ForeignKey("staff.Staff", on_delete=models.CASCADE)` |
| `loan_amount` | `DecimalField(max_digits=12, decimal_places=2)` |
| `payment_period` | `CharField(max_length=100)` (free text for now, e.g. "12 months" — see "To decide as a team") |
| `payment_amount` | `DecimalField(max_digits=12, decimal_places=2)` |

**`LoanPayment`**

| Field | Type |
|---|---|
| `payment_id` | `CharField(max_length=20, unique=True)` |
| `loan` | `ForeignKey("loans.Loan", on_delete=models.CASCADE)` (same-app FK, so just `"Loan"` without the app prefix also works) |
| `amount` | `DecimalField(max_digits=12, decimal_places=2)` |
| `date` | `DateField()` |

Because there are two models and two pages (`loan.html` and `loan_payment.html`),
`loans/views.py` has two view functions (`loan` and `loan_payment`) — each follows
the same five-step pattern, just scoped to its own model/form/template.

### `withdrawals` — `Withdrawal`

| Field | Type |
|---|---|
| `withdraw_id` | `CharField(max_length=20, unique=True)` |
| `member` | `ForeignKey("members.Member", on_delete=models.CASCADE)` |
| `amount` | `DecimalField(max_digits=12, decimal_places=2)` |
| `date` | `DateField()` |

### `dashboard` — no model

`dashboard/views.py`'s `index` view doesn't get its own model. Once the other apps
have real models, update it to pull small summary numbers from them, e.g.:

```python
from django.db.models import Sum
from django.shortcuts import render

from accounts.models import Account
from loans.models import Loan
from members.models import Member


def index(request):
    context = {
        "total_members": Member.objects.count(),
        "total_savings": Account.objects.aggregate(total=Sum("balance"))["total"] or 0,
        "active_loans": Loan.objects.count(),
    }
    return render(request, "dashboard/index.html", context)
```

Treat this as the very last step (see "Build order" below) — it depends on every
other app already having data to summarize. Leave it as a plain `render()` until then.

## Rules to implement

1. When a saving is recorded, add its amount to the account's balance (see the
   `savings` section above for the exact code).
2. Register every model in its app's `admin.py`, so data can be edited or deleted at
   `/admin/`.
3. There is no login, no editing or deleting from our own pages (use the admin site
   for that), no loan approval, no interest calculation, and no JavaScript beyond the
   existing client-side form-validation script (`static/js/form-validation.js`).

## Definition of done, per app

Before you call your app finished, check every box:

- [ ] Model(s) written in `models.py`, matching the field spec above.
- [ ] `makemigrations` and `migrate` run, with the migration file committed to git.
- [ ] `forms.py` created with a `ModelForm` per model.
- [ ] The existing view function updated: handles `POST` (validate + save), always
      fetches and passes the record list, re-renders the same template.
- [ ] Template's `<form>` uses `method="post"`, `{% csrf_token %}`, and real form
      fields (no more hand-typed `<input>`s with no `name` tied to a form).
- [ ] Template's `<table>` loops over real records with `{% for %}` (no more
      hardcoded `<tr>` dummy rows).
- [ ] Model registered in `admin.py`.
- [ ] You ran `python manage.py runserver`, submitted the form yourself at least
      once, and confirmed the new row shows up both in the table on the page and in
      `/admin/`.
- [ ] `python manage.py check` passes with no errors.

## How to run the project

```
python manage.py runserver
```

Open http://127.0.0.1:8000/ — every page already loads, with its CSS and the shared
nav. After writing or changing any `models.py`:

```
python manage.py makemigrations
python manage.py migrate
```

To look at your data directly, or manage it without building custom pages:

```
python manage.py createsuperuser
```

then log in at http://127.0.0.1:8000/admin/.

## Build order and who does what

Order matters: `staff` and `members` first, because `accounts`, `savings`, `loans`
and `withdrawals` all point to one or both of them via `ForeignKey`.

| Step | Work | Person | Depends on |
|---|---|---|---|
| 1 | `staff` and `members` | Person 1 | nothing |
| 2 | `accounts` | Person 2 | `members` |
| 3 | `savings` | Person 3 | `members`, `accounts`, `staff` |
| 4 | `loans` (`Loan` and `LoanPayment`) | Person 2 | `members`, `staff` |
| 5 | `withdrawals` | Person 3 | `members` |
| 6 | `dashboard` and the admin site | Person 1 | everything above |

If you're blocked waiting on someone else's model (e.g. you're building `savings` and
`accounts` isn't done yet), you can still write your own `models.py` and
`migrations` against a model that exists in code even if its migration hasn't been
run on your machine yet — just pull their branch first, or ask them to push the
model early so you're not stuck guessing at field names.

## Git tips

- Pull before you start work, and push when a feature works.
- Work mostly in your own app's folder (`models.py`, `forms.py`, `views.py`,
  `admin.py`, `migrations/`) and your own template, to avoid merge conflicts.
- The shared files are `core/settings.py` and `core/urls.py`, plus
  `templates/base.html`. Keep changes there small and flag them to the team before
  pushing, since everyone's pages depend on them.
- Do not commit `db.sqlite3` — it's already in `.gitignore`. Each of us runs
  `migrate` on our own machine to get our own local copy of the database.
- Do commit your `migrations/000x_*.py` files — those are code, not data, and
  everyone needs them to build the same database schema.

## Troubleshooting

- **`makemigrations` says "No changes detected"** — check you saved `models.py` and
  that your app is listed in `INSTALLED_APPS` in `core/settings.py` (all seven
  already are, so this is usually a typo in a field name or a forgotten import).
- **`TemplateSyntaxError` after editing a template** — usually a missing
  `{% endfor %}`/`{% endif %}`, or `{% csrf_token %}` placed outside the `<form>`.
  Compare against the worked example above line by line.
- **Form submits but nothing saves** — check the `<form>` tag has
  `method="post"` and that your view actually checks
  `if request.method == "POST":` before building the form from `request.POST`.
- **`RelatedObjectDoesNotExist` or similar when saving a form with a `ForeignKey`
  field** (e.g. `savings` needs an existing `Member`, `Account` and `Staff`) — you
  need at least one row in the apps you depend on before you can test your own form.
  Add a couple of rows through `/admin/` first.
- **Your page 404s** — the routes already exist in `core/urls.py` and shouldn't need
  changes; a 404 usually means you renamed a function in `views.py` without updating
  the import in `core/urls.py`, or the other way around.

## To decide as a team

- Is "payment period" free text or a number of months?
- Does a withdrawal mean the member leaves the SACCO (and if so, should it also
  close their accounts, or is that out of scope)?
- Which roles exist for staff? We suggest Admin and Teller, stored in the `role`
  field as plain text for now (no permissions logic yet).
- When do we build real login/authentication, and does `Staff` become Django's user
  model (`AbstractUser`) at that point, or stay separate with a one-to-one link to a
  `User`?
- When do we want to move from the current flat, literal routes (`/account.html`,
  etc., all in `core/urls.py`) to a proper namespaced `urls.py` per app with
  `{% url %}` tags in the templates? Worth doing once everyone is comfortable with
  the basics, but not before.
