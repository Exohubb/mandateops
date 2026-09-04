import { NavLink } from "react-router-dom";
import {
  Activity,
  FileSearch,
  Home,
  Moon,
  MessageSquareText,
  ShieldCheck,
  Sparkles,
  Sun,
} from "lucide-react";
import { useTheme } from "../../lib/theme";

const NAV_ITEMS = [
  { to: "/", label: "Home", icon: Home },
  { to: "/dashboard", label: "Live Simulation", icon: Activity },
  { to: "/mandates", label: "Mandate Explorer", icon: FileSearch },
  { to: "/copilot", label: "Ask Nira", icon: MessageSquareText },
  { to: "/audit", label: "Audit Trail", icon: ShieldCheck },
  { to: "/ai-judgment", label: "How We Use AI", icon: Sparkles },
];

export function Sidebar() {
  const { theme, toggleTheme } = useTheme();

  return (
    <aside className="fixed inset-y-0 left-0 z-20 hidden w-60 flex-col border-r border-border bg-surface md:flex">
      <div className="flex items-center justify-between gap-2 px-5 py-5">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-ai-500/15 text-ai-400">
            <Sparkles size={18} />
          </div>
          <div>
            <div className="text-sm font-bold text-text-primary">MandateOps</div>
            <div className="text-[11px] text-text-muted">Track 03 · Revenue Recovery</div>
          </div>
        </div>
      </div>

      <div className="px-3">
        <button
          onClick={toggleTheme}
          className="flex w-full items-center justify-between rounded-lg border border-border bg-bg px-3 py-2 text-xs font-medium text-text-secondary transition-colors hover:bg-surface-hover hover:text-text-primary"
        >
          <span className="flex items-center gap-2">
            {theme === "dark" ? <Moon size={14} /> : <Sun size={14} />}
            {theme === "dark" ? "Dark mode" : "Light mode"}
          </span>
          <span
            className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
              theme === "dark" ? "bg-ai-500" : "bg-border-strong"
            }`}
          >
            <span
              className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow-sm transition-transform ${
                theme === "dark" ? "translate-x-[18px]" : "translate-x-[3px]"
              }`}
            />
          </span>
        </button>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-3">
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors ${
                isActive
                  ? "bg-ai-500/10 text-ai-400 font-medium"
                  : "text-text-secondary hover:bg-surface-hover hover:text-text-primary"
              }`
            }
          >
            <Icon size={16} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-border px-5 py-4 text-[11px] text-text-muted">
        Built by the team behind{" "}
        <span className="text-text-secondary">AutoPay</span> — 740+ users in
        20 days on Play Store.
      </div>
    </aside>
  );
}
