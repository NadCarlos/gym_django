from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse


class LoginUpgradeTests(TestCase):
    def setUp(self):
        self.password = "rehearsal-only-password"
        self.legacy_hash = PBKDF2PasswordHasher().encode(
            self.password, "legacy-test-salt", iterations=390000
        )
        self.user = User.objects.create(username="legacy", password=self.legacy_hash)

    def login(self):
        return self.client.post(reverse("login"), {
            "username": self.user.username, "password": self.password,
        })

    def test_existing_password_logs_in_and_upgrades_without_losing_role(self):
        group = Group.objects.create(name="Rehabilitacion")
        self.user.groups.add(group)
        response = self.login()
        self.assertRedirects(response, reverse("inicio_rehab"), fetch_redirect_response=False)
        self.assertEqual(self.client.session["_auth_user_id"], str(self.user.pk))
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.password, self.legacy_hash)
        self.assertTrue(self.user.check_password(self.password))
        self.assertTrue(self.user.groups.filter(pk=group.pk).exists())

    def test_user_without_area_remains_denied(self):
        response = self.login()
        self.assertContains(response, "No tiene permisos para acceder al sistema")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_inactive_user_remains_denied(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        self.user.groups.add(Group.objects.create(name="Rehabilitacion"))
        response = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
