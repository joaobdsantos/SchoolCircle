from rest_framework import generics, permissions

from apps.study.models import StudySession
from apps.study.serializers import StudySessionSerializer


class StudySessionListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StudySessionSerializer

    def get_queryset(self):
        return StudySession.objects.filter(user=self.request.user).order_by(
            "-study_date",
            "-registered_at",
        )
