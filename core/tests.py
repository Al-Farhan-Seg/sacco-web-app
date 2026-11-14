from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from core.models import CodedModel
from core.search import search
from core.templatetags.sacco import ugx


class UgxFilterTests(TestCase):
    def test_ugx_formats_thousands(self):
        self.assertEqual(ugx(850000), "UGX 850,000")
        self.assertEqual(ugx(0), "UGX 0")
        self.assertEqual(ugx(None), "UGX 0")


class CodedModelTests(TestCase):
    def test_coded_model_code(self):
        class Fake:
            pk = 7
            code_prefix = "MEM"
            code = CodedModel.code

        self.assertEqual(Fake().code, "MEM-007")


class AuthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("clerk", password="s3cret-pass")

    def test_login_required_redirects(self):
        response = self.client.get("/")
        self.assertRedirects(
            response, "/login/?next=/", fetch_redirect_response=False
        )

    def test_login_flow(self):
        response = self.client.post(
            "/login/", {"username": "clerk", "password": "s3cret-pass"}
        )
        self.assertRedirects(response, "/", fetch_redirect_response=False)
        response = self.client.post("/logout/")
        self.assertRedirects(response, "/login/", fetch_redirect_response=False)

    def test_wrong_password_stays_on_login(self):
        response = self.client.post(
            "/login/", {"username": "clerk", "password": "wrong"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)


class SearchHelperTests(TestCase):
    """core.search.search, shown on Django's User model."""

    def setUp(self):
        self.ann = User.objects.create_user("ann", first_name="Ann", last_name="Lee")
        self.bob = User.objects.create_user("bob", first_name="Bob", last_name="Ray")

    def find(self, term):
        return list(search(
            User.objects.order_by("pk"), term,
            fields=["first_name", "last_name"], codes={"USR": "pk"},
        ))

    def test_partial_and_case_insensitive(self):
        self.assertEqual(self.find("ANN"), [self.ann])

    def test_every_word_must_match(self):
        self.assertEqual(self.find("bob ray"), [self.bob])
        self.assertEqual(self.find("bob lee"), [])

    def test_codes_and_bare_numbers_match_the_id(self):
        self.assertEqual(self.find(f"usr-{self.bob.pk}"), [self.bob])
        self.assertEqual(self.find(f"USR{self.ann.pk}"), [self.ann])
        self.assertEqual(self.find(str(self.bob.pk)), [self.bob])

    def test_unknown_prefix_falls_back_to_text(self):
        self.assertEqual(self.find("xyz-5"), [])

    def test_blank_term_changes_nothing(self):
        self.assertEqual(len(self.find("")), 2)

    def test_special_characters_are_harmless(self):
        for term in ["%", "_", "'", '"; DROP TABLE auth_user;--']:
            self.assertEqual(self.find(term), [], term)


STATIC_DIR = settings.BASE_DIR / "static"
TEMPLATES_DIR = settings.BASE_DIR / "templates"
PALETTE = [
    "#EEE9DF", "#FBF9F4", "#C9C1B1", "#1B2632",
    "#2C3B4D", "#F2A55C", "#A35139", "#5B6773",
]
OLD_CSS = [
    "account.css", "index.css", "loan-payment.css", "loan.css", "login.css",
    "member.css", "saving.css", "staff.css", "withdrawal.css",
]


class ShellTests(TestCase):
    def test_shell_has_all_nav_links(self):
        user = User.objects.create_user("clerk", password="s3cret-pass")
        self.client.force_login(user)
        response = self.client.get("/")
        for href in [
            "/members/", "/staff/", "/accounts/", "/savings/",
            "/withdrawals/", "/loans/", "/loan-payments/",
        ]:
            self.assertContains(response, f'href="{href}"')
        self.assertContains(response, "Dashboard")

    def test_django_admin_link_is_for_staff_only(self):
        clerk = User.objects.create_user("clerk", password="s3cret-pass")
        self.client.force_login(clerk)
        self.assertNotContains(self.client.get("/"), 'href="/admin/"')

        boss = User.objects.create_user("boss", password="s3cret-pass", is_staff=True)
        self.client.force_login(boss)
        self.assertContains(self.client.get("/"), 'href="/admin/"')

    def test_signed_up_user_can_use_the_data_pages_but_not_the_admin(self):
        self.client.force_login(User.objects.create_user("clerk", password="s3cret-pass"))
        self.assertEqual(self.client.get("/members/").status_code, 200)
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])

    def test_login_page_has_password_input(self):
        response = self.client.get("/login/")
        self.assertContains(response, 'type="password"')

    def test_static_assets_exist(self):
        for name in ["css/app.css", "js/modal.js", "js/lucide.min.js"]:
            self.assertTrue((STATIC_DIR / name).is_file(), name)
        css = (STATIC_DIR / "css/app.css").read_text(encoding="utf-8").upper()
        for colour in PALETTE:
            self.assertIn(colour, css)

    def test_no_framework_markup(self):
        files = [STATIC_DIR / "css/app.css", *TEMPLATES_DIR.rglob("*.html")]
        for file in files:
            text = file.read_text(encoding="utf-8").lower()
            self.assertNotIn("bootstrap", text, file)
            self.assertNotIn("tailwind", text, file)

    def test_old_css_removed(self):
        for name in OLD_CSS:
            self.assertFalse((STATIC_DIR / "css" / name).exists(), name)

    def test_modal_templates_exist(self):
        from django.template.loader import get_template

        for name in ["partials/_modal_form.html", "partials/_modal_delete.html"]:
            get_template(name)


class SignUpTests(TestCase):
    """Sign-up is for logged-out visitors; new users are plain, never staff."""

    VALID = {
        "username": "newclerk",
        "first_name": "Ann",
        "last_name": "Lee",
        "email": "ann@example.com",
        "password1": "a-long-pass-2026",
        "password2": "a-long-pass-2026",
    }

    def test_logged_out_visitor_sees_the_form(self):
        response = self.client.get("/sign-up/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="password2"')

    def test_valid_sign_up_creates_a_plain_user_and_logs_in(self):
        response = self.client.post("/sign-up/", self.VALID)
        self.assertRedirects(response, "/", fetch_redirect_response=False)
        user = User.objects.get(username="newclerk")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.email, "ann@example.com")
        self.assertEqual(self.client.session["_auth_user_id"], str(user.pk))

    def test_password_mismatch_creates_nobody(self):
        data = {**self.VALID, "password2": "something-else-2026"}
        response = self.client.post("/sign-up/", data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newclerk").exists())

    def test_duplicate_username_is_refused(self):
        User.objects.create_user("newclerk", password="s3cret-pass")
        response = self.client.post("/sign-up/", self.VALID)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username="newclerk").count(), 1)

    def test_logged_in_user_is_sent_away_from_sign_up_and_login(self):
        self.client.force_login(User.objects.create_user("clerk", password="s3cret-pass"))
        for url in ["/sign-up/", "/login/"]:
            response = self.client.get(url)
            self.assertRedirects(response, "/", fetch_redirect_response=False)


class AuthLayoutTests(TestCase):
    """Login and sign-up share one layout and link to each other while logged out."""

    def test_login_and_sign_up_extend_the_shared_layout(self):
        for url in ["/login/", "/sign-up/"]:
            response = self.client.get(url)
            self.assertTemplateUsed(response, "auth_base.html")
            self.assertTemplateUsed(response, "base.html")
            self.assertContains(response, 'class="auth"')
            self.assertContains(response, 'href="/sign-up/"')
            self.assertContains(response, 'href="/login/"')

    def test_logged_in_pages_never_mention_sign_up(self):
        self.client.force_login(User.objects.create_user("clerk", password="s3cret-pass"))
        for url in ["/", "/members/", "/analytics/"]:
            self.assertNotContains(self.client.get(url), "sign-up")


class AdminCustomisationTests(TestCase):
    """Every data model has its own ModelAdmin and the admin pages load."""

    def setUp(self):
        self.client.force_login(
            User.objects.create_superuser("boss", password="s3cret-pass")
        )

    def test_every_model_has_a_customised_admin(self):
        from django.contrib import admin
        from django.apps import apps

        for label in ["members.Member", "staff.Staff", "accounts.Account",
                      "savings.Saving", "withdrawals.Withdrawal",
                      "loans.Loan", "loans.LoanPayment"]:
            model = apps.get_model(label)
            model_admin = admin.site._registry[model]
            self.assertIn("code", model_admin.list_display, label)
            self.assertTrue(model_admin.search_fields, label)

    def test_changelists_load(self):
        for path in ["members/member", "staff/staff", "accounts/account",
                     "savings/saving", "withdrawals/withdrawal",
                     "loans/loan", "loans/loanpayment"]:
            response = self.client.get(f"/admin/{path}/?q=a")
            self.assertEqual(response.status_code, 200, path)
