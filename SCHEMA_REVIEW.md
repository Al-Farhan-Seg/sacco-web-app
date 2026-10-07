# SACCO HTML Pages vs. Our SQL Schema – Review

Every form and table should use the **same fields as the SQL script (`SACCO Script.sql`)**. Below is the schema, followed by what is wrong on each page.

## The Schema (what each page must show)

| Table | Fields |
|---|---|
| MEMBER | member_id, First_name, Last_name, Contact, Address, Email, Gender |
| ACCOUNT | Account_id, member_id, Account_No, Account_type, Balance |
| SAVINGS | savings_id, member_id, Account_id, Staff_id, Amount, Date, Payment_method, Tax |
| STAFF | Staff_id, First_name, Last_name, Contact, position, Role, Gender |
| LOAN | Loan_id, member_id, Staff_id, Loan_amount, payment_period, payment_amount |
| LOAN_PAYMENT | Payment_id, Loan_id, Amount, Date |
| WITHDRAW | Withdraw_id, member_id, Amount, Date (**no Account_id**, we dropped it) |

Login and Index are not schema tables, so they are not reviewed here.

## Status

| Page | Status |
|---|---|
| loan.html | OK |
| loan-payment.html | OK |
| withdrawal.html | OK (fixed) |
| saving.html | Minor fixes |
| account.html | Needs fixing |
| member.html | Needs fixing |
| staff.html | Needs fixing |

## What to fix, page by page

### staff.html (worst)
- **No table at all.** The lecturer requires a table with 5 rows of dummy data.
- Form is missing **Contact** and **Role**.
- Staff ID input has no `type`, and the placeholder `STFoo1` uses letter o's instead of zeros (`STF001`).
- Links `staff.js`, but that file does not exist in the project. Create it or remove the `<script>` line.
- Table columns should be: Staff ID, First Name, Last Name, Contact, Position, Role, Gender.

### member.html
- Form and table are missing **Last_name** and **Contact**.
- The table uses one combined "Name" column. Split it into First Name and Last Name.
- The form asks for Member ID, but it is `AUTO_INCREMENT` in the SQL, so the user would not type it. Fine to keep for now, but remember it for Django.
- Table columns should be: Member ID, First Name, Last Name, Contact, Address, Email, Gender.

### account.html
- Form and table are missing **Account_No**. The form is also missing **Balance**.
- Table has two columns that are **not in the schema**: *Member Name* and *Status*. Remove them.
- Account type options are "Savings Account / Loan Account", but our SQL data uses **Savings / Current**.
- Table columns should be: Account ID, Member ID, Account No, Account Type, Balance.

### saving.html (closest to correct)
- The table merges name and ID into one "Member" column. Use a separate **Member ID** column.
- Table is missing the **Tax** column (the SQL trigger calculates it as 5% of Amount). The form can leave Tax out because it is automatic.
- Payment methods are Cash / Mobile Money / Bank Transfer, while the SQL data uses **Cash / Mobile / Bank**.
- Table columns should be: Savings ID, Member ID, Account ID, Staff ID, Amount, Date, Payment Method, Tax.

## Things to check on every page
- Do the form fields and table columns match the schema above, with no extras and none missing?
- Does the table have **5 rows** of dummy data?
- Is the table wrapped in an `overflow-x: auto` container, so it scrolls sideways on phones instead of breaking the page?
- Is the HTML valid (no nested `<html>` or `<form>` tags, all tags closed)?

## Note for Django later
The SQL uses plain integer IDs (`1, 2, 3`). The HTML pages use text IDs like `MEM-001` for readability. This is fine for the HTML phase, but the Django models will use integers.
