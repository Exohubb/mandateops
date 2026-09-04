import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { CHART_COLORS, useTheme } from "../../lib/theme";

// UPI AutoPay approval-rate trend, sourced from Moneycontrol's reporting on
// NPCI/industry data. Interpolated between the two cited data points to
// show the trajectory — the two solid endpoints are the real figures.
const DATA = [
  { period: "Jan 2024", rate: 50 },
  { period: "Jun 2024", rate: 43 },
  { period: "Dec 2024", rate: 37 },
  { period: "Jun 2025", rate: 32 },
  { period: "Nov 2025", rate: 30 },
];

export function ApprovalRateTrendChart() {
  const { theme } = useTheme();
  const c = CHART_COLORS[theme];

  return (
    <div className="h-56">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={DATA} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
          <defs>
            <linearGradient id="approvalGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#f43f5e" stopOpacity={0.35} />
              <stop offset="100%" stopColor="#f43f5e" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke={c.grid} vertical={false} />
          <XAxis dataKey="period" stroke={c.axis} fontSize={11} tickLine={false} />
          <YAxis
            stroke={c.axis}
            fontSize={11}
            tickLine={false}
            axisLine={false}
            unit="%"
            domain={[20, 55]}
          />
          <Tooltip
            contentStyle={{
              background: c.tooltipBg,
              border: `1px solid ${c.tooltipBorder}`,
              borderRadius: 8,
              fontSize: 12,
              color: c.textMuted,
            }}
            formatter={(value) => [`${value}%`, "Approval rate"]}
          />
          <Area
            type="monotone"
            dataKey="rate"
            stroke="#f43f5e"
            strokeWidth={2}
            fill="url(#approvalGradient)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
