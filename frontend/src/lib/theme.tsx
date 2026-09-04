import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

export type ThemeMode = "light" | "dark";

const STORAGE_KEY = "mandateops-theme";

function getInitialTheme(): ThemeMode {
  if (typeof window === "undefined") return "dark";
  const stored = window.localStorage.getItem(STORAGE_KEY);
  if (stored === "light" || stored === "dark") return stored;
  const prefersLight = window.matchMedia?.("(prefers-color-scheme: light)").matches;
  return prefersLight ? "light" : "dark";
}

interface ThemeContextValue {
  theme: ThemeMode;
  toggleTheme: () => void;
  setTheme: (theme: ThemeMode) => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<ThemeMode>(getInitialTheme);

  useEffect(() => {
    const root = document.documentElement;
    if (theme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
    window.localStorage.setItem(STORAGE_KEY, theme);
  }, [theme]);

  const value = useMemo<ThemeContextValue>(
    () => ({
      theme,
      toggleTheme: () => setThemeState((t) => (t === "dark" ? "light" : "dark")),
      setTheme: setThemeState,
    }),
    [theme]
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme(): ThemeContextValue {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme must be used within a ThemeProvider");
  return ctx;
}

/** Literal color values (not CSS vars) for chart libraries like Recharts
 * that render to SVG and benefit from concrete values resolved in JS,
 * rather than depending on var() support inside SVG presentation
 * attributes across every environment. Kept in sync with index.css by hand
 * since there are only two themes and a handful of chart-relevant tokens.
 */
export const CHART_COLORS: Record<ThemeMode, {
  grid: string;
  axis: string;
  tooltipBg: string;
  tooltipBorder: string;
  textMuted: string;
}> = {
  dark: {
    grid: "#232936",
    axis: "#64748b",
    tooltipBg: "#12161f",
    tooltipBorder: "#232936",
    textMuted: "#94a3b8",
  },
  light: {
    grid: "#e4e7ec",
    axis: "#64748b",
    tooltipBg: "#ffffff",
    tooltipBorder: "#e4e7ec",
    textMuted: "#475569",
  },
};
