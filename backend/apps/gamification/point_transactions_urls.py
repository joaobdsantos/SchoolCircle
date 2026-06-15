from django.urls import path

from apps.gamification.views import PointTransactionListView


urlpatterns = [
    path("", PointTransactionListView.as_view(), name="point-transaction-list"),
]
