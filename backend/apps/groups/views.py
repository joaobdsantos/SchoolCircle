from rest_framework import permissions
from rest_framework import generics

from apps.groups.models import StudyGroup
from apps.groups.serializers import StudyGroupSerializer


class StudyGroupListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = StudyGroup.objects.all().order_by("name")
    serializer_class = StudyGroupSerializer


class StudyGroupDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = StudyGroup.objects.all()
    serializer_class = StudyGroupSerializer
    lookup_field = "id"
    lookup_url_kwarg = "group_id"
