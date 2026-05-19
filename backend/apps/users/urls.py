from django.urls import path

from apps.users.views import LoginView, RegisterView, UpdateUserView


urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("profile/", UpdateUserView.as_view(), name="update-user"),
]
