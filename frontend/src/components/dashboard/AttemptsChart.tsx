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
import type { StrategySummary } from "../../lib/types";

interface AttemptsChartProps {
  naive: StrategySummary | null;
  mandateops: StrategySummary | null;
}

export function AttemptsChart({ naive, mandateops }: AttemptsChartProps) {
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
            <CartesianGrid strokeDasharray="3 3" stroke="#232936" vertical={false} />
            <XAxis dataKey="name" stroke="#64748b" fontSize={12} tickLine={false} />
            <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
            <Tooltip
              contentStyle={{
                background: "#12161f",
                border: "1px solid #232936",
                borderRadius: 8,
                fontSize: 12,
              }}
            />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Bar dataKey="Naive" fill="#94a3b8" radius={[4, 4, 0, 0]} />
            <Bar dataKey="MandateOps" fill="#6366f1" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
