import { api } from "./api";

export type UserProgress = {
  id: string;
  user: string;
  current_streak: number;
  longest_streak: number;
  total_points: number;
  last_valid_activity_date: string | null;
};

export type PointTransaction = {
  id: string;
  user: string;
  points: number;
  reason: string;
  created_at: string;
  source_type: "ATTENDANCE" | "STUDY_SESSION";
  attendance_record: string | null;
  study_session: string | null;
  study_group: string | null;
};

export async function getUserProgress(): Promise<UserProgress> {
  const response = await api.get<UserProgress>("/user-progress/");
  return response.data;
}

export async function listPointTransactions(): Promise<PointTransaction[]> {
  const response = await api.get<PointTransaction[]>("/point-transactions/");
  return response.data;
}