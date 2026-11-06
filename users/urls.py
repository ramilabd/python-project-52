from django.urls import path

from . import views

urlpatterns = [
    path("users/", views.UserListView.as_view(), name="users_index"),
    path("users/create/", views.UserCreateView.as_view(), name="users_create"),
    path("users/<int:pk>/update/", views.UserUpdateView.as_view(), name="users_update"),
    path("users/<int:pk>/delete/", views.UserDeleteView.as_view(), name="users_delete"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
]