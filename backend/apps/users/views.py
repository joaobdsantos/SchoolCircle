from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import AcademicProfile
from apps.users.serializers import (
    AcademicProfileSerializer,
    EmailLoginSerializer,
    RegisterSerializer,
)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(RegisterSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = EmailLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
            {
                "access": serializer.validated_data["access"],
                "refresh": serializer.validated_data["refresh"],
            },
            status=status.HTTP_200_OK,
        )


class AcademicProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = AcademicProfile.objects.filter(user=request.user).first()
        if profile is None:
            return Response(None, status=status.HTTP_200_OK)
        return Response(AcademicProfileSerializer(profile).data, status=status.HTTP_200_OK)

    def put(self, request):
        profile = AcademicProfile.objects.filter(user=request.user).first()

        if profile is None:
            serializer = AcademicProfileSerializer(data=request.data)
        else:
            serializer = AcademicProfileSerializer(profile, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
