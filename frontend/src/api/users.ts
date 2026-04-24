import { api } from "./client";
import type { UserProfileSelf } from "../types";

export const usersApi = {
  me: async (): Promise<UserProfileSelf> => {
    const { data } = await api.get<UserProfileSelf>("/users/me");
    return data;
  },
  updateMe: async (patch: Partial<Pick<UserProfileSelf, "display_name" | "avatar_url" | "timezone" | "language">>) => {
    const { data } = await api.put<UserProfileSelf>("/users/me", patch);
    return data;
  },
  stats: async () => {
    const { data } = await api.get("/users/me/stats");
    return data;
  },
};
