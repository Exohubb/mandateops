import { useQuery } from "@tanstack/react-query";
import {
  AlertTriangle,
  Bot,
  CheckCircle2,
  Cog,
  MessageSquareText,
  ScrollText,
  ShieldOff,
  Sparkles,
  TrendingUp,
  XCircle,
} from "lucide-react";
import { api } from "../lib/api";
import { Card } from "../components/ui/Card";
import { Badge } from "../components/ui/Badge";

const AI_JOBS = [
  {
    icon: ScrollText,
    title: "Job 1 — Decline-reason normalizer",
    model: "gemma-4-31b-it",
    volume: "Batched · deduplicated · cached",
    input: '"txn declined - insufficient bal"',
    output: "insufficient_funds",
    body: "Real bank decline text is messy free-form strings with no fixed schema — exactly the kind of unstructured-to-structured mapping LLMs are good at. Before calling Gemini, MandateOps deduplicates every raw decline string in a batch (there are only ~25 distinct phrasings even across thousands of mandates), so one small call classifies the entire run instead of one call per mandate.",
  },
  {
    icon: MessageSquareText,
    title: "Job 2 — Customer message composer",
    model: "gemma-4-31b-it",
    volume: "On-demand · cached by (reason, language)",
    input: "template: recovery_link, amount: ₹499",
    output: '"Your payment of ₹499 didn\'t go through — please use the link below to keep your subscription active."',
    body: "Nira drafts the wording only, chosen strictly from merchant-approved template types. She cannot invent a new message purpose, a discount, or a promise that wasn't pre-authorized.",
  },
  {
    icon: Sparkles,
    title: "Job 3 — Ask Nira (grounded copilot)",
    model: "gemma-4-31b-it",
    volume: "Low volume · per user question",
    input: '"Which bank has the worst recovery rate?"',
    output: "Answered strictly from this batch's own aggregates, injected into the prompt as the only source of truth",
    body: "The backend retrieves the relevant numbers from SQLite first, then hands them to Gemini as the only ground truth. If the answer isn't in that data, Nira says so explicitly instead of guessing — this is what makes her grounded rather than a free chatbot.",
  },
  {
    icon: TrendingUp,
    title: "Job 4 — Executive summary",
    model: "gemma-4-31b-it",
    volume: "Once per completed batch run",
    input: "Batch totals: recovered ₹, recovery rate, attempts saved",
    output: '"This batch recovered ₹61,003 vs ₹50,323 under naive retry — a 15pp higher recovery rate, with 56 attempts saved from dead mandates."',
    body: "One paragraph, written once per run, turning raw numbers into the language a finance controller would put in a report. Never invents a figure not present in the input stats.",
  },
];

export function AiJudgmentPage() {
  const { data } = useQuery({
    queryKey: ["ai-judgment-table"],
    queryFn: () => api.getAiJudgmentTable(),
  });

  const healthQuery = useQuery({
    queryKey: ["health"],
    queryFn: () => api.health(),
    refetchInterval: 15_000,
  });

  const configured = healthQuery.data?.gemini_configured;

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

      {/* Live status */}
      <Card
        className={`flex flex-wrap items-center justify-between gap-3 ${
          configured ? "border-success-500/30" : "border-warning-500/30"
        }`}
      >
        <div className="flex items-center gap-3">
          {configured ? (
            <CheckCircle2 className="text-success-500" size={22} />
          ) : (
            <AlertTriangle className="text-warning-500" size={22} />
          )}
          <div>
            <div className="text-sm font-semibold text-text-primary">
              Nira is {configured ? "live" : "running on fallback"}
            </div>
            <div className="text-xs text-text-secondary">
              {configured
                ? "GEMINI_API_KEY configured. AI jobs call Gemini directly, with automatic fallback on rate limits."
                : "No GEMINI_API_KEY configured. Every AI job is using its deterministic fallback substitute right now."}
            </div>
          </div>
        </div>
        <Badge className={configured ? "text-success-500 bg-success-500/10 border-success-500/30" : "text-warning-500 bg-warning-500/10 border-warning-500/30"}>
          {configured ? "gemini_configured: true" : "gemini_configured: false"}
        </Badge>
      </Card>

      {/* The 3-layer split */}
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

      {/* Meet Nira */}
      <Card>
        <div className="flex items-start gap-4">
          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-ai-500/15 text-ai-400">
            <Bot size={22} />
          </div>
          <div>
            <h2 className="text-base font-semibold text-text-primary">
              Meet Nira — the MandateOps Recovery Analyst
            </h2>
            <p className="mt-1.5 text-sm text-text-secondary">
              Nira's system prompt gives her a fixed persona: a precise,
              conservative financial analyst who never invents a number, never
              approves or schedules a payment, and explicitly says "I don't
              have that in this data" rather than guessing. The same persona
              is reused across all four jobs below, so she reads as one
              disciplined analyst rather than four bolted-together AI features.
            </p>
          </div>
        </div>
      </Card>

      {/* The 4 jobs, in detail */}
      <div>
        <h2 className="mb-4 text-lg font-bold text-text-primary">
          Nira's four jobs — and only these four
        </h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {AI_JOBS.map(({ icon: Icon, title, model, volume, input, output, body }, i) => (
            <Card key={title} delay={i * 0.05}>
              <div className="mb-2 flex items-center gap-2">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-ai-500/10 text-ai-400">
                  <Icon size={16} />
                </div>
                <h3 className="text-sm font-semibold text-text-primary">{title}</h3>
              </div>
              <div className="mb-2 flex flex-wrap gap-1.5">
                <Badge className="text-ai-400 bg-ai-500/10 border-ai-500/30">{model}</Badge>
                <Badge className="text-text-secondary bg-border/40 border-border">{volume}</Badge>
              </div>
              <p className="text-xs text-text-secondary">{body}</p>
              <div className="mt-3 space-y-1.5 rounded-lg border border-border bg-bg p-3 text-xs">
                <div>
                  <span className="text-text-muted">Input: </span>
                  <span className="font-mono-num text-text-secondary">{input}</span>
                </div>
                <div>
                  <span className="text-text-muted">Output: </span>
                  <span className="text-success-500">{output}</span>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* The decision table */}
      <div>
        <h2 className="mb-4 text-lg font-bold text-text-primary">
          Every decision, and who's allowed to make it
        </h2>
        <Card className="overflow-x-auto p-0">
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
      </div>

      {/* Free tier / quota honesty */}
      <Card className="flex items-start gap-3 border-warning-500/30">
        <XCircle className="mt-0.5 shrink-0 text-warning-500" size={20} />
        <div>
          <div className="text-sm font-semibold text-text-primary">
            Why you might see the fallback fire often in this demo
          </div>
          <p className="mt-1 text-sm text-text-secondary">
            This build runs on the Gemini API's free tier, which caps
            requests per day per model — often in the low tens to low
            hundreds for the flagship Gemini models. MandateOps mitigates
            this three ways: it deduplicates decline text before ever
            calling the model (turning thousands of mandates into a handful
            of distinct calls), it caches every AI result by content hash so
            identical input never calls the API twice, and it runs on the
            Gemma model family — served on the same free API key but on
            separate, far less congested infrastructure than the flagship
            Gemini models. When a quota or outage happens anyway, the
            fallback takes over automatically — which is itself the AI-layer
            failure-recovery story, not a bug to hide.
          </p>
        </div>
      </Card>

      <Card className="flex items-start gap-3">
        <ShieldOff className="mt-0.5 shrink-0 text-warning-500" size={20} />
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
