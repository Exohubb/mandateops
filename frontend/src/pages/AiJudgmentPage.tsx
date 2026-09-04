import { useQuery } from "@tanstack/react-query";
import { Bot, Cog, ShieldOff, TrendingUp } from "lucide-react";
import { api } from "../lib/api";
import { Card } from "../components/ui/Card";

export function AiJudgmentPage() {
  const { data } = useQuery({
    queryKey: ["ai-judgment-table"],
    queryFn: () => api.getAiJudgmentTable(),
  });

  return (
    <div className="space-y-8 pb-12">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">How We Use AI</h1>
        <p className="mt-2 max-w-2xl text-sm text-text-secondary">
          The question every judge is implicitly scoring: where did you use
          AI, and — more importantly — where did you deliberately choose not
          to? Here's the exact answer, decision by decision.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <Cog className="mb-2 text-text-secondary" size={20} />
          <div className="text-sm font-semibold text-text-primary">Deterministic</div>
          <p className="mt-1 text-xs text-text-secondary">
            State machine, attempt ledger, compliance gate. 100% reproducible.
            No model ever touches a rupee amount or a retry decision.
          </p>
        </Card>
        <Card delay={0.05}>
          <TrendingUp className="mb-2 text-ai-400" size={20} />
          <div className="text-sm font-semibold text-text-primary">Statistical</div>
          <p className="mt-1 text-xs text-text-secondary">
            Empirical-Bayes retry-slot scorer. Inspectable math, reports its
            own sample size, refuses to overclaim on thin data.
          </p>
        </Card>
        <Card delay={0.1}>
          <Bot className="mb-2 text-ai-400" size={20} />
          <div className="text-sm font-semibold text-text-primary">Nira (Gemini)</div>
          <p className="mt-1 text-xs text-text-secondary">
            Reads messy text: decline reasons, customer messages, grounded
            Q&A, executive summaries. Never decides, never schedules.
          </p>
        </Card>
      </div>

      <Card>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left text-xs text-text-muted">
              <th className="px-4 py-3">Decision</th>
              <th className="px-4 py-3">Made by</th>
              <th className="px-4 py-3">Why</th>
            </tr>
          </thead>
          <tbody>
            {data?.map((row) => (
              <tr key={row.decision} className="border-b border-border/60 align-top">
                <td className="px-4 py-3 font-medium text-text-primary">
                  {row.decision}
                </td>
                <td className="px-4 py-3 text-ai-400">{row.made_by}</td>
                <td className="px-4 py-3 text-text-secondary">{row.why}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>

      <Card className="flex items-start gap-3">
        <ShieldOff className="mt-0.5 shrink-0 text-warning-400" size={20} />
        <div>
          <div className="text-sm font-semibold text-text-primary">
            AI availability is never a single point of failure
          </div>
          <p className="mt-1 text-sm text-text-secondary">
            If Gemini is unavailable, rate-limited, or not configured, every
            AI job falls back to a deterministic substitute automatically.
            Every record it touches is tagged{" "}
            <code className="rounded bg-bg px-1 py-0.5 text-xs">
              classified_by: fallback_rule_engine
            </code>{" "}
            instead of{" "}
            <code className="rounded bg-bg px-1 py-0.5 text-xs">nira</code>,
            so the degradation is honest and visible — never hidden.
          </p>
        </div>
      </Card>
    </div>
  );
}
