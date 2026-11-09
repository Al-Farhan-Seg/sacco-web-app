# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Django 6.1 with SQLite, server-rendered templates, plain CSS in one file, a few lines of vanilla JavaScript, Lucide icons. No Bootstrap, Tailwind, jQuery or any front-end framework. Decided by the user.

## Users

One administrator who runs a SACCO (a savings and loans group) in Uganda, working at a desk. They enter and check records for members, staff, accounts, savings, withdrawals, loans and loan payments. Members and staff never log in: members would have too little to do in the app, so the administrator does all the work on their behalf. A secondary audience is the lecturer who sees it in a university class demo.

## Product Purpose

A back-office web app to manage a SACCO's records and see its position at a glance. It exists as a university assignment, so success means a working demo: real login, a dashboard of live numbers from the database, Add, Edit and Delete in modals on every data page, linked data that stays consistent, and the same data visible in Django Admin. It must not be over-engineered.

## Positioning

Not a competitor to commercial SACCO software. The point is a clear, working example of Django models, forms, views, templates and the admin site, in a tool a real administrator could use.

## Operating Context

Desktop browser, one person, repeated data entry and look-up. Money is in Ugandan shillings (UGX), whole numbers, shown like "UGX 850,000". Records carry automatic IDs shown as codes (MEM-001, STF-001, ACC-001, SAV-001, LN-001, PAY-001, WDR-001). Source of field names is the original frontend pages, not SACCO Script.sql.

## Capabilities and Constraints

- Login and logout with Django's built-in user; one administrator; every page except login requires it.
- Dashboard: eight live number cards and two recent-activity tables.
- Seven data pages (members, staff, accounts, savings, withdrawals, loans, loan payments), each a table with an Add button, and per-row edit and delete icons; all forms open in modals.
- Account balance is opening balance plus savings. Loan still owed is loan amount minus payments. Deleting a member deletes what belongs to them.
- Staff role (Admin or User) is a label only. A withdrawal records a member leaving the SACCO and the final balance paid out; it is only a record and closes nothing in the app.
- Left sidebar is one flat list with a Django Admin link at the bottom.
- db.sqlite3 is committed to GitHub by the repository owner.

## Brand Commitments

Palette is binding, from the user's chosen reference image: Palladian #EEE9DF, Oatmeal #C9C1B1, Blue Fantastic #2C3B4D, Burning Flame #F2A55C, Truffle Trouble #A35139, Abyssal Anchorfish Blue #1B2632. Appearance borrows from the Material Dashboard template (floating dark sidebar, off-white page, rounded cards, icon tiles on stat cards) using our own CSS only.

## Evidence on Hand

Frontend pages in templates/ and sample rows in the original frontend show the real fields. SACCO Script.sql has sample members, staff and accounts. There are no logos, testimonials or real customer data; none may be invented beyond clearly marked sample data.

## Product Principles

- A working demo beats a complete product: if a feature is not needed to show the pattern, leave it out.
- One pattern repeated seven times: every data page behaves the same way.
- The numbers on screen come from the database, never typed in.
- Calm and legible for all-day data entry; colour marks meaning (delete is rust, actions are orange).
- Plain tools only: Django generic views, one stylesheet, one small script.

## Accessibility & Inclusion

No specific standard was stated. Sensible defaults: keyboard-operable modals with visible focus, text contrast at least 4.5 to 1, labels on every field, usable at laptop width and readable on a phone.
