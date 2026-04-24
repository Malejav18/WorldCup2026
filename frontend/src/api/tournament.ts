import { api } from "./client";
import type { GroupStandings, GroupWithTeams, Match, Team, TournamentInfo } from "../types";

export const tournamentApi = {
  info: async (): Promise<TournamentInfo> => (await api.get<TournamentInfo>("/tournament/info")).data,
  teams: async (): Promise<Team[]> => (await api.get<Team[]>("/tournament/teams")).data,
  groups: async (): Promise<GroupWithTeams[]> => (await api.get<GroupWithTeams[]>("/tournament/groups")).data,
  groupStandings: async (groupId: string): Promise<GroupStandings> =>
    (await api.get<GroupStandings>(`/tournament/groups/${groupId}/standings`)).data,
  matches: async (params?: { phase?: string; status?: string; group_id?: string }): Promise<Match[]> =>
    (await api.get<Match[]>("/tournament/matches", { params })).data,
  match: async (id: string): Promise<Match> => (await api.get<Match>(`/tournament/matches/${id}`)).data,
  registerResult: async (matchId: string, body: { home_goals_90: number; away_goals_90: number }) =>
    (await api.post(`/tournament/admin/matches/${matchId}/result`, body)).data,
};
