import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, Sparkles, Trash2 } from "lucide-react";
import { api } from "../lib/api";
import { ComparisonHero } from "../components/dashboard/ComparisonHero";
import { AttemptsChart } from "../components/dashboard/AttemptsChart";
import { DeclineDonut } from "../components/dashboard/DeclineDonut";
import { RetryHeatmap } from "../components/dashboard/RetryHeatmap";
import { RunControlBar } from "../components/dashboard/RunControlBar";
import { EventFeed } from "../components/dashboard/EventFeed";
import { Card, CardHeader, CardTitle } from "../components/ui/Card";
import { Badge } from "../components/ui/Badge";
import { loadFromCache, saveToCache } from "../lib/sessionCache";
import { invalidateBatchesList, useBatchesList } from "../lib/queries";

// The currently-viewed batch id is cached so navigating away to another
// tab and back keeps showing the same run instead of resetting to the
// empty state — the batch DATA itself already lives permanently in
// SQLite, this just remembers "which one was I looking at."
const SELECTED_BATCH_CACHE_KEY = "mandateops-selected-batch-id";
const SELECTED_BATCH_TTL_MS = 12 * 60 * 60 * 1000; // 12 hours

export function DashboardPage() {
  const queryClient = useQueryClient();
  const [batchId, setBatchId] = useState<string | null>(() =>
    loadFromCache<string>(SELECTED_BATCH_CACHE_KEY)
  );

  useEffect(() => {
    if (batchId) {
      saveToCache(SELECTED_BATCH_CACHE_KEY, batchId, SELECTED_BATCH_TTL_MS);
    }
  }, [batchId]);

  // The simulation math itself resolves in milliseconds, but showing a
  // batch appear literally instantly reads as "did that even run?" rather
  // than "a batch of mandates was just simulated." A short artificial
  // minimum duration gives the run a perceptible, deliberate feel — long
  // enough to register as "processing," short enough to never feel slow.
  const MIN_RUN_DURATION_MS = 3000;

  const runMutation = useMutation({
    mutationFn: async ({ cohortSize, seed }: { cohortSize: number; seed: number }) => {
      const [result] = await Promise.all([
        api.runBatch(cohortSize, seed),
        new Promise((resolve) => setTimeout(resolve, MIN_RUN_DURATION_MS)),
      ]);
      return result;
    },
    onSuccess: (data) => {
      setBatchId(data.batch_id);
      // A new batch now exists — every page's batches-list query (this
      // one, Mandate Explorer's, Ask Nira's, Audit Trail's) must refetch
      // rather than keep showing the pre-creation snapshot.
      invalidateBatchesList(queryClient);
    },
  });

  const batchesListQuery = useBatchesList(20);

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.deleteBatch(id),
    onSuccess: (_data, deletedId) => {
      invalidateBatchesList(queryClient);
      queryClient.removeQueries({ queryKey: ["batch", deletedId] });
      if (batchId === deletedId) {
        setBatchId(null);
      }
    },
  });

  const batchQuery = useQuery({
    queryKey: ["batch", batchId],
    queryFn: () => api.getBatch(batchId!),
    enabled: !!batchId,
    retry: false,
    // While Nira's background enrichment is still running, poll every 2s
    // so the executive summary and decline classifications upgrade in
    // place automatically once she's done — no manual refresh needed.
    refetchInterval: (query) => {
      const status = query.state.data?.ai_enrichment_status;
      return status === "pending" || status === "running" ? 2000 : false;
    },
  });

  // If the cached batch id points at a run that's since been deleted (404),
  // fall back to the empty state instead of showing a permanent error.
  useEffect(() => {
    if (batchQuery.isError && batchId) {
      setBatchId(null);
    }
  }, [batchQuery.isError, batchId]);

  const batch = batchQuery.data;

  const outcomesQuery = useQuery({
    queryKey: ["outcomes", batchId, "mandateops"],
    queryFn: () => api.getOutcomes(batchId!, "mandateops"),
    enabled: !!batchId,
  });

  // Once AI enrichment flips to completed, the decline-category/
  // classified_by columns on every outcome may have changed — refetch
  // once so the donut chart and any open mandate details reflect the
  // upgraded (real Nira) classification instead of the fallback rules.
  const enrichmentStatus = batch?.ai_enrichment_status;
  useEffect(() => {
    if (enrichmentStatus === "completed") {
      queryClient.invalidateQueries({ queryKey: ["outcomes", batchId] });
    }
  }, [enrichmentStatus, batchId, queryClient]);

  const eventsQuery = useQuery({
    queryKey: ["events", batchId, "mandateops"],
    queryFn: () =>
      fetch(`/api/batches/${batchId}/events/mandateops?limit=1000`).then((r) => r.json()),
    enabled: !!batchId,
  });

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Live Simulation</h1>
        <p className="mt-1 text-sm text-text-secondary">
          Run a synthetic batch of failed UPI AutoPay mandates through both
          strategies and compare the result.
        </p>
      </div>

      <RunControlBar
        onRun={(cohortSize, seed) => runMutation.mutate({ cohortSize, seed })}
        isRunning={runMutation.isPending}
      />

      {batchesListQuery.data && batchesListQuery.data.length > 0 && (
        <Card delay={0.02}>
          <CardHeader>
            <CardTitle>Previous Simulations</CardTitle>
          </CardHeader>
          <div className="flex flex-wrap gap-2">
            {batchesListQuery.data.map((b) => (
              <div
                key={b.id}
                className={`flex items-center gap-2 rounded-lg border px-3 py-1.5 text-xs transition-colors ${
                  b.id === batchId
                    ? "border-ai-500/50 bg-ai-500/10 text-ai-400"
                    : "border-border text-text-secondary hover:bg-surface-hover"
                }`}
              >
                <button
                  onClick={() => setBatchId(b.id)}
                  className="font-mono-num"
                  title={`Cohort size ${b.cohort_size}, seed ${b.seed}`}
                >
                  {b.id.replace("batch-", "")}
                </button>
                <button
                  onClick={() => deleteMutation.mutate(b.id)}
                  disabled={deleteMutation.isPending}
                  className="text-text-muted transition-colors hover:text-danger-500 disabled:opacity-50"
                  title="Delete this simulation"
                >
                  <Trash2 size={12} />
                </button>
              </div>
            ))}
          </div>
        </Card>
      )}

      {runMutation.isError && (
        <Card className="flex items-center gap-2 border-danger-500/30 text-danger-400">
          <AlertTriangle size={16} />
          <span className="text-sm">Batch run failed. Check the backend logs.</span>
        </Card>
      )}

      {batch && (
        <>
          <ComparisonHero
            naive={batch.naive_summary}
            mandateops={batch.mandateops_summary}
          />

          {batch.executive_summary_text && (
            <Card delay={0.02}>
              <CardHeader>
                <CardTitle>Executive Summary</CardTitle>
                {batch.ai_enrichment_status === "completed" ? (
                  <Badge className="text-ai-400 bg-ai-500/10 border-ai-500/30">
                    <span className="flex items-center gap-1">
                      <Sparkles size={11} /> Written by Nira
                    </span>
                  </Badge>
                ) : batch.ai_enrichment_status === "failed" ? (
                  <Badge className="text-warning-500 bg-warning-500/10 border-warning-500/30">
                    <span className="flex items-center gap-1">
                      <AlertTriangle size={11} /> Fallback text
                    </span>
                  </Badge>
                ) : (
                  <Badge className="text-text-secondary bg-border/40 border-border">
                    <span className="flex items-center gap-1.5">
                      <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-ai-400" />
                      Nira is upgrading this…
                    </span>
                  </Badge>
                )}
              </CardHeader>
              <p className="text-sm leading-relaxed text-text-secondary">
                {batch.executive_summary_text}
              </p>
            </Card>
          )}

          <div className="grid gap-6 lg:grid-cols-2">
            <AttemptsChart
              naive={batch.naive_summary}
              mandateops={batch.mandateops_summary}
            />
            <DeclineDonut outcomes={outcomesQuery.data ?? []} />
          </div>

          <div className="grid gap-6 lg:grid-cols-[1.4fr_1fr]">
            <RetryHeatmap declineCategory="insufficient_funds" />
            <EventFeed events={eventsQuery.data ?? []} />
          </div>
        </>
      )}

      {!batch && !runMutation.isPending && (
        <Card className="flex h-64 items-center justify-center text-sm text-text-muted">
          Run a batch above to see the comparison.
        </Card>
      )}
    </div>
  );
}
