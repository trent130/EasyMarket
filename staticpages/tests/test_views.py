import pytest


pytestmark = pytest.mark.django_db


class TestFooterAPI:
    def test_get_footer_data(self, client):
        resp = client.get("/api/footer/")
        assert resp.status_code == 200
