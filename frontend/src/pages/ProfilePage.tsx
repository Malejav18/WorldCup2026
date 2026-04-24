import { FormEvent, useEffect, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { AxiosError } from "axios";
import { usersApi } from "../api/users";
import { useAuth } from "../context/AuthContext";
import { Spinner } from "../components/Spinner";

export function ProfilePage() {
  const { user, refreshProfile, loading } = useAuth();
  const qc = useQueryClient();

  const [displayName, setDisplayName] = useState("");
  const [avatarUrl, setAvatarUrl] = useState("");
  const [timezone, setTimezone] = useState("");
  const [language, setLanguage] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (user) {
      setDisplayName(user.display_name);
      setAvatarUrl(user.avatar_url ?? "");
      setTimezone(user.timezone);
      setLanguage(user.language);
    }
  }, [user]);

  const save = useMutation({
    mutationFn: () =>
      usersApi.updateMe({
        display_name: displayName,
        avatar_url: avatarUrl || null,
        timezone,
        language,
      }),
    onSuccess: async () => {
      setSaved(true);
      setError(null);
      await refreshProfile();
      qc.invalidateQueries({ queryKey: ["rankings", "global"] });
    },
    onError: (err) => {
      setSaved(false);
      const ax = err as AxiosError<{ detail?: string }>;
      setError(ax.response?.data?.detail ?? "No se pudo guardar");
    },
  });

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    save.mutate();
  };

  if (loading) return <Spinner />;
  if (!user) return <div className="card text-sm text-slate-500">No hay perfil disponible.</div>;

  return (
    <div className="space-y-4 max-w-md">
      <div>
        <h1 className="text-2xl font-bold">Mi perfil</h1>
        <p className="text-slate-500 text-sm">Ajusta tu nombre publico y preferencias.</p>
      </div>
      <form onSubmit={onSubmit} className="card space-y-3">
        <div>
          <label className="label">Email</label>
          <input className="input bg-slate-100" value={user.email} disabled />
        </div>
        <div>
          <label className="label">Nombre a mostrar</label>
          <input className="input" value={displayName} onChange={(e) => setDisplayName(e.target.value)} required minLength={2} />
        </div>
        <div>
          <label className="label">URL del avatar (opcional)</label>
          <input className="input" value={avatarUrl} onChange={(e) => setAvatarUrl(e.target.value)} />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">Zona horaria</label>
            <input className="input" value={timezone} onChange={(e) => setTimezone(e.target.value)} />
          </div>
          <div>
            <label className="label">Idioma</label>
            <input className="input" value={language} onChange={(e) => setLanguage(e.target.value)} />
          </div>
        </div>
        <div className="text-xs text-slate-500">
          Puntos: {user.total_points} &bull; Ranking: {user.global_rank ?? "—"}
        </div>
        {error && <div className="text-sm text-red-600">{error}</div>}
        {saved && !error && <div className="text-sm text-emerald-600">Guardado!</div>}
        <button className="btn-primary" disabled={save.isPending}>
          {save.isPending ? "Guardando..." : "Guardar"}
        </button>
      </form>
    </div>
  );
}
