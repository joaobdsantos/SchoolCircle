from django.db import transaction
from rest_framework import generics, permissions

from apps.gamification.services import PointsService
from apps.gamification.strategies import StudySessionPointsStrategy
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

    def perform_create(self, serializer):
        with transaction.atomic():
            study_session = serializer.save()
            PointsService.grant_points(
                user=self.request.user,
                activity=study_session,
                strategy=StudySessionPointsStrategy(),
            )
