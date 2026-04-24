import { api } from "./client";
import type { GlobalRankingPage, MyPosition } from "../types";

export const rankingsApi = {
  global: async (page = 1, pageSize = 20): Promise<GlobalRankingPage> =>
    (await api.get<GlobalRankingPage>("/rankings/global", { params: { page, page_size: pageSize } })).data,
  me: async (): Promise<MyPosition> => (await api.get<MyPosition>("/rankings/global/me")).data,
};
