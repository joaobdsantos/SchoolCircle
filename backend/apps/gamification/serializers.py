from rest_framework import serializers

from apps.gamification.models import UserProgress


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
