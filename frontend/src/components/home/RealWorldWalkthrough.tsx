import { motion } from "framer-motion";
import {
  BellRing,
  CalendarClock,
  CheckCircle2,
  ShieldOff,
  Wallet,
} from "lucide-react";

const STEPS = [
  {
    icon: Wallet,
    time: "Day 0, 9:14 AM",
    title: "A subscription debit fails",
    body: "A ₹499 OTT subscription's UPI AutoPay debit fails — insufficient balance. That's attempt 1 of 4, already spent. Nothing to optimize yet, just a fact on the ledger.",
    color: "text-danger-500 bg-danger-500/10",
  },
  {
    icon: BellRing,
    time: "Day 0, 9:15 AM",
    title: "A pre-debit notice goes out",
    body: "Before any retry can even be considered, RBI's rule kicks in: a notice must reach the customer at least 24 hours before the next attempt. MandateOps queues it immediately — the clock only starts once it's actually sent.",
    color: "text-ai-400 bg-ai-500/10",
  },
  {
    icon: CalendarClock,
    time: "Day 1, 6:00 AM",
    title: "The scorer picks the best legal hour",
    body: "24 hours have passed. Of the legal non-peak hours available, the statistical scorer knows insufficient-funds retries for this bank do best right after typical salary-credit windows — so it schedules attempt 2 for 6 AM, not 11 AM.",
    color: "text-success-500 bg-success-500/10",
  },
  {
    icon: ShieldOff,
    time: "Day 1, 6:00 AM",
    title: "The customer revokes mid-cycle",
    body: "Moments before the scheduled attempt, the customer revokes the mandate in their UPI app. A naive system would still fire attempts 2, 3, and 4 into a mandate that can never succeed. MandateOps checks rail-side status first, sees REVOKED, and freezes the remaining budget instead.",
    color: "text-warning-500 bg-warning-500/10",
  },
  {
    icon: CheckCircle2,
    time: "Day 1, 6:00 AM",
    title: "Two attempts saved, logged forever",
    body: "2 of the original 4 attempts are preserved rather than burned on guaranteed failures. The decision — and the exact reason — is written to the hash-chained audit log, verifiable by anyone, forever.",
    color: "text-ai-400 bg-ai-500/10",
  },
];

export function RealWorldWalkthrough() {
  return (
    <div className="relative space-y-4 pl-4">
      <div className="absolute bottom-2 left-[15px] top-2 w-px bg-border" />
      {STEPS.map(({ icon: Icon, time, title, body, color }, i) => (
        <motion.div
          key={title}
          initial={{ opacity: 0, x: -10 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, margin: "-40px" }}
          transition={{ duration: 0.3, delay: i * 0.05 }}
          className="relative flex gap-4"
        >
          <div className={`relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${color}`}>
            <Icon size={15} />
          </div>
          <div className="flex-1 rounded-xl border border-border bg-bg p-3.5">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h4 className="text-sm font-semibold text-text-primary">{title}</h4>
              <span className="font-mono-num text-[10px] text-text-muted">{time}</span>
            </div>
            <p className="mt-1.5 text-sm text-text-secondary">{body}</p>
          </div>
        </motion.div>
      ))}
    </div>
  );
}
