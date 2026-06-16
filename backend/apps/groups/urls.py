from django.urls import path

from apps.groups.views import (
    GroupInviteAcceptView,
    GroupInviteCancelView,
    GroupInviteDeclineView,
    GroupInviteDetailView,
    GroupInviteListCreateView,
    GroupMembershipDetailView,
    GroupMembershipLeaveView,
    GroupMembershipListView,
    GroupRankingView,
    StudyGroupDetailView,
    StudyGroupListCreateView,
)


urlpatterns = [
    path("", StudyGroupListCreateView.as_view(), name="study-group-list-create"),
    path(
        "invites/", GroupInviteListCreateView.as_view(), name="group-invite-list-create"
    ),
    path(
        "invites/<uuid:invite_id>/",
        GroupInviteDetailView.as_view(),
        name="group-invite-detail",
    ),
    path(
        "invites/<uuid:invite_id>/accept/",
        GroupInviteAcceptView.as_view(),
        name="group-invite-accept",
    ),
    path(
        "invites/<uuid:invite_id>/decline/",
        GroupInviteDeclineView.as_view(),
        name="group-invite-decline",
    ),
    path(
        "invites/<uuid:invite_id>/cancel/",
        GroupInviteCancelView.as_view(),
        name="group-invite-cancel",
    ),
    path(
        "<uuid:group_id>/",
        StudyGroupDetailView.as_view(),
        name="study-group-detail",
    ),
    path(
        "<uuid:group_id>/members/",
        GroupMembershipListView.as_view(),
        name="group-membership-list",
    ),
    path(
        "<uuid:group_id>/members/<uuid:membership_id>/",
        GroupMembershipDetailView.as_view(),
        name="group-membership-detail",
    ),
    path(
        "<uuid:group_id>/members/<uuid:membership_id>/leave/",
        GroupMembershipLeaveView.as_view(),
        name="group-membership-leave",
    ),
    path(
        "<uuid:group_id>/ranking/",
        GroupRankingView.as_view(),
        name="group-ranking",
    ),
]
