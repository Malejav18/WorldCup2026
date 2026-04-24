export function formatDateTime(iso: string): string {
  try {
    return new Date(iso).toLocaleString("es-CO", {
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

export function phaseLabel(phase: string): string {
  switch (phase) {
    case "GROUP": return "Grupos";
    case "R32": return "Ronda de 32";
    case "R16": return "Octavos";
    case "QF": return "Cuartos";
    case "SF": return "Semifinales";
    case "THIRD_PLACE": return "3er puesto";
    case "FINAL": return "Final";
    default: return phase;
  }
}

export function statusBadge(status: string): string {
  switch (status) {
    case "SCHEDULED": return "bg-blue-100 text-blue-700";
    case "LIVE": return "bg-amber-100 text-amber-700";
    case "FINISHED": return "bg-emerald-100 text-emerald-700";
    default: return "bg-slate-100 text-slate-700";
  }
}
