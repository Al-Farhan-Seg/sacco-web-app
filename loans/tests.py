from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from members.models import Member
from staff.models import Staff

from .models import Loan, LoanPayment


def make_member(**overrides):
    data = {
        "first_name": "Sarah",
        "last_name": "Nam",
        "contact": "0772000000",
        "address": "Kampala",
        "email": "sarah@example.com",
        "gender": "F",
    }
    data.update(overrides)
    return Member.objects.create(**data)


def make_staff(**overrides):
    data = {
        "first_name": "Grace",
        "last_name": "Akello",
        "gender": "F",
        "position": "Teller",
        "role": "User",
        "contact": "0772000001",
        "address": "Kampala",
    }
    data.update(overrides)
    return Staff.objects.create(**data)


def make_loan(member, staff, **overrides):
    data = {
        "member": member,
        "staff": staff,
        "loan_amount": 2000000,
        "payment_period": "12 months",
        "payment_amount": 200000,
    }
    data.update(overrides)
    return Loan.objects.create(**data)


def make_payment(loan, **overrides):
    data = {"loan": loan, "amount": 180000, "date": "2026-01-15"}
    data.update(overrides)
    return LoanPayment.objects.create(**data)


def loan_post(member, staff, **overrides):
    data = {
        "member": member.pk,
        "staff": staff.pk,
        "loan_amount": 1000000,
        "payment_period": "6 months",
        "payment_amount": 170000,
    }
    data.update(overrides)
    return data


def payment_post(base_loan, **overrides):
    data = {"loan": base_loan.pk, "amount": 50000, "date": "2026-02-01"}
    data.update(overrides)
    return data


class LoanModelTests(TestCase):
    def setUp(self):
        self.member = make_member()
        self.staff = make_staff()

    def test_code_is_prefixed_and_padded(self):
        self.assertEqual(make_loan(self.member, self.staff).code, "LN-001")

    def test_str_shows_code_and_member_name(self):
        loan = make_loan(self.member, self.staff)
        self.assertEqual(str(loan), "LN-001 · Sarah Nam")

    def test_total_paid_is_zero_without_payments(self):
        loan = make_loan(self.member, self.staff)
        self.assertEqual(loan.total_paid, 0)
        self.assertEqual(loan.outstanding, 2000000)

    def test_outstanding_is_loan_minus_payments(self):
        loan = make_loan(self.member, self.staff, loan_amount=2000000)
        make_payment(loan, amount=180000)
        make_payment(loan, amount=90000)
        self.assertEqual(loan.total_paid, 270000)
        self.assertEqual(loan.outstanding, 1730000)

    def test_deleting_loan_deletes_payments(self):
        loan = make_loan(self.member, self.staff)
        make_payment(loan)
        loan.delete()
        self.assertFalse(LoanPayment.objects.exists())

    def test_deleting_member_deletes_loans(self):
        make_loan(self.member, self.staff)
        self.member.delete()
        self.assertFalse(Loan.objects.exists())


class LoanPaymentModelTests(TestCase):
    def test_code_is_prefixed_and_padded(self):
        loan = make_loan(make_member(), make_staff())
        self.assertEqual(make_payment(loan).code, "PAY-001")


class LoanViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("clerk", password="s3cret-pass")
        self.client.force_login(self.user)
        self.member = make_member()
        self.staff = make_staff()

    def post(self, **overrides):
        return self.client.post(
            reverse("loan_add"), loan_post(self.member, self.staff, **overrides)
        )

    def test_list_requires_login(self):
        self.client.logout()
        url = reverse("loan_list")
        response = self.client.get(url)
        self.assertRedirects(
            response, f"/login/?next={url}", fetch_redirect_response=False
        )

    def test_list_shows_loans_newest_first_and_empty_state(self):
        response = self.client.get(reverse("loan_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No loans yet.")

        make_loan(self.member, self.staff, loan_amount=500000)
        second = make_loan(self.member, self.staff, loan_amount=2000000)
        make_payment(second, amount=180000)
        make_payment(second, amount=90000)
        response = self.client.get(reverse("loan_list"))
        self.assertNotContains(response, "No loans yet.")
        self.assertEqual(
            [loan.loan_amount for loan in response.context["object_list"]],
            [2000000, 500000],
        )
        self.assertContains(response, "LN-002")
        self.assertContains(response, "MEM-001 · Sarah Nam")
        self.assertContains(response, "STF-001 · Grace Akello")
        self.assertContains(response, "UGX 2,000,000")
        self.assertContains(response, "12 months")
        self.assertContains(response, "UGX 200,000")
        self.assertContains(response, "UGX 1,730,000")
        self.assertContains(response, "UGX 500,000")
        self.assertContains(response, reverse("loan_add"))

    def test_add_get_renders_form_with_str_labels(self):
        response = self.client.get(reverse("loan_add"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add loan")
        self.assertContains(response, "MEM-001 · Sarah Nam")
        self.assertContains(response, "STF-001 · Grace Akello")

    def test_add_valid_returns_204_and_creates(self):
        response = self.post()
        self.assertEqual(response.status_code, 204)
        loan = Loan.objects.get()
        self.assertEqual(loan.loan_amount, 1000000)
        self.assertEqual(loan.payment_period, "6 months")
        self.assertEqual(
            [str(m) for m in get_messages(response.wsgi_request)],
            ["LN-001 saved"],
        )

    def test_add_invalid_returns_400_with_error(self):
        response = self.post(payment_period="")
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "This field is required", status_code=400)
        self.assertFalse(Loan.objects.exists())

    def test_loan_amount_zero_rejected(self):
        response = self.post(loan_amount=0)
        self.assertEqual(response.status_code, 400)
        self.assertContains(
            response, "greater than or equal to 1", status_code=400
        )
        self.assertFalse(Loan.objects.exists())

    def test_payment_amount_zero_rejected(self):
        response = self.post(payment_amount=0)
        self.assertEqual(response.status_code, 400)
        self.assertContains(
            response, "greater than or equal to 1", status_code=400
        )
        self.assertFalse(Loan.objects.exists())

    def test_edit_get_prefilled_and_post_updates(self):
        loan = make_loan(self.member, self.staff)
        url = reverse("loan_edit", args=[loan.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit LN-001")
        self.assertContains(response, "12 months")

        response = self.client.post(
            url, loan_post(self.member, self.staff, payment_period="3 months")
        )
        self.assertEqual(response.status_code, 204)
        loan.refresh_from_db()
        self.assertEqual(loan.payment_period, "3 months")

    def test_edit_invalid_returns_400_and_keeps_row(self):
        loan = make_loan(self.member, self.staff)
        url = reverse("loan_edit", args=[loan.pk])
        response = self.client.post(
            url, loan_post(self.member, self.staff, loan_amount=0)
        )
        self.assertEqual(response.status_code, 400)
        loan.refresh_from_db()
        self.assertEqual(loan.loan_amount, 2000000)

    def test_delete_get_confirms_and_post_removes(self):
        loan = make_loan(self.member, self.staff)
        url = reverse("loan_delete", args=[loan.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "LN-001")
        self.assertContains(response, "its payments")

        response = self.client.post(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Loan.objects.exists())
        self.assertEqual(
            [str(m) for m in get_messages(response.wsgi_request)],
            ["LN-001 deleted"],
        )

    def test_modal_urls_redirect_to_login_when_anonymous(self):
        loan = make_loan(self.member, self.staff)
        self.client.logout()
        urls = [
            reverse("loan_add"),
            reverse("loan_edit", args=[loan.pk]),
            reverse("loan_delete", args=[loan.pk]),
        ]
        for url in urls:
            for method in (self.client.get, self.client.post):
                with self.subTest(url=url, method=method.__name__):
                    response = method(url)
                    self.assertRedirects(
                        response,
                        f"/login/?next={url}",
                        fetch_redirect_response=False,
                    )
        self.assertTrue(Loan.objects.exists())


class LoanPaymentViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("clerk", password="s3cret-pass")
        self.client.force_login(self.user)
        self.member = make_member()
        self.staff = make_staff()
        self.loan = make_loan(self.member, self.staff, loan_amount=2000000)

    def post(self, **overrides):
        return self.client.post(
            reverse("payment_add"), payment_post(self.loan, **overrides)
        )

    def test_list_requires_login(self):
        self.client.logout()
        url = reverse("payment_list")
        response = self.client.get(url)
        self.assertRedirects(
            response, f"/login/?next={url}", fetch_redirect_response=False
        )

    def test_list_shows_payments_newest_first_and_empty_state(self):
        response = self.client.get(reverse("payment_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No loan payments yet.")

        make_payment(self.loan, amount=1000)
        make_payment(self.loan, amount=180000)
        response = self.client.get(reverse("payment_list"))
        self.assertNotContains(response, "No loan payments yet.")
        self.assertEqual(
            [p.amount for p in response.context["object_list"]], [180000, 1000]
        )
        self.assertContains(response, "PAY-002")
        self.assertContains(response, "LN-001 · Sarah Nam")
        self.assertContains(response, "UGX 180,000")
        self.assertContains(response, reverse("payment_add"))

    def test_add_get_renders_form_with_loan_label(self):
        response = self.client.get(reverse("payment_add"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add loan payment")
        self.assertContains(response, "LN-001 · Sarah Nam")
        self.assertContains(response, 'type="date"')

    def test_add_valid_returns_204_and_creates(self):
        response = self.post()
        self.assertEqual(response.status_code, 204)
        payment = LoanPayment.objects.get()
        self.assertEqual(payment.amount, 50000)
        self.assertEqual(
            [str(m) for m in get_messages(response.wsgi_request)],
            ["PAY-001 saved"],
        )

    def test_add_invalid_returns_400_with_error(self):
        response = self.post(amount="abc")
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "whole number", status_code=400)
        self.assertFalse(LoanPayment.objects.exists())

    def test_payment_amount_zero_rejected(self):
        response = self.post(amount=0)
        self.assertEqual(response.status_code, 400)
        self.assertContains(
            response, "greater than or equal to 1", status_code=400
        )
        self.assertFalse(LoanPayment.objects.exists())

    def test_payment_date_required(self):
        response = self.post(date="")
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "This field is required", status_code=400)
        self.assertFalse(LoanPayment.objects.exists())

    def test_missing_loan_or_amount_is_a_form_error_not_a_crash(self):
        for field in ("loan", "amount"):
            with self.subTest(field=field):
                response = self.post(**{field: ""})
                self.assertEqual(response.status_code, 400)
                self.assertContains(
                    response, "This field is required", status_code=400
                )
        self.assertFalse(LoanPayment.objects.exists())

    def test_payment_cannot_exceed_outstanding(self):
        make_payment(self.loan, amount=1900000)
        response = self.post(amount=100001)
        self.assertEqual(response.status_code, 400)
        self.assertContains(
            response, "exceeds the outstanding balance", status_code=400
        )
        self.assertEqual(LoanPayment.objects.count(), 1)

    def test_payment_up_to_outstanding_is_allowed(self):
        make_payment(self.loan, amount=1900000)
        self.assertEqual(self.post(amount=100000).status_code, 204)

    def test_editing_payment_ignores_its_own_amount(self):
        make_payment(self.loan, amount=1500000)
        payment = make_payment(self.loan, amount=400000)
        url = reverse("payment_edit", args=[payment.pk])
        response = self.client.post(url, payment_post(self.loan, amount=500000))
        self.assertEqual(response.status_code, 204)
        payment.refresh_from_db()
        self.assertEqual(payment.amount, 500000)

        response = self.client.post(url, payment_post(self.loan, amount=500001))
        self.assertEqual(response.status_code, 400)
        payment.refresh_from_db()
        self.assertEqual(payment.amount, 500000)

    def test_edit_get_prefilled_and_post_updates(self):
        payment = make_payment(self.loan)
        url = reverse("payment_edit", args=[payment.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit PAY-001")
        self.assertContains(response, 'value="2026-01-15"')

        response = self.client.post(url, payment_post(self.loan, amount=7))
        self.assertEqual(response.status_code, 204)
        payment.refresh_from_db()
        self.assertEqual(payment.amount, 7)

    def test_edit_invalid_returns_400_and_keeps_row(self):
        payment = make_payment(self.loan)
        url = reverse("payment_edit", args=[payment.pk])
        response = self.client.post(url, payment_post(self.loan, amount=0))
        self.assertEqual(response.status_code, 400)
        payment.refresh_from_db()
        self.assertEqual(payment.amount, 180000)

    def test_delete_get_confirms_and_post_removes(self):
        payment = make_payment(self.loan)
        url = reverse("payment_delete", args=[payment.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PAY-001")

        response = self.client.post(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(LoanPayment.objects.exists())
        self.assertEqual(
            [str(m) for m in get_messages(response.wsgi_request)],
            ["PAY-001 deleted"],
        )

    def test_modal_urls_redirect_to_login_when_anonymous(self):
        payment = make_payment(self.loan)
        self.client.logout()
        urls = [
            reverse("payment_add"),
            reverse("payment_edit", args=[payment.pk]),
            reverse("payment_delete", args=[payment.pk]),
        ]
        for url in urls:
            for method in (self.client.get, self.client.post):
                with self.subTest(url=url, method=method.__name__):
                    response = method(url)
                    self.assertRedirects(
                        response,
                        f"/login/?next={url}",
                        fetch_redirect_response=False,
                    )
        self.assertTrue(LoanPayment.objects.exists())
