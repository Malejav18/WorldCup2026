import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, useEffect } from "react";
import { predictionsApi } from "../api/predictions";
import type { Match, Team } from "../types";
import { AxiosError } from "axios";

export function PredictionRow({ match, teams }: { match: Match; teams: Map<string, Team> }) {
  const qc = useQueryClient();
  const home = match.home_team_id ? teams.get(match.home_team_id) : null;
  const away = match.away_team_id ? teams.get(match.away_team_id) : null;

  const existing = useQuery({
    queryKey: ["predictions", "match", match.id],
    queryFn: () => predictionsApi.mineForMatch(match.id),
    staleTime: 10_000,
  });

  const [homeGoals, setHomeGoals] = useState<number | "">("");
  const [awayGoals, setAwayGoals] = useState<number | "">("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (existing.data) {
      setHomeGoals(existing.data.predicted_home_goals_90);
      setAwayGoals(existing.data.predicted_away_goals_90);
    }
  }, [existing.data]);

  const isFinished = match.status === "FINISHED";
  const isLocked = existing.data?.is_locked || isFinished;
  const canSubmit = !isLocked && typeof homeGoals === "number" && typeof awayGoals === "number";

  const save = async () => {
    if (!canSubmit) return;
    setSaving(true);
    setError(null);
    setSaved(false);
    try {
      await predictionsApi.upsert({
        match_id: match.id,
        predicted_home_goals_90: homeGoals as number,
        predicted_away_goals_90: awayGoals as number,
      });
      setSaved(true);
      qc.invalidateQueries({ queryKey: ["predictions", "match", match.id] });
      qc.invalidateQueries({ queryKey: ["predictions", "mine"] });
    } catch (err) {
      const ax = err as AxiosError<{ detail?: string }>;
      setError(ax.response?.data?.detail ?? "Error al guardar");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="card flex flex-wrap items-center gap-3">
      <div className="flex-1 min-w-[12rem]">
        <div className="text-xs text-slate-500">#{match.match_number} &bull; {match.phase}</div>
        <div className="font-medium">
          {home?.name ?? match.home_team_slot ?? "TBD"} <span className="text-slate-400">vs</span> {away?.name ?? match.away_team_slot ?? "TBD"}
        </div>
        {isFinished && (
          <div className="text-xs text-emerald-700 mt-1">
            Final: {match.home_goals_90} - {match.away_goals_90}
          </div>
        )}
      </div>
      <div className="flex items-center gap-2">
        <input
          type="number"
          min={0}
          max={20}
          className="input w-16 text-center"
          disabled={isLocked}
          value={homeGoals}
          onChange={(e) => setHomeGoals(e.target.value === "" ? "" : Number(e.target.value))}
        />
        <span className="text-slate-400">-</span>
        <input
          type="number"
          min={0}
          max={20}
          className="input w-16 text-center"
          disabled={isLocked}
          value={awayGoals}
          onChange={(e) => setAwayGoals(e.target.value === "" ? "" : Number(e.target.value))}
        />
      </div>
      <button onClick={save} className="btn-primary" disabled={!canSubmit || saving}>
        {saving ? "Guardando..." : existing.data ? "Actualizar" : "Predecir"}
      </button>
      {isLocked && <span className="badge bg-slate-200 text-slate-700">Bloqueada</span>}
      {saved && !error && <span className="text-emerald-600 text-xs">Guardado!</span>}
      {error && <span className="text-red-600 text-xs">{error}</span>}
    </div>
  );
}
