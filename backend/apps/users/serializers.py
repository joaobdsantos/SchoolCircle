from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import AcademicProfile


User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_name(self, value):
        name = value.strip()
        if not name:
            raise serializers.ValidationError("Nome e obrigatorio.")
        return name

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("Ja existe conta com este email.")
        return email

    def create(self, validated_data):
        name = validated_data["name"]
        email = validated_data["email"]
        password = validated_data["password"]

        user = User.objects.create_user(
            username=email,
            first_name=name,
            email=email,
            password=password,
        )
        return user

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "name": instance.first_name,
            "email": instance.email,
        }


class EmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        email = attrs.get("email", "").strip().lower()
        password = attrs.get("password", "")

        if not email or not password:
            raise serializers.ValidationError("Email e senha sao obrigatorios.")

        user = User.objects.filter(email__iexact=email).first()
        if user is None or not user.check_password(password):
            raise serializers.ValidationError("Credenciais invalidas.")

        if not user.is_active:
            raise serializers.ValidationError("Usuario inativo.")

        refresh = RefreshToken.for_user(user)
        attrs["access"] = str(refresh.access_token)
        attrs["refresh"] = str(refresh)
        return attrs


class AcademicProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicProfile
        fields = (
            "education_level",
            "is_independent",
            "institution_name",
            "course_name",
        )

    def validate(self, attrs):
        is_independent = attrs.get("is_independent")
        institution_name = (attrs.get("institution_name") or "").strip()
        course_name = (attrs.get("course_name") or "").strip()

        if is_independent is False:
            errors = {}
            if not institution_name:
                errors["institution_name"] = ["Este campo e obrigatorio para nao independente."]
            if not course_name:
                errors["course_name"] = ["Este campo e obrigatorio para nao independente."]
            if errors:
                raise serializers.ValidationError(errors)

        attrs["institution_name"] = institution_name
        attrs["course_name"] = course_name
        return attrs
