from django.urls import path

from apps.study.views import StudySessionListCreateView


urlpatterns = [
    path("", StudySessionListCreateView.as_view(), name="study-session-list"),
]
