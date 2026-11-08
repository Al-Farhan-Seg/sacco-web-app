from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from accounts.models import Account
from members.models import Member
from staff.models import Staff

from .models import Saving


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


def make_account(member=None, **overrides):
    data = {
        "member": member or make_member(),
        "account_number": "1001",
        "account_type": "Savings",
        "opening_balance": 0,
    }
    data.update(overrides)
    return Account.objects.create(**data)


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


def make_saving(account, staff, **overrides):
    data = {
        "member": account.member,
        "account": account,
        "staff": staff,
        "payment_method": "Cash",
        "amount": 1000,
        "date": "2026-01-15",
    }
    data.update(overrides)
    return Saving.objects.create(**data)


def valid_post(base_account, base_staff, **overrides):
    data = {
        "member": base_account.member.pk,
        "account": base_account.pk,
        "staff": base_staff.pk,
        "payment_method": "Mobile",
        "amount": 25000,
        "date": "2026-02-01",
    }
    data.update(overrides)
    return data


class SavingModelTests(TestCase):
    def test_code_is_prefixed_and_padded(self):
        account = make_account()
        self.assertEqual(make_saving(account, make_staff()).code, "SAV-001")

    def test_deleting_account_deletes_savings(self):
        account = make_account()
        make_saving(account, make_staff())
        account.delete()
        self.assertFalse(Saving.objects.exists())


class SavingViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("clerk", password="s3cret-pass")
        self.client.force_login(self.user)
        self.account = make_account()
        self.member = self.account.member
        self.staff = make_staff()

    def post(self, **overrides):
        return self.client.post(
            reverse("saving_add"), valid_post(self.account, self.staff, **overrides)
        )

    def test_list_requires_login(self):
        self.client.logout()
        url = reverse("saving_list")
        response = self.client.get(url)
        self.assertRedirects(
            response, f"/login/?next={url}", fetch_redirect_response=False
        )

    def test_list_shows_savings_newest_first_and_empty_state(self):
        response = self.client.get(reverse("saving_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No savings yet.")

        make_saving(self.account, self.staff, amount=1000)
        make_saving(self.account, self.staff, amount=850000, payment_method="Bank")
        response = self.client.get(reverse("saving_list"))
        self.assertNotContains(response, "No savings yet.")
        self.assertEqual(
            [s.amount for s in response.context["object_list"]], [850000, 1000]
        )
        self.assertContains(response, "SAV-002")
        self.assertContains(response, "MEM-001 · Sarah Nam")
        self.assertContains(response, "ACC-001 · 1001 (Savings)")
        self.assertContains(response, "Bank Transfer")
        self.assertContains(response, "UGX 850,000")
        self.assertContains(response, "STF-001 · Grace Akello")
        self.assertContains(response, reverse("saving_add"))

    def test_list_query_count_does_not_grow_with_rows(self):
        make_saving(self.account, self.staff)
        self.client.get(reverse("saving_list"))  # warm up session/user queries
        with CaptureQueriesContext(connection) as one_row:
            self.client.get(reverse("saving_list"))
        for _ in range(3):
            make_saving(self.account, self.staff)
        with self.assertNumQueries(len(one_row.captured_queries)):
            self.client.get(reverse("saving_list"))

    def test_add_get_renders_form_with_str_labels(self):
        response = self.client.get(reverse("saving_add"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add saving")
        self.assertContains(response, "MEM-001 · Sarah Nam")
        self.assertContains(response, "ACC-001 · 1001 (Savings)")
        self.assertContains(response, "STF-001 · Grace Akello")
        self.assertContains(response, 'type="date"')

    def test_add_valid_returns_204_and_creates(self):
        response = self.post()
        self.assertEqual(response.status_code, 204)
        saving = Saving.objects.get()
        self.assertEqual(saving.amount, 25000)
        self.assertEqual(saving.payment_method, "Mobile")
        self.assertEqual(
            [str(m) for m in get_messages(response.wsgi_request)],
            ["SAV-001 saved"],
        )

    def test_add_invalid_returns_400_with_error(self):
        response = self.post(payment_method="Cheque")
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "valid choice", status_code=400)
        self.assertFalse(Saving.objects.exists())

    def test_saving_rejects_account_of_other_member(self):
        other = make_member(first_name="John", last_name="Doe", email="j@example.com")
        response = self.post(member=other.pk)
        self.assertEqual(response.status_code, 400)
        self.assertContains(
            response, "account does not belong to the selected member", status_code=400
        )
        self.assertFalse(Saving.objects.exists())

    def test_missing_member_or_account_is_a_form_error_not_a_crash(self):
        for field in ("member", "account"):
            with self.subTest(field=field):
                response = self.post(**{field: ""})
                self.assertEqual(response.status_code, 400)
                self.assertContains(
                    response, "This field is required", status_code=400
                )
        self.assertFalse(Saving.objects.exists())

    def test_saving_amount_zero_rejected(self):
        response = self.post(amount=0)
        self.assertEqual(response.status_code, 400)
        self.assertContains(
            response, "greater than or equal to 1", status_code=400
        )
        self.assertFalse(Saving.objects.exists())

    def test_saving_date_required(self):
        response = self.post(date="")
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "This field is required", status_code=400)
        self.assertFalse(Saving.objects.exists())

    def test_edit_get_prefilled_and_post_updates(self):
        saving = make_saving(self.account, self.staff)
        url = reverse("saving_edit", args=[saving.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit SAV-001")
        self.assertContains(response, 'value="2026-01-15"')

        response = self.client.post(
            url, valid_post(self.account, self.staff, amount=7)
        )
        self.assertEqual(response.status_code, 204)
        saving.refresh_from_db()
        self.assertEqual(saving.amount, 7)

    def test_edit_invalid_returns_400_and_keeps_row(self):
        saving = make_saving(self.account, self.staff)
        url = reverse("saving_edit", args=[saving.pk])
        response = self.client.post(
            url, valid_post(self.account, self.staff, amount=0)
        )
        self.assertEqual(response.status_code, 400)
        saving.refresh_from_db()
        self.assertEqual(saving.amount, 1000)

    def test_delete_get_confirms_and_post_removes(self):
        saving = make_saving(self.account, self.staff)
        url = reverse("saving_delete", args=[saving.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SAV-001")

        response = self.client.post(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Saving.objects.exists())
        self.assertEqual(
            [str(m) for m in get_messages(response.wsgi_request)],
            ["SAV-001 deleted"],
        )

    def test_modal_urls_redirect_to_login_when_anonymous(self):
        saving = make_saving(self.account, self.staff)
        self.client.logout()
        urls = [
            reverse("saving_add"),
            reverse("saving_edit", args=[saving.pk]),
            reverse("saving_delete", args=[saving.pk]),
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
        self.assertTrue(Saving.objects.exists())
