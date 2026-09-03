import pytest

from adminapp.views import is_staff_or_admin
from users.models import CustomUser


pytestmark = pytest.mark.django_db


def test_traditional_admin_views_require_authorization(client):
    user = CustomUser.objects.create_user(
        email="regular@example.com",
        username="regular",
        first_name="Regular",
        password="StrongPass1!",
    )
    client.force_login(user)

    assert client.get("/api/admin/").status_code == 302
    assert client.get("/api/admin/web/users/").status_code == 403


def test_traditional_admin_guard_allows_staff_or_admin():
    staff_user = CustomUser.objects.create_user(
        email="staff@example.com",
        username="staff",
        first_name="Staff",
        password="StrongPass1!",
        is_staff=True,
    )
    admin_user = CustomUser.objects.create_user(
        email="appadmin@example.com",
        username="appadmin",
        first_name="App Admin",
        password="StrongPass1!",
        user_type="admin",
    )

    assert is_staff_or_admin(staff_user) is True
    assert is_staff_or_admin(admin_user) is True
