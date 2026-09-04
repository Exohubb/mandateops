import { useEffect, useRef, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  AlertTriangle,
  Banknote,
  CheckCircle2,
  Landmark,
  Send,
  ShieldQuestion,
  Sparkles,
  Trash2,
  TrendingUp,
} from "lucide-react";
import { motion } from "framer-motion";
import { api } from "../lib/api";
import { Card } from "../components/ui/Card";
import { Badge } from "../components/ui/Badge";
import { clearCache, loadFromCache, saveToCache } from "../lib/sessionCache";
import { cleanAiText } from "../lib/format";

interface ChatMessage {
  role: "user" | "nira";
  text: string;
  grounded?: boolean;
  usedFallback?: boolean;
}

// Grouped, purpose-labeled suggestions rather than one flat row — easier to
// scan, and each icon hints at what kind of question it is before reading
// the text.
const SUGGESTED_QUESTIONS = [
  { icon: Landmark, text: "Which bank has the worst recovery rate, and by how much?" },
  { icon: ShieldQuestion, text: "How many attempts were saved by the revocation freeze?" },
  { icon: TrendingUp, text: "How does MandateOps compare to naive retry overall?" },
  { icon: Banknote, text: "Which decline reason cost the most in unrecovered rupees?" },
];

// Chat history is cached in sessionStorage (not component state alone) so
// switching to another tab and back doesn't wipe the conversation — React
// Router unmounts this page's component tree on navigation, which would
// otherwise reset useState back to its initial value every time.
const CHAT_CACHE_KEY = "mandateops-copilot-chat";
const CHAT_CACHE_TTL_MS = 30 * 60 * 1000; // 30 minutes

export function CopilotPage() {
  const [messages, setMessages] = useState<ChatMessage[]>(
    () => loadFromCache<ChatMessage[]>(CHAT_CACHE_KEY) ?? []
  );
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (messages.length > 0) {
      saveToCache(CHAT_CACHE_KEY, messages, CHAT_CACHE_TTL_MS);
    }
  }, [messages]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  function clearChat() {
    setMessages([]);
    clearCache(CHAT_CACHE_KEY);
  }

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
          text: cleanAiText(data.answer),
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
        <div className="flex items-center gap-2">
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
          {messages.length > 0 && (
            <button
              onClick={clearChat}
              className="flex items-center gap-1.5 rounded-lg border border-border px-2.5 py-1 text-xs text-text-secondary transition-colors hover:border-danger-500/40 hover:text-danger-500"
            >
              <Trash2 size={12} /> Clear chat
            </button>
          )}
        </div>
      </div>

      {!batchId && (
        <Card className="text-sm text-text-muted">
          Run a batch from the Dashboard first, then come back to ask Nira
          about it.
        </Card>
      )}

      {batchId && (
        <>
          <div className="grid gap-2 sm:grid-cols-2">
            {SUGGESTED_QUESTIONS.map(({ icon: Icon, text }) => (
              <button
                key={text}
                onClick={() => send(text)}
                disabled={askMutation.isPending}
                className="flex items-center gap-2.5 rounded-lg border border-ai-500/25 bg-ai-500/5 px-3 py-2.5 text-left text-xs font-medium text-ai-400 transition-colors hover:bg-ai-500/15 disabled:opacity-50"
              >
                <Icon size={14} className="shrink-0" />
                {text}
              </button>
            ))}
          </div>

          <Card className="flex h-[520px] flex-col">
            <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto px-1 py-1">
              {messages.length === 0 && (
                <div className="flex h-full flex-col items-center justify-center gap-2 text-center text-text-muted">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-ai-500/10 text-ai-400">
                    <Sparkles size={22} />
                  </div>
                  <p className="text-sm">Ask Nira anything about this batch run.</p>
                  <p className="text-xs text-text-muted">
                    Try one of the suggestions above to get started.
                  </p>
                </div>
              )}
              {messages.map((m, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2 }}
                  className={`flex items-start gap-2.5 ${
                    m.role === "user" ? "flex-row-reverse" : ""
                  }`}
                >
                  {m.role === "nira" && (
                    <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-ai-500/15 text-ai-400">
                      <Sparkles size={13} />
                    </div>
                  )}
                  <div
                    className={`max-w-[78%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                      m.role === "user"
                        ? "rounded-tr-sm bg-ai-500 text-white"
                        : "rounded-tl-sm border border-border bg-bg text-text-primary"
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{m.text}</p>
                    {m.role === "nira" && (
                      <div
                        className={`mt-2 flex items-center gap-1 border-t pt-1.5 text-[11px] ${
                          m.usedFallback
                            ? "border-warning-500/20 text-warning-500"
                            : m.grounded
                              ? "border-success-500/20 text-success-500"
                              : "border-border text-text-muted"
                        }`}
                      >
                        {m.usedFallback ? (
                          <>
                            <AlertTriangle size={11} />
                            Fallback — Gemini unavailable or rate-limited
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
                <div className="flex items-center gap-2.5">
                  <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-ai-500/15 text-ai-400">
                    <Sparkles size={13} />
                  </div>
                  <div className="flex items-center gap-1 rounded-2xl rounded-tl-sm border border-border bg-bg px-4 py-3">
                    <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-ai-400 [animation-delay:-0.3s]" />
                    <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-ai-400 [animation-delay:-0.15s]" />
                    <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-ai-400" />
                  </div>
                </div>
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
                className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-ai-500 text-white transition-colors hover:bg-ai-600 disabled:opacity-60"
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
