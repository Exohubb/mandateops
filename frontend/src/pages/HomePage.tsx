import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowRight, Clock, ShieldAlert, Zap } from "lucide-react";
import { Card } from "../components/ui/Card";

const STAT_CARDS = [
  {
    icon: Zap,
    value: "50% → 30%",
    label: "UPI AutoPay approval rate, Jan 2024 → Nov 2025",
    source: "Moneycontrol",
  },
  {
    icon: ShieldAlert,
    value: "1 + 3",
    label: "Initial attempt + retries. Hard NPCI ceiling per cycle.",
    source: "NPCI / Economic Times",
  },
  {
    icon: Clock,
    value: "24 hours",
    label: "Minimum pre-debit notice required before any attempt",
    source: "RBI e-mandate framework",
  },
];

export function HomePage() {
  return (
    <div className="space-y-16 pb-12">
      {/* Hero */}
      <section className="pt-10 text-center">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <span className="inline-flex items-center gap-2 rounded-full border border-ai-500/30 bg-ai-500/10 px-3 py-1 text-xs font-medium text-ai-400">
            Razorpay Buildathon · Track 03: AI Revenue Recovery
          </span>
          <h1 className="mx-auto mt-6 max-w-3xl text-4xl font-extrabold tracking-tight text-text-primary sm:text-5xl">
            UPI AutoPay is leaking revenue.{" "}
            <span className="text-ai-400">MandateOps recovers it.</span>
          </h1>
          <p className="mx-auto mt-5 max-w-2xl text-base text-text-secondary sm:text-lg">
            NPCI gives every failed mandate exactly four attempts, inside fixed
            legal hours, with a mandatory 24-hour notice. Retry blindly and you
            burn scarce chances on dead mandates. MandateOps treats every
            attempt as a budgeted resource — and uses AI only where AI
            belongs: reading messy text, never moving money.
          </p>
          <div className="mt-8 flex items-center justify-center gap-3">
            <Link
              to="/dashboard"
              className="inline-flex items-center gap-2 rounded-lg bg-ai-500 px-5 py-3 text-sm font-semibold text-white transition-colors hover:bg-ai-600"
            >
              Launch Live Simulation
              <ArrowRight size={16} />
            </Link>
            <Link
              to="/ai-judgment"
              className="inline-flex items-center gap-2 rounded-lg border border-border px-5 py-3 text-sm font-medium text-text-secondary transition-colors hover:bg-surface-hover hover:text-text-primary"
            >
              How we use AI
            </Link>
          </div>
        </motion.div>
      </section>

      {/* Stat strip */}
      <section>
        <div className="grid gap-4 sm:grid-cols-3">
          {STAT_CARDS.map(({ icon: Icon, value, label, source }, i) => (
            <Card key={value} delay={i * 0.08}>
              <div className="flex items-start gap-3">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-ai-500/10 text-ai-400">
                  <Icon size={18} />
                </div>
                <div>
                  <div className="text-2xl font-bold text-text-primary font-mono-num">
                    {value}
                  </div>
                  <p className="mt-1 text-sm text-text-secondary">{label}</p>
                  <p className="mt-1 text-[11px] text-text-muted">Source: {source}</p>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </section>

      {/* Credibility strip */}
      <section>
        <Card className="flex flex-col items-center gap-2 text-center sm:flex-row sm:justify-center sm:gap-4 sm:text-left">
          <p className="text-sm text-text-secondary">
            Built by the team behind{" "}
            <a
              href="https://play.google.com/store/apps/details?id=com.airolabs.autopayy"
              target="_blank"
              rel="noreferrer"
              className="font-semibold text-ai-400 hover:underline"
            >
              AutoPay
            </a>{" "}
            — 740+ users in 20 days on the Play Store, tracking UPI AutoPay
            mandates from the consumer side. MandateOps solves the same
            problem from the merchant side.
          </p>
        </Card>
      </section>

      {/* AI teaser */}
      <section>
        <Card>
          <div className="flex flex-col items-center gap-4 py-6 text-center sm:py-8">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-ai-500/15 text-ai-400">
              <Zap size={22} />
            </div>
            <h2 className="text-xl font-semibold text-text-primary">
              Meet Nira, the MandateOps Recovery Analyst
            </h2>
            <p className="max-w-xl text-sm text-text-secondary">
              Nira reads messy bank decline text and answers questions about a
              batch run — grounded strictly in that run's own data. She never
              approves, denies, or schedules a payment. That authority belongs
              entirely to deterministic code she cannot see or influence.
            </p>
            <Link
              to="/ai-judgment"
              className="text-sm font-medium text-ai-400 hover:underline"
            >
              See exactly where AI is used — and where it deliberately isn't →
            </Link>
          </div>
        </Card>
      </section>
    </div>
  );
}
