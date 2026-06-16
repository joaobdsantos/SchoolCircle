from django.db import transaction
from rest_framework import generics, permissions

from apps.attendance.models import AttendanceRecord
from apps.attendance.serializers import AttendanceRecordSerializer
from apps.gamification.services import PointsService
from apps.gamification.strategies import AttendancePointsStrategy
from apps.groups.permissions import IsActiveGroupMember


class AttendanceRecordListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsActiveGroupMember]
    serializer_class = AttendanceRecordSerializer

    def get_queryset(self):
        return AttendanceRecord.objects.filter(user=self.request.user).order_by(
            "-class_date",
            "-registered_at",
        )

    def perform_create(self, serializer):
        with transaction.atomic():
            attendance_record = serializer.save()
            PointsService.grant_points(
                user=self.request.user,
                activity=attendance_record,
                strategy=AttendancePointsStrategy(),
            )
