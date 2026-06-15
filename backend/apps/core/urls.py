from django.urls import include, path

from apps.core.views import healthcheck_view
from apps.users.views import AcademicProfileView


urlpatterns = [
    path("health/", healthcheck_view, name="healthcheck"),
    path("auth/", include("apps.users.urls")),
    path("academic-profile/", AcademicProfileView.as_view(), name="academic-profile"),
    path("groups/", include("apps.groups.urls")),
    path("attendance-records/", include("apps.attendance.urls")),
    path("study-sessions/", include("apps.study.urls")),
    path("user-progress/", include("apps.gamification.urls")),
]
