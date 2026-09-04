import { AnimatePresence, motion } from "framer-motion";
import { X } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../lib/api";
import { Badge } from "../ui/Badge";
import {
  ACTOR_LAYER_COLOR,
  ACTOR_LAYER_LABEL,
  STATE_COLOR,
  formatRupees,
  paiseToRupees,
} from "../../lib/format";

interface MandateDetailDrawerProps {
  batchId: string;
  mandateId: string | null;
  onClose: () => void;
}

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
  const attemptsRemaining = Math.max(0, 4 - attemptsUsed);

  return (
    <AnimatePresence>
      {mandateId && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 z-30 bg-black/60"
          />
          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "tween", duration: 0.25 }}
            className="fixed inset-y-0 right-0 z-40 w-full max-w-md overflow-y-auto border-l border-border bg-surface p-6"
          >
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-text-primary">
                Mandate Detail
              </h2>
              <button
                onClick={onClose}
                className="rounded-md p-1 text-text-muted hover:bg-surface-hover hover:text-text-primary"
              >
                <X size={18} />
              </button>
            </div>

            {outcome && (
              <div className="mt-5 space-y-5">
                <div>
                  <div className="text-lg font-semibold text-text-primary">
                    {outcome.subscriber_name}
                  </div>
                  <div className="text-xs text-text-muted font-mono-num">
                    {outcome.mandate_id}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <div className="text-text-muted">Bank</div>
                    <div className="font-medium text-text-primary">{outcome.bank}</div>
                  </div>
                  <div>
                    <div className="text-text-muted">Plan amount</div>
                    <div className="font-medium text-text-primary font-mono-num">
                      {formatRupees(paiseToRupees(outcome.plan_amount_paise))}
                    </div>
                  </div>
                  <div>
                    <div className="text-text-muted">Final state</div>
                    <Badge className={STATE_COLOR[outcome.final_state] ?? ""}>
                      {outcome.final_state}
                    </Badge>
                  </div>
                  <div>
                    <div className="text-text-muted">Classified by</div>
                    <div className="font-medium text-text-primary text-xs">
                      {outcome.classified_by}
                    </div>
                  </div>
                </div>

                {/* Attempt budget gauge */}
                <div>
                  <div className="mb-2 flex items-center justify-between text-xs text-text-muted">
                    <span>Attempt budget</span>
                    <span className="font-mono-num">
                      {attemptsUsed} / 4 used
                    </span>
                  </div>
                  <div className="flex gap-1.5">
                    {Array.from({ length: 4 }).map((_, i) => (
                      <div
                        key={i}
                        className={`h-2 flex-1 rounded-full ${
                          i < attemptsUsed ? "bg-ai-500" : "bg-white/10"
                        }`}
                      />
                    ))}
                  </div>
                  {attemptsRemaining > 0 && outcome.attempts_saved > 0 && (
                    <p className="mt-2 text-xs text-warning-400">
                      {outcome.attempts_saved} attempt(s) saved by freezing
                      instead of burning on a dead mandate.
                    </p>
                  )}
                </div>

                <div>
                  <div className="mb-2 text-xs font-medium text-text-muted">
                    Raw decline text
                  </div>
                  <p className="rounded-md border border-border bg-bg p-3 text-xs text-text-secondary">
                    {outcome.decline_raw_text}
                  </p>
                </div>

                <div>
                  <div className="mb-2 text-xs font-medium text-text-muted">
                    Event timeline (MandateOps)
                  </div>
                  <div className="space-y-2">
                    {data?.events?.map((e) => (
                      <div
                        key={e.id}
                        className="flex items-center justify-between gap-2 rounded-md border border-border bg-bg px-3 py-2 text-xs"
                      >
                        <span className="text-text-secondary">{e.event_type}</span>
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
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
