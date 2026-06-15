from rest_framework import serializers

from apps.gamification.models import PointTransaction, UserProgress


class UserProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProgress
        fields = (
            "id",
            "user",
            "current_streak",
            "longest_streak",
            "total_points",
            "last_valid_activity_date",
        )
        read_only_fields = (
            "id",
            "user",
            "current_streak",
            "longest_streak",
            "total_points",
            "last_valid_activity_date",
        )


class PointTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointTransaction
        fields = (
            "id",
            "user",
            "points",
            "reason",
            "created_at",
            "source_type",
            "attendance_record",
            "study_session",
            "study_group",
        )
        read_only_fields = (
            "id",
            "user",
            "points",
            "reason",
            "created_at",
            "source_type",
            "attendance_record",
            "study_session",
            "study_group",
        )
