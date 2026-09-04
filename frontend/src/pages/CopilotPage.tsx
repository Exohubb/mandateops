import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { AlertTriangle, CheckCircle2, Sparkles, Send } from "lucide-react";
import { motion } from "framer-motion";
import { api } from "../lib/api";
import { Card } from "../components/ui/Card";
import { Badge } from "../components/ui/Badge";

interface ChatMessage {
  role: "user" | "nira";
  text: string;
  grounded?: boolean;
  usedFallback?: boolean;
}

const SUGGESTED_QUESTIONS = [
  "Which bank has the worst recovery rate?",
  "How many attempts were saved by the revocation freeze?",
  "How does MandateOps compare to naive retry overall?",
];

export function CopilotPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");

  const batchesQuery = useQuery({
    queryKey: ["batches-list"],
    queryFn: () => api.listBatches(5),
  });
  const batchId = batchesQuery.data?.[0]?.id ?? null;

  const healthQuery = useQuery({
    queryKey: ["health"],
    queryFn: () => api.health(),
    refetchInterval: 15_000,
  });
  const configured = healthQuery.data?.gemini_configured;

  const askMutation = useMutation({
    mutationFn: (question: string) => api.askCopilot(batchId!, question),
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        {
          role: "nira",
          text: data.answer,
          grounded: data.grounded,
          usedFallback: data.used_fallback,
        },
      ]);
    },
    onError: () => {
      setMessages((prev) => [
        ...prev,
        { role: "nira", text: "Something went wrong reaching Nira. Please try again." },
      ]);
    },
  });

  function send(question: string) {
    if (!question.trim() || !batchId) return;
    setMessages((prev) => [...prev, { role: "user", text: question }]);
    askMutation.mutate(question);
    setInput("");
  }

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Ask Nira</h1>
          <p className="mt-1 text-sm text-text-secondary">
            Nira answers questions grounded strictly in this batch run's data.
            She cannot approve, deny, or schedule a payment.
          </p>
        </div>
        <Badge
          className={
            configured
              ? "text-success-500 bg-success-500/10 border-success-500/30"
              : "text-warning-500 bg-warning-500/10 border-warning-500/30"
          }
        >
          <span className="flex items-center gap-1.5">
            {configured ? <CheckCircle2 size={12} /> : <AlertTriangle size={12} />}
            {configured ? "Gemini live" : "Fallback mode"}
          </span>
        </Badge>
      </div>

      {!batchId && (
        <Card className="text-sm text-text-muted">
          Run a batch from the Dashboard first, then come back to ask Nira
          about it.
        </Card>
      )}

      {batchId && (
        <>
          <div className="flex flex-wrap gap-2">
            {SUGGESTED_QUESTIONS.map((q) => (
              <button
                key={q}
                onClick={() => send(q)}
                className="rounded-full border border-ai-500/30 bg-ai-500/10 px-3 py-1.5 text-xs font-medium text-ai-400 transition-colors hover:bg-ai-500/20"
              >
                {q}
              </button>
            ))}
          </div>

          <Card className="flex h-[480px] flex-col">
            <div className="flex-1 space-y-3 overflow-y-auto pr-1">
              {messages.length === 0 && (
                <div className="flex h-full flex-col items-center justify-center gap-2 text-center text-text-muted">
                  <Sparkles size={28} className="text-ai-400" />
                  <p className="text-sm">Ask Nira anything about this batch run.</p>
                </div>
              )}
              {messages.map((m, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[80%] rounded-xl px-4 py-2.5 text-sm ${
                      m.role === "user"
                        ? "bg-ai-500 text-white"
                        : "border border-border bg-bg text-text-secondary"
                    }`}
                  >
                    {m.text}
                    {m.role === "nira" && (
                      <div
                        className={`mt-1.5 flex items-center gap-1 text-[11px] ${
                          m.usedFallback
                            ? "text-warning-500"
                            : m.grounded
                              ? "text-success-500"
                              : "text-text-muted"
                        }`}
                      >
                        {m.usedFallback ? (
                          <>
                            <AlertTriangle size={11} />
                            Fallback — Gemini unavailable or rate-limited, no AI call made
                          </>
                        ) : m.grounded ? (
                          <>
                            <CheckCircle2 size={11} />
                            Grounded in this run's data
                          </>
                        ) : (
                          "Not found in this run's data"
                        )}
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
              {askMutation.isPending && (
                <div className="text-xs text-text-muted">Nira is thinking…</div>
              )}
            </div>

            <div className="mt-3 flex items-center gap-2 border-t border-border pt-3">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && send(input)}
                placeholder="Ask about this batch run…"
                className="w-full rounded-lg border border-border bg-bg px-3 py-2 text-sm text-text-primary outline-none focus:border-ai-500"
              />
              <button
                onClick={() => send(input)}
                disabled={askMutation.isPending}
                className="flex h-9 w-9 items-center justify-center rounded-lg bg-ai-500 text-white transition-colors hover:bg-ai-600 disabled:opacity-60"
              >
                <Send size={16} />
              </button>
            </div>
          </Card>

          <p className="text-center text-xs text-text-muted">
            Nira cannot approve, deny, or schedule payments — she can only
            explain what already happened.
          </p>
        </>
      )}
    </div>
  );
}
