import { api } from "./api";

export type StudyGroup = {
  id: string;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
};

export type StudyGroupPayload = {
  name: string;
  description: string;
};

export type GroupMembership = {
  id: string;
  user: string;
  user_name: string;
  group: string;
  group_name: string;
  role: "OWNER" | "MEMBER";
  joined_at: string;
  group_points: number;
  is_active: boolean;
  rank: number | null;
  current_streak?: number;
};

export type GroupInvite = {
  id: string;
  group: string;
  group_name: string;
  sent_by: string;
  sent_by_name: string;
  sent_to: string;
  sent_to_name: string;
  status: "PENDING" | "ACCEPTED" | "DECLINED" | "CANCELED";
  sent_at: string;
  responded_at: string | null;
};

export type GroupRankingRow = {
  rank: number;
  user_id: string;
  user_name: string;
  group_points: number;
  current_streak: number;
  role: "OWNER" | "MEMBER";
};

export async function listGroups(): Promise<StudyGroup[]> {
  const response = await api.get<StudyGroup[]>("/groups/");
  return response.data;
}

export async function createGroup(payload: StudyGroupPayload): Promise<StudyGroup> {
  const response = await api.post<StudyGroup>("/groups/", payload);
  return response.data;
}

export async function listGroupMembers(groupId: string): Promise<GroupMembership[]> {
  const response = await api.get<GroupMembership[]>(`/groups/${groupId}/members/`);
  return response.data;
}

export async function leaveGroupMember(groupId: string, membershipId: string): Promise<void> {
  await api.delete(`/groups/${groupId}/members/${membershipId}/leave/`);
}

export async function listGroupRanking(groupId: string): Promise<GroupRankingRow[]> {
  const response = await api.get<GroupRankingRow[]>(`/groups/${groupId}/ranking/`);
  return response.data;
}

export async function listInvites(): Promise<GroupInvite[]> {
  const response = await api.get<GroupInvite[]>("/groups/invites/");
  return response.data;
}

export async function createInvite(payload: { group: string; sent_to_email: string }): Promise<GroupInvite> {
  const response = await api.post<GroupInvite>("/groups/invites/", payload);
  return response.data;
}

export async function acceptInvite(inviteId: string): Promise<GroupInvite> {
  const response = await api.post<GroupInvite>(`/groups/invites/${inviteId}/accept/`);
  return response.data;
}

export async function declineInvite(inviteId: string): Promise<GroupInvite> {
  const response = await api.post<GroupInvite>(`/groups/invites/${inviteId}/decline/`);
  return response.data;
}

export async function cancelInvite(inviteId: string): Promise<GroupInvite> {
  const response = await api.post<GroupInvite>(`/groups/invites/${inviteId}/cancel/`);
  return response.data;
}