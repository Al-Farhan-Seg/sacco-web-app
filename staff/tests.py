from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from .models import Staff


def make_staff(**overrides):
    data = {
        "first_name": "Grace",
        "last_name": "Akello",
        "gender": "F",
        "position": "Teller",
        "role": "User",
        "contact": "0772000000",
        "address": "Kampala",
    }
    data.update(overrides)
    return Staff.objects.create(**data)


VALID_POST = {
    "first_name": "Peter",
    "last_name": "Opio",
    "gender": "M",
    "position": "Manager",
    "role": "Admin",
    "contact": "0701000000",
    "address": "Gulu",
}


class StaffModelTests(TestCase):
    def test_code_is_prefixed_and_padded(self):
        self.assertEqual(make_staff().code, "STF-001")

    def test_str_includes_code_and_name(self):
        self.assertEqual(str(make_staff()), "STF-001 · Grace Akello")


class StaffViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("clerk", password="s3cret-pass")
        self.client.force_login(self.user)

    def test_list_requires_login(self):
        self.client.logout()
        url = reverse("staff_list")
        response = self.client.get(url)
        self.assertRedirects(
            response, f"/login/?next={url}", fetch_redirect_response=False
        )

    def test_list_shows_staff_newest_first_and_empty_state(self):
        response = self.client.get(reverse("staff_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No staff yet.")

        make_staff(first_name="Older")
        make_staff(first_name="Newer", role="Admin")
        response = self.client.get(reverse("staff_list"))
        self.assertNotContains(response, "No staff yet.")
        self.assertEqual(
            [s.first_name for s in response.context["object_list"]],
            ["Newer", "Older"],
        )
        self.assertContains(response, "STF-002")
        self.assertContains(response, "Female")
        self.assertContains(response, '<span class="tag tag-accent">Admin</span>')
        self.assertContains(response, '<span class="tag">User</span>')
        self.assertContains(response, reverse("staff_add"))

    def test_add_get_renders_form(self):
        response = self.client.get(reverse("staff_add"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add staff")
        self.assertContains(response, "Position")

    def test_add_valid_returns_204_and_creates(self):
        response = self.client.post(reverse("staff_add"), VALID_POST)
        self.assertEqual(response.status_code, 204)
        self.assertTrue(Staff.objects.filter(first_name="Peter").exists())

    def test_add_invalid_returns_400_with_error(self):
        response = self.client.post(
            reverse("staff_add"), dict(VALID_POST, position="")
        )
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "required", status_code=400)
        self.assertFalse(Staff.objects.exists())

    def test_role_choices_only_admin_or_user(self):
        response = self.client.post(
            reverse("staff_add"), dict(VALID_POST, role="Superuser")
        )
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "valid choice", status_code=400)
        self.assertFalse(Staff.objects.exists())

    def test_edit_get_prefilled_and_post_updates(self):
        staff = make_staff()
        url = reverse("staff_edit", args=[staff.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="Grace"')
        self.assertContains(response, "Edit STF-001")

        response = self.client.post(url, dict(VALID_POST, first_name="Gracie"))
        self.assertEqual(response.status_code, 204)
        staff.refresh_from_db()
        self.assertEqual(staff.first_name, "Gracie")

    def test_edit_invalid_returns_400_and_keeps_row(self):
        staff = make_staff()
        url = reverse("staff_edit", args=[staff.pk])
        response = self.client.post(url, dict(VALID_POST, first_name=""))
        self.assertEqual(response.status_code, 400)
        staff.refresh_from_db()
        self.assertEqual(staff.first_name, "Grace")

    def test_delete_get_confirms_and_post_removes(self):
        staff = make_staff()
        url = reverse("staff_delete", args=[staff.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "STF-001 · Grace Akello")
        self.assertContains(response, "the savings and loans they recorded")

        response = self.client.post(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Staff.objects.exists())
        self.assertEqual(
            [str(m) for m in get_messages(response.wsgi_request)],
            ["STF-001 deleted"],
        )

    def test_modal_urls_redirect_to_login_when_anonymous(self):
        staff = make_staff()
        self.client.logout()
        urls = [
            reverse("staff_add"),
            reverse("staff_edit", args=[staff.pk]),
            reverse("staff_delete", args=[staff.pk]),
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
        self.assertTrue(Staff.objects.exists())

    def test_success_message_set(self):
        response = self.client.post(reverse("staff_add"), VALID_POST)
        self.assertEqual(
            [str(m) for m in get_messages(response.wsgi_request)],
            ["STF-001 saved"],
        )
