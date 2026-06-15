from rest_framework import generics, permissions

from apps.gamification.models import PointTransaction, UserProgress
from apps.gamification.serializers import (
    PointTransactionSerializer,
    UserProgressSerializer,
)


class UserProgressDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProgressSerializer

    def get_object(self):
        progress, _ = UserProgress.objects.get_or_create(user=self.request.user)
        return progress


class PointTransactionListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PointTransactionSerializer

    def get_queryset(self):
        return PointTransaction.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )
