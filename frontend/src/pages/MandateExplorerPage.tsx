import { useEffect, useMemo, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Search, Sparkles } from "lucide-react";
import { api } from "../lib/api";
import { Card } from "../components/ui/Card";
import { Badge } from "../components/ui/Badge";
import { MandateDetailDrawer } from "../components/dashboard/MandateDetailDrawer";
import { useBatchesList } from "../lib/queries";
import {
  STATE_COLOR,
  declineCategoryLabel,
  formatRupees,
  paiseToRupees,
} from "../lib/format";

export function MandateExplorerPage() {
  const queryClient = useQueryClient();
  const [batchId, setBatchId] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [selectedMandate, setSelectedMandate] = useState<string | null>(null);

  const batchesQuery = useBatchesList(20);

  const effectiveBatchId = batchId ?? batchesQuery.data?.[0]?.id ?? null;

  // Poll the batch record itself while Nira's background classification
  // upgrade is still in progress, so this page's decline-reason column and
  // classified-by labels refresh automatically once it completes — the
  // same auto-update behavior as the Live Simulation dashboard, applied
  // everywhere outcome data is shown, not just where the batch was run.
  const batchQuery = useQuery({
    queryKey: ["batch", effectiveBatchId],
    queryFn: () => api.getBatch(effectiveBatchId!),
    enabled: !!effectiveBatchId,
    staleTime: 0,
    refetchOnMount: "always",
    refetchInterval: (query) => {
      const status = query.state.data?.ai_enrichment_status;
      return status === "pending" || status === "running" ? 2000 : false;
    },
  });
  const enrichmentStatus = batchQuery.data?.ai_enrichment_status;

  const outcomesQuery = useQuery({
    queryKey: ["outcomes", effectiveBatchId, "mandateops"],
    queryFn: () => api.getOutcomes(effectiveBatchId!, "mandateops"),
    enabled: !!effectiveBatchId,
    // Without this, navigating here right after creating a batch elsewhere
    // could serve a stale/empty cache entry for up to 30s (the app-wide
    // default staleTime) — the exact "I have to reload to see it" bug.
    staleTime: 0,
    refetchOnMount: "always",
  });

  useEffect(() => {
    if (enrichmentStatus === "completed") {
      queryClient.invalidateQueries({ queryKey: ["outcomes", effectiveBatchId] });
    }
  }, [enrichmentStatus, effectiveBatchId, queryClient]);

  const filtered = useMemo(() => {
    const outcomes = outcomesQuery.data ?? [];
    if (!search.trim()) return outcomes;
    const q = search.toLowerCase();
    return outcomes.filter(
      (o) =>
        o.subscriber_name.toLowerCase().includes(q) ||
        o.bank.toLowerCase().includes(q) ||
        o.mandate_id.toLowerCase().includes(q)
    );
  }, [outcomesQuery.data, search]);

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Mandate Explorer</h1>
          <p className="mt-1 text-sm text-text-secondary">
            Browse every mandate in a batch, its attempt budget, and its
            outcome.
          </p>
          {(enrichmentStatus === "pending" || enrichmentStatus === "running") && (
            <span className="mt-1.5 inline-flex items-center gap-1.5 text-xs text-text-muted">
              <Sparkles size={11} className="text-ai-400" />
              Nira is upgrading decline classifications for this batch…
            </span>
          )}
        </div>
        <select
          value={effectiveBatchId ?? ""}
          onChange={(e) => setBatchId(e.target.value)}
          className="rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text-primary outline-none focus:border-ai-500"
        >
          {batchesQuery.data?.map((b) => (
            <option key={b.id} value={b.id}>
              {b.id} ({b.cohort_size} mandates)
            </option>
          ))}
        </select>
      </div>

      <Card>
        <div className="flex items-center gap-2 rounded-lg border border-border bg-bg px-3 py-2">
          <Search size={16} className="text-text-muted" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by subscriber, bank, or mandate ID…"
            className="w-full bg-transparent text-sm text-text-primary outline-none placeholder:text-text-muted"
          />
        </div>
      </Card>

      <Card className="overflow-x-auto p-0">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left text-xs text-text-muted">
              <th className="px-4 py-3">Subscriber</th>
              <th className="px-4 py-3">Bank</th>
              <th className="px-4 py-3">Decline Reason</th>
              <th className="px-4 py-3">Attempts</th>
              <th className="px-4 py-3">Final State</th>
              <th className="px-4 py-3">Amount</th>
            </tr>
          </thead>
          <tbody>
            {filtered.slice(0, 300).map((o) => (
              <tr
                key={o.mandate_id}
                onClick={() => setSelectedMandate(o.mandate_id)}
                className="cursor-pointer border-b border-border/60 transition-colors hover:bg-surface-hover"
              >
                <td className="px-4 py-3 text-text-primary">{o.subscriber_name}</td>
                <td className="px-4 py-3 font-mono-num text-text-secondary">{o.bank}</td>
                <td className="px-4 py-3 text-text-secondary">
                  {declineCategoryLabel(o.decline_category)}
                </td>
                <td className="px-4 py-3 font-mono-num text-text-secondary">
                  {o.attempts_used}/4
                  {o.attempts_saved > 0 && (
                    <span className="ml-1 text-warning-400">
                      (+{o.attempts_saved} saved)
                    </span>
                  )}
                </td>
                <td className="px-4 py-3">
                  <Badge className={STATE_COLOR[o.final_state] ?? ""}>
                    {o.final_state}
                  </Badge>
                </td>
                <td className="px-4 py-3 font-mono-num text-text-secondary">
                  {formatRupees(paiseToRupees(o.plan_amount_paise))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && (
          <div className="flex h-40 items-center justify-center text-sm text-text-muted">
            {effectiveBatchId ? "No mandates match your search." : "Run a batch from the Dashboard first."}
          </div>
        )}
        {filtered.length > 300 && (
          <div className="px-4 py-3 text-xs text-text-muted">
            Showing first 300 of {filtered.length} matches. Refine your search
            to narrow down.
          </div>
        )}
      </Card>

      {effectiveBatchId && (
        <MandateDetailDrawer
          batchId={effectiveBatchId}
          mandateId={selectedMandate}
          onClose={() => setSelectedMandate(null)}
        />
      )}
    </div>
  );
}
