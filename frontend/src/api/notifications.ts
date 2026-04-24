import { api } from "./client";
import type { Notification } from "../types";

export const notificationsApi = {
  mine: async (): Promise<Notification[]> => (await api.get<Notification[]>("/notifications/me")).data,
  unreadCount: async (): Promise<number> =>
    (await api.get<{ unread: number }>("/notifications/me/unread-count")).data.unread,
  markRead: async (id: number): Promise<Notification> =>
    (await api.put<Notification>(`/notifications/me/${id}/read`)).data,
};
