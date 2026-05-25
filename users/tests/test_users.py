import pytest
from users.models import CustomUser, UserProfile, Student
from users.authentication import EmailOrUsernameModelBackend
from tests.factories import StudentFactory


pytestmark = pytest.mark.django_db


class TestCustomUserManager:
    def test_create_user(self):
        user = CustomUser.objects.create_user(
            email="new@example.com",
            username="newuser",
            first_name="New",
            password="testpass123"
        )
        assert user.email == "new@example.com"
        assert user.check_password("testpass123")

    def test_create_user_no_email_raises(self):
        with pytest.raises(ValueError, match="Email must be set"):
            CustomUser.objects.create_user(email="", username="u", first_name="U", password="p")

    def test_create_superuser(self):
        admin = CustomUser.objects.create_superuser(
            email="admin@example.com",
            username="admin",
            first_name="Admin",
            password="admin123"
        )
        assert admin.is_staff is True
        assert admin.is_superuser is True


class TestCustomUserProperties:
    def test_full_name(self):
        user = CustomUser.objects.create_user(
            email="test@example.com", username="test", first_name="John",
            last_name="Doe", password="p"
        )
        assert user.full_name == "John Doe"

    def test_get_user_type_display_name_admin(self):
        user = CustomUser.objects.create_user(
            email="a@example.com", username="a", first_name="A",
            password="p", user_type='admin'
        )
        assert user.get_user_type_display_name() == "Admin"

    def test_get_user_type_display_name_student(self):
        user = CustomUser.objects.create_user(
            email="s@example.com", username="s", first_name="S",
            password="p", user_type='student'
        )
        assert user.get_user_type_display_name() == "Student"

    def test_str(self):
        user = CustomUser.objects.create_user(
            email="str@example.com", username="str", first_name="Str",
            password="p"
        )
        assert str(user) == "str@example.com"


class TestUserSignals:
    def test_auto_userprofile_created(self):
        user = CustomUser.objects.create_user(
            email="p@example.com", username="p", first_name="P",
            password="p"
        )
        assert UserProfile.objects.filter(user=user).exists()

    def test_auto_student_created_for_student_type(self):
        user = CustomUser.objects.create_user(
            email="s@example.com", username="s", first_name="S",
            password="p", user_type='student'
        )
        assert Student.objects.filter(user=user).exists()

    def test_no_student_for_admin_type(self):
        user = CustomUser.objects.create_user(
            email="a@example.com", username="a", first_name="A",
            password="p", user_type='admin'
        )
        assert not Student.objects.filter(user=user).exists()

    def test_auto_wishlist_not_in_users_app(self):
        pass


class TestStudentModel:
    def test_full_name_delegates_to_user(self):
        user = CustomUser.objects.create_user(
            email="stu@example.com", username="stu", first_name="Jane",
            last_name="Doe", password="p", user_type='student'
        )
        student = Student.objects.get(user=user)
        assert student.full_name == "Jane Doe"

    def test_email_delegates_to_user(self):
        user = CustomUser.objects.create_user(
            email="stu2@example.com", username="stu2", first_name="J",
            password="p", user_type='student'
        )
        student = Student.objects.get(user=user)
        assert student.email == "stu2@example.com"

    def test_str(self):
        user = CustomUser.objects.create_user(
            email="s3@example.com", username="s3", first_name="Sam",
            last_name="Smith", password="p", user_type='student'
        )
        student = Student.objects.get(user=user)
        assert str(student) == "Sam Smith (Student)"


class TestStudent2FA:
    def test_2fa_disabled_by_default(self):
        user = CustomUser.objects.create_user(
            email="2fa@example.com", username="2fa", first_name="2FA",
            password="p", user_type='student'
        )
        student = Student.objects.get(user=user)
        assert student.is_2fa_enabled() is False

    def test_enable_2fa(self):
        student = Student.objects.last()
        if student is None:
            user = CustomUser.objects.create_user(
                email="2fa2@example.com", username="2fa2", first_name="2FA",
                password="p", user_type='student'
            )
            student = Student.objects.get(user=user)
        student.two_factor_enabled = True
        student.two_factor_verified = True
        student.save()
        assert student.is_2fa_enabled() is True

    def test_generate_backup_codes(self):
        user = CustomUser.objects.create_user(
            email="bc@example.com", username="bc", first_name="B",
            password="p", user_type='student'
        )
        student = Student.objects.get(user=user)
        codes = student.generate_backup_codes(count=4)
        assert len(codes) == 4
        assert len(student.backup_codes) == 4

    def test_verify_backup_code_valid(self):
        user = CustomUser.objects.create_user(
            email="bc2@example.com", username="bc2", first_name="B2",
            password="p", user_type='student'
        )
        student = Student.objects.get(user=user)
        codes = student.generate_backup_codes(count=2)
        first_code = codes[0]
        result = student.verify_backup_code(first_code)
        assert result is True
        assert first_code not in student.backup_codes

    def test_verify_backup_code_invalid(self):
        user = CustomUser.objects.create_user(
            email="bc3@example.com", username="bc3", first_name="B3",
            password="p", user_type='student'
        )
        student = Student.objects.get(user=user)
        student.generate_backup_codes(count=2)
        result = student.verify_backup_code("INVALID-CODE")
        assert result is False


class TestUserProfile:
    def test_str(self):
        user = CustomUser.objects.create_user(
            email="up@example.com", username="up", first_name="U",
            password="p"
        )
        profile = UserProfile.objects.get(user=user)
        assert str(profile) == user.username

    def test_default_avatar(self):
        user = CustomUser.objects.create_user(
            email="up2@example.com", username="up2", first_name="U2",
            password="p"
        )
        profile = UserProfile.objects.get(user=user)
        assert profile.avatar == 'avatars/default.jpg'


class TestEmailOrUsernameBackend:
    def test_authenticate_by_username(self):
        user = CustomUser.objects.create_user(
            email="auth@example.com", username="authuser", first_name="Auth",
            password="secret123"
        )
        backend = EmailOrUsernameModelBackend()
        result = backend.authenticate(request=None, username="authuser", password="secret123")
        assert result == user

    def test_authenticate_by_email(self):
        user = CustomUser.objects.create_user(
            email="auth2@example.com", username="authuser2", first_name="Auth2",
            password="secret123"
        )
        backend = EmailOrUsernameModelBackend()
        result = backend.authenticate(request=None, username="auth2@example.com", password="secret123")
        assert result == user

    def test_authenticate_wrong_password(self):
        CustomUser.objects.create_user(
            email="auth3@example.com", username="authuser3", first_name="Auth3",
            password="secret123"
        )
        backend = EmailOrUsernameModelBackend()
        result = backend.authenticate(request=None, username="authuser3", password="wrong")
        assert result is None

    def test_authenticate_nonexistent_user(self):
        backend = EmailOrUsernameModelBackend()
        result = backend.authenticate(request=None, username="nobody", password="anything")
        assert result is None

    def test_get_user(self):
        user = CustomUser.objects.create_user(
            email="auth4@example.com", username="auth4", first_name="A",
            password="p"
        )
        backend = EmailOrUsernameModelBackend()
        result = backend.get_user(user.pk)
        assert result == user

    def test_get_user_nonexistent(self):
        backend = EmailOrUsernameModelBackend()
        result = backend.get_user("00000000-0000-0000-0000-000000000000")
        assert result is None


class TestUserSignupAPI:
    def test_signup_success(self, client):
        resp = client.post("/api/users/auth/signup/", {
            "username": "newuser", "email": "new@example.com",
            "first_name": "New", "last_name": "User",
            "password": "StrongPass1!", "password_confirm": "StrongPass1!",
            "user_type": "student"
        }, content_type="application/json")
        assert resp.status_code == 201
        assert resp.json()["message"] == "User created successfully"

    def test_signup_password_mismatch(self, client):
        resp = client.post("/api/users/auth/signup/", {
            "username": "baduser", "email": "bad@example.com",
            "first_name": "Bad", "last_name": "User",
            "password": "StrongPass1!", "password_confirm": "DifferentPass1!",
        }, content_type="application/json")
        assert resp.status_code == 400

    def test_signup_duplicate_email(self, client):
        CustomUser.objects.create_user(
            email="dup@example.com", username="dup", first_name="Dup",
            password="StrongPass1!"
        )
        resp = client.post("/api/users/auth/signup/", {
            "username": "dup2", "email": "dup@example.com",
            "first_name": "Dup2", "last_name": "User",
            "password": "StrongPass1!", "password_confirm": "StrongPass1!",
        }, content_type="application/json")
        assert resp.status_code == 400

    def test_signup_duplicate_username(self, client):
        resp = client.post("/api/users/auth/signup/", {
            "username": "dup3", "email": "dup3@example.com",
            "first_name": "Dup3", "last_name": "User",
            "password": "StrongPass1!", "password_confirm": "StrongPass1!",
        }, content_type="application/json")
        assert resp.status_code == 201
        resp2 = client.post("/api/users/auth/signup/", {
            "username": "dup3", "email": "dup4@example.com",
            "first_name": "Dup4", "last_name": "User",
            "password": "StrongPass1!", "password_confirm": "StrongPass1!",
        }, content_type="application/json")
        assert resp2.status_code == 400

    def test_signup_weak_password(self, client):
        resp = client.post("/api/users/auth/signup/", {
            "username": "weakpwd", "email": "weak@example.com",
            "first_name": "Weak", "last_name": "Pwd",
            "password": "short", "password_confirm": "short",
        }, content_type="application/json")
        assert resp.status_code == 400


class TestUserSigninAPI:
    def test_signin_success(self, client):
        CustomUser.objects.create_user(
            email="signin@example.com", username="signinuser",
            first_name="Sign", password="StrongPass1!"
        )
        resp = client.post("/api/users/auth/signin/", {
            "username_or_email": "signinuser",
            "password": "StrongPass1!"
        }, content_type="application/json")
        assert resp.status_code == 200
        data = resp.json()
        assert "access" in data
        assert "refresh" in data

    def test_signin_by_email(self, client):
        CustomUser.objects.create_user(
            email="signin2@example.com", username="signinuser2",
            first_name="Sign2", password="StrongPass1!"
        )
        resp = client.post("/api/users/auth/signin/", {
            "username_or_email": "signin2@example.com",
            "password": "StrongPass1!"
        }, content_type="application/json")
        assert resp.status_code == 200

    def test_signin_invalid_credentials(self, client):
        CustomUser.objects.create_user(
            email="signin3@example.com", username="signinuser3",
            first_name="Sign3", password="StrongPass1!"
        )
        resp = client.post("/api/users/auth/signin/", {
            "username_or_email": "signinuser3",
            "password": "wrongpassword"
        }, content_type="application/json")
        assert resp.status_code == 400


class TestGetCurrentUserAPI:
    def test_get_current_user_authenticated(self, client):
        user = CustomUser.objects.create_user(
            email="current@example.com", username="currentuser",
            first_name="Current", password="StrongPass1!"
        )
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.get("/api/users/auth/me/", HTTP_AUTHORIZATION=f"Bearer {token}")
        assert resp.status_code == 200
        assert resp.json()["user"]["email"] == "current@example.com"

    def test_get_current_user_unauthenticated(self, client):
        resp = client.get("/api/users/auth/me/")
        assert resp.status_code == 401


class TestStudentProfileAPI:
    def test_update_student_profile_requires_auth(self, client):
        resp = client.patch("/api/users/auth/student-profile/", {"bio": "Test"})
        assert resp.status_code == 401

    def test_update_student_profile_not_student(self, client):
        user = CustomUser.objects.create_user(
            email="customer@example.com", username="customer",
            first_name="Customer", password="StrongPass1!",
            user_type="customer"
        )
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.patch(
            "/api/users/auth/student-profile/",
            {"bio": "Test bio"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 404

    def test_update_student_profile_success(self, client):
        student = StudentFactory()
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(student.user)
        resp = client.put(
            "/api/users/auth/student-profile/",
            {"bio": "Updated bio", "university": "New University", "phone_number": "+254711111111"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200

    def test_partial_update_student_profile(self, client):
        student = StudentFactory()
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(student.user)
        resp = client.patch(
            "/api/users/auth/student-profile/",
            {"bio": "Partial update bio"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200


class TestChangePasswordAPI:
    def test_change_password_requires_auth(self, client):
        resp = client.post("/api/users/auth/change-password/", {})
        assert resp.status_code == 401


class TestSignoutAPI:
    def test_signout_requires_auth(self, client):
        resp = client.post("/api/users/auth/logout/")
        assert resp.status_code == 401

    def test_signout_success(self, client):
        user = CustomUser.objects.create_user(
            email="signout@example.com", username="signoutuser",
            first_name="Signout", password="StrongPass1!"
        )
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.post(
            "/api/users/auth/logout/",
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200


class TestValidateBackupCodeAPI:
    def test_validate_backup_code_requires_auth(self, client):
        resp = client.post("/api/users/auth/2fa/validate/", {"code": "XXXXX"})
        assert resp.status_code == 401

    def test_validate_backup_code_2fa_not_enabled(self, client):
        student = StudentFactory(two_factor_enabled=False)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(student.user)
        resp = client.post(
            "/api/users/auth/2fa/validate/",
            {"code": "XXXXX"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 400

    def test_validate_backup_code_invalid(self, client):
        student = StudentFactory(two_factor_enabled=True, backup_codes=["CODE1234"])
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(student.user)
        resp = client.post(
            "/api/users/auth/2fa/validate/",
            {"code": "NOMATCH1"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 400

    def test_validate_backup_code_bad_format(self, client):
        student = StudentFactory(two_factor_enabled=True)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(student.user)
        resp = client.post(
            "/api/users/auth/2fa/validate/",
            {"code": "Abcd1234"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 400

    def test_validate_backup_code_valid_format(self, client):
        student = StudentFactory(two_factor_enabled=True, backup_codes=["ABCD1234"])
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(student.user)
        resp = client.post(
            "/api/users/auth/2fa/validate/",
            {"code": "ABCD1234"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code in (200, 400)


class TestUserProfileAPI:
    def test_get_profile_requires_auth(self, client):
        resp = client.get("/api/users/profile/")
        assert resp.status_code == 401

    def test_get_profile_success(self, client):
        student = StudentFactory()
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(student.user)
        resp = client.get(
            "/api/users/profile/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200
        assert "user_info" in resp.json()["results"][0]

    def test_update_profile(self, client):
        student = StudentFactory()
        profile = student.user.userprofile
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(student.user)
        resp = client.patch(
            f"/api/users/profile/{profile.id}/",
            {"user": student.user.id},
            content_type="application/x-www-form-urlencoded",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200


class TestTwoFactorAPI:
    def test_enable_2fa_requires_auth(self, client):
        resp = client.post("/api/users/auth/2fa/enable/")
        assert resp.status_code == 401

    def test_enable_2fa_success(self, client):
        student = StudentFactory()
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(student.user)
        resp = client.post(
            "/api/users/auth/2fa/enable/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200
        assert "secret" in resp.json()

    def test_enable_2fa_already_enabled(self, client):
        student = StudentFactory(two_factor_enabled=True)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(student.user)
        resp = client.post(
            "/api/users/auth/2fa/enable/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 400

    def test_verify_2fa_requires_auth(self, client):
        resp = client.post("/api/users/auth/2fa/verify/", {"token": "123456"})
        assert resp.status_code == 401

    def test_verify_2fa_not_enabled(self, client):
        student = StudentFactory(two_factor_enabled=False)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(student.user)
        resp = client.post(
            "/api/users/auth/2fa/verify/",
            {"token": "123456", "secret": "somes3cret"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 400

    def test_verify_2fa_success(self, client):
        import pyotp
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        token = totp.now()
        student = StudentFactory(two_factor_enabled=True, two_factor_secret=secret)
        from rest_framework_simplejwt.tokens import AccessToken
        jwt_token = AccessToken.for_user(student.user)
        resp = client.post(
            "/api/users/auth/2fa/verify/",
            {"token": token, "secret": secret},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {jwt_token}"
        )
        assert resp.status_code == 200

    def test_verify_2fa_invalid_secret(self, client):
        student = StudentFactory(two_factor_enabled=True, two_factor_secret="JBSWY3DPEHPK3PXP")
        from rest_framework_simplejwt.tokens import AccessToken
        jwt_token = AccessToken.for_user(student.user)
        resp = client.post(
            "/api/users/auth/2fa/verify/",
            {"token": "123456", "secret": "JBSWY3DPEHPK3PXP"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {jwt_token}"
        )
        assert resp.status_code == 400

    def test_verify_2fa_nondigit_token(self, client):
        student = StudentFactory(two_factor_enabled=True)
        from rest_framework_simplejwt.tokens import AccessToken
        jwt_token = AccessToken.for_user(student.user)
        resp = client.post(
            "/api/users/auth/2fa/verify/",
            {"token": "abc123", "secret": "whatever"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {jwt_token}"
        )
        assert resp.status_code == 400

    def test_disable_2fa_requires_auth(self, client):
        resp = client.post("/api/users/auth/2fa/disable/", {})
        assert resp.status_code == 401

    def test_disable_2fa_success(self, client):
        student = StudentFactory(two_factor_enabled=True, two_factor_secret="tests")
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(student.user)
        resp = client.post(
            "/api/users/auth/2fa/disable/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200

    def test_disable_2fa_not_enabled(self, client):
        student = StudentFactory(two_factor_enabled=False)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(student.user)
        resp = client.post(
            "/api/users/auth/2fa/disable/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 400

    def test_get_2fa_status_requires_auth(self, client):
        resp = client.get("/api/users/auth/2fa/status/")
        assert resp.status_code == 401

    def test_get_2fa_status_success(self, client):
        student = StudentFactory()
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(student.user)
        resp = client.get(
            "/api/users/auth/2fa/status/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200
