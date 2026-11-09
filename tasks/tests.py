from typing import ClassVar

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from statuses.models import Status

from .models import Task


class TaskCrudTest(TestCase):
    fixtures: ClassVar[list] = ["users.json"]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.other = User.objects.get(pk=2)
        self.status = Status.objects.create(name="новый")
        self.task = Task.objects.create(
            name="Первая задача",
            description="Описание",
            status=self.status,
            author=self.user,
        )

    def login(self, user=None):
        self.client.force_login(user or self.user)

    def test_list(self):
        self.login()
        response = self.client.get(reverse("tasks_index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Первая задача")
        self.assertContains(response, "Создать задачу")
        self.assertContains(response, "Показать")

    def test_menu_link_for_authenticated_only(self):
        response = self.client.get(reverse("index"))
        self.assertNotContains(response, reverse("tasks_index"))
        self.login()
        response = self.client.get(reverse("index"))
        self.assertContains(response, reverse("tasks_index"))
        self.assertContains(response, "Задачи")

    def test_detail(self):
        self.login()
        response = self.client.get(reverse("tasks_detail", args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Первая задача")
        self.assertContains(response, "новый")

    def test_create_sets_author(self):
        self.login(self.other)
        response = self.client.post(
            reverse("tasks_create"),
            {"name": "Новая", "description": "", "status": self.status.pk},
            follow=True,
        )
        self.assertRedirects(response, reverse("tasks_index"))
        self.assertContains(response, "Задача успешно создана")
        task = Task.objects.get(name="Новая")
        self.assertEqual(task.author, self.other)

    def test_create_duplicate_name(self):
        self.login()
        response = self.client.post(
            reverse("tasks_create"),
            {"name": "Первая задача", "status": self.status.pk},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "уже существует")
        self.assertEqual(Task.objects.filter(name="Первая задача").count(), 1)

    def test_update_by_non_author(self):
        self.login(self.other)
        response = self.client.post(
            reverse("tasks_update", args=[self.task.pk]),
            {
                "name": "Изменённая",
                "description": "",
                "status": self.status.pk,
                "executor": self.other.pk,
            },
            follow=True,
        )
        self.assertRedirects(response, reverse("tasks_index"))
        self.assertContains(response, "Задача успешно изменена")
        self.task.refresh_from_db()  # перечитываем объект из БД
        self.assertEqual(self.task.name, "Изменённая")
        self.assertEqual(self.task.executor, self.other)

    def test_delete_by_author(self):
        self.login()
        response = self.client.post(
            reverse("tasks_delete", args=[self.task.pk]), follow=True
        )
        self.assertRedirects(response, reverse("tasks_index"))
        self.assertContains(response, "Задача успешно удалена")
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())

    def test_delete_by_non_author_forbidden(self):
        self.login(self.other)
        response = self.client.post(
            reverse("tasks_delete", args=[self.task.pk]), follow=True
        )
        self.assertRedirects(response, reverse("tasks_index"))
        self.assertContains(response, "Задачу может удалить только ее автор")
        self.assertTrue(Task.objects.filter(pk=self.task.pk).exists())

    def test_cannot_delete_user_with_tasks(self):
        self.login()
        response = self.client.post(
            reverse("users_delete", args=[self.user.pk]), follow=True
        )
        self.assertRedirects(response, reverse("users_index"))
        self.assertContains(response, "Невозможно удалить пользователя")
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())

    def test_cannot_delete_executor_user(self):
        self.task.executor = self.other
        self.task.save()
        self.login(self.other)
        self.client.post(reverse("users_delete", args=[self.other.pk]))
        self.assertTrue(User.objects.filter(pk=self.other.pk).exists())

    def test_cannot_delete_status_with_tasks(self):
        self.login()
        response = self.client.post(
            reverse("statuses_delete", args=[self.status.pk]), follow=True
        )
        self.assertContains(response, "Невозможно удалить статус")
        self.assertTrue(Status.objects.filter(pk=self.status.pk).exists())


class TaskAccessTest(TestCase):
    """Незалогиненный пользователь перенаправляется на вход."""

    fixtures: ClassVar[list] = ["users.json"]

    def setUp(self):
        user = User.objects.get(pk=1)
        status = Status.objects.create(name="новый")
        self.task = Task.objects.create(name="Задача", status=status, author=user)

    def test_all_pages_redirect_to_login(self):
        urls = [
            reverse("tasks_index"),
            reverse("tasks_create"),
            reverse("tasks_detail", args=[self.task.pk]),
            reverse("tasks_update", args=[self.task.pk]),
            reverse("tasks_delete", args=[self.task.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, f"{reverse('login')}?next={url}")