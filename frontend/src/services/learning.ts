import { api, multipartHeaders } from "./api";

export type AttendanceRecord = {
  id: string;
  user: string;
  shared_group: string | null;
  class_date: string;
  period: "MORNING" | "AFTERNOON" | "NIGHT";
  photo_url: string;
  registered_at: string;
  is_valid: boolean;
  points_granted: number;
};

export type StudySession = {
  id: string;
  user: string;
  study_date: string;
  content_description: string;
  photo_url: string;
  registered_at: string;
  is_valid: boolean;
  points_granted: number;
};

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

export async function listAttendanceRecords(): Promise<AttendanceRecord[]> {
  const response = await api.get<AttendanceRecord[]>('/attendance-records/');
  return response.data;
}

export async function createAttendanceRecord(formData: FormData): Promise<AttendanceRecord> {
  const response = await api.post<AttendanceRecord>('/attendance-records/', formData, {
    headers: multipartHeaders,
  });
  return response.data;
}

export async function listStudySessions(): Promise<StudySession[]> {
  const response = await api.get<StudySession[]>('/study-sessions/');
  return response.data;
}

export async function createStudySession(formData: FormData): Promise<StudySession> {
  const response = await api.post<StudySession>('/study-sessions/', formData, {
    headers: multipartHeaders,
  });
  return response.data;
}

export async function getUserProgress(): Promise<UserProgress> {
  const response = await api.get<UserProgress>('/user-progress/');
  return response.data;
}

export async function getPointTransactions(): Promise<PointTransaction[]> {
  const response = await api.get<PointTransaction[]>('/point-transactions/');
  return response.data;
}