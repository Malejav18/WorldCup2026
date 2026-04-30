import { useQuery } from "@tanstack/react-query";
import { useMemo, useState, useEffect, useCallback } from "react";
import { tournamentApi } from "../api/tournament";
import { predictionsApi } from "../api/predictions";
import { PredictionRow } from "../components/PredictionRow";
import { Spinner } from "../components/Spinner";
import { phaseLabel, statusBadge } from "../utils/format";
import type { Match, Prediction } from "../types";

const STATUSES = ["ALL", "SCHEDULED", "LIVE", "FINISHED"] as const;
const PHASES = ["ALL", "GROUP", "R32", "R16", "QF", "SF", "THIRD_PLACE", "FINAL"] as const;
  
const R32_ALLOWED_GROUPS: Record<number, { home: string[]; away: string[] }> = {
  73: { home: ['A'], away: ['B'] },
  74: { home: ['A'], away: ['A', 'B', 'C', 'D', 'F'] },
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

export function MatchesPage() {
  const [status, setStatus] = useState<(typeof STATUSES)[number]>("SCHEDULED");
  const [phase, setPhase] = useState<(typeof PHASES)[number]>("ALL");

  const teams = useQuery({ queryKey: ["tournament", "teams"], queryFn: tournamentApi.teams });
  const groups = useQuery({ queryKey: ["tournament", "groups"], queryFn: tournamentApi.groups });
  const allMatches = useQuery({
    queryKey: ["tournament", "matches", "all"],
    queryFn: () => tournamentApi.matches({}),
  });
  const matches = useQuery({
    queryKey: ["tournament", "matches", status, phase],
    queryFn: () =>
      tournamentApi.matches({
        status: status === "ALL" ? undefined : status,
        phase: phase === "ALL" ? undefined : phase,
      }),
  });

  const teamMap = useMemo(() => {
    const m = new Map<string, { id: string; name: string; country_code: string; confederation: string; group_id: string | null }>();
    (teams.data ?? []).forEach((t) => m.set(t.id, t));
    return m;
  }, [teams.data]);

  const groupMap = useMemo(() => {
    const m = new Map<string, { id: string; letter: string; name: string }>();
    (groups.data ?? []).forEach((g) => m.set(g.id, g));
    return m;
  }, [groups.data]);

  const matchNumberToId = useMemo(() => {
    const m = new Map<number, string>();
    (allMatches.data ?? []).forEach((match) => m.set(match.match_number, match.id));
    return m;
  }, [allMatches.data]);

  const predictions = useQuery({ queryKey: ["predictions", "mine"], queryFn: predictionsApi.mine });
  const predictionsByMatch = useMemo(() => {
    const map = new Map<string, Prediction>();
    (predictions.data ?? []).forEach((prediction) => map.set(prediction.match_id, prediction));
    return map;
  }, [predictions.data]);

  const [r32Selections, setR32Selections] = useState<Record<string, { homeTeamId: string; awayTeamId: string }>>({});

  useEffect(() => {
    if (!predictions.data) return;

    setR32Selections((current) => {
      const next = { ...current };
      (predictions.data ?? []).forEach((prediction: Prediction) => {
        if (prediction.match_phase !== "R32") return;
        next[prediction.match_id] = {
          homeTeamId: prediction.predicted_home_team_id ?? "",
          awayTeamId: prediction.predicted_away_team_id ?? "",
        };
      });
      return next;
    });
  }, [predictions.data]);

  const r32UsedTeamIds = useMemo(() => {
    const used = new Set<string>();
    Object.values(r32Selections).forEach((selection) => {
      if (selection.homeTeamId) used.add(selection.homeTeamId);
      if (selection.awayTeamId) used.add(selection.awayTeamId);
    });
    return used;
  }, [r32Selections]);

  const blockedGroups = useMemo(() => {
    const blocked = new Set<string>();
    Object.entries(r32Selections).forEach(([matchId, selection]) => {
      const match = allMatches.data?.find(m => m.id === matchId);
      if (!match || match.phase !== "R32") return;
      const allowed = R32_ALLOWED_GROUPS[match.match_number];
      if (!allowed) return;
      if (selection.homeTeamId && allowed.home.length > 1) {
        const team = teamMap.get(selection.homeTeamId);
        if (team?.group_id) {
          const group = groupMap.get(team.group_id);
          if (group) blocked.add(group.letter);
        }
      }
      if (selection.awayTeamId && allowed.away.length > 1) {
        const team = teamMap.get(selection.awayTeamId);
        if (team?.group_id) {
          const group = groupMap.get(team.group_id);
          if (group) blocked.add(group.letter);
        }
      }
    });
    return blocked;
  }, [r32Selections, allMatches.data, teamMap, groupMap]);

  const handleR32SelectionChange = useCallback(
    (matchId: string, selection: { homeTeamId: string; awayTeamId: string }) => {
      setR32Selections((current) => {
        const existing = current[matchId];
        if (existing?.homeTeamId === selection.homeTeamId && existing?.awayTeamId === selection.awayTeamId) {
          return current;
        }
        return {
          ...current,
          [matchId]: selection,
        };
      });
    },
    [],
  );

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Partidos</h1>
        <p className="text-slate-500 text-sm">Filtra por fase o estado. Haz tu prediccion antes de que el partido empiece.</p>
      </div>

      <div className="flex flex-wrap gap-2">
        <div className="flex items-center gap-1">
          <span className="text-sm text-slate-500">Estado:</span>
          {STATUSES.map((s) => (
            <button
              key={s}
              onClick={() => setStatus(s)}
              className={`badge px-2 py-1 text-xs ${status === s ? "bg-brand-600 text-white" : statusBadge(s)}`}
            >
              {s === "ALL" ? "Todos" : s}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-1">
          <span className="text-sm text-slate-500">Fase:</span>
          {PHASES.map((p) => (
            <button
              key={p}
              onClick={() => setPhase(p)}
              className={`badge px-2 py-1 text-xs ${phase === p ? "bg-brand-600 text-white" : "bg-slate-200 text-slate-700"}`}
            >
              {p === "ALL" ? "Todas" : phaseLabel(p)}
            </button>
          ))}
        </div>
      </div>

      {matches.isLoading || teams.isLoading || groups.isLoading || allMatches.isLoading || predictions.isLoading ? (
        <Spinner label="Cargando partidos..." />
      ) : (
        <div className="space-y-2">
          <div className="text-xs text-slate-500">
            {matches.data?.length ?? 0} partidos
          </div>
          {(matches.data ?? []).map((m: Match) => (
            <PredictionRow
              key={m.id}
              match={m}
              teams={teamMap}
              groups={groupMap}
              matchNumberToId={matchNumberToId}
              existingPrediction={predictionsByMatch.get(m.id) ?? null}
              r32UsedTeamIds={r32UsedTeamIds}
              onR32SelectionChange={handleR32SelectionChange}
              blockedGroups={blockedGroups}
            />
          ))}
        </div>
      )}
    </div>
  );
}
