import { AnimatePresence, motion } from "framer-motion";
import {
  Banknote,
  Building2,
  CheckCircle2,
  Clock,
  ShieldAlert,
  Tag,
  X,
  XCircle,
} from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../lib/api";
import { Badge } from "../ui/Badge";
import {
  ACTOR_LAYER_COLOR,
  ACTOR_LAYER_LABEL,
  declineCategoryLabel,
  formatRupees,
  paiseToRupees,
} from "../../lib/format";

interface MandateDetailDrawerProps {
  batchId: string;
  mandateId: string | null;
  onClose: () => void;
}

const OUTCOME_META: Record<
  string,
  { label: string; icon: typeof CheckCircle2; color: string; bg: string }
> = {
  RECOVERED: {
    label: "Recovered",
    icon: CheckCircle2,
    color: "text-success-500",
    bg: "bg-success-500/10",
  },
  EXHAUSTED: {
    label: "Attempts Exhausted",
    icon: XCircle,
    color: "text-danger-500",
    bg: "bg-danger-500/10",
  },
  FROZEN_REVOKED: {
    label: "Frozen — Revoked",
    icon: ShieldAlert,
    color: "text-warning-500",
    bg: "bg-warning-500/10",
  },
  FROZEN_PAUSED: {
    label: "Frozen — Paused",
    icon: ShieldAlert,
    color: "text-warning-500",
    bg: "bg-warning-500/10",
  },
  FROZEN_NOTIFICATION_FAILED: {
    label: "Frozen — Notice Failed",
    icon: ShieldAlert,
    color: "text-warning-500",
    bg: "bg-warning-500/10",
  },
  PENDING: {
    label: "Pending",
    icon: Clock,
    color: "text-text-secondary",
    bg: "bg-border/40",
  },
};

export function MandateDetailDrawer({
  batchId,
  mandateId,
  onClose,
}: MandateDetailDrawerProps) {
  const { data } = useQuery({
    queryKey: ["mandate-detail", batchId, mandateId],
    queryFn: () => api.getMandateDetail(batchId, mandateId!),
    enabled: !!mandateId,
  });

  const outcome = data?.mandateops ?? data?.naive;
  const attemptsUsed = outcome?.attempts_used ?? 0;
  const meta = outcome ? OUTCOME_META[outcome.final_state] ?? OUTCOME_META.PENDING : null;
  const OutcomeIcon = meta?.icon ?? Clock;

  return (
    <AnimatePresence>
      {mandateId && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 z-30 bg-black/40 backdrop-blur-sm dark:bg-black/60"
          />
          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "tween", duration: 0.28, ease: "easeOut" }}
            className="fixed inset-y-0 right-0 z-40 w-full max-w-lg overflow-y-auto border-l border-border bg-surface shadow-2xl"
          >
            <button
              onClick={onClose}
              className="absolute right-4 top-4 z-10 rounded-full bg-surface p-1.5 text-text-muted shadow-sm transition-colors hover:bg-surface-hover hover:text-text-primary"
            >
              <X size={16} />
            </button>

            {outcome && meta && (
              <div>
                {/* Hero banner, colored by outcome */}
                <div className={`px-6 pb-6 pt-8 ${meta.bg}`}>
                  <div className="flex items-center gap-2 text-xs font-medium text-text-muted">
                    <Tag size={12} />
                    Mandate Detail
                  </div>
                  <div className="mt-3 flex items-center gap-3">
                    <div className={`flex h-12 w-12 items-center justify-center rounded-full ${meta.bg} ${meta.color}`}>
                      <OutcomeIcon size={22} />
                    </div>
                    <div>
                      <div className="text-lg font-bold text-text-primary">
                        {outcome.subscriber_name}
                      </div>
                      <div className="font-mono-num text-xs text-text-muted">
                        {outcome.mandate_id}
                      </div>
                    </div>
                  </div>
                  <div className={`mt-4 inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold ${meta.bg} ${meta.color}`}>
                    <OutcomeIcon size={13} />
                    {meta.label}
                  </div>
                </div>

                <div className="space-y-6 p-6">
                  {/* Key stats grid */}
                  <div className="grid grid-cols-2 gap-3">
                    <div className="rounded-xl border border-border bg-bg p-3.5">
                      <div className="flex items-center gap-1.5 text-[11px] text-text-muted">
                        <Building2 size={12} /> Bank
                      </div>
                      <div className="mt-1 text-sm font-semibold text-text-primary">
                        {outcome.bank}
                      </div>
                    </div>
                    <div className="rounded-xl border border-border bg-bg p-3.5">
                      <div className="flex items-center gap-1.5 text-[11px] text-text-muted">
                        <Banknote size={12} /> Plan amount
                      </div>
                      <div className="mt-1 font-mono-num text-sm font-semibold text-text-primary">
                        {formatRupees(paiseToRupees(outcome.plan_amount_paise))}
                      </div>
                    </div>
                    <div className="rounded-xl border border-border bg-bg p-3.5">
                      <div className="text-[11px] text-text-muted">Decline reason</div>
                      <div className="mt-1 text-sm font-semibold text-text-primary">
                        {declineCategoryLabel(outcome.decline_category)}
                      </div>
                    </div>
                    <div className="rounded-xl border border-border bg-bg p-3.5">
                      <div className="text-[11px] text-text-muted">Classified by</div>
                      <div className="mt-1 text-sm font-semibold text-ai-400">
                        {outcome.classified_by === "nira" ? "Nira (AI)" : "Fallback rules"}
                      </div>
                    </div>
                  </div>

                  {/* Attempt budget gauge */}
                  <div className="rounded-xl border border-border bg-bg p-4">
                    <div className="mb-2.5 flex items-center justify-between text-xs">
                      <span className="font-medium text-text-secondary">Attempt budget</span>
                      <span className="font-mono-num text-text-muted">{attemptsUsed} / 4 used</span>
                    </div>
                    <div className="flex gap-1.5">
                      {Array.from({ length: 4 }).map((_, i) => (
                        <div
                          key={i}
                          className={`h-2.5 flex-1 rounded-full transition-colors ${
                            i < attemptsUsed ? "bg-ai-500" : "bg-border-strong"
                          }`}
                        />
                      ))}
                    </div>
                    {outcome.attempts_saved > 0 && (
                      <p className="mt-3 flex items-center gap-1.5 text-xs text-warning-500">
                        <ShieldAlert size={13} />
                        {outcome.attempts_saved} attempt(s) saved by freezing instead of
                        burning on a dead mandate.
                      </p>
                    )}
                  </div>

                  {/* Raw decline text */}
                  <div>
                    <div className="mb-2 text-xs font-medium text-text-muted">
                      Raw decline text (as received)
                    </div>
                    <p className="rounded-xl border border-border bg-bg p-3.5 font-mono-num text-xs text-text-secondary">
                      "{outcome.decline_raw_text}"
                    </p>
                  </div>

                  {/* Event timeline */}
                  <div>
                    <div className="mb-3 text-xs font-medium text-text-muted">
                      Event timeline — MandateOps strategy
                    </div>
                    <div className="relative space-y-3 pl-4">
                      <div className="absolute bottom-1 left-[3px] top-1 w-px bg-border" />
                      {data?.events?.map((e) => (
                        <div key={e.id} className="relative flex items-center justify-between gap-2">
                          <span className="absolute -left-4 top-1/2 h-2 w-2 -translate-y-1/2 rounded-full border-2 border-surface bg-ai-500" />
                          <span className="text-xs text-text-secondary">{e.event_type}</span>
                          <Badge className={ACTOR_LAYER_COLOR[e.actor_layer] ?? ""}>
                            {ACTOR_LAYER_LABEL[e.actor_layer] ?? e.actor_layer}
                          </Badge>
                        </div>
                      ))}
                      {(!data?.events || data.events.length === 0) && (
                        <p className="text-xs text-text-muted">No events recorded.</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
