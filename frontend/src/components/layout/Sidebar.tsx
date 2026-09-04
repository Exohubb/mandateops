import { NavLink } from "react-router-dom";
import {
  Activity,
  ArrowUpRight,
  FileSearch,
  Home,
  Moon,
  MessageSquareText,
  ShieldCheck,
  Sparkles,
  Sun,
} from "lucide-react";
import { useTheme } from "../../lib/theme";
import { PlayStoreIcon } from "./PlayStoreIcon";

const NAV_SECTIONS = [
  {
    label: "Overview",
    items: [{ to: "/", label: "Home", icon: Home }],
  },
  {
    label: "Recovery Engine",
    items: [
      { to: "/dashboard", label: "Live Simulation", icon: Activity },
      { to: "/mandates", label: "Mandate Explorer", icon: FileSearch },
    ],
  },
  {
    label: "Trust & AI",
    items: [
      { to: "/copilot", label: "Ask Nira", icon: MessageSquareText },
      { to: "/audit", label: "Audit Trail", icon: ShieldCheck },
      { to: "/ai-judgment", label: "How We Use AI", icon: Sparkles },
    ],
  },
];

const AUTOPAY_URL =
  "https://play.google.com/store/apps/details?id=com.airolabs.autopayy";

export function Sidebar() {
  const { theme, toggleTheme } = useTheme();

  return (
    <aside className="fixed inset-y-0 left-0 z-20 hidden w-72 flex-col border-r border-border bg-surface md:flex">
      {/* Brand header */}
      <div className="flex items-center gap-3 px-6 py-6">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-ai-500/15 text-ai-400 shadow-sm">
          <Sparkles size={20} />
        </div>
        <div>
          <div className="text-base font-bold leading-tight text-text-primary">
            MandateOps
          </div>
          <div className="text-[11px] font-medium text-text-muted">
            Track 03 · AI Revenue Recovery
          </div>
        </div>
      </div>

      {/* Theme toggle */}
      <div className="px-4">
        <button
          onClick={toggleTheme}
          className="flex w-full items-center justify-between rounded-xl border border-border bg-bg px-3.5 py-2.5 text-xs font-medium text-text-secondary transition-colors hover:bg-surface-hover hover:text-text-primary"
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

      {/* Navigation, grouped into sections */}
      <nav className="flex-1 space-y-5 overflow-y-auto px-4 py-5">
        {NAV_SECTIONS.map((section) => (
          <div key={section.label}>
            <div className="mb-1.5 px-2 text-[10px] font-semibold uppercase tracking-wider text-text-muted">
              {section.label}
            </div>
            <div className="space-y-0.5">
              {section.items.map(({ to, label, icon: Icon }) => (
                <NavLink
                  key={to}
                  to={to}
                  end={to === "/"}
                  className={({ isActive }) =>
                    `group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition-colors ${
                      isActive
                        ? "bg-ai-500/10 font-medium text-ai-400"
                        : "text-text-secondary hover:bg-surface-hover hover:text-text-primary"
                    }`
                  }
                >
                  {({ isActive }) => (
                    <>
                      {isActive && (
                        <span className="absolute left-0 top-1/2 h-4 w-0.5 -translate-y-1/2 rounded-full bg-ai-500" />
                      )}
                      <Icon size={16} />
                      {label}
                    </>
                  )}
                </NavLink>
              ))}
            </div>
          </div>
        ))}
      </nav>

      {/* AutoPay credibility card */}
      <div className="border-t border-border p-4">
        <a
          href={AUTOPAY_URL}
          target="_blank"
          rel="noreferrer"
          className="group flex items-start gap-3 rounded-xl border border-border bg-bg p-3.5 transition-colors hover:border-ai-500/40 hover:bg-surface-hover"
        >
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-surface shadow-sm">
            <PlayStoreIcon size={18} />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-1 text-xs font-semibold text-text-primary">
              Also shipped: AutoPay
              <ArrowUpRight
                size={12}
                className="text-text-muted transition-colors group-hover:text-ai-400"
              />
            </div>
            <p className="mt-0.5 text-[11px] leading-snug text-text-muted">
              Consumer UPI mandate manager — 740+ users in 20 days on the
              Play Store.
            </p>
          </div>
        </a>
      </div>
    </aside>
  );
}
