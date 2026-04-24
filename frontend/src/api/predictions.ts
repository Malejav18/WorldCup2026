import { api } from "./client";
import type { Prediction, SpecialPrediction } from "../types";

export const predictionsApi = {
  upsert: async (body: {
    match_id: string;
    predicted_home_goals_90: number;
    predicted_away_goals_90: number;
    predicted_winner_id?: string | null;
    predicted_goes_to_penalties?: boolean;
  }): Promise<Prediction> => (await api.post<Prediction>("/predictions", body)).data,

  mine: async (): Promise<Prediction[]> => (await api.get<Prediction[]>("/predictions/me")).data,
  mineForMatch: async (matchId: string): Promise<Prediction | null> => {
    try {
      const { data } = await api.get<Prediction>(`/predictions/me/match/${matchId}`);
      return data;
    } catch {
      return null;
    }
  },

  specialUpsert: async (type: "CHAMPION" | "RUNNER_UP" | "THIRD_PLACE", teamId: string) =>
    (await api.post<SpecialPrediction>("/predictions/special", { prediction_type: type, team_id: teamId })).data,
  specialMine: async (): Promise<SpecialPrediction[]> =>
    (await api.get<SpecialPrediction[]>("/predictions/special/me")).data,
};
