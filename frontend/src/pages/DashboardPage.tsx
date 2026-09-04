import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { AlertTriangle } from "lucide-react";
import { api } from "../lib/api";
import { ComparisonHero } from "../components/dashboard/ComparisonHero";
import { AttemptsChart } from "../components/dashboard/AttemptsChart";
import { DeclineDonut } from "../components/dashboard/DeclineDonut";
import { RetryHeatmap } from "../components/dashboard/RetryHeatmap";
import { RunControlBar } from "../components/dashboard/RunControlBar";
import { EventFeed } from "../components/dashboard/EventFeed";
import { Card, CardHeader, CardTitle } from "../components/ui/Card";

export function DashboardPage() {
  const [batchId, setBatchId] = useState<string | null>(null);

  const runMutation = useMutation({
    mutationFn: ({ cohortSize, seed }: { cohortSize: number; seed: number }) =>
      api.runBatch(cohortSize, seed),
    onSuccess: (data) => setBatchId(data.batch_id),
  });

  const batchQuery = useQuery({
    queryKey: ["batch", batchId],
    queryFn: () => api.getBatch(batchId!),
    enabled: !!batchId,
  });

  const outcomesQuery = useQuery({
    queryKey: ["outcomes", batchId, "mandateops"],
    queryFn: () => api.getOutcomes(batchId!, "mandateops"),
    enabled: !!batchId,
  });

  const eventsQuery = useQuery({
    queryKey: ["events", batchId, "mandateops"],
    queryFn: () =>
      fetch(`/api/batches/${batchId}/events/mandateops?limit=1000`).then((r) => r.json()),
    enabled: !!batchId,
  });

  const batch = batchQuery.data;

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
                <CardTitle>Nira's Executive Summary</CardTitle>
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
