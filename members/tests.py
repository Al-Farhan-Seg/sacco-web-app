from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from .models import Member


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


VALID_POST = {
    "first_name": "John",
    "last_name": "Okello",
    "contact": "0701000000",
    "address": "Gulu",
    "email": "john@example.com",
    "gender": "M",
}


class MemberModelTests(TestCase):
    def test_code_is_prefixed_and_padded(self):
        self.assertEqual(make_member().code, "MEM-001")

    def test_str_includes_code_and_name(self):
        member = make_member()
        self.assertEqual(str(member), "MEM-001 · Sarah Nam")
        self.assertEqual(member.full_name, "Sarah Nam")


class MemberViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("clerk", password="s3cret-pass")
        self.client.force_login(self.user)

    def test_list_requires_login(self):
        self.client.logout()
        url = reverse("member_list")
        response = self.client.get(url)
        self.assertRedirects(
            response, f"/login/?next={url}", fetch_redirect_response=False
        )

    def test_list_shows_members_newest_first_and_empty_state(self):
        response = self.client.get(reverse("member_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No members yet.")

        make_member(first_name="Older")
        make_member(first_name="Newer")
        response = self.client.get(reverse("member_list"))
        self.assertNotContains(response, "No members yet.")
        self.assertEqual(
            [m.first_name for m in response.context["object_list"]],
            ["Newer", "Older"],
        )
        self.assertContains(response, "MEM-002")
        self.assertContains(response, "Female")
        self.assertContains(response, reverse("member_add"))

    def test_add_get_renders_form(self):
        response = self.client.get(reverse("member_add"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add member")
        self.assertContains(response, "First name")

    def test_add_valid_returns_204_and_creates(self):
        response = self.client.post(reverse("member_add"), VALID_POST)
        self.assertEqual(response.status_code, 204)
        self.assertTrue(Member.objects.filter(first_name="John").exists())

    def test_add_invalid_returns_400_with_error(self):
        data = dict(VALID_POST, email="not-an-email")
        response = self.client.post(reverse("member_add"), data)
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "valid email", status_code=400)
        self.assertFalse(Member.objects.exists())

    def test_edit_get_prefilled_and_post_updates(self):
        member = make_member()
        url = reverse("member_edit", args=[member.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="Sarah"')
        self.assertContains(response, "Edit MEM-001")

        response = self.client.post(url, dict(VALID_POST, first_name="Sara"))
        self.assertEqual(response.status_code, 204)
        member.refresh_from_db()
        self.assertEqual(member.first_name, "Sara")

    def test_delete_get_confirms_and_post_removes(self):
        member = make_member()
        url = reverse("member_delete", args=[member.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "MEM-001 · Sarah Nam")
        self.assertContains(
            response, "their accounts, savings, loans and withdrawals"
        )

        response = self.client.post(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Member.objects.exists())

    def test_modal_urls_redirect_to_login_when_anonymous(self):
        member = make_member()
        self.client.logout()
        urls = [
            reverse("member_add"),
            reverse("member_edit", args=[member.pk]),
            reverse("member_delete", args=[member.pk]),
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
        self.assertTrue(Member.objects.exists())

    def test_delete_last_row_of_last_page_reload_ok(self):
        members = [make_member(first_name=f"M{i}") for i in range(11)]
        oldest = members[0]
        response = self.client.post(reverse("member_delete", args=[oldest.pk]))
        self.assertEqual(response.status_code, 204)

        response = self.client.get(reverse("member_list") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].number, 1)
        self.assertEqual(len(response.context["object_list"]), 10)

    def test_success_message_set(self):
        response = self.client.post(reverse("member_add"), VALID_POST)
        self.assertEqual(
            [str(m) for m in get_messages(response.wsgi_request)],
            ["MEM-001 saved"],
        )


class DeleteModalWordingTests(TestCase):
    def setUp(self):
        self.client.force_login(User.objects.create_user("clerk", password="s3cret-pass"))

    def test_member_delete_modal_lists_what_goes_with_it(self):
        member = make_member()
        response = self.client.get(reverse("member_delete", args=[member.pk]))
        self.assertContains(response, "will be deleted, along with their accounts")
        self.assertNotContains(response, "will be deleted.")

    def test_modal_without_note_has_plain_sentence(self):
        from withdrawals.models import Withdrawal

        withdrawal = Withdrawal.objects.create(
            member=make_member(), amount=1000, date="2026-01-15"
        )
        response = self.client.get(reverse("withdrawal_delete", args=[withdrawal.pk]))
        self.assertContains(response, "will be deleted.")
        self.assertNotContains(response, "along with")
