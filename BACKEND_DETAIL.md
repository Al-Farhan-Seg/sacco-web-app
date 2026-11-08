# Backend Guide

How the data pages are built, and how to add another one. Members is the simplest
complete example; every other app follows the same shape.

## Request path

```
Browser -> core/urls.py -> <app>/urls.py -> <app>/views.py -> <app>/forms.py + models.py
        -> templates/<app>/<name>_list.html  (list pages)
        -> templates/partials/_modal_form.html or _modal_delete.html  (modals)
```

Every view requires login (`LoginRequiredMixin`) except Django's login view.
`core/urls.py` mounts `/login/`, `/logout/`, the dashboard at `/`, `/admin/`, and
includes each app's `urls.py`.

## Models and codes

Records have a number Django assigns (`pk`); people never type IDs. Each model
extends `CodedModel` (`core/models.py`) and sets a `code_prefix`. The `code`
property builds the display code from the number, for example `MEM-007`; it is not
stored, and deleted numbers are not reused.

| Model (app) | Prefix | Fields besides the foreign keys |
|---|---|---|
| Member (members) | `MEM` | first_name, last_name, contact, address, email, gender |
| Staff (staff) | `STF` | first_name, last_name, gender, position, role (Admin/User label only), contact, address |
| Account (accounts) | `ACC` | member, account_number (unique), account_type, opening_balance |
| Saving (savings) | `SAV` | member, account, staff, payment_method, amount, date |
| Withdrawal (withdrawals) | `WDR` | member, amount, date |
| Loan (loans) | `LN` | member, staff, loan_amount, payment_period (free text), payment_amount |
| LoanPayment (loans) | `PAY` | loan, amount, date |

- Money is whole UGX in `PositiveBigIntegerField`, shown as `UGX 850,000` by the `ugx` filter (`core/templatetags/sacco.py`).
- All foreign keys use `on_delete=models.CASCADE`.
- Account balance is not stored: `Account.balance` is opening balance plus all savings into it.
- Loan still owed is `Loan.outstanding`: loan amount minus all its payments. No interest.

## Validation rules

- Amount fields (savings, withdrawals, loans, loan payments) must be at least 1. `opening_balance` may be 0.
- Date fields are required.
- `account_number` must be unique.
- A saving's account must belong to the saving's member (`Saving.clean`).
- A loan payment cannot exceed what is still owed on the loan. When editing a payment, its own old amount is left out of the total (`LoanPayment.clean`).
- Deleting a member removes their accounts, savings, loans and withdrawals. Deleting a loan removes its payments, an account its savings, a staff record the savings and loans it recorded. The delete modal names these through `delete_note`.

Validation lives in model `clean()` and field validators, so the forms, the modals
and Django Admin all enforce it.

## `core/crud.py`

| Piece | Job |
|---|---|
| `ListPage` | `ListView` with login required, 10 rows per page, newest first. An out-of-range `?page=` shows the last page instead of a 404. Set `model`, `page_title`, `add_label`, `url_name` |
| `ModalFormMixin` | For `CreateView`/`UpdateView`. Renders `partials/_modal_form.html`. Valid: saves, queues a "saved" message, answers 204. Invalid: re-renders the form with status 400 |
| `ModalDeleteMixin` | For `DeleteView`. Renders `partials/_modal_delete.html` with `delete_note`. Confirmed: deletes, queues a message, answers 204 |
| `crud_urls(prefix, name, list, create, update, delete)` | Returns the four routes `<prefix>/`, `add/`, `<pk>/edit/`, `<pk>/delete/`, named `<name>_list`, `<name>_add`, `<name>_edit`, `<name>_delete` |

## The modal flow

`static/js/modal.js` drives a single `<dialog id="modal">` in `base.html`.

1. A button or icon with `data-modal-url="..."` is clicked. The script fetches that URL and puts the returned form into the dialog.
2. On Save, the form is POSTed with `fetch`.
3. 204: the page reloads and the saved message shows. 400: the dialog is replaced with the form and its error messages. Other errors show a message inside the dialog.
4. If the session has expired, the fetch is redirected to `/login/`; the script sends the whole browser there rather than showing the login page in the dialog.

## Adding a new data page in five steps

1. **Model** in `<app>/models.py`: extend `CodedModel`, set `code_prefix`, add fields (amounts with `MinValueValidator(1)`, foreign keys with `CASCADE`), put cross-field rules in `clean()`. Add the app to `INSTALLED_APPS`, then `python manage.py makemigrations` and `migrate`.
2. **Form** in `<app>/forms.py`: a `ModelForm` with `fields`, `labels`, and `DateInput` from `core/forms.py` for date fields.
3. **Views** in `<app>/views.py`: a `ListPage` subclass and `CreateView`, `UpdateView`, `DeleteView` subclasses using `ModalFormMixin` / `ModalDeleteMixin` (copy `members/views.py`).
4. **URLs**: `<app>/urls.py` calls `crud_urls(...)`; add `path("", include("<app>.urls"))` to `core/urls.py`.
5. **Template and sidebar**: copy `templates/members/member_list.html` to `templates/<app>/<name>_list.html` and change the columns; add a link in `templates/partials/_sidebar.html`. Register the model in `admin.py` and add tests in `<app>/tests.py` (login required, add/edit/delete, each validation rule, empty page).

Optionally add the new numbers to `dashboard/stats.py` and demo rows to
`dashboard/management/commands/seed.py`.

## Dashboard and seed data

- `dashboard/stats.py` `summary()` works every figure out in the database: counts, total savings (opening balances plus savings), total lent, total repaid, still owed, withdrawals, and the latest five savings and loans.
- `python manage.py seed --reset` deletes all SACCO records and creates repeatable demo data (60 members, 8 staff, 90 accounts, 300 savings, 25 loans, 70 loan payments, 6 withdrawals) plus the `admin` user if it does not exist. Without `--reset` it does nothing when members already exist. Codes continue from the database's numbering, so a repeated `--reset` on the same file starts above `MEM-001`.
