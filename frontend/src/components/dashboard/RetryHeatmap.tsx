import { useQuery } from "@tanstack/react-query";
import { api } from "../../lib/api";
import { Card, CardHeader, CardTitle } from "../ui/Card";
import { declineCategoryLabel } from "../../lib/format";

interface RetryHeatmapProps {
  declineCategory: string;
}

/** Bank x hour heatmap of the empirical-Bayes scorer's shrunk success
 * probability. Cells with insufficient historical support are rendered
 * hatched/greyed rather than colored with false confidence — this is the
 * scorer's honesty about thin data, made visible.
 */
export function RetryHeatmap({ declineCategory }: RetryHeatmapProps) {
  const { data, isLoading } = useQuery({
    queryKey: ["heatmap", declineCategory],
    queryFn: () => api.getHeatmap(declineCategory),
  });

  if (isLoading || !data) {
    return (
      <Card delay={0.15}>
        <CardHeader>
          <CardTitle>Retry Slot Success Heatmap</CardTitle>
        </CardHeader>
        <div className="flex h-48 items-center justify-center text-sm text-text-muted">
          Loading heatmap…
        </div>
      </Card>
    );
  }

  const banks = Array.from(new Set(data.map((d) => d.bank_code)));
  const hours = Array.from(new Set(data.map((d) => d.hour))).sort((a, b) => a - b);
  const cellByKey = new Map(data.map((d) => [`${d.bank_code}-${d.hour}`, d]));

  return (
    <Card delay={0.15}>
      <CardHeader>
        <CardTitle>
          Retry Slot Success Heatmap — {declineCategoryLabel(declineCategory)}
        </CardTitle>
      </CardHeader>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-xs">
          <thead>
            <tr>
              <th className="sticky left-0 bg-surface px-2 py-1 text-left text-text-muted">
                Bank
              </th>
              {hours.map((h) => (
                <th key={h} className="px-1 py-1 text-center font-mono-num text-text-muted">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {banks.map((bank) => (
              <tr key={bank}>
                <td className="sticky left-0 bg-surface px-2 py-1 font-medium text-text-secondary">
                  {bank}
                </td>
                {hours.map((h) => {
                  const cell = cellByKey.get(`${bank}-${h}`);
                  const p = cell?.shrunk_probability ?? 0;
                  const sufficient = cell?.sufficient_support ?? false;
                  const intensity = Math.min(1, p / 0.6);
                  return (
                    <td key={h} className="px-1 py-1 text-center">
                      <div
                        title={
                          sufficient
                            ? `p=${p.toFixed(2)} (n=${cell?.observed_trials})`
                            : `Insufficient data — using global prior (n=${cell?.observed_trials ?? 0})`
                        }
                        className="mx-auto h-5 w-5 rounded-sm"
                        style={{
                          backgroundColor: sufficient
                            ? `rgba(99, 102, 241, ${0.15 + intensity * 0.75})`
                            : "transparent",
                          border: sufficient
                            ? "none"
                            : "1px dashed rgba(148, 163, 184, 0.4)",
                        }}
                      />
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-3 text-[11px] text-text-muted">
        Solid cells: sufficient historical data. Dashed outline: insufficient
        support — the scorer falls back to the global prior rather than
        overclaiming confidence.
      </p>
    </Card>
  );
}
