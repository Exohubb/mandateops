import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card, CardHeader, CardTitle } from "../ui/Card";
import { CHART_COLORS, useTheme } from "../../lib/theme";
import type { StrategySummary } from "../../lib/types";

interface AttemptsChartProps {
  naive: StrategySummary | null;
  mandateops: StrategySummary | null;
}

export function AttemptsChart({ naive, mandateops }: AttemptsChartProps) {
  const { theme } = useTheme();
  const c = CHART_COLORS[theme];
  const data = [
    {
      name: "Attempts Used",
      Naive: naive?.total_attempts_used ?? 0,
      MandateOps: mandateops?.total_attempts_used ?? 0,
    },
    {
      name: "Attempts Saved",
      Naive: naive?.total_attempts_saved ?? 0,
      MandateOps: mandateops?.total_attempts_saved ?? 0,
    },
  ];

  return (
    <Card delay={0.05}>
      <CardHeader>
        <CardTitle>Attempts Consumed vs. Attempts Saved</CardTitle>
      </CardHeader>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} barGap={6}>
            <CartesianGrid strokeDasharray="3 3" stroke={c.grid} vertical={false} />
            <XAxis dataKey="name" stroke={c.axis} fontSize={12} tickLine={false} />
            <YAxis stroke={c.axis} fontSize={12} tickLine={false} axisLine={false} />
            <Tooltip
              contentStyle={{
                background: c.tooltipBg,
                border: `1px solid ${c.tooltipBorder}`,
                borderRadius: 8,
                fontSize: 12,
                color: c.textMuted,
              }}
            />
            <Legend wrapperStyle={{ fontSize: 12, color: c.textMuted }} />
            <Bar dataKey="Naive" fill={c.axis} radius={[4, 4, 0, 0]} />
            <Bar dataKey="MandateOps" fill="#6366f1" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
