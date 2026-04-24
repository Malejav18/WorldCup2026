import { api } from "./client";
import type { Score, ScoreSummary } from "../types";

export const scoringApi = {
  mine: async (): Promise<Score[]> => (await api.get<Score[]>("/scoring/me")).data,
  summary: async (): Promise<ScoreSummary> => (await api.get<ScoreSummary>("/scoring/me/summary")).data,
};
