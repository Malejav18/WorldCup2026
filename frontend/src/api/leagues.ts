import { api } from "./client";
import type { League, LeagueDetail, LeagueMembers, LeagueRanking } from "../types";

export const leaguesApi = {
  create: async (name: string, description?: string): Promise<League> =>
    (await api.post<League>("/leagues", { name, description })).data,
  mine: async (): Promise<League[]> => (await api.get<League[]>("/leagues/me")).data,
  detail: async (id: string): Promise<LeagueDetail> =>
    (await api.get<LeagueDetail>(`/leagues/${id}`)).data,
  members: async (id: string): Promise<LeagueMembers> =>
    (await api.get<LeagueMembers>(`/leagues/${id}/members`)).data,
  ranking: async (id: string): Promise<LeagueRanking> =>
    (await api.get<LeagueRanking>(`/leagues/${id}/ranking`)).data,
  joinByCode: async (inviteCode: string): Promise<League> =>
    (await api.post<League>("/leagues/join", { invite_code: inviteCode })).data,
  leave: async (id: string): Promise<void> => {
    await api.delete(`/leagues/${id}/leave`);
  },
  getInviteCode: async (id: string): Promise<{ invite_code: string }> =>
    (await api.get<{ league_id: string; invite_code: string }>(`/leagues/${id}/invite-code`)).data,
  regenerateInviteCode: async (id: string): Promise<{ invite_code: string }> =>
    (await api.post<{ league_id: string; invite_code: string }>(`/leagues/${id}/invite-code/regenerate`)).data,
};
