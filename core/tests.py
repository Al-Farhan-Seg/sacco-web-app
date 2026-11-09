from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase, override_settings
from django.urls import path

from core.crud import ListPage, ModalDeleteMixin, ModalFormMixin
from core.models import CodedModel
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


class UserListPage(ListPage):
    model = User
    template_name = "registration/login.html"
    page_title = "Users"
    add_label = "Add user"
    url_name = "user"


urlpatterns = [
    path("users/add/", lambda request: HttpResponse(), name="user_add"),
]


@override_settings(ROOT_URLCONF=__name__)
class ListPageTests(TestCase):
    def test_out_of_range_page_shows_last_page(self):
        for i in range(12):
            User.objects.create_user(f"user{i}")
        request = RequestFactory().get("/users/", {"page": 9})
        request.user = User.objects.first()
        response = UserListPage.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data["page_obj"].number, 2)


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
            "/withdrawals/", "/loans/", "/loan-payments/", "/admin/",
        ]:
            self.assertContains(response, f'href="{href}"')
        self.assertContains(response, "Dashboard")

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

    def test_modal_mixin_templates_exist(self):
        from django.template.loader import get_template

        for mixin in [ModalFormMixin, ModalDeleteMixin]:
            get_template(mixin.template_name)
