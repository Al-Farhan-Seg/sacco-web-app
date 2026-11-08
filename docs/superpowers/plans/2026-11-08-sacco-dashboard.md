# SACCO Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the SACCO Django project into a logged-in administrator dashboard with live numbers and Add/Edit/Delete modals for seven record types.

**Architecture:** Django generic list/create/update/delete views share small mixins in `core/crud.py`; every data page is one list template plus two shared modal templates; `static/js/modal.js` loads forms into one `<dialog>` and submits them with `fetch`. One stylesheet `static/css/app.css` carries the palette as CSS variables. Money is whole-shilling integers; IDs are Django's automatic `id`, shown as codes.

**Tech Stack:** Django 6.1, SQLite, plain CSS, vanilla JS, Lucide icons (vendored). No other packages.

**Spec:** `docs/superpowers/specs/2026-11-08-sacco-dashboard-design.md`. Visual direction: `PRODUCT.md` and the surface brief at `.impeccable/surfaces/templates-base-html.md` (direction contract). UI tasks also follow `C:/Users/ASUS ROG/.claude/skills/impeccable/reference/craft-floor.md`.

## Global Constraints

- Python 3.13, Django 6.1 only. `requirements.txt` stays `Django==6.1`. Do not use `django-crispy-forms` even though it is installed on this machine.
- No Bootstrap, Tailwind, jQuery, React, charts library, or REST API.
- Exactly one stylesheet: `static/css/app.css`. The old per-page CSS files in `static/css/` are deleted.
- Palette (verbatim): Palladian `#EEE9DF` page, card tint `#FBF9F4`, Oatmeal `#C9C1B1` lines, Abyssal Anchorfish Blue `#1B2632` sidebar and text, Blue Fantastic `#2C3B4D` secondary tiles, Burning Flame `#FFB162` primary buttons and current page, Truffle Trouble `#A35139` delete and errors only, muted grey text `#5B6773`. No green.
- Icons: Lucide, file saved at `static/js/lucide.min.js`. No emoji or glyphs as icons.
- Money fields are `PositiveBigIntegerField` whole UGX, displayed `UGX 850,000` by the `ugx` filter. Amount fields reject 0; `opening_balance` may be 0.
- IDs are never typed. Codes: `MEM-001`, `STF-001`, `ACC-001`, `SAV-001`, `LN-001`, `PAY-001`, `WDR-001` (prefix + `pk` zero-padded to 3).
- All FKs use `on_delete=models.CASCADE`.
- Every view except `login` requires login. Login at `/login/`, logout at `/logout/` (POST), dashboard at `/`. After login go to `/`; after logout go to `/login/`.
- URL names are `<name>_list`, `<name>_add`, `<name>_edit`, `<name>_delete` where `<name>` is `member`, `staff`, `account`, `saving`, `withdrawal`, `loan`, `payment`. Addresses: `/members/`, `/staff/`, `/accounts/`, `/savings/`, `/withdrawals/`, `/loans/`, `/loan-payments/`, each with `add/`, `<int:pk>/edit/`, `<int:pk>/delete/`.
- Sidebar order: Dashboard, Members, Staff, Accounts, Savings, Withdrawals, Loans, Loan payments, Django Admin (bottom), signed-in user, Log out.
- Do not touch `db.sqlite3`. Never run `migrate` against it except in Task 9. Tests use Django's test database.
- Do not commit `db.sqlite3`. Commit messages carry no AI attribution lines.
- Field names follow the frontend pages (see spec section 5), not `SACCO Script.sql`.

## Review Focus

- A fetch or POST to a modal URL while logged out must send the browser to the login page, never inject the login page into the modal (Task 2 owns `modal.js`; Task 1 owns the redirect).
- Deleting the only row on the last page, then reloading the same `?page=N`, must show the last remaining page, not a 404 (Task 1).
- Amount fields reject 0, negatives and blanks; date fields are required (Tasks 4, 5, 6).
- A saving's account must belong to the saving's member; a loan payment must not exceed what is still owed on the loan, including when editing the payment itself (Tasks 5, 6).
- `account_number` duplicates are rejected; every list page and the dashboard work on an empty database (empty-state row, zeros) (Tasks 3 to 7).

---

## File Structure

```
core/models.py                CodedModel (abstract)
core/crud.py                  ListPage, ModalFormMixin, ModalDeleteMixin, crud_urls
core/forms.py                 DateInput widget
core/templatetags/sacco.py    ugx filter
core/urls.py                  root routes (modified)   core/settings.py (modified)
templates/base.html           app shell
templates/partials/           _sidebar.html _modal_form.html _modal_delete.html _pagination.html _row_actions.html
templates/registration/login.html
templates/<app>/<model>_list.html   one per data page; templates/dashboard/index.html
static/css/app.css  static/js/modal.js  static/js/lucide.min.js
<app>/models.py forms.py views.py urls.py admin.py tests.py   (members staff accounts savings withdrawals loans)
dashboard/stats.py dashboard/views.py dashboard/management/commands/seed.py
```

---

### Task 1: Core utilities and authentication

**Files:**
- Create: `core/models.py`, `core/crud.py`, `core/forms.py`, `core/templatetags/__init__.py`, `core/templatetags/sacco.py`, `core/tests.py`, `templates/registration/login.html` (a minimal placeholder: a plain `<form method="post">` with `{% csrf_token %}`, `{{ form.as_p }}` and a submit button, so login tests can render; Task 2 replaces it with the real page)
- Modify: `core/settings.py`, `core/urls.py`, `dashboard/views.py`

**Interfaces:**
- Produces:
  - `core.models.CodedModel` (abstract `models.Model`): class attribute `code_prefix: str`; property `code -> str` returning `f"{code_prefix}-{pk:03d}"`; `__str__` returns `self.code`.
  - `core.forms.DateInput(forms.DateInput)` with `input_type = "date"` and `format = "%Y-%m-%d"`.
  - Template filter `ugx` in library `sacco`: `ugx(value: int | None) -> str` giving `"UGX 850,000"`; `None` gives `"UGX 0"`.
  - `core.crud.ListPage(LoginRequiredMixin, ListView)`: `paginate_by = 10`, `ordering = ["-id"]`, attributes `page_title: str`, `add_label: str`, `url_name: str` (the `<name>` prefix). Context adds `page_title`, `add_label`, `add_url` (reverse of `<url_name>_add`). An out-of-range `?page=` shows the last page instead of 404.
  - `core.crud.ModalFormMixin(LoginRequiredMixin)`: `template_name = "partials/modal_form.html"`; context `modal_title` (`"Add <verbose_name>"` or `"Edit <code>"`) ; `form_valid` saves, calls `messages.success(request, f"{code} saved")`, returns `HttpResponse(status=204)`; `form_invalid` renders the template with status 400.
  - `core.crud.ModalDeleteMixin(LoginRequiredMixin)`: `template_name = "partials/modal_delete.html"`, attribute `delete_note: str = ""`; context adds `delete_note`; `form_valid` deletes, `messages.success(request, f"{code} deleted")`, returns 204.
  - `core.crud.crud_urls(prefix: str, name: str, list_view, create_view, update_view, delete_view) -> list` of `path()` entries named as in Global Constraints.
- Consumes: nothing.

- [ ] **Step 1: Write failing tests in `core/tests.py`:** `test_ugx_formats_thousands` (`ugx(850000) == "UGX 850,000"`, `ugx(0) == "UGX 0"`, `ugx(None) == "UGX 0"`); `test_coded_model_code` (define `class Fake: pk = 7; code_prefix = "MEM"; code = CodedModel.code` and assert `Fake().code == "MEM-007"`, no database needed); `test_login_required_redirects` (GET `/` as anonymous gives 302 to `/login/?next=/`); `test_login_flow` (create user, POST `/login/` with credentials gives 302 to `/`; POST `/logout/` gives 302 to `/login/`); `test_wrong_password_stays_on_login` (200 and the form error present).
- [ ] **Step 2: Run** `python manage.py test core -v 2`. Expected: FAIL (imports and routes missing).
- [ ] **Step 3: Implement** the interfaces above in the listed files. In `core/settings.py` add `"core"` to `INSTALLED_APPS` first, and set `LOGIN_URL = "login"`, `LOGIN_REDIRECT_URL = "/"`, `LOGOUT_REDIRECT_URL = "login"`. In `core/urls.py` replace the old flat `.html` routes with: `admin/`, `login/` (`LoginView`, name `login`), `logout/` (`LogoutView`, name `logout`), `""` (dashboard `index`, name `dashboard`); leave a clearly marked place for later includes. `dashboard/views.py::index` becomes `@login_required` and renders `dashboard/index.html` (the old template stays until Task 2). Remove the unused imports of the old views (staff `login_view` and the rest) from `core/urls.py`, leaving the old view modules untouched until their tasks.
- [ ] **Step 4: Add tests** for `ListPage` pagination using `django.test.RequestFactory` with a minimal view over `django.contrib.auth.models.User` (`test_out_of_range_page_shows_last_page`: 12 users, `?page=9` gives page 2, status 200) and the modal mixins are tested through the real Members model in Task 3.
- [ ] **Step 5: Run** `python manage.py test core -v 2` and `python manage.py check`. Expected: all PASS, no issues.
- [ ] **Step 6: Commit** `git add core dashboard && git commit -m "Add core CRUD helpers, ugx filter and login routes"`.

---

### Task 2: App shell, styling and modal script

**Files:**
- Create: `templates/base.html`, `templates/partials/_sidebar.html`, `_modal_form.html`, `_modal_delete.html`, `_pagination.html`, `_row_actions.html`, `templates/registration/login.html`, `static/css/app.css`, `static/js/modal.js`, `static/js/lucide.min.js`
- Delete: the old per-page CSS files in `static/css/` (`account.css index.css loan-payment.css loan.css login.css member.css saving.css staff.css withdrawal.css`), `static/js/form-validation.js`, `static/images/images.png`, and the old templates `templates/accounts/account.html`, `templates/staff/login.html`, `templates/staff/staff.html`, `templates/members/member.html`, `templates/savings/saving.html`, `templates/loans/loan.html`, `templates/loans/loan_payment.html`, `templates/withdrawals/withdrawal.html`
- Modify: `templates/dashboard/index.html`, `core/tests.py`

**Interfaces:**
- Consumes: Task 1 (`login`, `logout`, `dashboard` URL names; `ugx` filter; messages framework).
- Produces:
  - `_sidebar.html` uses literal paths (not `{% url %}`) for every link so it works before the later routes exist; the current page is highlighted when `request.path` starts with that link's path.
  - `base.html` blocks: `title`, `page_title` (top bar heading), `actions` (right side of the title row, where the Add button goes), `content`. It contains one empty `<dialog id="modal">` and renders `messages` as toasts.
  - Partial `_row_actions.html`, include with `edit_url=` and `delete_url=`, renders a pencil button and a trash button with `data-modal-url` attributes and `aria-label`s "Edit" and "Delete".
  - Partial `_pagination.html`, include with `page_obj`; renders "Showing X to Y of N" and page links preserving no other query params.
  - Partials `_modal_form.html` (context `form`, `modal_title`; renders each field with label and errors in a two-column grid, `non_field_errors`, Cancel and Save buttons, `<form method="post">` with `{% csrf_token %}`) and `_modal_delete.html` (context `object`, `delete_note`; names the record's `__str__`, states "This cannot be undone.", Cancel and Delete buttons).
  - Any element with `data-modal-url="<url>"` opens the modal; `modal.js` behavior: GET the url into `#modal`, `showModal()`; form submit via `fetch` POST with `FormData`; status 204 reloads the page; status 400 replaces the modal content with the returned HTML; if the response was redirected to a URL containing `/login/`, set `window.location` to it; Cancel and the close button call `close()`; after any injection call `lucide.createIcons()`. Messages toasts disappear after 5 seconds.

- [ ] **Step 1: Write failing tests in `core/tests.py`:** `test_shell_has_all_nav_links` (logged-in GET `/` response contains the href of each of `/members/ /staff/ /accounts/ /savings/ /withdrawals/ /loans/ /loan-payments/ /admin/` and the text "Dashboard"); `test_login_page_has_password_input` (`type="password"`); `test_static_assets_exist` (the three static files exist and `app.css` contains each palette hex); `test_no_framework_markup` (`app.css` and templates do not contain `bootstrap` or `tailwind`); `test_old_css_removed`.
- [ ] **Step 2: Run** `python manage.py test core -v 2`. Expected: FAIL.
- [ ] **Step 3: Build the shell and styles** per the surface brief's direction contract: floating dark sidebar (Abyssal, rounded, about 250px) with brand, Dashboard, a "Manage" label, the flat icon list in the Global Constraints order, the Django Admin link pushed to the bottom, then the signed-in username and a Log out form button (POST with CSRF); off-white page; top row with `page_title` and the `actions` block; white-tint cards, 14px radius, soft offset shadows with real blur; tables with small uppercase column heads, tabular figures for numbers; primary buttons Burning Flame with Abyssal text; delete buttons and error text Truffle Trouble; visible `:focus-visible` rings; styled selection, caret and scrollbars from the palette; `prefers-reduced-motion` respected; layout works at 390px (sidebar stacks above content, tables scroll horizontally inside their own container). Palette as CSS variables at the top of `app.css`. Download Lucide with `curl -L https://unpkg.com/lucide@0.469.0/dist/umd/lucide.min.js -o static/js/lucide.min.js` (fall back to jsDelivr `https://cdn.jsdelivr.net/npm/lucide@0.469.0/dist/umd/lucide.min.js`) and use `<i data-lucide="...">`. Icons: layout-dashboard, users, briefcase, wallet, coins, arrow-down-to-line, banknote, credit-card, shield, log-out, plus, pencil, trash-2, x. UI font stack `"Roboto", system-ui, "Segoe UI", sans-serif` with the Google Fonts link for Roboto weights 400 500 700 (the page must still look right if the link fails). Login page is a standalone centred card on an Abyssal ground with the brand tile, "SACCO Management", "Staff sign in", username and password fields, an orange Log in button, and the form error shown in rust.
- [ ] **Step 4: Build `modal.js`** (about 40 lines, no dependencies beyond Lucide) per the Interfaces behavior. Use the native `<dialog>` so Esc and focus trapping work; set `aria-labelledby` from the modal title.
- [ ] **Step 5: Delete** the old CSS, JS, image and templates listed above. Dashboard placeholder `templates/dashboard/index.html` extends `base.html` and shows the text "Dashboard" in `page_title` (real content comes in Task 7).
- [ ] **Step 6: Run** `python manage.py test core -v 2` and `python manage.py check`. Expected: all PASS.
- [ ] **Step 7: Commit** `git add -A templates static core && git commit -m "Add app shell, stylesheet, modal script and login page"`.

---

### Task 3: Members, start to finish (the reference app)

**Files:**
- Create: `members/forms.py`, `members/urls.py`, `templates/members/member_list.html`
- Modify: `members/models.py`, `members/views.py`, `members/admin.py`, `members/tests.py`, `core/urls.py`
- Generated: `members/migrations/0001_initial.py`

**Interfaces:**
- Consumes: `CodedModel`, `ListPage`, `ModalFormMixin`, `ModalDeleteMixin`, `crud_urls`, `DateInput`, partials from Task 2.
- Produces:
  - `members.models.Member(CodedModel)`: `code_prefix = "MEM"`; fields `first_name`, `last_name` (CharField 100), `contact` (CharField 20), `address` (CharField 255), `email` (EmailField), `gender` (CharField 1, choices `("M","Male"),("F","Female")`); `__str__` returns `f"{code} · {first_name} {last_name}"`; `full_name` property.
  - `members.forms.MemberForm` (ModelForm, all fields above, labels "First name", "Last name", "Contact", "Address", "Email", "Gender").
  - Views `MemberList`, `MemberCreate`, `MemberUpdate`, `MemberDelete` in `members/views.py`, URL names `member_list`, `member_add`, `member_edit`, `member_delete` at `/members/...`. `MemberDelete.delete_note = "their accounts, savings, loans and withdrawals"`.
  - Pattern note for Tasks 4 to 6: copy this structure exactly.

- [ ] **Step 1: Write failing tests in `members/tests.py`:** `test_code_is_prefixed_and_padded` (first member `MEM-001`); `test_str_includes_code_and_name`; `test_list_requires_login` (302 to login); `test_list_shows_members_newest_first_and_empty_state` (empty DB shows "No members yet"); `test_add_valid_returns_204_and_creates`; `test_add_invalid_returns_400_with_error` (bad email); `test_edit_get_prefilled_and_post_updates`; `test_delete_get_confirms_and_post_removes`; `test_modal_urls_redirect_to_login_when_anonymous` (GET and POST of add/edit/delete give 302 to login); `test_delete_last_row_of_last_page_reload_ok` (11 members, delete the one on page 2, GET `?page=2` returns 200 showing page 1 content); `test_success_message_set` (message "MEM-001 saved" present after valid add).
- [ ] **Step 2: Run** `python manage.py test members -v 2`. Expected: FAIL.
- [ ] **Step 3: Implement** model, form, views, `members/urls.py` (a `urlpatterns = crud_urls("members", "member", ...)`), include in `core/urls.py`, admin `admin.site.register(Member)`, `python manage.py makemigrations members`. List template extends `base.html`: `page_title` "Members", `actions` block holds the orange "Add member" button (`data-modal-url` to `member_add`); a card with a table whose columns are Member ID (the `code`), First name, Last name, Contact, Address, Email, Gender (`get_gender_display`), and a row-actions column using `_row_actions.html`; `{% empty %}` row "No members yet."; `_pagination.html` below.
- [ ] **Step 4: Run** `python manage.py test members core -v 2` and `python manage.py check`. Expected: all PASS.
- [ ] **Step 5: Commit** `git add members core templates && git commit -m "Add members with list, add, edit and delete modals"`.

---

### Task 4: Staff and Accounts

**Files:**
- Create: `staff/forms.py`, `staff/urls.py`, `accounts/forms.py`, `accounts/urls.py`, `templates/staff/staff_list.html`, `templates/accounts/account_list.html`
- Modify: models, views, admin, tests of both apps; `core/urls.py`
- Generated: both apps' `0001_initial.py`

**Interfaces:**
- Consumes: the Task 3 pattern; `members.models.Member`.
- Produces:
  - `staff.models.Staff(CodedModel)`: `code_prefix = "STF"`; `first_name`, `last_name`, `gender` (M/F as Member), `position` (CharField 100), `role` (CharField 10, choices `("Admin","Admin"),("User","User")`), `contact` (CharField 20), `address` (CharField 255); `__str__` is `f"{code} · {first_name} {last_name}"`. URL names `staff_list`, `staff_add`, `staff_edit`, `staff_delete`; `StaffDelete.delete_note = "the savings and loans they recorded"`. Table shows role as a small tag.
  - `accounts.models.Account(CodedModel)`: `code_prefix = "ACC"`; `member` FK to `members.Member`, `account_number` (CharField 20, unique), `account_type` (CharField 10, choices Savings/Current), `opening_balance` (PositiveBigIntegerField, default 0); no `balance` property yet (Task 5 adds it). `__str__` is `f"{code} · {account_number} ({account_type})"`. URL names `account_*`; `AccountDelete.delete_note = "its savings"`. Table columns: Account ID, Member (`member` str), Account number, Type, Opening balance (`opening_balance|ugx`); Task 5 replaces this column with Balance.

- [ ] **Step 1: Write failing tests** in both `tests.py` files covering, for each model: code prefix, list requires login with empty state, valid add returns 204, invalid add returns 400, edit, delete, plus `test_role_choices_only_admin_or_user`, `test_account_number_must_be_unique` (400 and error text), `test_opening_balance_may_be_zero`, `test_negative_opening_balance_rejected`, `test_deleting_member_deletes_accounts`.
- [ ] **Step 2: Run** `python manage.py test staff accounts -v 2`. Expected: FAIL.
- [ ] **Step 3: Implement** models, forms, views, urls, includes, admin registrations and list templates, then `python manage.py makemigrations staff accounts`. Note `accounts` depends on `members` migration `0001`.
- [ ] **Step 4: Run** `python manage.py test staff accounts members core -v 2` and `python manage.py check`. Expected: all PASS.
- [ ] **Step 5: Commit** `git add staff accounts core templates && git commit -m "Add staff and accounts pages"`.

---

### Task 5: Savings and Withdrawals

**Files:**
- Create: `savings/forms.py`, `savings/urls.py`, `withdrawals/forms.py`, `withdrawals/urls.py`, `templates/savings/saving_list.html`, `templates/withdrawals/withdrawal_list.html`
- Modify: models, views, admin, tests of both apps; `core/urls.py`; `accounts/models.py`; `templates/accounts/account_list.html`
- Generated: both apps' `0001_initial.py`

**Interfaces:**
- Consumes: Task 3 pattern; `Member`, `Account`, `Staff`.
- Produces:
  - `savings.models.Saving(CodedModel)`: `code_prefix = "SAV"`; `member`, `account` (FK, `related_name="savings"`), `staff` (FK); `payment_method` (CharField 10, choices `("Cash","Cash"),("Mobile","Mobile Money"),("Bank","Bank Transfer")`); `amount` (PositiveBigIntegerField, validator `MinValueValidator(1)`); `date` (DateField). `clean()` raises `ValidationError` when `account.member != member`, and does nothing when `member_id` or `account_id` is missing (the field errors are already reported). URL names `saving_*`. Table columns: Savings ID, Member, Account, Method (display), Amount (`ugx`), Date, Staff. Form uses `DateInput` for `date`.
  - `Account.balance` property added in `accounts/models.py`: `opening_balance` plus the sum of `savings.amount` (0 when none), using one aggregate query. The Accounts table column becomes "Balance" (`balance|ugx`) in `templates/accounts/account_list.html`. Task 5 therefore also modifies `accounts/models.py` and that template.
  - `withdrawals.models.Withdrawal(CodedModel)`: `code_prefix = "WDR"`; `member` FK; `amount` (PositiveBigIntegerField, `MinValueValidator(1)`); `date` (DateField). URL names `withdrawal_*`. Table header for amount is "Amount (final balance)".

- [ ] **Step 1: Write failing tests:** for both apps the standard set (code prefix, login required, empty state, valid add 204, invalid add 400, edit, delete); plus `test_account_balance_equals_opening_when_no_savings`, `test_account_balance_adds_savings` (opening 5,000 plus savings 1,000 and 2,500 gives 8,500), `test_balance_updates_after_saving_edit_and_delete`, `test_saving_rejects_account_of_other_member` (400, error text names the problem), `test_saving_amount_zero_rejected`, `test_saving_date_required`, `test_withdrawal_amount_zero_rejected`, `test_withdrawal_does_not_change_balances` (account balance unchanged after a withdrawal).
- [ ] **Step 2: Run** `python manage.py test savings withdrawals -v 2`. Expected: FAIL.
- [ ] **Step 3: Implement** as in Task 3; foreign-key dropdowns show each object's `__str__`; run `makemigrations savings withdrawals`.
- [ ] **Step 4: Run** `python manage.py test savings withdrawals accounts members staff core -v 2` and `python manage.py check`. Expected: all PASS.
- [ ] **Step 5: Commit** `git add savings withdrawals core templates && git commit -m "Add savings and withdrawals pages"`.

---

### Task 6: Loans and Loan payments

**Files:**
- Create: `loans/forms.py`, `loans/urls.py`, `templates/loans/loan_list.html`, `templates/loans/payment_list.html`
- Modify: `loans/models.py`, `loans/views.py`, `loans/admin.py`, `loans/tests.py`, `core/urls.py`
- Generated: `loans/migrations/0001_initial.py`

**Interfaces:**
- Consumes: Task 3 pattern; `Member`, `Staff`.
- Produces:
  - `loans.models.Loan(CodedModel)`: `code_prefix = "LN"`; `member`, `staff` FKs; `loan_amount` (PositiveBigIntegerField, min 1); `payment_period` (CharField 100); `payment_amount` (PositiveBigIntegerField, min 1); properties `total_paid -> int` and `outstanding -> int` (loan_amount minus total_paid). `__str__` is `f"{code} · {member.full_name}"`. URL names `loan_*` at `/loans/...`; `LoanDelete.delete_note = "its payments"`.
  - `loans.models.LoanPayment(CodedModel)`: `code_prefix = "PAY"`; `loan` FK (`related_name="payments"`); `amount` (min 1); `date`. `clean()` raises `ValidationError` when `amount` exceeds the loan's `loan_amount` minus the sum of its other payments (exclude `self.pk`), and does nothing when `loan_id` or `amount` is missing. URL names `payment_list`, `payment_add`, `payment_edit`, `payment_delete` at `/loan-payments/...`. Loan table columns: Loan ID, Member, Staff, Loan amount, Payment period, Payment amount, Still owed (`outstanding|ugx`). Payment table columns: Payment ID, Loan, Amount, Date. Both apps' views live in `loans/views.py`; both URL lists come from `crud_urls` in `loans/urls.py` and are included at the root (`path("", include("loans.urls"))`).

- [ ] **Step 1: Write failing tests:** standard set for both models; `test_outstanding_is_loan_minus_payments` (2,000,000 loan, payments 180,000 and 90,000 gives 1,730,000), `test_payment_cannot_exceed_outstanding` (400), `test_editing_payment_ignores_its_own_amount` (editing a payment up to exactly the remaining balance succeeds), `test_loan_amount_zero_rejected`, `test_payment_date_required`, `test_deleting_loan_deletes_payments`, `test_deleting_member_deletes_loans`.
- [ ] **Step 2: Run** `python manage.py test loans -v 2`. Expected: FAIL.
- [ ] **Step 3: Implement** as in Task 3; run `makemigrations loans`.
- [ ] **Step 4: Run** `python manage.py test` (whole suite) and `python manage.py check`. Expected: all PASS.
- [ ] **Step 5: Commit** `git add loans core templates && git commit -m "Add loans and loan payments pages"`.

---

### Task 7: Dashboard

**Files:**
- Create: `dashboard/stats.py`
- Modify: `dashboard/views.py`, `dashboard/tests.py`, `templates/dashboard/index.html`, `static/css/app.css`

**Interfaces:**
- Consumes: all models.
- Produces: `dashboard.stats.summary() -> dict` with integer keys `members`, `staff`, `accounts`, `total_savings` (sum of all `opening_balance` plus sum of all `Saving.amount`), `loans_count`, `loans_total`, `repayments_total`, `still_owed` (`loans_total - repayments_total`), `withdrawals_count`, `withdrawals_total`; and querysets `recent_savings`, `recent_loans` (newest five by `-id`, with `select_related`). `dashboard.views.index` passes `summary()` as the template context.

- [ ] **Step 1: Write failing tests in `dashboard/tests.py`:** `test_summary_on_empty_database_is_all_zeros`; `test_summary_values` (known fixture: 2 members, 1 staff, 2 accounts with opening 5,000 and 7,000, savings 1,000 and 2,000, one loan of 2,000,000, payments 180,000 and 90,000, one withdrawal of 850,000; assert every key); `test_total_savings_tracks_edits_and_deletes`; `test_recent_lists_limited_to_five_newest_first`; `test_dashboard_renders_numbers_formatted` (response contains `UGX 3,000` style output and each card label); `test_dashboard_empty_state_renders` (200 with no records, recent tables show "No savings yet." and "No loans yet.").
- [ ] **Step 2: Run** `python manage.py test dashboard -v 2`. Expected: FAIL.
- [ ] **Step 3: Implement** `summary()` with database aggregates (no per-row Python loops), the view, and the template: two rows of four number cards in this order: Members, Staff, Accounts, Total savings, Loans issued (count; caption shows `loans_total|ugx` lent), Loan repayments, Still owed, Withdrawals (count; caption shows `withdrawals_total|ugx` paid out); each card has the raised coloured icon tile standing on its top edge (tiles alternate Burning Flame, Blue Fantastic, Truffle Trouble backgrounds; Truffle Trouble tiles are decoration only here, so use it for at most two tiles) with Lucide icons users, briefcase, wallet, coins, banknote, credit-card, circle-alert, arrow-down-to-line; then two cards side by side: "Recent savings" and "Recent loans" with compact tables. Total savings is visually the largest figure. Only dashboard-specific CSS goes in `app.css`.
- [ ] **Step 4: Run** `python manage.py test` and `python manage.py check`. Expected: all PASS.
- [ ] **Step 5: Commit** `git add dashboard static templates && git commit -m "Add dashboard with live numbers and recent activity"`.

---

### Task 8: Seed command

**Files:**
- Create: `dashboard/management/__init__.py`, `dashboard/management/commands/__init__.py`, `dashboard/management/commands/seed.py`
- Modify: `dashboard/tests.py`

**Interfaces:**
- Consumes: all models.
- Produces: management command `python manage.py seed [--reset]` that is idempotent: with `--reset` it deletes all Saving, Withdrawal, LoanPayment, Loan, Account, Staff, Member rows first; without it, it exits with a message when `Member` rows exist. It ensures a user `admin` exists (superuser, password `sacco-demo-2026`, printed at the end). Uses `random.Random(2026)` so output is repeatable, plain Python only. Creates about 60 members (Ugandan names and Kampala-area addresses, valid-format emails and `07xxxxxxxx` contacts), 8 staff (mix of Admin and User, varied positions), 90 accounts (1 to 3 per member, unique account numbers starting `10001`), about 300 savings (account always belongs to the member, dates over the last 12 months, all three payment methods), about 25 loans, about 70 loan payments (never exceeding the loan), 6 withdrawals. All amounts are whole UGX, multiples of 1,000.

- [ ] **Step 1: Write failing tests:** `test_seed_creates_expected_counts_ranges`; `test_seed_is_repeatable_with_reset` (two runs give identical counts); `test_seed_refuses_without_reset_when_data_exists`; `test_seed_invariants` (every saving's account belongs to its member; no loan has negative outstanding; account numbers unique); `test_seed_creates_admin_who_can_log_in`.
- [ ] **Step 2: Run** `python manage.py test dashboard -v 2`. Expected: FAIL.
- [ ] **Step 3: Implement** `seed.py`; wrap the whole run in `transaction.atomic`.
- [ ] **Step 4: Run** `python manage.py test` and `python manage.py check`. Expected: all PASS.
- [ ] **Step 5: Commit** `git add dashboard && git commit -m "Add seed command for demo data"`.

---

### Task 9: Documentation and final wiring

**Files:**
- Modify: `README.md`, `BACKEND_DETAIL.md`, `requirements.txt` (only if it is not exactly `Django==6.1`)
- Do not commit: `db.sqlite3`

**Interfaces:**
- Consumes: everything.
- Produces: README with setup (venv, `pip install -r requirements.txt`, `python manage.py migrate`, `python manage.py seed --reset`, `python manage.py runserver`), the demo login (`admin` / `sacco-demo-2026`, labelled throwaway), the list of pages and addresses, and a short project layout; `BACKEND_DETAIL.md` rewritten to describe the built CRUD pattern (models, `core/crud.py` mixins, modal flow, where to add a new data page in five steps) and to no longer mention flat `.html` routes, typed IDs, or "no login".

- [ ] **Step 1: Write the docs** as described; remove statements that are now false (no login, no models, flat routes, typed IDs, `db.sqlite3` ignored).
- [ ] **Step 2: Run the real database setup:** `python manage.py migrate` then `python manage.py seed --reset`. Expected: migrations apply, seed prints counts and the demo login.
- [ ] **Step 3: Run** `python manage.py test` and `python manage.py check`. Expected: all PASS, "System check identified no issues".
- [ ] **Step 4: Smoke test the live site** with the Django test client against the real database (a short script run with `python manage.py shell`): log in as `admin`, GET `/` and each of the seven list addresses, assert status 200 and that each page contains its Add button text. Expected: all 200.
- [ ] **Step 5: Commit** `git add README.md BACKEND_DETAIL.md requirements.txt && git commit -m "Update README and backend guide for the dashboard"`. Leave `db.sqlite3` uncommitted for the repository owner.
