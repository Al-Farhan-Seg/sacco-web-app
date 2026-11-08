from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import Account
from loans.models import Loan, LoanPayment
from members.models import Member
from savings.models import Saving
from staff.models import Staff
from withdrawals.models import Withdrawal

from .stats import summary

ZERO_KEYS = [
    "members",
    "staff",
    "accounts",
    "total_savings",
    "loans_count",
    "loans_total",
    "repayments_total",
    "still_owed",
    "withdrawals_count",
    "withdrawals_total",
]

CARD_LABELS = [
    "Members",
    "Staff",
    "Accounts",
    "Total savings",
    "Loans issued",
    "Loan repayments",
    "Still owed",
    "Withdrawals",
]


def make_member(n=1):
    return Member.objects.create(
        first_name=f"Member{n}",
        last_name="Nam",
        contact="0772000000",
        address="Kampala",
        email=f"m{n}@example.com",
        gender="F",
    )


def make_staff():
    return Staff.objects.create(
        first_name="Grace",
        last_name="Akello",
        gender="F",
        position="Teller",
        role="User",
        contact="0772000001",
        address="Kampala",
    )


def make_account(member, number, opening=0):
    return Account.objects.create(
        member=member,
        account_number=number,
        account_type="Savings",
        opening_balance=opening,
    )


def make_saving(account, staff, amount):
    return Saving.objects.create(
        member=account.member,
        account=account,
        staff=staff,
        payment_method="Cash",
        amount=amount,
        date="2026-01-10",
    )


def make_loan(member, staff, amount=2000000):
    return Loan.objects.create(
        member=member,
        staff=staff,
        loan_amount=amount,
        payment_period="12 months",
        payment_amount=200000,
    )


def build_fixture():
    m1, m2 = make_member(1), make_member(2)
    staff = make_staff()
    a1 = make_account(m1, "100001", 5000)
    a2 = make_account(m2, "100002", 7000)
    make_saving(a1, staff, 1000)
    make_saving(a2, staff, 2000)
    loan = make_loan(m1, staff, 2000000)
    LoanPayment.objects.create(loan=loan, amount=180000, date="2026-02-01")
    LoanPayment.objects.create(loan=loan, amount=90000, date="2026-03-01")
    Withdrawal.objects.create(member=m2, amount=850000, date="2026-03-05")
    return {"a1": a1, "a2": a2, "staff": staff}


class SummaryTests(TestCase):
    def test_summary_on_empty_database_is_all_zeros(self):
        data = summary()
        for key in ZERO_KEYS:
            with self.subTest(key=key):
                self.assertEqual(data[key], 0)
                self.assertIsInstance(data[key], int)
        self.assertEqual(list(data["recent_savings"]), [])
        self.assertEqual(list(data["recent_loans"]), [])

    def test_summary_values(self):
        build_fixture()
        data = summary()
        expected = {
            "members": 2,
            "staff": 1,
            "accounts": 2,
            "total_savings": 15000,
            "loans_count": 1,
            "loans_total": 2000000,
            "repayments_total": 270000,
            "still_owed": 1730000,
            "withdrawals_count": 1,
            "withdrawals_total": 850000,
        }
        for key, value in expected.items():
            with self.subTest(key=key):
                self.assertEqual(data[key], value)

    def test_total_savings_tracks_edits_and_deletes(self):
        fx = build_fixture()
        saving = Saving.objects.get(amount=1000)
        saving.amount = 4000
        saving.save()
        self.assertEqual(summary()["total_savings"], 18000)

        fx["a2"].opening_balance = 0
        fx["a2"].save()
        self.assertEqual(summary()["total_savings"], 11000)

        saving.delete()
        self.assertEqual(summary()["total_savings"], 7000)

        fx["a2"].delete()
        self.assertEqual(summary()["total_savings"], 5000)

    def test_recent_lists_limited_to_five_newest_first(self):
        member, staff = make_member(), make_staff()
        account = make_account(member, "100001")
        savings = [make_saving(account, staff, 1000 + i) for i in range(7)]
        loans = [make_loan(member, staff, 100000 + i) for i in range(7)]
        data = summary()
        self.assertEqual(
            [s.pk for s in data["recent_savings"]],
            [s.pk for s in reversed(savings[2:])],
        )
        self.assertEqual(
            [loan.pk for loan in data["recent_loans"]],
            [loan.pk for loan in reversed(loans[2:])],
        )

    def test_summary_query_count_does_not_grow_with_rows(self):
        member, staff = make_member(), make_staff()
        for i in range(6):
            account = make_account(member, f"10000{i}", 1000)
            make_saving(account, staff, 500)
            loan = make_loan(member, staff)
            LoanPayment.objects.create(loan=loan, amount=1000, date="2026-02-01")
            Withdrawal.objects.create(member=member, amount=100, date="2026-03-05")
        # Seven aggregate queries plus one for each recent list.
        with self.assertNumQueries(9):
            data = summary()
            for saving in data["recent_savings"]:
                str(saving.member)
            for loan in data["recent_loans"]:
                str(loan.member)


class DashboardViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("admin", password="pass12345")
        self.client.force_login(self.user)

    def test_dashboard_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(
            response, "/login/?next=/", fetch_redirect_response=False
        )

    def test_dashboard_renders_numbers_formatted(self):
        build_fixture()
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        for label in CARD_LABELS:
            with self.subTest(label=label):
                self.assertContains(
                    response, f'<p class="stat-label">{label}</p>', html=True
                )
        self.assertContains(response, "UGX 15,000")
        self.assertContains(response, "UGX 2,000,000")
        self.assertContains(response, "UGX 270,000")
        self.assertContains(response, "UGX 1,730,000")
        self.assertContains(response, "UGX 850,000")
        self.assertContains(response, "UGX 2,000")
        self.assertContains(response, "SAV-001")
        self.assertContains(response, "LN-001")
        self.assertContains(response, "12 months")
        self.assertContains(response, 'href="/savings/"')
        self.assertContains(response, 'href="/loans/"')

    def test_dashboard_empty_state_renders(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No savings yet.")
        self.assertContains(response, "No loans yet.")
        self.assertContains(response, "UGX 0")
