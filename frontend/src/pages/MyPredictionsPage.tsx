import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { predictionsApi } from "../api/predictions";
import { scoringApi } from "../api/scoring";
import { tournamentApi } from "../api/tournament";
import { Spinner } from "../components/Spinner";
import { phaseLabel } from "../utils/format";

export function MyPredictionsPage() {
  const preds = useQuery({ queryKey: ["predictions", "mine"], queryFn: predictionsApi.mine });
  const specials = useQuery({ queryKey: ["predictions", "special", "mine"], queryFn: predictionsApi.specialMine });
  const scores = useQuery({ queryKey: ["scoring", "mine"], queryFn: scoringApi.mine });
  const teams = useQuery({ queryKey: ["tournament", "teams"], queryFn: tournamentApi.teams });
  const matches = useQuery({ queryKey: ["tournament", "matches", "all"], queryFn: () => tournamentApi.matches() });

  const teamName = (id: string | null) => (id ? teams.data?.find((t) => t.id === id)?.name ?? "—" : "—");
  const scoreByMatch = useMemo(() => {
    const m = new Map<string, number>();
    (scores.data ?? []).forEach((s) => m.set(s.match_id, s.points_total));
    return m;
  }, [scores.data]);
  const matchById = useMemo(() => {
    const m = new Map<string, { home: string | null; away: string | null; phase: string }>();
    (matches.data ?? []).forEach((x) => m.set(x.id, { home: x.home_team_id, away: x.away_team_id, phase: x.phase }));
    return m;
  }, [matches.data]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Mis predicciones</h1>
        <p className="text-slate-500 text-sm">Lista completa con puntos obtenidos cuando el partido ya fue puntuado.</p>
      </div>

      <section>
        <h2 className="font-semibold mb-2">Partidos</h2>
        {preds.isLoading ? (
          <Spinner />
        ) : (
          <div className="overflow-x-auto card p-0">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-slate-600 text-xs uppercase">
                <tr>
                  <th className="p-2 text-left">Fase</th>
                  <th className="p-2 text-left">Partido</th>
                  <th className="p-2 text-left">Mi prediccion</th>
                  <th className="p-2 text-left">Estado</th>
                  <th className="p-2 text-right">Puntos</th>
                </tr>
              </thead>
              <tbody>
                {(preds.data ?? []).map((p) => {
                  const info = matchById.get(p.match_id);
                  return (
                    <tr key={p.id} className="border-t border-slate-100">
                      <td className="p-2">{phaseLabel(p.match_phase)}</td>
                      <td className="p-2">
                        {info ? `${teamName(info.home)} vs ${teamName(info.away)}` : p.match_id.slice(0, 8)}
                      </td>
                      <td className="p-2 font-medium">
                        {p.predicted_home_goals_90} - {p.predicted_away_goals_90}
                      </td>
                      <td className="p-2">
                        {p.is_locked ? (
                          <span className="badge bg-slate-200 text-slate-700">Bloqueada</span>
                        ) : (
                          <span className="badge bg-blue-100 text-blue-700">Abierta</span>
                        )}
                      </td>
                      <td className="p-2 text-right font-semibold">
                        {scoreByMatch.has(p.match_id) ? scoreByMatch.get(p.match_id) : "—"}
                      </td>
                    </tr>
                  );
                })}
                {(preds.data ?? []).length === 0 && (
                  <tr><td colSpan={5} className="p-4 text-center text-slate-500">Aun no tienes predicciones.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section>
        <h2 className="font-semibold mb-2">Predicciones especiales</h2>
        {specials.isLoading ? (
          <Spinner />
        ) : (specials.data ?? []).length === 0 ? (
          <div className="card text-sm text-slate-500">Aun no has elegido campeon/subcampeon/tercer puesto.</div>
        ) : (
          <div className="grid md:grid-cols-3 gap-2">
            {(specials.data ?? []).map((s) => (
              <div key={s.id} className="card">
                <div className="text-xs uppercase text-slate-500">{s.prediction_type}</div>
                <div className="font-semibold">{teamName(s.team_id)}</div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
