from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import Account
from loans.models import Loan, LoanPayment
from members.models import Member
from savings.models import Saving
from staff.models import Staff
from withdrawals.models import Withdrawal

from .analytics import (
    loan_book,
    month_starts,
    exits_per_month,
    monthly_totals,
    repayments,
    savings_by_method,
    savings_per_month,
)


def build():
    member = Member.objects.create(
        first_name="Sarah", last_name="Nam", contact="0772000000",
        address="Kampala", email="s@example.com", gender="F",
    )
    staff = Staff.objects.create(
        first_name="Grace", last_name="Akello", gender="F", position="Teller",
        role="User", contact="0772000001", address="Kampala",
    )
    account = Account.objects.create(
        member=member, account_number="1001", account_type="Savings", opening_balance=0
    )
    return member, staff, account


def add_saving(account, staff, amount, when, method="Cash"):
    return Saving.objects.create(
        member=account.member, account=account, staff=staff,
        payment_method=method, amount=amount, date=when,
    )


class MonthTests(TestCase):
    def test_months_oldest_first_across_a_year_boundary(self):
        self.assertEqual(
            month_starts(3, today=date(2026, 1, 20)),
            [date(2025, 11, 1), date(2025, 12, 1), date(2026, 1, 1)],
        )

    def test_totals_sum_per_month_and_fill_gaps_with_zero(self):
        member, staff, account = build()
        add_saving(account, staff, 1000, date(2026, 11, 2))
        add_saving(account, staff, 500, date(2026, 11, 20))
        add_saving(account, staff, 700, date(2026, 9, 5))
        add_saving(account, staff, 999, date(2020, 1, 1))  # outside the window
        months = month_starts(3, today=date(2026, 11, 9))
        self.assertEqual(monthly_totals(Saving, months), [700, 0, 1500])


class ChartTests(TestCase):
    def test_empty_database_gives_twelve_empty_months(self):
        chart = savings_per_month()
        self.assertEqual(len(chart["rows"]), 12)
        self.assertTrue(all(bar["pct"] == 0 for row in chart["rows"] for bar in row["bars"]))

    def test_bars_scale_to_the_biggest_month(self):
        member, staff, account = build()
        add_saving(account, staff, 1000, date.today())
        add_saving(account, staff, 250, month_starts(12)[0])
        rows = savings_per_month()["rows"]
        self.assertEqual((rows[0]["bars"][0]["pct"], rows[-1]["bars"][0]["pct"]), (25, 100))

    def test_exits_are_final_balances_per_month(self):
        member, staff, account = build()
        Withdrawal.objects.create(member=member, amount=250, date=date.today())
        chart = exits_per_month()
        self.assertEqual(chart["rows"][-1]["bars"][0]["value"], 250)
        self.assertEqual(chart["totals"]["out"], 250)

    def test_repayments_by_month(self):
        member, staff, account = build()
        loan = Loan.objects.create(
            member=member, staff=staff, loan_amount=5000, payment_period="6 months", payment_amount=500
        )
        LoanPayment.objects.create(loan=loan, amount=400, date=date.today())
        chart = repayments()
        self.assertEqual(chart["rows"][-1]["bars"][0]["value"], 400)
        self.assertEqual(chart["totals"]["in"], 400)


class LoanBookTests(TestCase):
    def test_no_loans_is_zero_percent_not_an_error(self):
        self.assertEqual(loan_book(), {"lent": 0, "repaid": 0, "owed": 0, "percent": 0})

    def test_repaid_plus_owed_equals_lent(self):
        member, staff, account = build()
        loan = Loan.objects.create(
            member=member, staff=staff, loan_amount=2000, payment_period="6 months", payment_amount=500
        )
        LoanPayment.objects.create(loan=loan, amount=500, date=date.today())
        book = loan_book()
        self.assertEqual(book["repaid"] + book["owed"], book["lent"])
        self.assertEqual(book["percent"], 25)


class MethodTests(TestCase):
    def test_groups_by_method_and_adds_up(self):
        member, staff, account = build()
        add_saving(account, staff, 600, date.today(), "Cash")
        add_saving(account, staff, 300, date.today(), "Mobile")
        add_saving(account, staff, 100, date.today(), "Bank")
        result = savings_by_method()
        self.assertEqual([r["label"] for r in result["rows"]], ["Cash", "Mobile Money", "Bank Transfer"])
        self.assertEqual([r["pct"] for r in result["rows"]], [60, 30, 10])
        self.assertEqual(sum(r["total"] for r in result["rows"]), result["total"])

    def test_empty(self):
        self.assertEqual(savings_by_method(), {"rows": [], "total": 0})


class PageTests(TestCase):
    def setUp(self):
        self.client.force_login(User.objects.create_user("clerk", password="s3cret-pass"))

    def test_analytics_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("analytics"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_analytics_renders_empty(self):
        response = self.client.get(reverse("analytics"))
        self.assertContains(response, "Analytics")
        self.assertContains(response, "No savings yet")

    def test_analytics_shows_exits_card(self):
        response = self.client.get(reverse("analytics"))
        self.assertContains(response, "Are members leaving")

    def test_analytics_renders_data(self):
        member, staff, account = build()
        add_saving(account, staff, 1000, date.today(), "Mobile")
        response = self.client.get(reverse("analytics"))
        self.assertContains(response, "Mobile Money")
        self.assertContains(response, "UGX 1,000")

    def test_dashboard_has_the_brief_and_link(self):
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, 'href="/analytics/"')
        self.assertContains(response, "View analytics")

    def test_sidebar_marks_analytics_current(self):
        response = self.client.get(reverse("analytics"))
        self.assertContains(response, 'href="/analytics/" aria-current="page"')
