from typing import ClassVar

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import LabelForm
from .models import Label


class LabelListView(LoginRequiredMixin, ListView):
    model = Label
    template_name = "labels/index.html"
    context_object_name = "labels"


class LabelCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    form_class = LabelForm
    template_name = "labels/form.html"
    success_url = reverse_lazy("labels_index")
    success_message = _("Label created successfully")
    extra_context: ClassVar[dict] = {
        "title": _("Create label"),
        "button": _("Create"),
    }


class LabelUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Label
    form_class = LabelForm
    template_name = "labels/form.html"
    success_url = reverse_lazy("labels_index")
    success_message = _("Label updated successfully")
    extra_context: ClassVar[dict] = {
        "title": _("Edit label"),
        "button": _("Change"),
    }


class LabelDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Label
    template_name = "labels/delete.html"
    success_url = reverse_lazy("labels_index")
    success_message = _("Label deleted successfully")

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, _("Unable to delete label"))
            return redirect(self.success_url)