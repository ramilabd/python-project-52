from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from statuses.models import Status


class Task(models.Model):
    name = models.CharField(_("Name"), max_length=255, unique=True)  # unique -> «уже существует»
    description = models.TextField(_("Description"), blank=True)     # blank=True: поле необязательное
    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,  # нельзя удалить статус, пока есть задачи с ним
        related_name="tasks",
        verbose_name=_("Status"),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,  # нельзя удалить автора задач
        related_name="authored_tasks",
        verbose_name=_("Author"),
    )
    executor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,  # нельзя удалить исполнителя задач
        null=True,
        blank=True,                # исполнитель необязателен (null — в БД, blank — в форме)
        related_name="executed_tasks",
        verbose_name=_("Executor"),
    )
    created_at = models.DateTimeField(_("Creation date"), auto_now_add=True)  # ставится при создании

    class Meta:
        ordering = ("id",)
        verbose_name = _("task")
        verbose_name_plural = _("tasks")

    def __str__(self):
        return self.name