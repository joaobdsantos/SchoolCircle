from rest_framework import serializers

from apps.groups.models import StudyGroup


class StudyGroupSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, allow_blank=False)
    description = serializers.CharField(allow_blank=True)

    class Meta:
        model = StudyGroup
        fields = (
            "id",
            "name",
            "description",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_name(self, value):
        name = value.strip()
        if not name:
            raise serializers.ValidationError("Nome e obrigatorio.")
        return name

    def validate_description(self, value):
        return value.strip()

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError(
                "Informe pelo menos um campo para atualizar."
            )
        return attrs

    def create(self, validated_data):
        return StudyGroup.objects.create(**validated_data)

    def update(self, instance, validated_data):
        name = validated_data.get("name", instance.name)
        description = validated_data.get("description", instance.description)
        instance.update_group(name=name, description=description)
        return instance
