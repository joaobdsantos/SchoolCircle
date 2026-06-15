from django.db import transaction
from rest_framework import generics, permissions

from apps.groups.models import GroupMembership, StudyGroup
from apps.groups.serializers import StudyGroupSerializer


class StudyGroupListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = StudyGroup.objects.all().order_by("name")
    serializer_class = StudyGroupSerializer

    def perform_create(self, serializer):
        with transaction.atomic():
            group = serializer.save()
            GroupMembership.objects.create(
                user=self.request.user,
                group=group,
                role=GroupMembership.MembershipRole.OWNER,
            )


class StudyGroupDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = StudyGroup.objects.all()
    serializer_class = StudyGroupSerializer
    lookup_field = "id"
    lookup_url_kwarg = "group_id"
