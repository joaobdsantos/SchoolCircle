from django.urls import include, path

from apps.core.views import healthcheck_view


urlpatterns = [
    path("health/", healthcheck_view, name="healthcheck"),
    path("auth/", include("apps.users.urls")),
]
