from django.urls import path

from . import views

urlpatterns = [
    path("statuses/", views.StatusListView.as_view(), name="statuses_index"),
    path(
        "statuses/create/",
        views.StatusCreateView.as_view(),
        name="statuses_create",
    ),
    path(
        "statuses/<int:pk>/update/",
        views.StatusUpdateView.as_view(),
        name="statuses_update",
    ),
    path(
        "statuses/<int:pk>/delete/",
        views.StatusDeleteView.as_view(),
        name="statuses_delete",
    ),
]