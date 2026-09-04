import { AnimatePresence, motion } from "framer-motion";
import { Card, CardHeader, CardTitle } from "../ui/Card";
import { Badge } from "../ui/Badge";
import { ACTOR_LAYER_COLOR, ACTOR_LAYER_LABEL } from "../../lib/format";
import type { SimulationEventRow } from "../../lib/types";

interface EventFeedProps {
  events: SimulationEventRow[];
}

const EVENT_LABEL: Record<string, string> = {
  ATTEMPT_EXECUTED: "Attempt succeeded",
  ATTEMPT_FAILED: "Attempt failed",
  ATTEMPT_BUDGET_FROZEN: "Budget frozen",
  ATTEMPT_SUPPRESSED: "Attempt suppressed",
  ATTEMPT_BUDGET_EXHAUSTED: "Budget exhausted",
  MANDATE_REVOKED_UPSTREAM: "Mandate revoked upstream",
  NOTIFICATION_SENT: "Notification sent",
  NOTIFICATION_SEND_FAILED: "Notification send failed",
};

export function EventFeed({ events }: EventFeedProps) {
  const recent = events.slice(-40).reverse();

  return (
    <Card delay={0.2} className="flex h-[420px] flex-col">
      <CardHeader>
        <CardTitle>Live Event Feed</CardTitle>
      </CardHeader>
      <div className="flex-1 space-y-1.5 overflow-y-auto pr-1">
        <AnimatePresence initial={false}>
          {recent.map((e, idx) => (
            <motion.div
              key={`${e.mandate_id}-${e.sequence}-${idx}`}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.2 }}
              className="flex items-center justify-between gap-2 rounded-md border border-border bg-bg px-3 py-2 text-xs"
            >
              <div className="flex items-center gap-2 truncate">
                <span className="truncate text-text-secondary">
                  {EVENT_LABEL[e.event_type] ?? e.event_type}
                </span>
                <span className="truncate text-text-muted font-mono-num">
                  {e.mandate_id.slice(0, 14)}…
                </span>
              </div>
              <Badge className={ACTOR_LAYER_COLOR[e.actor_layer] ?? ""}>
                {ACTOR_LAYER_LABEL[e.actor_layer] ?? e.actor_layer}
              </Badge>
            </motion.div>
          ))}
        </AnimatePresence>
        {recent.length === 0 && (
          <div className="flex h-full items-center justify-center text-sm text-text-muted">
            Run a batch to see live events.
          </div>
        )}
      </div>
    </Card>
  );
}
