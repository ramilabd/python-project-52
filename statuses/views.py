from typing import ClassVar

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import StatusForm
from .models import Status


class StatusListView(LoginRequiredMixin, ListView):
    model = Status
    template_name = "statuses/index.html"
    context_object_name = "statuses"


class StatusCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    form_class = StatusForm
    template_name = "statuses/form.html"
    success_url = reverse_lazy("statuses_index")
    success_message = _("Status created successfully")
    extra_context: ClassVar[dict] = {
        "title": _("Create status"),
        "button": _("Create"),
    }


class StatusUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Status
    form_class = StatusForm
    template_name = "statuses/form.html"
    success_url = reverse_lazy("statuses_index")
    success_message = _("Status updated successfully")
    extra_context: ClassVar[dict] = {
        "title": _("Edit status"),
        "button": _("Change"),
    }


class StatusDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Status
    template_name = "statuses/delete.html"
    success_url = reverse_lazy("statuses_index")
    success_message = _("Status deleted successfully")

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, _("Unable to delete status"))
            return redirect(self.success_url)