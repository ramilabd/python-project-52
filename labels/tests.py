from typing import ClassVar

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from statuses.models import Status
from tasks.models import Task

from .models import Label


class LabelCrudTest(TestCase):
    fixtures: ClassVar[list] = ["users.json"]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.label = Label.objects.create(name="bug")
        self.other_label = Label.objects.create(name="feature")

    def login(self):
        self.client.force_login(self.user)

    def test_list(self):
        self.login()
        response = self.client.get(reverse("labels_index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "bug")
        self.assertContains(response, "feature")
        self.assertContains(response, "Создать метку")
        self.assertContains(response, "Изменить")
        self.assertContains(response, "Удалить")

    def test_menu_link_for_authenticated_only(self):
        response = self.client.get(reverse("index"))
        self.assertNotContains(response, reverse("labels_index"))
        self.login()
        response = self.client.get(reverse("index"))
        self.assertContains(response, reverse("labels_index"))
        self.assertContains(response, "Метки")

    def test_create(self):
        self.login()
        response = self.client.post(
            reverse("labels_create"), {"name": "docs"}, follow=True
        )
        self.assertRedirects(response, reverse("labels_index"))
        self.assertContains(response, "Метка успешно создана")
        self.assertTrue(Label.objects.filter(name="docs").exists())

    def test_create_duplicate_name(self):
        self.login()
        response = self.client.post(reverse("labels_create"), {"name": "bug"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "уже существует")
        self.assertEqual(Label.objects.filter(name="bug").count(), 1)

    def test_update(self):
        self.login()
        response = self.client.post(
            reverse("labels_update", args=[self.label.pk]),
            {"name": "defect"},
            follow=True,
        )
        self.assertRedirects(response, reverse("labels_index"))
        self.assertContains(response, "Метка успешно изменена")
        self.label.refresh_from_db()
        self.assertEqual(self.label.name, "defect")

    def test_update_duplicate_name(self):
        self.login()
        response = self.client.post(
            reverse("labels_update", args=[self.label.pk]), {"name": "feature"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "уже существует")
        self.label.refresh_from_db()
        self.assertEqual(self.label.name, "bug")

    def test_delete_page_asks_confirmation(self):
        self.login()
        response = self.client.get(reverse("labels_delete", args=[self.label.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Вы уверены, что хотите удалить bug?")
        self.assertContains(response, "Да, удалить")

    def test_delete(self):
        self.login()
        response = self.client.post(
            reverse("labels_delete", args=[self.label.pk]), follow=True
        )
        self.assertRedirects(response, reverse("labels_index"))
        self.assertContains(response, "Метка успешно удалена")
        self.assertFalse(Label.objects.filter(pk=self.label.pk).exists())

    def test_cannot_delete_label_linked_to_task(self):
        status = Status.objects.create(name="новый")
        task = Task.objects.create(name="Задача", status=status, author=self.user)
        task.labels.add(self.label)
        self.login()
        response = self.client.post(
            reverse("labels_delete", args=[self.label.pk]), follow=True
        )
        self.assertRedirects(response, reverse("labels_index"))
        self.assertContains(response, "Невозможно удалить метку")
        self.assertNotContains(response, "Метка успешно удалена")
        self.assertTrue(Label.objects.filter(pk=self.label.pk).exists())

    def test_can_delete_label_after_task_deleted(self):
        status = Status.objects.create(name="новый")
        task = Task.objects.create(name="Задача", status=status, author=self.user)
        task.labels.add(self.label)
        task.delete()
        self.login()
        self.client.post(reverse("labels_delete", args=[self.label.pk]))
        self.assertFalse(Label.objects.filter(pk=self.label.pk).exists())


class LabelAccessTest(TestCase):
    def setUp(self):
        self.label = Label.objects.create(name="bug")

    def assert_redirects_to_login(self, response, url):
        self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_get_pages_redirect_to_login(self):
        urls = [
            reverse("labels_index"),
            reverse("labels_create"),
            reverse("labels_update", args=[self.label.pk]),
            reverse("labels_delete", args=[self.label.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assert_redirects_to_login(self.client.get(url), url)

    def test_create_requires_login(self):
        url = reverse("labels_create")
        response = self.client.post(url, {"name": "docs"})
        self.assert_redirects_to_login(response, url)
        self.assertFalse(Label.objects.filter(name="docs").exists())

    def test_update_requires_login(self):
        url = reverse("labels_update", args=[self.label.pk])
        response = self.client.post(url, {"name": "взлом"})
        self.assert_redirects_to_login(response, url)
        self.label.refresh_from_db()
        self.assertEqual(self.label.name, "bug")

    def test_delete_requires_login(self):
        url = reverse("labels_delete", args=[self.label.pk])
        response = self.client.post(url)
        self.assert_redirects_to_login(response, url)
        self.assertTrue(Label.objects.filter(pk=self.label.pk).exists())