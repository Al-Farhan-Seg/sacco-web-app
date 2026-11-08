import random
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import Account
from loans.models import Loan, LoanPayment
from members.models import Member
from savings.models import Saving
from staff.models import Staff
from withdrawals.models import Withdrawal

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "sacco-demo-2026"

MEMBER_COUNT = 60
STAFF_COUNT = 8
ACCOUNT_COUNT = 90
SAVING_COUNT = 300
LOAN_COUNT = 25
PAYMENT_COUNT = 70
WITHDRAWAL_COUNT = 6

FEMALE_NAMES = [
    "Grace", "Sarah", "Esther", "Josephine", "Rose", "Prossy", "Juliet",
    "Agnes", "Harriet", "Winnie", "Immaculate", "Florence", "Betty", "Mary",
    "Scovia", "Racheal", "Patience", "Stella", "Proscovia", "Annet",
]
MALE_NAMES = [
    "Moses", "Joseph", "Samuel", "Peter", "Robert", "David", "Isaac",
    "Patrick", "Brian", "Ronald", "Charles", "Emmanuel", "Henry", "Denis",
    "Fred", "Geoffrey", "Ivan", "Richard", "Joel", "Simon",
]
LAST_NAMES = [
    "Nakato", "Ssempa", "Okello", "Namukasa", "Mugisha", "Atim", "Kato",
    "Nabirye", "Tumusiime", "Opio", "Nansubuga", "Byaruhanga", "Akello",
    "Mukasa", "Namatovu", "Ochieng", "Kiiza", "Nalubega", "Ssekandi",
    "Apio", "Kasozi", "Namuli", "Wasswa", "Auma", "Lubega", "Nankya",
    "Muwanga", "Achieng", "Ssemakula", "Birungi",
]
AREAS = [
    "Kampala", "Entebbe", "Jinja", "Mukono", "Wakiso", "Gulu", "Mbarara",
    "Masaka", "Mbale", "Lira", "Kawempe", "Nakawa", "Makindye", "Rubaga",
]
POSITIONS = [
    "Branch Manager", "Loans Officer", "Teller", "Accountant",
    "Customer Service", "Credit Analyst", "Cashier", "Records Clerk",
]
PAYMENT_METHODS = ["Cash", "Mobile", "Bank"]
LOAN_TERMS = [
    (6, "6 months"),
    (12, "12 months"),
    (18, "18 months"),
    (24, "24 months"),
]


class Command(BaseCommand):
    help = "Fill the database with repeatable demo data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete all existing SACCO data before seeding.",
        )

    def handle(self, *args, **options):
        if not options["reset"] and Member.objects.exists():
            self.stdout.write(
                "Data already exists, nothing changed. "
                "Run with --reset to replace it."
            )
            return

        self.rng = random.Random(2026)
        self.today = timezone.localdate()

        with transaction.atomic():
            for model in (
                Saving, Withdrawal, LoanPayment, Loan, Account, Staff, Member
            ):
                model.objects.all().delete()
            self.make_people()
            self.make_accounts()
            self.make_savings()
            self.make_loans()
            self.make_payments()
            self.make_withdrawals()
            created = self.ensure_admin()

        self.stdout.write(
            f"Seeded {len(self.members)} members, {len(self.staff)} staff, "
            f"{len(self.accounts)} accounts, {len(self.savings)} savings, "
            f"{len(self.loans)} loans, {len(self.payments)} loan payments "
            f"and {len(self.withdrawals)} withdrawals."
        )
        if created:
            self.stdout.write(
                f"Created user {ADMIN_USERNAME} with password "
                f"{ADMIN_PASSWORD} (demo only)."
            )
        else:
            self.stdout.write(
                f"User {ADMIN_USERNAME} already exists, password unchanged."
            )

    # Helpers

    def random_date(self):
        return self.today - timedelta(days=self.rng.randint(0, 364))

    def random_person(self):
        gender = self.rng.choice(["F", "M"])
        names = FEMALE_NAMES if gender == "F" else MALE_NAMES
        return self.rng.choice(names), self.rng.choice(LAST_NAMES), gender

    def random_contact(self):
        return f"07{self.rng.randint(0, 99_999_999):08d}"

    def random_address(self):
        return f"Plot {self.rng.randint(1, 120)}, {self.rng.choice(AREAS)}"

    # Creation steps

    def make_people(self):
        members = []
        for n in range(1, MEMBER_COUNT + 1):
            first, last, gender = self.random_person()
            members.append(
                Member(
                    first_name=first,
                    last_name=last,
                    contact=self.random_contact(),
                    address=self.random_address(),
                    email=f"{first.lower()}.{last.lower()}{n}@example.com",
                    gender=gender,
                )
            )
        Member.objects.bulk_create(members)
        self.members = list(Member.objects.order_by("pk"))

        staff = []
        for n in range(STAFF_COUNT):
            first, last, gender = self.random_person()
            staff.append(
                Staff(
                    first_name=first,
                    last_name=last,
                    gender=gender,
                    position=POSITIONS[n % len(POSITIONS)],
                    role="Admin" if n < 3 else "User",
                    contact=self.random_contact(),
                    address=self.random_address(),
                )
            )
        Staff.objects.bulk_create(staff)
        self.staff = list(Staff.objects.order_by("pk"))

    def make_accounts(self):
        # Everyone gets one account; the rest go to randomly chosen members,
        # capped at three each.
        owners = list(self.members)
        extras = ACCOUNT_COUNT - len(owners)
        pool = [m for m in self.members for _ in range(2)]
        self.rng.shuffle(pool)
        held = {m.pk: 1 for m in self.members}
        for member in pool:
            if extras == 0:
                break
            if held[member.pk] < 3:
                held[member.pk] += 1
                owners.append(member)
                extras -= 1

        accounts = [
            Account(
                member=member,
                account_number=str(10001 + i),
                account_type=self.rng.choice(["Savings", "Current"]),
                opening_balance=self.rng.randint(0, 200) * 1000,
            )
            for i, member in enumerate(owners)
        ]
        Account.objects.bulk_create(accounts)
        self.accounts = list(Account.objects.order_by("pk"))

    def make_savings(self):
        savings = []
        for i in range(SAVING_COUNT):
            account = self.rng.choice(self.accounts)
            # The first three cover every payment method for certain.
            method = (
                PAYMENT_METHODS[i]
                if i < 3
                else self.rng.choice(PAYMENT_METHODS)
            )
            savings.append(
                Saving(
                    member_id=account.member_id,
                    account=account,
                    staff=self.rng.choice(self.staff),
                    payment_method=method,
                    amount=self.rng.randint(20, 500) * 1000,
                    date=self.random_date(),
                )
            )
        # Oldest first, so ids (and codes) follow date order.
        savings.sort(key=lambda row: row.date)
        Saving.objects.bulk_create(savings)
        self.savings = savings

    def make_loans(self):
        loans = []
        for _ in range(LOAN_COUNT):
            months, label = self.rng.choice(LOAN_TERMS)
            amount = self.rng.randint(5, 100) * 100_000
            loans.append(
                Loan(
                    member=self.rng.choice(self.members),
                    staff=self.rng.choice(self.staff),
                    loan_amount=amount,
                    payment_period=label,
                    payment_amount=max(1000, round(amount / months, -3)),
                )
            )
        Loan.objects.bulk_create(loans)
        self.loans = list(Loan.objects.order_by("pk"))

    def make_payments(self):
        # Track what is still owed so a payment never exceeds it.
        owed = {loan.pk: loan.loan_amount for loan in self.loans}
        payments = []
        while len(payments) < PAYMENT_COUNT:
            loan = self.rng.choice(self.loans)
            if owed[loan.pk] < 1000:
                continue
            amount = min(int(loan.payment_amount), owed[loan.pk])
            owed[loan.pk] -= amount
            payments.append(
                LoanPayment(loan=loan, amount=amount, date=self.random_date())
            )
        payments.sort(key=lambda row: row.date)
        LoanPayment.objects.bulk_create(payments)
        self.payments = payments

    def make_withdrawals(self):
        withdrawals = [
            Withdrawal(
                member=self.rng.choice(self.members),
                amount=self.rng.randint(10, 150) * 1000,
                date=self.random_date(),
            )
            for _ in range(WITHDRAWAL_COUNT)
        ]
        withdrawals.sort(key=lambda row: row.date)
        Withdrawal.objects.bulk_create(withdrawals)
        self.withdrawals = withdrawals

    def ensure_admin(self):
        if User.objects.filter(username=ADMIN_USERNAME).exists():
            return False
        User.objects.create_superuser(
            username=ADMIN_USERNAME, password=ADMIN_PASSWORD
        )
        return True
