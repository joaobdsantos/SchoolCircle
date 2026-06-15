from django.urls import path

from apps.gamification.views import UserProgressDetailView


urlpatterns = [
    path("", UserProgressDetailView.as_view(), name="user-progress"),
]
