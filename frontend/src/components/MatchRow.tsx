import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, useEffect } from "react";
import { tournamentApi } from "../api/tournament";
import type { Match, Team } from "../types";
import { AxiosError } from "axios";

const R32_ALLOWED_GROUPS: Record<number, { home: string[]; away: string[] }> = {
  73: { home: ['A'], away: ['C', 'D', 'E'] },
  74: { home: ['A'], away: ['C'] },
  75: { home: ['B'], away: ['E', 'F', 'A'] },
  76: { home: ['B'], away: ['D'] },
  77: { home: ['C'], away: ['A', 'B', 'F'] },
  78: { home: ['C'], away: ['A'] },
  79: { home: ['D'], away: ['B', 'C', 'E'] },
  80: { home: ['D'], away: ['B'] },
  81: { home: ['E'], away: ['A', 'D', 'F'] },
  82: { home: ['E'], away: ['F'] },
  83: { home: ['F'], away: ['B', 'C', 'D'] },
  84: { home: ['F'], away: ['E'] },
  // Para otros partidos, permitir todos
};

export function MatchRow({ match, teams, groups }: { match: Match; teams: Map<string, Team>; groups: Map<string, { id: string; letter: string; name: string }>; }) {
  const qc = useQueryClient();
  const home = match.home_team_id ? teams.get(match.home_team_id) : null;
  const away = match.away_team_id ? teams.get(match.away_team_id) : null;
  const allTeams = Array.from(teams.values());

  const allowed = R32_ALLOWED_GROUPS[match.match_number];
  const allowedHomeGroups = allowed?.home || ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L'];
  const allowedAwayGroups = allowed?.away || ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L'];

  const homeTeams = allTeams.filter(t => t.group_id && allowedHomeGroups.includes(groups.get(t.group_id)?.letter || ''));
  const awayTeams = allTeams.filter(t => t.group_id && allowedAwayGroups.includes(groups.get(t.group_id)?.letter || ''));

  const [homeGoals90, setHomeGoals90] = useState<number | "">("");
  const [awayGoals90, setAwayGoals90] = useState<number | "">("");
  const [selectedWinnerId, setSelectedWinnerId] = useState<string>("");
  const [selectedHomeTeamId, setSelectedHomeTeamId] = useState<string | "">("");
  const [selectedAwayTeamId, setSelectedAwayTeamId] = useState<string | "">("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (match.home_goals_90 !== null) {
      setHomeGoals90(match.home_goals_90);
    }
    if (match.away_goals_90 !== null) {
      setAwayGoals90(match.away_goals_90);
    }
    if (match.winner_id) {
      setSelectedWinnerId(match.winner_id);
    }
    if (match.home_team_id) {
      setSelectedHomeTeamId(match.home_team_id);
    }
    if (match.away_team_id) {
      setSelectedAwayTeamId(match.away_team_id);
    }
  }, [match]);

  const isKnockout = ["R32", "R16", "QF", "SF", "THIRD_PLACE", "FINAL"].includes(match.phase);
  const needsHomeTeamSelection = match.phase === "R32" && !match.home_team_id;
  const needsAwayTeamSelection = match.phase === "R32" && !match.away_team_id;

  const canSubmit = typeof homeGoals90 === "number" && typeof awayGoals90 === "number" &&
    (!needsHomeTeamSelection || selectedHomeTeamId) &&
    (!needsAwayTeamSelection || selectedAwayTeamId) &&
    (!isKnockout || selectedWinnerId);

  const save = async () => {
    if (!canSubmit) return;
    setSaving(true);
    setError(null);
    setSaved(false);
    try {
      const payload: any = {
        home_goals_90: homeGoals90,
        away_goals_90: awayGoals90,
      };

      if (needsHomeTeamSelection && selectedHomeTeamId) payload.home_team_id = selectedHomeTeamId;
      if (needsAwayTeamSelection && selectedAwayTeamId) payload.away_team_id = selectedAwayTeamId;

      if (isKnockout && selectedWinnerId) {
        payload.winner_id = selectedWinnerId;
      }

      const updateExisting = match.home_goals_90 !== null || match.away_goals_90 !== null;
      await (updateExisting
        ? tournamentApi.updateResult(match.id, payload)
        : tournamentApi.registerResult(match.id, payload)
      );
      setSaved(true);
      qc.invalidateQueries({ queryKey: ["tournament", "matches"] });
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
        <div className="text-xs text-slate-500">
          #{match.match_number} &bull; {match.phase}
        </div>
        <div className="font-medium">
          {needsHomeTeamSelection ? (
            <select
              value={selectedHomeTeamId}
              onChange={(e) => setSelectedHomeTeamId(e.target.value)}
              className="input mr-2"
            >
              <option value="">Seleccionar equipo</option>
              {homeTeams.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
          ) : (
            teams.get(selectedHomeTeamId || match.home_team_id || "")?.name ?? home?.name ?? match.home_team_slot ?? "TBD"
          )}
          <span className="text-slate-400">vs</span>
          {needsAwayTeamSelection ? (
            <select
              value={selectedAwayTeamId}
              onChange={(e) => setSelectedAwayTeamId(e.target.value)}
              className="input ml-2"
            >
              <option value="">Seleccionar equipo</option>
              {awayTeams.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
          ) : (
            teams.get(selectedAwayTeamId || match.away_team_id || "")?.name ?? away?.name ?? match.away_team_slot ?? "TBD"
          )}
        </div>
        {match.status === "FINISHED" && (
          <div className="text-xs text-emerald-700 mt-1">
            Actual: {match.home_goals_90} - {match.away_goals_90}
            {match.went_to_extra_time && match.home_goals_final !== null && match.away_goals_final !== null && (
              <> (ET: {match.home_goals_final} - {match.away_goals_final})</>
            )}
            {match.went_to_penalties && (
              <> (Pen: {match.winner_id === match.home_team_id ? "Local" : "Visitante"})</>
            )}
          </div>
        )}
      </div>
      <div className="flex items-center gap-2">
        <input
          type="number"
          min={0}
          max={20}
          className="input w-16 text-center"
          value={homeGoals90}
          onChange={(e) => setHomeGoals90(e.target.value === "" ? "" : Number(e.target.value))}
        />
        <span className="text-slate-400">-</span>
        <input
          type="number"
          min={0}
          max={20}
          className="input w-16 text-center"
          value={awayGoals90}
          onChange={(e) => setAwayGoals90(e.target.value === "" ? "" : Number(e.target.value))}
        />
      </div>
      {isKnockout && (
        <div className="flex flex-col gap-1">
          <label className="text-xs text-slate-500">Ganador:</label>
          <select
            value={selectedWinnerId}
            onChange={(e) => setSelectedWinnerId(e.target.value)}
            className="input w-full"
          >
            <option value="">Seleccionar ganador</option>
            {(selectedHomeTeamId || match.home_team_id) && (
              <option value={selectedHomeTeamId || match.home_team_id || ""}>
                {teams.get(selectedHomeTeamId || match.home_team_id || "")?.name}
              </option>
            )}
            {(selectedAwayTeamId || match.away_team_id) && (
              <option value={selectedAwayTeamId || match.away_team_id || ""}>
                {teams.get(selectedAwayTeamId || match.away_team_id || "")?.name}
              </option>
            )}
          </select>
        </div>
      )}
      <button onClick={save} className="btn-primary" disabled={!canSubmit || saving}>
        {saving ? "Guardando..." : "Registrar Resultado"}
      </button>
      {saved && !error && <span className="text-emerald-600 text-xs">Guardado!</span>}
      {error && <span className="text-red-600 text-xs">{error}</span>}
    </div>
  );
}