from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from labels.models import Label
from statuses.models import Status


class Task(models.Model):
    name = models.CharField(_("Name"), max_length=255, unique=True)
    description = models.TextField(_("Description"), blank=True)
    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        related_name="tasks",
        verbose_name=_("Status"),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="authored_tasks",
        verbose_name=_("Author"),
    )
    executor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="executed_tasks",
        verbose_name=_("Executor"),
    )
    labels = models.ManyToManyField(
        Label,
        through="TaskLabel",
        blank=True,
        related_name="tasks",
        verbose_name=_("Labels"),
    )
    created_at = models.DateTimeField(_("Creation date"), auto_now_add=True)

    class Meta:
        ordering = ("id",)
        verbose_name = _("task")
        verbose_name_plural = _("tasks")

    def __str__(self):
        return self.name


class TaskLabel(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    label = models.ForeignKey(Label, on_delete=models.PROTECT)