from rest_framework import serializers

from apps.attendance.models import AttendanceRecord


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

    def validate_photo_url(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Photo URL e obrigatoria.")
        return value.strip()

    def validate_points_granted(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Pontos concedidos nao podem ser negativos."
            )
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        instance = AttendanceRecord(user=user, **attrs)
        if self.instance is not None:
            instance.pk = self.instance.pk
        instance.clean()
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        return AttendanceRecord.objects.create(
            user=request.user,
            is_valid=True,
            points_granted=10,
            **validated_data,
        )
