import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { CheckCircle2, ShieldCheck, XCircle } from "lucide-react";
import { api } from "../lib/api";
import { Card, CardHeader, CardTitle } from "../components/ui/Card";
import { Badge } from "../components/ui/Badge";
import { ACTOR_LAYER_COLOR, ACTOR_LAYER_LABEL } from "../lib/format";

export function AuditTrailPage() {
  const [batchId, setBatchId] = useState<string | null>(null);

  const batchesQuery = useQuery({
    queryKey: ["batches-list"],
    queryFn: () => api.listBatches(20),
  });
  const effectiveBatchId = batchId ?? batchesQuery.data?.[0]?.id ?? null;

  const auditQuery = useQuery({
    queryKey: ["audit", effectiveBatchId],
    queryFn: () => api.getAuditTrail(effectiveBatchId!, 300),
    enabled: !!effectiveBatchId,
  });

  const verifyMutation = useMutation({
    mutationFn: () => api.verifyChain(effectiveBatchId!),
  });

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Audit Trail</h1>
          <p className="mt-1 text-sm text-text-secondary">
            Every decision, hash-chained. Tamper with one row and every hash
            after it stops matching.
          </p>
        </div>
        <select
          value={effectiveBatchId ?? ""}
          onChange={(e) => setBatchId(e.target.value)}
          className="rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text-primary outline-none focus:border-ai-500"
        >
          {batchesQuery.data?.map((b) => (
            <option key={b.id} value={b.id}>
              {b.id}
            </option>
          ))}
        </select>
      </div>

      <Card className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-ai-500/10 text-ai-400">
            <ShieldCheck size={20} />
          </div>
          <div>
            <div className="text-sm font-medium text-text-primary">
              Chain Integrity
            </div>
            <div className="text-xs text-text-muted">
              Recomputes every hash and confirms the chain is intact.
            </div>
          </div>
        </div>
        <button
          onClick={() => verifyMutation.mutate()}
          disabled={!effectiveBatchId || verifyMutation.isPending}
          className="rounded-lg bg-ai-500 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-ai-600 disabled:opacity-60"
        >
          {verifyMutation.isPending ? "Verifying…" : "Verify Chain Integrity"}
        </button>
      </Card>

      {verifyMutation.data && (
        <Card
          className={`flex items-center gap-3 ${
            verifyMutation.data.valid
              ? "border-success-500/30"
              : "border-danger-500/30"
          }`}
        >
          {verifyMutation.data.valid ? (
            <CheckCircle2 className="text-success-400" size={20} />
          ) : (
            <XCircle className="text-danger-400" size={20} />
          )}
          <span
            className={`text-sm font-medium ${
              verifyMutation.data.valid ? "text-success-400" : "text-danger-400"
            }`}
          >
            {verifyMutation.data.valid
              ? `Chain verified — ${verifyMutation.data.total_events} events, all hashes match.`
              : `Tampering detected at sequence ${verifyMutation.data.first_invalid_sequence}.`}
          </span>
        </Card>
      )}

      <Card delay={0.05} className="overflow-x-auto p-0">
        <CardHeader>
          <CardTitle>Event Log</CardTitle>
        </CardHeader>
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-border text-left text-text-muted">
              <th className="px-4 py-2">Seq</th>
              <th className="px-4 py-2">Event</th>
              <th className="px-4 py-2">Layer</th>
              <th className="px-4 py-2">This Hash</th>
            </tr>
          </thead>
          <tbody>
            {auditQuery.data?.slice(0, 200).map((e) => (
              <tr key={e.id} className="border-b border-border/60">
                <td className="px-4 py-2 font-mono-num text-text-muted">{e.sequence}</td>
                <td className="px-4 py-2 text-text-secondary">{e.event_type}</td>
                <td className="px-4 py-2">
                  <Badge className={ACTOR_LAYER_COLOR[e.actor_layer] ?? ""}>
                    {ACTOR_LAYER_LABEL[e.actor_layer] ?? e.actor_layer}
                  </Badge>
                </td>
                <td className="px-4 py-2 font-mono-num text-text-muted">
                  {e.this_hash.slice(0, 16)}…
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {(!auditQuery.data || auditQuery.data.length === 0) && (
          <div className="flex h-32 items-center justify-center text-sm text-text-muted">
            No audit events yet — run a batch first.
          </div>
        )}
      </Card>
    </div>
  );
}
