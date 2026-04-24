import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { notificationsApi } from "../api/notifications";
import { Spinner } from "../components/Spinner";
import { formatDateTime } from "../utils/format";

export function NotificationsPage() {
  const qc = useQueryClient();
  const list = useQuery({ queryKey: ["notifications", "mine"], queryFn: notificationsApi.mine, refetchInterval: 10000 });

  const markRead = useMutation({
    mutationFn: (id: number) => notificationsApi.markRead(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["notifications", "mine"] });
      qc.invalidateQueries({ queryKey: ["notifications", "unread"] });
    },
  });

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Notificaciones</h1>
        <p className="text-slate-500 text-sm">Historial reciente de alertas del sistema.</p>
      </div>

      {list.isLoading ? (
        <Spinner />
      ) : (list.data ?? []).length === 0 ? (
        <div className="card text-sm text-slate-500">No tienes notificaciones.</div>
      ) : (
        <div className="space-y-2">
          {(list.data ?? []).map((n) => (
            <div key={n.id} className={`card ${n.read_at ? "opacity-70" : "border-brand-200"}`}>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className={`badge ${n.channel === "EMAIL" ? "bg-amber-100 text-amber-700" : "bg-blue-100 text-blue-700"}`}>
                      {n.channel}
                    </span>
                    <span className="font-semibold">{n.subject}</span>
                  </div>
                  <p className="text-sm text-slate-600 mt-1 whitespace-pre-line">{n.body}</p>
                  <div className="text-xs text-slate-400 mt-1">
                    {formatDateTime(n.created_at)} &bull; {n.event_type}
                  </div>
                </div>
                {!n.read_at && (
                  <button onClick={() => markRead.mutate(n.id)} className="btn-secondary text-xs" disabled={markRead.isPending}>
                    Marcar leida
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
