from rest_framework import generics, permissions

from apps.gamification.models import UserProgress
from apps.gamification.serializers import UserProgressSerializer


class UserProgressDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProgressSerializer

    def get_object(self):
        progress, _ = UserProgress.objects.get_or_create(user=self.request.user)
        return progress
