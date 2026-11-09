from django.urls import path

from . import views

urlpatterns = [
    path("labels/", views.LabelListView.as_view(), name="labels_index"),
    path("labels/create/", views.LabelCreateView.as_view(), name="labels_create"),
    path(
        "labels/<int:pk>/update/",
        views.LabelUpdateView.as_view(),
        name="labels_update",
    ),
    path(
        "labels/<int:pk>/delete/",
        views.LabelDeleteView.as_view(),
        name="labels_delete",
    ),
]