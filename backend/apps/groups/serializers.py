from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.groups.models import GroupInvite, GroupMembership, StudyGroup


User = get_user_model()


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


class GroupMembershipSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)
    rank = serializers.IntegerField(read_only=True, allow_null=True)

    class Meta:
        model = GroupMembership
        fields = (
            "id",
            "user",
            "user_name",
            "group",
            "group_name",
            "role",
            "joined_at",
            "group_points",
            "is_active",
            "rank",
        )
        read_only_fields = ("id", "joined_at", "rank")


class GroupInviteSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source="group.name", read_only=True)
    sent_by_name = serializers.CharField(source="sent_by.full_name", read_only=True)
    sent_to_name = serializers.CharField(source="sent_to.full_name", read_only=True)
    sent_to = serializers.PrimaryKeyRelatedField(read_only=True)
    sent_to_email = serializers.EmailField(write_only=True, required=False)

    class Meta:
        model = GroupInvite
        fields = (
            "id",
            "group",
            "group_name",
            "sent_by",
            "sent_by_name",
            "sent_to",
            "sent_to_name",
            "sent_to_email",
            "status",
            "sent_at",
            "responded_at",
        )
        read_only_fields = ("id", "sent_by", "status", "sent_at", "responded_at")

    def validate(self, attrs):
        sent_to_email = attrs.pop("sent_to_email", None)

        if sent_to_email and "sent_to" not in attrs:
            email = sent_to_email.strip().lower()
            try:
                attrs["sent_to"] = User.objects.get(email__iexact=email)
            except User.DoesNotExist as exc:
                raise serializers.ValidationError(
                    {"sent_to_email": "Usuario com este email nao foi encontrado."}
                ) from exc

        if "sent_to" not in attrs and self.instance is None:
            raise serializers.ValidationError(
                {"sent_to_email": "Informe o email do destinatario."}
            )

        values = {}
        for field in ("group", "sent_by", "sent_to", "status", "responded_at"):
            if field in attrs:
                values[field] = attrs[field]
            elif self.instance is not None:
                values[field] = getattr(self.instance, field)

        instance = GroupInvite(**values)
        if self.instance is not None:
            instance.pk = self.instance.pk
        instance.clean()
        return attrs


class GroupRankingSerializer(serializers.ModelSerializer):
    rank = serializers.SerializerMethodField()
    user_id = serializers.UUIDField(source="user.id", read_only=True)
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    current_streak = serializers.SerializerMethodField()

    class Meta:
        model = GroupMembership
        fields = (
            "rank",
            "user_id",
            "user_name",
            "group_points",
            "current_streak",
            "role",
        )

    def get_rank(self, obj):
        return getattr(obj, "calculated_rank", obj.rank)

    def get_current_streak(self, obj):
        progress = getattr(obj.user, "progress", None)
        if progress is None:
            return 0
        return progress.current_streak
