from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from accounts.models import Account
from members.models import Member

from .models import Withdrawal


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


def make_withdrawal(member=None, **overrides):
    data = {
        "member": member or make_member(),
        "amount": 1000,
        "date": "2026-01-15",
    }
    data.update(overrides)
    return Withdrawal.objects.create(**data)


def valid_post(member, **overrides):
    data = {"member": member.pk, "amount": 25000, "date": "2026-02-01"}
    data.update(overrides)
    return data


class WithdrawalModelTests(TestCase):
    def test_code_is_prefixed_and_padded(self):
        self.assertEqual(make_withdrawal().code, "WDR-001")

    def test_deleting_member_deletes_withdrawals(self):
        withdrawal = make_withdrawal()
        withdrawal.member.delete()
        self.assertFalse(Withdrawal.objects.exists())


class WithdrawalViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("clerk", password="s3cret-pass")
        self.client.force_login(self.user)
        self.member = make_member()

    def test_list_requires_login(self):
        self.client.logout()
        url = reverse("withdrawal_list")
        response = self.client.get(url)
        self.assertRedirects(
            response, f"/login/?next={url}", fetch_redirect_response=False
        )

    def test_list_shows_withdrawals_newest_first_and_empty_state(self):
        response = self.client.get(reverse("withdrawal_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No withdrawals yet.")

        make_withdrawal(self.member, amount=1000)
        make_withdrawal(self.member, amount=850000)
        response = self.client.get(reverse("withdrawal_list"))
        self.assertNotContains(response, "No withdrawals yet.")
        self.assertEqual(
            [w.amount for w in response.context["object_list"]], [850000, 1000]
        )
        self.assertContains(response, "WDR-002")
        self.assertContains(response, "MEM-001 · Sarah Nam")
        self.assertContains(response, "Amount (final balance)")
        self.assertContains(response, "UGX 850,000")
        self.assertContains(response, reverse("withdrawal_add"))

    def test_list_query_count_does_not_grow_with_rows(self):
        make_withdrawal(self.member)
        self.client.get(reverse("withdrawal_list"))  # warm up
        with CaptureQueriesContext(connection) as one_row:
            self.client.get(reverse("withdrawal_list"))
        for _ in range(3):
            make_withdrawal(self.member)
        with self.assertNumQueries(len(one_row.captured_queries)):
            self.client.get(reverse("withdrawal_list"))

    def test_add_get_renders_form_with_member_labels(self):
        response = self.client.get(reverse("withdrawal_add"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add withdrawal")
        self.assertContains(response, "MEM-001 · Sarah Nam")
        self.assertContains(response, 'type="date"')

    def test_add_valid_returns_204_and_creates(self):
        response = self.client.post(
            reverse("withdrawal_add"), valid_post(self.member)
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Withdrawal.objects.get().amount, 25000)
        self.assertEqual(
            [str(m) for m in get_messages(response.wsgi_request)],
            ["WDR-001 saved"],
        )

    def test_add_invalid_returns_400_with_error(self):
        response = self.client.post(
            reverse("withdrawal_add"), valid_post(self.member, date="")
        )
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "This field is required", status_code=400)
        self.assertFalse(Withdrawal.objects.exists())

    def test_withdrawal_amount_zero_rejected(self):
        response = self.client.post(
            reverse("withdrawal_add"), valid_post(self.member, amount=0)
        )
        self.assertEqual(response.status_code, 400)
        self.assertContains(
            response, "greater than or equal to 1", status_code=400
        )
        self.assertFalse(Withdrawal.objects.exists())

    def test_withdrawal_does_not_change_balances(self):
        account = Account.objects.create(
            member=self.member,
            account_number="1001",
            account_type="Savings",
            opening_balance=5000,
        )
        response = self.client.post(
            reverse("withdrawal_add"), valid_post(self.member, amount=3000)
        )
        self.assertEqual(response.status_code, 204)
        account.refresh_from_db()
        self.assertEqual(account.opening_balance, 5000)
        self.assertEqual(account.balance, 5000)

    def test_edit_get_prefilled_and_post_updates(self):
        withdrawal = make_withdrawal(self.member)
        url = reverse("withdrawal_edit", args=[withdrawal.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit WDR-001")
        self.assertContains(response, 'value="2026-01-15"')

        response = self.client.post(url, valid_post(self.member, amount=7))
        self.assertEqual(response.status_code, 204)
        withdrawal.refresh_from_db()
        self.assertEqual(withdrawal.amount, 7)

    def test_edit_invalid_returns_400_and_keeps_row(self):
        withdrawal = make_withdrawal(self.member)
        url = reverse("withdrawal_edit", args=[withdrawal.pk])
        response = self.client.post(url, valid_post(self.member, amount=0))
        self.assertEqual(response.status_code, 400)
        withdrawal.refresh_from_db()
        self.assertEqual(withdrawal.amount, 1000)

    def test_delete_get_confirms_and_post_removes(self):
        withdrawal = make_withdrawal(self.member)
        url = reverse("withdrawal_delete", args=[withdrawal.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "WDR-001")

        response = self.client.post(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Withdrawal.objects.exists())
        self.assertEqual(
            [str(m) for m in get_messages(response.wsgi_request)],
            ["WDR-001 deleted"],
        )

    def test_modal_urls_redirect_to_login_when_anonymous(self):
        withdrawal = make_withdrawal(self.member)
        self.client.logout()
        urls = [
            reverse("withdrawal_add"),
            reverse("withdrawal_edit", args=[withdrawal.pk]),
            reverse("withdrawal_delete", args=[withdrawal.pk]),
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
        self.assertTrue(Withdrawal.objects.exists())
