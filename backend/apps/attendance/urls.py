from django.urls import path

from apps.attendance.views import AttendanceRecordListCreateView


urlpatterns = [
    path("", AttendanceRecordListCreateView.as_view(), name="attendance-record-list"),
]
