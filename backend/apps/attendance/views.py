from rest_framework import generics, permissions

from apps.attendance.models import AttendanceRecord
from apps.attendance.serializers import AttendanceRecordSerializer


class AttendanceRecordListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AttendanceRecordSerializer

    def get_queryset(self):
        return AttendanceRecord.objects.filter(user=self.request.user).order_by(
            "-class_date",
            "-registered_at",
        )
