from typing import ClassVar

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import UserForm


class UserListView(ListView):
    model = User
    template_name = "users/index.html"
    context_object_name = "users"


class UserCreateView(SuccessMessageMixin, CreateView):
    form_class = UserForm
    template_name = "users/form.html"
    success_url = reverse_lazy("login")
    success_message = _("User registered successfully")
    extra_context: ClassVar[dict] = {"title": _("Sign up"), "button": _("Register")}


class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.pk == self.kwargs["pk"]

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, _("You have no rights to change"))
            return redirect("users_index")
        return redirect("login")


class UserUpdateView(OwnerRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = "users/form.html"
    success_url = reverse_lazy("users_index")
    success_message = _("User updated successfully")
    extra_context: ClassVar[dict] = {"title": _("Edit user"), "button": _("Change")}


class UserDeleteView(OwnerRequiredMixin, SuccessMessageMixin, DeleteView):
    model = User
    template_name = "users/delete.html"
    success_url = reverse_lazy("users_index")
    success_message = _("User deleted successfully")


class UserLoginView(SuccessMessageMixin, LoginView):
    template_name = "users/login.html"
    success_message = _("You are logged in")
    extra_context: ClassVar[dict] = {"title": _("Login"), "button": _("Log in")}


class UserLogoutView(LogoutView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        messages.info(request, _("You are logged out"))
        return response