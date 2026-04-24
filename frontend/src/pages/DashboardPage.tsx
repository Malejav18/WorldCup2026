import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { rankingsApi } from "../api/rankings";
import { scoringApi } from "../api/scoring";
import { tournamentApi } from "../api/tournament";
import { notificationsApi } from "../api/notifications";
import { leaguesApi } from "../api/leagues";
import { Spinner } from "../components/Spinner";
import { formatDateTime, phaseLabel } from "../utils/format";

export function DashboardPage() {
  const { user } = useAuth();
  const info = useQuery({ queryKey: ["tournament", "info"], queryFn: tournamentApi.info });
  const myRank = useQuery({ queryKey: ["rankings", "me"], queryFn: rankingsApi.me });
  const summary = useQuery({ queryKey: ["scoring", "summary"], queryFn: scoringApi.summary });
  const unread = useQuery({ queryKey: ["notifications", "unread"], queryFn: notificationsApi.unreadCount });
  const myLeagues = useQuery({ queryKey: ["leagues", "mine"], queryFn: leaguesApi.mine });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Hola, {user?.display_name ?? "jugador"}</h1>
        <p className="text-slate-500">Estado general del torneo y tu progreso.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="text-xs uppercase text-slate-500">Mis puntos</div>
          <div className="text-3xl font-bold text-brand-700">
            {summary.isLoading ? "..." : summary.data?.total_points ?? 0}
          </div>
          <div className="text-xs text-slate-500 mt-1">
            {summary.data?.scored_matches ?? 0} partidos puntuados
          </div>
        </div>
        <div className="card">
          <div className="text-xs uppercase text-slate-500">Mi posicion</div>
          <div className="text-3xl font-bold">
            {myRank.isLoading ? "..." : myRank.data?.position ?? "—"}
          </div>
          <div className="text-xs text-slate-500 mt-1">
            de {myRank.data?.total_users ?? 0} jugadores
          </div>
        </div>
        <div className="card">
          <div className="text-xs uppercase text-slate-500">Notificaciones</div>
          <div className="text-3xl font-bold text-amber-600">
            {unread.isLoading ? "..." : unread.data ?? 0}
          </div>
          <div className="text-xs text-slate-500 mt-1">sin leer</div>
        </div>
        <div className="card">
          <div className="text-xs uppercase text-slate-500">Mis ligas</div>
          <div className="text-3xl font-bold">
            {myLeagues.isLoading ? "..." : myLeagues.data?.length ?? 0}
          </div>
          <div className="text-xs text-slate-500 mt-1">privadas</div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card">
          <h2 className="font-semibold mb-2">Estado del torneo</h2>
          {info.isLoading ? (
            <Spinner />
          ) : info.data ? (
            <div className="space-y-1 text-sm">
              <div><span className="text-slate-500">Fase actual:</span> <span className="font-medium">{info.data.status}</span></div>
              <div><span className="text-slate-500">Partidos jugados:</span> <span className="font-medium">{info.data.finished_matches} / {info.data.total_matches}</span></div>
            </div>
          ) : (
            <p className="text-sm text-slate-500">No se pudo cargar.</p>
          )}
        </div>
        <div className="card">
          <h2 className="font-semibold mb-2">Proximo partido</h2>
          {info.data?.next_match ? (
            <div className="space-y-1 text-sm">
              <div>
                <span className={`badge ${phaseLabel(info.data.next_match.phase) ? "bg-blue-100 text-blue-700" : ""}`}>
                  {phaseLabel(info.data.next_match.phase)}
                </span>
                <span className="ml-2 text-slate-500">#{info.data.next_match.match_number}</span>
              </div>
              <div className="text-slate-700">{formatDateTime(info.data.next_match.scheduled_at)}</div>
              <Link to="/matches" className="text-brand-600 text-sm hover:underline">Ir a predecir &rarr;</Link>
            </div>
          ) : (
            <p className="text-sm text-slate-500">No hay partidos pendientes.</p>
          )}
        </div>
      </div>
    </div>
  );
}
