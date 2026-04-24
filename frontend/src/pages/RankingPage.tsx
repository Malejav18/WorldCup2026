import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { rankingsApi } from "../api/rankings";
import { useAuth } from "../context/AuthContext";
import { Spinner } from "../components/Spinner";

export function RankingPage() {
  const [page, setPage] = useState(1);
  const pageSize = 20;
  const { user } = useAuth();

  const list = useQuery({
    queryKey: ["rankings", "global", page],
    queryFn: () => rankingsApi.global(page, pageSize),
  });
  const me = useQuery({ queryKey: ["rankings", "me"], queryFn: rankingsApi.me });

  const totalPages = list.data ? Math.max(1, Math.ceil(list.data.total_users / pageSize)) : 1;

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Ranking global</h1>
        <p className="text-slate-500 text-sm">Clasificacion en tiempo real de todos los jugadores.</p>
      </div>

      <div className="card inline-flex gap-6 items-center">
        <div>
          <div className="text-xs text-slate-500 uppercase">Mi posicion</div>
          <div className="text-2xl font-bold">{me.data?.position ?? "—"}</div>
        </div>
        <div>
          <div className="text-xs text-slate-500 uppercase">Mis puntos</div>
          <div className="text-2xl font-bold text-brand-700">{me.data?.total_points ?? 0}</div>
        </div>
        <div>
          <div className="text-xs text-slate-500 uppercase">Total jugadores</div>
          <div className="text-2xl font-bold">{me.data?.total_users ?? 0}</div>
        </div>
      </div>

      {list.isLoading ? (
        <Spinner />
      ) : (
        <div className="overflow-x-auto card p-0">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-600 text-xs uppercase">
              <tr>
                <th className="p-2 text-left w-16">#</th>
                <th className="p-2 text-left">Jugador</th>
                <th className="p-2 text-right">Puntos</th>
              </tr>
            </thead>
            <tbody>
              {list.data?.entries.map((e) => {
                const isMe = user && e.user_id === user.id;
                return (
                  <tr key={e.user_id} className={`border-t border-slate-100 ${isMe ? "bg-brand-50 font-semibold" : ""}`}>
                    <td className="p-2">{e.position}</td>
                    <td className="p-2">{e.display_name ?? e.user_id.slice(0, 8)}</td>
                    <td className="p-2 text-right">{e.total_points}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <div className="flex items-center gap-2 text-sm">
        <button className="btn-secondary" disabled={page === 1} onClick={() => setPage((p) => p - 1)}>Anterior</button>
        <span className="text-slate-600">Pagina {page} de {totalPages}</span>
        <button className="btn-secondary" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>Siguiente</button>
      </div>
    </div>
  );
}
