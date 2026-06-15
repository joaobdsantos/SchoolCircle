from rest_framework import serializers

from apps.study.models import StudySession


class StudySessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudySession
        fields = (
            "id",
            "user",
            "study_date",
            "content_description",
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

    def validate_content_description(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError(
                "Descricao do estudo e obrigatoria."
            )
        return value.strip()

    def validate_photo_url(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Photo URL e obrigatoria.")
        return value.strip()

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        instance = StudySession(
            user=user,
            study_date=attrs.get("study_date"),
            content_description=attrs.get("content_description"),
            photo_url=attrs.get("photo_url"),
            is_valid=True,
            points_granted=5,
        )
        if self.instance is not None:
            instance.pk = self.instance.pk
        instance.clean()
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        return StudySession.objects.create(
            user=request.user,
            is_valid=True,
            points_granted=5,
            **validated_data,
        )
