from typing import ClassVar

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

PASSWORD = "Str0ng-pass!"


class UserCrudTest(TestCase):
    fixtures: ClassVar[list] = ["users.json"]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.other = User.objects.get(pk=2)

    def test_list_is_public(self):
        response = self.client.get(reverse("users_index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ivan")
        self.assertContains(response, "anna")

    def test_create(self):
        data = {"first_name": "Олег", "last_name": "Смирнов", "username": "oleg",
                "password1": PASSWORD, "password2": PASSWORD}
        response = self.client.post(reverse("users_create"), data)
        self.assertRedirects(response, reverse("login"))
        self.assertTrue(User.objects.filter(username="oleg").exists())

    def test_create_duplicate_username(self):
        data = {"first_name": "X", "last_name": "Y", "username": "ivan",
                "password1": PASSWORD, "password2": PASSWORD}
        response = self.client.post(reverse("users_create"), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "уже существует")

    def test_update_self(self):
        self.client.force_login(self.user)
        data = {"first_name": "Новое", "last_name": "Имя", "username": "ivan",
                "password1": PASSWORD, "password2": PASSWORD}
        response = self.client.post(reverse("users_update", args=[self.user.pk]), data)
        self.assertRedirects(response, reverse("users_index"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Новое")

    def test_update_other_forbidden(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("users_update", args=[self.other.pk]),
            {"username": "hack", "password1": PASSWORD, "password2": PASSWORD},
            follow=True,
        )
        self.assertRedirects(response, reverse("users_index"))
        self.assertContains(response, "У вас нет прав для изменения")
        self.other.refresh_from_db()
        self.assertEqual(self.other.username, "anna")

    def test_update_anonymous_redirects_to_login(self):
        response = self.client.get(reverse("users_update", args=[self.user.pk]))
        self.assertRedirects(response, reverse("login"))

    def test_delete_self(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("users_delete", args=[self.user.pk]))
        self.assertRedirects(response, reverse("users_index"))
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())

    def test_delete_other_forbidden(self):
        self.client.force_login(self.user)
        self.client.post(reverse("users_delete", args=[self.other.pk]))
        self.assertTrue(User.objects.filter(pk=self.other.pk).exists())


class AuthTest(TestCase):
    fixtures: ClassVar[list] = ["users.json"]

    def test_login_logout(self):
        response = self.client.post(
            reverse("login"), {"username": "ivan", "password": PASSWORD}, follow=True
        )
        self.assertRedirects(response, reverse("index"))
        self.assertContains(response, "Вы залогинены")
        response = self.client.post(reverse("logout"), follow=True)
        self.assertRedirects(response, reverse("index"))
        self.assertContains(response, "Вы разлогинены")