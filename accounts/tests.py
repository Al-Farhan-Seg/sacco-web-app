from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from members.models import Member

from .models import Account


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
        "opening_balance": 50000,
    }
    data.update(overrides)
    return Account.objects.create(**data)


def valid_post(member, **overrides):
    data = {
        "member": member.pk,
        "account_number": "2002",
        "account_type": "Current",
        "opening_balance": 100000,
    }
    data.update(overrides)
    return data


class AccountModelTests(TestCase):
    def test_code_is_prefixed_and_padded(self):
        self.assertEqual(make_account().code, "ACC-001")

    def test_str_includes_code_number_and_type(self):
        self.assertEqual(str(make_account()), "ACC-001 · 1001 (Savings)")

    def test_deleting_member_deletes_accounts(self):
        account = make_account()
        account.member.delete()
        self.assertFalse(Account.objects.exists())


class AccountViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("clerk", password="s3cret-pass")
        self.client.force_login(self.user)
        self.member = make_member()

    def test_list_requires_login(self):
        self.client.logout()
        url = reverse("account_list")
        response = self.client.get(url)
        self.assertRedirects(
            response, f"/login/?next={url}", fetch_redirect_response=False
        )

    def test_list_shows_accounts_newest_first_and_empty_state(self):
        response = self.client.get(reverse("account_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No accounts yet.")

        make_account(self.member, account_number="1001")
        make_account(self.member, account_number="1002", opening_balance=850000)
        response = self.client.get(reverse("account_list"))
        self.assertNotContains(response, "No accounts yet.")
        self.assertEqual(
            [a.account_number for a in response.context["object_list"]],
            ["1002", "1001"],
        )
        self.assertContains(response, "ACC-002")
        self.assertContains(response, "MEM-001 · Sarah Nam")
        self.assertContains(response, "UGX 850,000")
        self.assertContains(response, reverse("account_add"))

    def test_add_get_renders_form_with_member_labels(self):
        response = self.client.get(reverse("account_add"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add account")
        self.assertContains(response, "MEM-001 · Sarah Nam")

    def test_add_valid_returns_204_and_creates(self):
        response = self.client.post(
            reverse("account_add"), valid_post(self.member)
        )
        self.assertEqual(response.status_code, 204)
        self.assertTrue(Account.objects.filter(account_number="2002").exists())

    def test_add_invalid_returns_400_with_error(self):
        response = self.client.post(
            reverse("account_add"), valid_post(self.member, account_type="Fixed")
        )
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "valid choice", status_code=400)
        self.assertFalse(Account.objects.exists())

    def test_account_number_must_be_unique(self):
        make_account(self.member, account_number="2002")
        response = self.client.post(
            reverse("account_add"), valid_post(self.member)
        )
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "already exists", status_code=400)
        self.assertEqual(Account.objects.count(), 1)

    def test_opening_balance_may_be_zero(self):
        response = self.client.post(
            reverse("account_add"), valid_post(self.member, opening_balance=0)
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Account.objects.get().opening_balance, 0)

    def test_negative_opening_balance_rejected(self):
        response = self.client.post(
            reverse("account_add"), valid_post(self.member, opening_balance=-1)
        )
        self.assertEqual(response.status_code, 400)
        self.assertContains(
            response, "greater than or equal to 0", status_code=400
        )
        self.assertFalse(Account.objects.exists())

    def test_edit_get_prefilled_and_post_updates(self):
        account = make_account(self.member)
        url = reverse("account_edit", args=[account.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="1001"')
        self.assertContains(response, "Edit ACC-001")

        response = self.client.post(
            url, valid_post(self.member, account_number="1001", opening_balance=7)
        )
        self.assertEqual(response.status_code, 204)
        account.refresh_from_db()
        self.assertEqual(account.opening_balance, 7)

    def test_edit_invalid_returns_400_and_keeps_row(self):
        account = make_account(self.member)
        url = reverse("account_edit", args=[account.pk])
        response = self.client.post(
            url, valid_post(self.member, account_number="")
        )
        self.assertEqual(response.status_code, 400)
        account.refresh_from_db()
        self.assertEqual(account.account_number, "1001")

    def test_delete_get_confirms_and_post_removes(self):
        account = make_account(self.member)
        url = reverse("account_delete", args=[account.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ACC-001 · 1001 (Savings)")
        self.assertContains(response, "its savings")

        response = self.client.post(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Account.objects.exists())
        self.assertEqual(
            [str(m) for m in get_messages(response.wsgi_request)],
            ["ACC-001 deleted"],
        )

    def test_modal_urls_redirect_to_login_when_anonymous(self):
        account = make_account(self.member)
        self.client.logout()
        urls = [
            reverse("account_add"),
            reverse("account_edit", args=[account.pk]),
            reverse("account_delete", args=[account.pk]),
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
        self.assertTrue(Account.objects.exists())

    def test_success_message_set(self):
        response = self.client.post(
            reverse("account_add"), valid_post(self.member)
        )
        self.assertEqual(
            [str(m) for m in get_messages(response.wsgi_request)],
            ["ACC-001 saved"],
        )
