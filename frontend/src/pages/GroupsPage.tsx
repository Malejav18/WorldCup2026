import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { tournamentApi } from "../api/tournament";
import { Spinner } from "../components/Spinner";

export function GroupsPage() {
  const groups = useQuery({ queryKey: ["tournament", "groups"], queryFn: tournamentApi.groups });
  const [openGroup, setOpenGroup] = useState<string | null>(null);
  const standings = useQuery({
    queryKey: ["tournament", "standings", openGroup],
    queryFn: () => (openGroup ? tournamentApi.groupStandings(openGroup) : Promise.resolve(null)),
    enabled: !!openGroup,
  });

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Grupos</h1>
        <p className="text-slate-500 text-sm">48 equipos organizados en 12 grupos (A a L).</p>
      </div>

      {groups.isLoading ? (
        <Spinner />
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {(groups.data ?? []).map((g) => (
            <div key={g.id} className="card">
              <div className="flex items-center justify-between mb-2">
                <h2 className="font-bold text-brand-700">{g.name}</h2>
                <button
                  onClick={() => setOpenGroup((cur) => (cur === g.id ? null : g.id))}
                  className="text-xs text-brand-600 hover:underline"
                >
                  {openGroup === g.id ? "Ocultar" : "Ver standings"}
                </button>
              </div>
              <ul className="space-y-1 text-sm">
                {g.teams.map((t) => (
                  <li key={t.id} className="flex justify-between">
                    <span>{t.name}</span>
                    <span className="text-slate-500 text-xs">{t.country_code}</span>
                  </li>
                ))}
              </ul>
              {openGroup === g.id && (
                <div className="mt-3 border-t border-slate-200 pt-2">
                  {standings.isLoading ? (
                    <Spinner label="Cargando..." />
                  ) : standings.data && standings.data.rows.length > 0 ? (
                    <table className="w-full text-xs">
                      <thead className="text-slate-500">
                        <tr>
                          <th className="text-left">#</th>
                          <th className="text-left">Equipo</th>
                          <th className="text-right">PJ</th>
                          <th className="text-right">G</th>
                          <th className="text-right">E</th>
                          <th className="text-right">P</th>
                          <th className="text-right">DG</th>
                          <th className="text-right">Pts</th>
                        </tr>
                      </thead>
                      <tbody>
                        {standings.data.rows.map((r) => (
                          <tr key={r.team_id} className="border-t border-slate-100">
                            <td>{r.position}</td>
                            <td>{r.team_name}</td>
                            <td className="text-right">{r.played}</td>
                            <td className="text-right">{r.won}</td>
                            <td className="text-right">{r.drawn}</td>
                            <td className="text-right">{r.lost}</td>
                            <td className="text-right">{r.goal_difference}</td>
                            <td className="text-right font-bold">{r.points}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="text-xs text-slate-500">Aun no hay partidos finalizados en este grupo.</p>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
