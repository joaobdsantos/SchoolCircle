from django.db import IntegrityError
from rest_framework import serializers

from apps.attendance.models import AttendanceRecord


ATTENDANCE_ALREADY_REGISTERED_MESSAGE = (
    "Presença já registrada para esta data e período."
)


class AttendanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = (
            "id",
            "user",
            "shared_group",
            "class_date",
            "period",
            "photo_url",
            "registered_at",
            "is_valid",
            "points_granted",
        )
        read_only_fields = (
            "id",
            "user",
            "registered_at",
            "is_valid",
            "points_granted",
        )

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        instance = AttendanceRecord(user=user, **attrs)
        if self.instance is not None:
            instance.pk = self.instance.pk
        instance.clean()

        duplicate_query = AttendanceRecord.objects.filter(
            user=user,
            class_date=attrs.get("class_date"),
            period=attrs.get("period"),
        )
        if self.instance is not None:
            duplicate_query = duplicate_query.exclude(pk=self.instance.pk)

        if duplicate_query.exists():
            raise serializers.ValidationError(ATTENDANCE_ALREADY_REGISTERED_MESSAGE)

        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        try:
            return AttendanceRecord.objects.create(
                user=request.user,
                is_valid=True,
                points_granted=10,
                **validated_data,
            )
        except IntegrityError as exc:
            raise serializers.ValidationError(
                ATTENDANCE_ALREADY_REGISTERED_MESSAGE
            ) from exc
