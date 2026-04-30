import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, useEffect, useMemo } from "react";
import { predictionsApi } from "../api/predictions";
import type { Match, Team, Prediction } from "../types";
import { AxiosError } from "axios";

const R32_ALLOWED_GROUPS: Record<number, { home: string[]; away: string[] }> = {
  73: { home: ['A'], away: ['B'] },
  74: { home: ['E'], away: ['A', 'B', 'C', 'D', 'F'] },
  75: { home: ['F'], away: ['C'] },
  76: { home: ['C'], away: ['F'] },
  77: { home: ['I'], away: ['C', 'D', 'F', 'G', 'H'] },
  78: { home: ['E'], away: ['I'] },
  79: { home: ['A'], away: ['C', 'E', 'F', 'H', 'I'] },
  80: { home: ['L'], away: ['E', 'H', 'I', 'J', 'K'] },
  81: { home: ['D'], away: ['B', 'E', 'F', 'I', 'J'] },
  82: { home: ['G'], away: ['A','E','H','I','J'] },
  83: { home: ['K'], away: ['L'] },
  84: { home: ['H'], away: ['J'] },
  85: { home: ['B'], away: ['E', 'F', 'G','I', 'J'] },
  86: { home: ['J'], away: ['H'] },
  87: { home: ['K'], away: ['D','E','I', 'J','L'] },
  88: { home: ['D'], away: ['G'] },
  // Para otros partidos, permitir todos
};

type KnockoutSource = "winner" | "loser";

const KNOCKOUT_DEPENDENCIES: Record<number, { homeMatch: number; awayMatch: number; homeSource?: KnockoutSource; awaySource?: KnockoutSource }> = {
  89: { homeMatch: 74, awayMatch: 77 },
  90: { homeMatch: 73, awayMatch: 75 },
  91: { homeMatch: 76, awayMatch: 78 },
  92: { homeMatch: 79, awayMatch: 80 },
  93: { homeMatch: 83, awayMatch: 84 },
  94: { homeMatch: 81, awayMatch: 82 },
  95: { homeMatch: 86, awayMatch: 88 },
  96: { homeMatch: 85, awayMatch: 87 },
  97: { homeMatch: 89, awayMatch: 90 },
  98: { homeMatch: 93, awayMatch: 94 },
  99: { homeMatch: 91, awayMatch: 92 },
  100: { homeMatch: 95, awayMatch: 96 },
  101: { homeMatch: 97, awayMatch: 98 },
  102: { homeMatch: 99, awayMatch: 100 },
  103: { homeMatch: 101, awayMatch: 102, homeSource: "loser", awaySource: "loser" },
  104: { homeMatch: 101, awayMatch: 102 },
};

const R32_POSITION_LABELS: Record<number, string> = {
  73: '2° Grupo A vs 2° Grupo B',
  74: '2° Grupo E vs 3° (mejor de A/B/C/D/F)',
  75: '1° Grupo F vs 2° Grupo C',
  76: '2° Grupo C vs 2° Grupo F',
  77: '1° Grupo I vs 3° (mejor de C/D/F/G/H)',
  78: '2° Grupo E vs 2° Grupo I',
  79: '1° Grupo A vs 3° (mejor de C/E/F/H/I)',
  80: '2° Grupo L vs 3° (mejor de E/H/I/J/K)',
  81: '1° Grupo D vs 3° (mejor de B/E/F/I/J)',
  82: '2° Grupo G vs 3° (mejor de A/E/H/I/J)',
  83: '1° Grupo K vs 2° Grupo L',
  84: '2° Grupo H vs 2° Grupo J',
  85: '2° Grupo B vs 3° (mejor de E/F/G/I/J)',
  86: '2° Grupo J vs 2° Grupo H',
  87: '2° Grupo K vs 3° (mejor de D/E/I/J/L)',
  88: '2° Grupo D vs 2° Grupo G',
};

const getLoserTeamId = (prediction: Prediction | null): string | null => {
  if (!prediction) return null;
  const homeId = prediction.predicted_home_team_id;
  const awayId = prediction.predicted_away_team_id;
  const winnerId = prediction.predicted_winner_id;
  if (!homeId || !awayId || !winnerId) return null;
  if (winnerId === homeId) return awayId;
  if (winnerId === awayId) return homeId;
  return null;
};

export function PredictionRow({ match, teams, groups, matchNumberToId, existingPrediction, r32UsedTeamIds, onR32SelectionChange, blockedGroups }: { match: Match; teams: Map<string, Team>; groups: Map<string, { id: string; letter: string; name: string }>; matchNumberToId: Map<number, string>; existingPrediction?: Prediction | null; r32UsedTeamIds: Set<string>; onR32SelectionChange: (matchId: string, selection: { homeTeamId: string; awayTeamId: string }) => void; blockedGroups?: Set<string>; }) {
  const qc = useQueryClient();
  const home = match.home_team_id ? teams.get(match.home_team_id) : null;
  const away = match.away_team_id ? teams.get(match.away_team_id) : null;
  const allTeams = Array.from(teams.values());

  const dep = KNOCKOUT_DEPENDENCIES[match.match_number];
  const homeDepMatchId = dep ? matchNumberToId.get(dep.homeMatch) : null;
  const awayDepMatchId = dep ? matchNumberToId.get(dep.awayMatch) : null;

  const homeDepPrediction = useQuery({
    queryKey: ["predictions", "match", homeDepMatchId],
    queryFn: () => homeDepMatchId ? predictionsApi.mineForMatch(homeDepMatchId) : Promise.resolve(null),
    enabled: !!homeDepMatchId,
    staleTime: 10_000,
  });

  const awayDepPrediction = useQuery({
    queryKey: ["predictions", "match", awayDepMatchId],
    queryFn: () => awayDepMatchId ? predictionsApi.mineForMatch(awayDepMatchId) : Promise.resolve(null),
    enabled: !!awayDepMatchId,
    staleTime: 10_000,
  });

  const homeDepTeamId = dep
    ? (dep.homeSource === "loser" ? getLoserTeamId(homeDepPrediction.data ?? null) : homeDepPrediction.data?.predicted_winner_id ?? null)
    : null;
  const awayDepTeamId = dep
    ? (dep.awaySource === "loser" ? getLoserTeamId(awayDepPrediction.data ?? null) : awayDepPrediction.data?.predicted_winner_id ?? null)
    : null;

  const allowed = R32_ALLOWED_GROUPS[match.match_number];
  const allowedHomeGroups = allowed?.home || ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L'];
  const allowedAwayGroups = allowed?.away || ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L'];

  const homeTeams = allTeams.filter(t => t.group_id && allowedHomeGroups.includes(groups.get(t.group_id)?.letter || ''));
  const awayTeams = allTeams.filter(t => t.group_id && allowedAwayGroups.includes(groups.get(t.group_id)?.letter || ''));

  const [homeGoals, setHomeGoals] = useState<number | "">("");
  const [awayGoals, setAwayGoals] = useState<number | "">("");
  const [selectedHomeTeamId, setSelectedHomeTeamId] = useState<string | "">("");
  const [selectedAwayTeamId, setSelectedAwayTeamId] = useState<string | "">("");
  const [selectedWinnerId, setSelectedWinnerId] = useState<string>("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (existingPrediction) {
      setHomeGoals(existingPrediction.predicted_home_goals_90);
      setAwayGoals(existingPrediction.predicted_away_goals_90);
      setSelectedHomeTeamId(existingPrediction.predicted_home_team_id || "");
      setSelectedAwayTeamId(existingPrediction.predicted_away_team_id || "");
      setSelectedWinnerId(existingPrediction.predicted_winner_id || "");
    }
  }, [existingPrediction]);

  useEffect(() => {
    if (match.phase === "R32") {
      onR32SelectionChange(match.id, {
        homeTeamId: selectedHomeTeamId,
        awayTeamId: selectedAwayTeamId,
      });
    }
  }, [match.id, match.phase, onR32SelectionChange, selectedHomeTeamId, selectedAwayTeamId]);

  const duplicateR32TeamIds = useMemo(() => {
    const blocked = new Set<string>(r32UsedTeamIds);
    if (selectedHomeTeamId) blocked.delete(selectedHomeTeamId);
    if (selectedAwayTeamId) blocked.delete(selectedAwayTeamId);
    if (existingPrediction?.predicted_home_team_id) blocked.delete(existingPrediction.predicted_home_team_id);
    if (existingPrediction?.predicted_away_team_id) blocked.delete(existingPrediction.predicted_away_team_id);
    return blocked;
  }, [r32UsedTeamIds, selectedHomeTeamId, selectedAwayTeamId, existingPrediction]);

  const isHomeTeamOptionDisabled = (teamId: string) => {
    const team = teams.get(teamId);
    const groupLetter = team && team.group_id ? groups.get(team.group_id)?.letter : '';
    const isGroupBlocked = blockedGroups && allowedHomeGroups.length > 1 && groupLetter && blockedGroups.has(groupLetter);
    return duplicateR32TeamIds.has(teamId) || teamId === selectedAwayTeamId || isGroupBlocked;
  };
  const isAwayTeamOptionDisabled = (teamId: string) => {
    const team = teams.get(teamId);
    const groupLetter = team && team.group_id ? groups.get(team.group_id)?.letter : '';
    const isGroupBlocked = blockedGroups && allowedAwayGroups.length > 1 && groupLetter && blockedGroups.has(groupLetter);
    return duplicateR32TeamIds.has(teamId) || teamId === selectedHomeTeamId || isGroupBlocked;
  };

  const isFinished = match.status === "FINISHED";
  const isLocked = existingPrediction?.is_locked || isFinished;
  const needsHomeTeamSelection = match.phase === "R32" && !match.home_team_id;
  const needsAwayTeamSelection = match.phase === "R32" && !match.away_team_id;
  const isKnockout = ["R32", "R16", "QF", "SF", "THIRD_PLACE", "FINAL"].includes(match.phase);
  const needsDepTeams = !!dep;

  const predictedHomeTeamId = existingPrediction?.predicted_home_team_id || homeDepTeamId || match.home_team_id;
  const predictedAwayTeamId = existingPrediction?.predicted_away_team_id || awayDepTeamId || match.away_team_id;

  const canSubmit = !isLocked && typeof homeGoals === "number" && typeof awayGoals === "number" &&
    (!needsHomeTeamSelection || selectedHomeTeamId) &&
    (!needsAwayTeamSelection || selectedAwayTeamId) &&
    (!isKnockout || selectedWinnerId) &&
    (!needsDepTeams || (predictedHomeTeamId && predictedAwayTeamId));

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
        predicted_home_team_id: needsHomeTeamSelection ? selectedHomeTeamId || null : (needsDepTeams ? predictedHomeTeamId || null : null),
        predicted_away_team_id: needsAwayTeamSelection ? selectedAwayTeamId || null : (needsDepTeams ? predictedAwayTeamId || null : null),
        predicted_winner_id: selectedWinnerId || null,
        predicted_goes_to_penalties: isKnockout && homeGoals === awayGoals,
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
        <div className="text-xs text-slate-500">
          #{match.match_number} &bull; {match.phase}
          {match.phase === 'R32' && R32_POSITION_LABELS[match.match_number] ? `: ${R32_POSITION_LABELS[match.match_number]}` : ''}
        </div>
        <div className="font-medium">
          {needsHomeTeamSelection ? (
            <select
              value={selectedHomeTeamId}
              onChange={(e) => setSelectedHomeTeamId(e.target.value)}
              className="input mr-2"
              disabled={isLocked}
            >
              <option value="">Seleccionar equipo</option>
              {homeTeams.map((t) => {
                const isDisabled: boolean = isHomeTeamOptionDisabled(t.id);
                const team = teams.get(t.id);
                const groupLetter = team && team.group_id ? groups.get(team.group_id)?.letter : '';
                const isGroupBlocked = blockedGroups && allowedHomeGroups.length > 1 && groupLetter && blockedGroups.has(groupLetter);
                const reason = duplicateR32TeamIds.has(t.id) ? " (Seleccionado en otro partido)" : isGroupBlocked ? " (Grupo bloqueado)" : "";
                return (
                  <option key={t.id} value={t.id} disabled={isDisabled}>
                    {t.name}{reason}
                  </option>
                );
              })}
            </select>
          ) : (
            teams.get(predictedHomeTeamId || "")?.name ?? home?.name ?? match.home_team_slot ?? "TBD"
          )}
          <span className="text-slate-400">vs</span>
          {needsAwayTeamSelection ? (
            <select
              value={selectedAwayTeamId}
              onChange={(e) => setSelectedAwayTeamId(e.target.value)}
              className="input ml-2"
              disabled={isLocked}
            >
              <option value="">Seleccionar equipo</option>
              {awayTeams.map((t) => {
                const isDisabled: boolean = isAwayTeamOptionDisabled(t.id);
                const team = teams.get(t.id);
                const groupLetter = team && team.group_id ? groups.get(team.group_id)?.letter : '';
                const isGroupBlocked = blockedGroups && allowedAwayGroups.length > 1 && groupLetter && blockedGroups.has(groupLetter);
                const reason = duplicateR32TeamIds.has(t.id) ? " (Seleccionado en otro partido)" : isGroupBlocked ? " (Grupo bloqueado)" : "";
                return (
                  <option key={t.id} value={t.id} disabled={isDisabled}>
                    {t.name}{reason}
                  </option>
                );
              })}
            </select>
          ) : (
            teams.get(predictedAwayTeamId || "")?.name ?? away?.name ?? match.away_team_slot ?? "TBD"
          )}
        </div>
        {isKnockout && (
          <div className="mt-2">
            <label className="text-xs text-slate-500">Ganador:</label>
            <select
              value={selectedWinnerId}
              onChange={(e) => setSelectedWinnerId(e.target.value)}
              className="input w-full"
              disabled={isLocked}
            >
              <option value="">Seleccionar ganador</option>
              {(selectedHomeTeamId || predictedHomeTeamId || match.home_team_id) && (
                <option value={selectedHomeTeamId || predictedHomeTeamId || match.home_team_id || ""}>
                  {teams.get(selectedHomeTeamId || predictedHomeTeamId || match.home_team_id || "")?.name}
                </option>
              )}
              {(selectedAwayTeamId || predictedAwayTeamId || match.away_team_id) && (
                <option value={selectedAwayTeamId || predictedAwayTeamId || match.away_team_id || ""}>
                  {teams.get(selectedAwayTeamId || predictedAwayTeamId || match.away_team_id || "")?.name}
                </option>
              )}
            </select>
          </div>
        )}
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
        {saving ? "Guardando..." : existingPrediction ? "Actualizar" : "Predecir"}
      </button>
      {isLocked && <span className="badge bg-slate-200 text-slate-700">Bloqueada</span>}
      {saved && !error && <span className="text-emerald-600 text-xs">Guardado!</span>}
      {error && <span className="text-red-600 text-xs">{error}</span>}
    </div>
  );
}
