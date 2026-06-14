from django.urls import path

from apps.groups.views import StudyGroupDetailView, StudyGroupListCreateView


urlpatterns = [
    path("", StudyGroupListCreateView.as_view(), name="study-group-list-create"),
    path(
        "<uuid:group_id>/",
        StudyGroupDetailView.as_view(),
        name="study-group-detail",
    ),
]
