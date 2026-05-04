import { useQuery } from "@tanstack/react-query";
import { useMemo, useState, useEffect, useCallback } from "react";
import { tournamentApi } from "../api/tournament";
import { predictionsApi } from "../api/predictions";
import { authApi } from "../api/auth";
import { useAuth } from "../context/AuthContext";
import { PredictionRow } from "../components/PredictionRow";
import { MatchRow } from "../components/MatchRow";
import { Spinner } from "../components/Spinner";
import { phaseLabel, statusBadge } from "../utils/format";
import type { Match, Prediction } from "../types";

const STATUSES = ["ALL", "SCHEDULED", "LIVE", "FINISHED"] as const;
const PHASES = ["ALL", "GROUP", "R32", "R16", "QF", "SF", "THIRD_PLACE", "FINAL"] as const;

export function MatchesPage() {
  const { user } = useAuth();
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

  const userValidation = useQuery({
    queryKey: ["auth", "validate"],
    queryFn: authApi.validate,
    enabled: !!user,
  });

  const isAdmin = userValidation.data?.role === "ADMIN";

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
        <p className="text-slate-500 text-sm">
          {isAdmin
            ? "Registra los resultados oficiales de los partidos."
            : "Filtra por fase o estado. Haz tu prediccion antes de que el partido empiece."
          }
        </p>
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

      {matches.isLoading || teams.isLoading || groups.isLoading || allMatches.isLoading || predictions.isLoading || userValidation.isLoading ? (
        <Spinner label="Cargando partidos..." />
      ) : (
        <div className="space-y-2">
          <div className="text-xs text-slate-500">
            {matches.data?.length ?? 0} partidos
          </div>
          {(matches.data ?? []).map((m: Match) => (
            isAdmin ? (
              <MatchRow
                key={m.id}
                match={m}
                teams={teamMap}
                groups={groupMap}
              />
            ) : (
              <PredictionRow
                key={m.id}
                match={m}
                teams={teamMap}
                groups={groupMap}
                matchNumberToId={matchNumberToId}
                existingPrediction={predictionsByMatch.get(m.id) ?? null}
                r32UsedTeamIds={r32UsedTeamIds}
                onR32SelectionChange={handleR32SelectionChange}
              />
            )
          ))}
        </div>
      )}
    </div>
  );
}
