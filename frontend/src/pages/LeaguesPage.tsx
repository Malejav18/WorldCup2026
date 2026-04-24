import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { AxiosError } from "axios";
import { leaguesApi } from "../api/leagues";
import { Spinner } from "../components/Spinner";

export function LeaguesPage() {
  const qc = useQueryClient();
  const mine = useQuery({ queryKey: ["leagues", "mine"], queryFn: leaguesApi.mine });

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [code, setCode] = useState("");
  const [errCreate, setErrCreate] = useState<string | null>(null);
  const [errJoin, setErrJoin] = useState<string | null>(null);

  const createMut = useMutation({
    mutationFn: () => leaguesApi.create(name, description || undefined),
    onSuccess: () => {
      setName("");
      setDescription("");
      setErrCreate(null);
      qc.invalidateQueries({ queryKey: ["leagues", "mine"] });
    },
    onError: (err) => {
      const ax = err as AxiosError<{ detail?: string }>;
      setErrCreate(ax.response?.data?.detail ?? "No se pudo crear");
    },
  });

  const joinMut = useMutation({
    mutationFn: () => leaguesApi.joinByCode(code.trim()),
    onSuccess: () => {
      setCode("");
      setErrJoin(null);
      qc.invalidateQueries({ queryKey: ["leagues", "mine"] });
    },
    onError: (err) => {
      const ax = err as AxiosError<{ detail?: string }>;
      setErrJoin(ax.response?.data?.detail ?? "No se pudo unir");
    },
  });

  const onCreate = (e: FormEvent) => {
    e.preventDefault();
    createMut.mutate();
  };
  const onJoin = (e: FormEvent) => {
    e.preventDefault();
    joinMut.mutate();
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Mis ligas</h1>
        <p className="text-slate-500 text-sm">Crea ligas privadas o unete a las de tus amigos con un codigo.</p>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <form onSubmit={onCreate} className="card space-y-3">
          <h2 className="font-semibold">Crear liga</h2>
          <div>
            <label className="label">Nombre</label>
            <input className="input" value={name} onChange={(e) => setName(e.target.value)} required minLength={3} />
          </div>
          <div>
            <label className="label">Descripcion (opcional)</label>
            <input className="input" value={description} onChange={(e) => setDescription(e.target.value)} />
          </div>
          {errCreate && <div className="text-sm text-red-600">{errCreate}</div>}
          <button type="submit" className="btn-primary" disabled={createMut.isPending}>
            {createMut.isPending ? "Creando..." : "Crear"}
          </button>
        </form>

        <form onSubmit={onJoin} className="card space-y-3">
          <h2 className="font-semibold">Unirme con codigo</h2>
          <div>
            <label className="label">Codigo de invitacion</label>
            <input className="input uppercase tracking-widest" value={code} onChange={(e) => setCode(e.target.value.toUpperCase())} required />
          </div>
          {errJoin && <div className="text-sm text-red-600">{errJoin}</div>}
          <button type="submit" className="btn-primary" disabled={joinMut.isPending}>
            {joinMut.isPending ? "Uniendo..." : "Unirme"}
          </button>
        </form>
      </div>

      <div>
        <h2 className="font-semibold mb-2">Mis ligas actuales</h2>
        {mine.isLoading ? (
          <Spinner />
        ) : (mine.data ?? []).length === 0 ? (
          <div className="card text-sm text-slate-500">Todavia no perteneces a ninguna liga.</div>
        ) : (
          <div className="grid md:grid-cols-2 gap-3">
            {(mine.data ?? []).map((l) => (
              <Link key={l.id} to={`/leagues/${l.id}`} className="card hover:border-brand-500 transition">
                <div className="font-semibold text-brand-700">{l.name}</div>
                {l.description && <div className="text-sm text-slate-500">{l.description}</div>}
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
