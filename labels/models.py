from django.db import models
from django.utils.translation import gettext_lazy as _


class Label(models.Model):
    name = models.CharField(_("Name"), max_length=255, unique=True)
    created_at = models.DateTimeField(_("Creation date"), auto_now_add=True)

    class Meta:
        ordering = ("id",)
        verbose_name = _("label")
        verbose_name_plural = _("labels")

    def __str__(self):
        return self.name