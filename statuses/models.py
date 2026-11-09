from django.db import models
from django.utils.translation import gettext_lazy as _


class Status(models.Model):
    name = models.CharField(_("Name"), max_length=255, unique=True)
    created_at = models.DateTimeField(_("Creation date"), auto_now_add=True)

    class Meta:
        ordering = ("id",)
        verbose_name = _("status")
        verbose_name_plural = _("statuses")

    def __str__(self):
        return self.name