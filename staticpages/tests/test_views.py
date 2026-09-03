import pytest
from staticpages.models import StaticPage
from users.models import CustomUser


pytestmark = pytest.mark.django_db


class TestFooterAPI:
    def test_get_footer_data(self, client):
        resp = client.get("/api/footer/")
        assert resp.status_code == 200


class TestStaticPageAPI:
    def test_unpublished_home_page_is_not_public(self, client):
        StaticPage.objects.create(
            title="Home",
            content="Draft home",
            slug="home",
            is_published=False,
        )

        resp = client.get("/api/pages/home/")

        assert resp.status_code == 404

    def test_authenticated_non_admin_cannot_mutate_static_pages(self, client):
        user = CustomUser.objects.create_user(
            email="static-page-user@example.com",
            username="static-page-user",
            first_name="Regular",
            password="StrongPass1!",
        )
        client.force_login(user)

        resp = client.post(
            "/api/pages/",
            {"title": "Injected", "content": "Injected", "slug": "injected"},
        )

        assert resp.status_code == 403
