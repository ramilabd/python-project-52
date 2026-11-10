from typing import ClassVar

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from labels.models import Label
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
        self.task.refresh_from_db()
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

class TaskLabelsTest(TestCase):
    fixtures: ClassVar[list] = ["users.json"]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.status = Status.objects.create(name="новый")
        self.bug = Label.objects.create(name="bug")
        self.feature = Label.objects.create(name="feature")
        self.client.force_login(self.user)

    def test_create_task_with_labels(self):
        response = self.client.post(
            reverse("tasks_create"),
            {
                "name": "С метками",
                "description": "",
                "status": self.status.pk,
                "labels": [self.bug.pk, self.feature.pk],
            },
            follow=True,
        )
        self.assertRedirects(response, reverse("tasks_index"))
        task = Task.objects.get(name="С метками")
        self.assertCountEqual(task.labels.all(), [self.bug, self.feature])

    def test_create_task_without_labels(self):
        self.client.post(
            reverse("tasks_create"),
            {"name": "Без меток", "description": "", "status": self.status.pk},
        )
        self.assertEqual(Task.objects.get(name="Без меток").labels.count(), 0)

    def test_update_task_labels(self):
        task = Task.objects.create(name="Задача", status=self.status, author=self.user)
        task.labels.add(self.bug)
        self.client.post(
            reverse("tasks_update", args=[task.pk]),
            {
                "name": "Задача",
                "description": "",
                "status": self.status.pk,
                "labels": [self.feature.pk],
            },
        )
        self.assertEqual(list(task.labels.all()), [self.feature])

    def test_form_has_multiple_select_for_labels(self):
        response = self.client.get(reverse("tasks_create"))
        self.assertContains(response, 'name="labels"')
        self.assertContains(response, "multiple")
        self.assertContains(response, "Метки")

    def test_detail_shows_labels(self):
        task = Task.objects.create(name="Задача", status=self.status, author=self.user)
        task.labels.add(self.bug)
        response = self.client.get(reverse("tasks_detail", args=[task.pk]))
        self.assertContains(response, "Метки")
        self.assertContains(response, "bug")
        self.assertNotContains(response, "feature")

class TaskAccessTest(TestCase):
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


class TaskFilterTest(TestCase):
    fixtures: ClassVar[list] = ["users.json"]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.other = User.objects.get(pk=2)
        self.new = Status.objects.create(name="новый")
        self.done = Status.objects.create(name="завершён")
        self.bug = Label.objects.create(name="баг")
        self.feature = Label.objects.create(name="фича")
        self.task1 = Task.objects.create(
            name="Задача один",
            status=self.new,
            author=self.user,
            executor=self.other,
        )
        self.task1.labels.add(self.bug)
        self.task2 = Task.objects.create(
            name="Задача два",
            status=self.done,
            author=self.other,
            executor=self.user,
        )
        self.task2.labels.add(self.feature)
        self.client.force_login(self.user)

    def get_tasks(self, **params):
        response = self.client.get(reverse("tasks_index"), params)
        self.assertEqual(response.status_code, 200)
        return list(response.context["tasks"])

    def test_filter_form_is_displayed(self):
        response = self.client.get(reverse("tasks_index"))
        for text in ("Статус", "Исполнитель", "Метка", "Только свои задачи"):
            self.assertContains(response, text)

    def test_no_filters_returns_all_tasks(self):
        self.assertEqual(self.get_tasks(), [self.task1, self.task2])

    def test_filter_by_status(self):
        self.assertEqual(self.get_tasks(status=self.done.pk), [self.task2])

    def test_filter_by_executor(self):
        self.assertEqual(self.get_tasks(executor=self.other.pk), [self.task1])

    def test_filter_by_label(self):
        self.assertEqual(self.get_tasks(labels=self.bug.pk), [self.task1])

    def test_filter_only_own_tasks(self):
        self.assertEqual(self.get_tasks(self_tasks="on"), [self.task1])

    def test_combined_filters(self):
        tasks = self.get_tasks(status=self.new.pk, labels=self.feature.pk)
        self.assertEqual(tasks, [])
        tasks = self.get_tasks(status=self.new.pk, self_tasks="on")
        self.assertEqual(tasks, [self.task1])