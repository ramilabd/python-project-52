from typing import ClassVar
from unittest import mock

from django.contrib.auth.models import User
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse

from .models import Status


class StatusCrudTest(TestCase):
    fixtures: ClassVar[list] = ["users.json"]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.status = Status.objects.create(name="новый")
        self.other_status = Status.objects.create(name="в работе")

    def login(self):
        self.client.force_login(self.user)

    def test_list(self):
        self.login()
        response = self.client.get(reverse("statuses_index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "новый")
        self.assertContains(response, "в работе")
        self.assertContains(response, "Создать статус")
        self.assertContains(response, "Изменить")
        self.assertContains(response, "Удалить")

    def test_menu_link_for_authenticated_only(self):
        response = self.client.get(reverse("index"))
        self.assertNotContains(response, reverse("statuses_index"))
        self.login()
        response = self.client.get(reverse("index"))
        self.assertContains(response, reverse("statuses_index"))
        self.assertContains(response, "Статусы")

    def test_create(self):
        self.login()
        response = self.client.post(
            reverse("statuses_create"), {"name": "завершен"}, follow=True
        )
        self.assertRedirects(response, reverse("statuses_index"))
        self.assertTrue(Status.objects.filter(name="завершен").exists())
        self.assertContains(response, "Статус успешно создан")

    def test_create_duplicate_name(self):
        self.login()
        response = self.client.post(reverse("statuses_create"), {"name": "новый"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "уже существует")
        self.assertEqual(Status.objects.filter(name="новый").count(), 1)

    def test_update(self):
        self.login()
        response = self.client.post(
            reverse("statuses_update", args=[self.status.pk]),
            {"name": "на тестировании"},
            follow=True,
        )
        self.assertRedirects(response, reverse("statuses_index"))
        self.assertContains(response, "Статус успешно изменен")
        self.status.refresh_from_db()
        self.assertEqual(self.status.name, "на тестировании")

    def test_update_duplicate_name(self):
        self.login()
        response = self.client.post(
            reverse("statuses_update", args=[self.status.pk]),
            {"name": "в работе"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "уже существует")
        self.status.refresh_from_db()
        self.assertEqual(self.status.name, "новый")

    def test_delete_page_asks_confirmation(self):
        self.login()
        response = self.client.get(reverse("statuses_delete", args=[self.status.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Вы уверены, что хотите удалить новый?")
        self.assertContains(response, "Да, удалить")

    def test_delete(self):
        self.login()
        response = self.client.post(
            reverse("statuses_delete", args=[self.status.pk]), follow=True
        )
        self.assertRedirects(response, reverse("statuses_index"))
        self.assertContains(response, "Статус успешно удален")
        self.assertFalse(Status.objects.filter(pk=self.status.pk).exists())

    def test_delete_protected_status(self):
        # Модели задач ещё нет, поэтому связь со статусом имитируем:
        # delete() выбрасывает ProtectedError, как при on_delete=PROTECT.
        self.login()
        with mock.patch.object(
            Status, "delete", side_effect=ProtectedError("protected", [])
        ):
            response = self.client.post(
                reverse("statuses_delete", args=[self.status.pk]), follow=True
            )
        self.assertRedirects(response, reverse("statuses_index"))
        self.assertContains(response, "Невозможно удалить статус")
        self.assertNotContains(response, "Статус успешно удален")
        self.assertTrue(Status.objects.filter(pk=self.status.pk).exists())


class StatusAccessTest(TestCase):
    """Незалогиненный пользователь не может работать со статусами."""

    def setUp(self):
        self.status = Status.objects.create(name="новый")

    def assert_redirects_to_login(self, response, url):
        self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_get_pages_redirect_to_login(self):
        urls = [
            reverse("statuses_index"),
            reverse("statuses_create"),
            reverse("statuses_update", args=[self.status.pk]),
            reverse("statuses_delete", args=[self.status.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assert_redirects_to_login(self.client.get(url), url)

    def test_create_requires_login(self):
        url = reverse("statuses_create")
        response = self.client.post(url, {"name": "завершен"})
        self.assert_redirects_to_login(response, url)
        self.assertFalse(Status.objects.filter(name="завершен").exists())

    def test_update_requires_login(self):
        url = reverse("statuses_update", args=[self.status.pk])
        response = self.client.post(url, {"name": "взлом"})
        self.assert_redirects_to_login(response, url)
        self.status.refresh_from_db()
        self.assertEqual(self.status.name, "новый")

    def test_delete_requires_login(self):
        url = reverse("statuses_delete", args=[self.status.pk])
        response = self.client.post(url)
        self.assert_redirects_to_login(response, url)
        self.assertTrue(Status.objects.filter(pk=self.status.pk).exists())