import { Link, NavLink, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "../context/AuthContext";
import { notificationsApi } from "../api/notifications";

const LINKS: { to: string; label: string }[] = [
  { to: "/", label: "Inicio" },
  { to: "/matches", label: "Partidos" },
  { to: "/groups", label: "Grupos" },
  { to: "/predictions", label: "Mis predicciones" },
  { to: "/ranking", label: "Ranking" },
  { to: "/leagues", label: "Ligas" },
];

export function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const { data: unread = 0 } = useQuery({
    queryKey: ["notifications", "unread"],
    queryFn: notificationsApi.unreadCount,
    refetchInterval: 15000,
    staleTime: 10000,
  });

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-40">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center gap-6">
        <Link to="/" className="font-bold text-brand-700">Mundial 2026</Link>
        <nav className="flex gap-3 text-sm">
          {LINKS.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.to === "/"}
              className={({ isActive }) =>
                `px-2 py-1 rounded transition ${
                  isActive ? "bg-brand-100 text-brand-700 font-medium" : "text-slate-600 hover:text-slate-900"
                }`
              }
            >
              {l.label}
            </NavLink>
          ))}
        </nav>
        <div className="ml-auto flex items-center gap-3">
          <NavLink
            to="/notifications"
            className="relative text-slate-600 hover:text-slate-900 text-sm"
          >
            Notificaciones
            {unread > 0 && (
              <span className="absolute -top-2 -right-4 bg-red-500 text-white rounded-full text-xs px-1.5">
                {unread}
              </span>
            )}
          </NavLink>
          {user && (
            <NavLink to="/profile" className="text-sm text-slate-700 hover:underline">
              {user.display_name}
            </NavLink>
          )}
          <button onClick={handleLogout} className="btn-secondary text-sm">Salir</button>
        </div>
      </div>
    </header>
  );
}
