from django.urls import path

from . import views

urlpatterns = [
    path("tasks/", views.TaskListView.as_view(), name="tasks_index"),
    path("tasks/create/", views.TaskCreateView.as_view(), name="tasks_create"),
    path("tasks/<int:pk>/", views.TaskDetailView.as_view(), name="tasks_detail"),
    path("tasks/<int:pk>/update/", views.TaskUpdateView.as_view(), name="tasks_update"),
    path("tasks/<int:pk>/delete/", views.TaskDeleteView.as_view(), name="tasks_delete"),
]