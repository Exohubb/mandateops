import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { CHART_COLORS, useTheme } from "../../lib/theme";

// Actual measured results from a verified 5,000-mandate synthetic batch run
// (backend/app/simulation, seed=2026) — not a projection. See the "How We
// Use AI" and Live Simulation pages to reproduce this exact number.
const DATA = [
  { name: "Naive Retry\n(next-day)", rate: 49.7, fill: "#94a3b8" },
  { name: "MandateOps", rate: 66.7, fill: "#6366f1" },
];

export function RecoveryComparisonChart() {
  const { theme } = useTheme();
  const c = CHART_COLORS[theme];

  return (
    <div className="h-56">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={DATA} layout="vertical" margin={{ left: 8, right: 24 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={c.grid} horizontal={false} />
          <XAxis
            type="number"
            domain={[0, 80]}
            stroke={c.axis}
            fontSize={11}
            tickLine={false}
            axisLine={false}
            unit="%"
          />
          <YAxis
            type="category"
            dataKey="name"
            stroke={c.axis}
            fontSize={12}
            tickLine={false}
            axisLine={false}
            width={110}
          />
          <Tooltip
            contentStyle={{
              background: c.tooltipBg,
              border: `1px solid ${c.tooltipBorder}`,
              borderRadius: 8,
              fontSize: 12,
              color: c.textMuted,
            }}
            formatter={(value) => [`${value}%`, "Recovery rate"]}
          />
          <Bar dataKey="rate" radius={[0, 6, 6, 0]} barSize={28}>
            {DATA.map((entry) => (
              <Cell key={entry.name} fill={entry.fill} />
            ))}
            <LabelList
              dataKey="rate"
              position="right"
              formatter={(v: unknown) => `${v}%`}
              style={{ fill: c.textMuted, fontSize: 12, fontWeight: 600 }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
