import { api } from "./api";

export type AttendancePayload = {
  class_date: string;
  period: "MORNING" | "AFTERNOON" | "NIGHT";
  photo_url: File;
  shared_group?: string;
};

export type AttendanceRecord = Omit<AttendancePayload, "photo_url"> & {
  id: string;
  user: string;
  photo_url: string;
  registered_at: string;
  is_valid: boolean;
  points_granted: number;
};

export async function createAttendanceRecord(payload: AttendancePayload): Promise<AttendanceRecord> {
  const formData = new FormData();
  formData.append("class_date", payload.class_date);
  formData.append("period", payload.period);
  formData.append("photo_url", payload.photo_url);

  if (payload.shared_group) {
    formData.append("shared_group", payload.shared_group);
  }

  const response = await api.post<AttendanceRecord>("/attendance-records/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}
