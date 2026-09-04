import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { Card, CardHeader, CardTitle } from "../ui/Card";
import { declineCategoryLabel } from "../../lib/format";
import { CHART_COLORS, useTheme } from "../../lib/theme";
import type { MandateOutcome } from "../../lib/types";

interface DeclineDonutProps {
  outcomes: MandateOutcome[];
}

const COLORS: Record<string, string> = {
  insufficient_funds: "#6366f1",
  bank_down: "#f59e0b",
  mandate_paused: "#94a3b8",
  mandate_revoked: "#f43f5e",
  other: "#34d399",
  unclassified: "#64748b",
};

export function DeclineDonut({ outcomes }: DeclineDonutProps) {
  const { theme } = useTheme();
  const c = CHART_COLORS[theme];
  const counts = new Map<string, number>();
  for (const o of outcomes) {
    counts.set(o.decline_category, (counts.get(o.decline_category) ?? 0) + 1);
  }
  const data = Array.from(counts.entries()).map(([category, count]) => ({
    name: declineCategoryLabel(category),
    value: count,
    color: COLORS[category] ?? "#64748b",
  }));

  return (
    <Card delay={0.1}>
      <CardHeader>
        <CardTitle>Decline Reason Breakdown (AI-classified)</CardTitle>
      </CardHeader>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              innerRadius={55}
              outerRadius={85}
              paddingAngle={2}
            >
              {data.map((entry) => (
                <Cell key={entry.name} fill={entry.color} stroke="none" />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                background: c.tooltipBg,
                border: `1px solid ${c.tooltipBorder}`,
                borderRadius: 8,
                fontSize: 12,
                color: c.textMuted,
              }}
            />
            <Legend wrapperStyle={{ fontSize: 11, color: c.textMuted }} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
