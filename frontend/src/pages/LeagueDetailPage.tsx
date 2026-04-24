import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams, useNavigate } from "react-router-dom";
import { leaguesApi } from "../api/leagues";
import { Spinner } from "../components/Spinner";
import { useAuth } from "../context/AuthContext";

export function LeagueDetailPage() {
  const { id } = useParams<{ id: string }>();
  const leagueId = id ?? "";
  const { user } = useAuth();
  const qc = useQueryClient();
  const navigate = useNavigate();

  const detail = useQuery({ queryKey: ["leagues", "detail", leagueId], queryFn: () => leaguesApi.detail(leagueId), enabled: !!leagueId });
  const ranking = useQuery({ queryKey: ["leagues", "ranking", leagueId], queryFn: () => leaguesApi.ranking(leagueId), enabled: !!leagueId });
  const invite = useQuery({ queryKey: ["leagues", "invite", leagueId], queryFn: () => leaguesApi.getInviteCode(leagueId), enabled: !!detail.data && detail.data.my_role !== null });

  const regen = useMutation({
    mutationFn: () => leaguesApi.regenerateInviteCode(leagueId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["leagues", "invite", leagueId] }),
  });

  const leave = useMutation({
    mutationFn: () => leaguesApi.leave(leagueId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["leagues", "mine"] });
      navigate("/leagues");
    },
  });

  if (detail.isLoading) return <Spinner />;
  if (!detail.data) return <div>Liga no encontrada.</div>;

  const isAdmin = detail.data.my_role === "ADMIN";
  const isCreator = user?.id === detail.data.created_by_user_id;

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-brand-700">{detail.data.name}</h1>
          {detail.data.description && <p className="text-slate-600">{detail.data.description}</p>}
          <div className="text-xs text-slate-500 mt-1">
            Miembros: {detail.data.member_count} &bull; Tu rol: {detail.data.my_role ?? "invitado"}
          </div>
        </div>
        {!isCreator && detail.data.my_role !== null && (
          <button onClick={() => leave.mutate()} className="btn-danger">
            {leave.isPending ? "Saliendo..." : "Salir de la liga"}
          </button>
        )}
      </div>

      {invite.data && (
        <div className="card flex items-center gap-4">
          <div>
            <div className="text-xs uppercase text-slate-500">Codigo de invitacion</div>
            <div className="text-xl font-mono tracking-widest font-bold">{invite.data.invite_code}</div>
          </div>
          {isAdmin && (
            <button onClick={() => regen.mutate()} className="btn-secondary" disabled={regen.isPending}>
              {regen.isPending ? "..." : "Regenerar"}
            </button>
          )}
        </div>
      )}

      <div>
        <h2 className="font-semibold mb-2">Ranking de la liga</h2>
        {ranking.isLoading ? (
          <Spinner />
        ) : (
          <div className="overflow-x-auto card p-0">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-slate-600 text-xs uppercase">
                <tr>
                  <th className="p-2 text-left w-12">#</th>
                  <th className="p-2 text-left">Jugador</th>
                  <th className="p-2 text-right">Puntos</th>
                </tr>
              </thead>
              <tbody>
                {ranking.data?.entries.map((e) => {
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
      </div>
    </div>
  );
}
