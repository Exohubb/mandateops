import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  Bot,
  Clock,
  Cog,
  IndianRupee,
  Layers,
  ShieldAlert,
  ShieldCheck,
  Smartphone,
  TrendingDown,
  Zap,
} from "lucide-react";
import { Card } from "../components/ui/Card";
import { ApprovalRateTrendChart } from "../components/home/ApprovalRateTrendChart";
import { RecoveryComparisonChart } from "../components/home/RecoveryComparisonChart";
import { ConstraintDiagram } from "../components/home/ConstraintDiagram";
import { SourcesFooter } from "../components/home/SourcesFooter";

const STAT_CARDS = [
  {
    icon: TrendingDown,
    value: "50% → 30%",
    label: "UPI AutoPay approval rate, Jan 2024 → Nov 2025, even as volume grew 10x",
    source: "Moneycontrol",
  },
  {
    icon: ShieldAlert,
    value: "1 + 3",
    label: "Initial attempt + retries. Hard NPCI ceiling — no fifth chance, ever.",
    source: "NPCI / Economic Times",
  },
  {
    icon: Clock,
    value: "24 hours",
    label: "Minimum pre-debit notice legally required before any attempt fires",
    source: "RBI e-mandate framework",
  },
  {
    icon: IndianRupee,
    value: "20–90%",
    label: "Share of subsequent debits failing on balance, bank downtime, or dead mandates",
    source: "Razorpay / Livemint",
  },
];

const HOW_IT_WORKS = [
  {
    icon: Cog,
    title: "Deterministic rulebook",
    body: "The 4-attempt ceiling, non-peak execution windows, and 24h notification gate are hard-coded, not learned. Every retry decision is 100% reproducible and independently auditable.",
    tag: "No AI here",
    tagColor: "text-text-secondary bg-border/40",
  },
  {
    icon: Layers,
    title: "Statistical retry-slot scorer",
    body: "An empirical-Bayes model ranks the legal hours by (bank × decline reason) success probability — with shrinkage toward a global prior, and an honest refusal to score thin-data cells confidently.",
    tag: "Inspectable math",
    tagColor: "text-ai-400 bg-ai-500/10",
  },
  {
    icon: Bot,
    title: "Nira — the AI layer",
    body: "Gemini reads messy bank decline text, drafts customer messages, and answers grounded questions about a batch run. She never touches an amount, a probability, or a scheduling decision.",
    tag: "Gemini, boxed in",
    tagColor: "text-ai-400 bg-ai-500/10",
  },
  {
    icon: ShieldCheck,
    title: "Hash-chained audit trail",
    body: "Every decision — deterministic, statistical, or AI — is written to an append-only, hash-chained log. Tamper with one row and every hash after it stops matching, verifiably.",
    tag: "Tamper-evident",
    tagColor: "text-warning-400 bg-warning-500/10",
  },
];

export function HomePage() {
  return (
    <div className="space-y-16 pb-16">
      {/* Hero */}
      <section className="hero-grid -mx-4 rounded-b-3xl pb-4 pt-10 text-center sm:-mx-6 lg:-mx-8">
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
          <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
            <Link
              to="/dashboard"
              className="inline-flex items-center gap-2 rounded-lg bg-ai-500 px-5 py-3 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-ai-600"
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
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {STAT_CARDS.map(({ icon: Icon, value, label, source }, i) => (
            <Card key={value} delay={i * 0.06}>
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

      {/* Two charts: the problem, then the result */}
      <section>
        <div className="mb-5">
          <h2 className="text-xl font-bold text-text-primary">
            The problem, and the measured result
          </h2>
          <p className="mt-1 text-sm text-text-secondary">
            Left: the industry-wide trend that created this problem. Right:
            what MandateOps actually recovers on a verified 5,000-mandate
            synthetic batch — reproducible from the Live Simulation page.
          </p>
        </div>
        <div className="grid gap-6 lg:grid-cols-2">
          <Card delay={0.05}>
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-text-primary">
                UPI AutoPay Approval Rate Decline
              </h3>
              <span className="rounded-full bg-danger-500/10 px-2 py-0.5 text-[11px] font-medium text-danger-400">
                Industry-wide
              </span>
            </div>
            <ApprovalRateTrendChart />
            <p className="mt-2 text-[11px] text-text-muted">
              Source: Moneycontrol, citing NPCI/industry data. Endpoints (Jan
              2024, Nov 2025) are the reported figures; intermediate points
              are interpolated to show trajectory.
            </p>
          </Card>
          <Card delay={0.1}>
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-text-primary">
                Recovery Rate: Naive Retry vs. MandateOps
              </h3>
              <span className="rounded-full bg-success-500/10 px-2 py-0.5 text-[11px] font-medium text-success-400">
                Measured
              </span>
            </div>
            <RecoveryComparisonChart />
            <p className="mt-2 text-[11px] text-text-muted">
              5,000-mandate synthetic batch, seed 2026. ₹5.18L more recovered,
              2,219 attempts saved from being wasted on dead mandates.
              Reproduce it yourself on the Live Simulation page.
            </p>
          </Card>
        </div>
      </section>

      {/* Constraint diagram */}
      <section>
        <Card delay={0.05}>
          <div className="mb-4">
            <h2 className="text-lg font-bold text-text-primary">
              Why this is a scheduling problem, not a retry loop
            </h2>
            <p className="mt-1 text-sm text-text-secondary">
              NPCI restricts AutoPay debit execution to fixed non-peak windows.
              An attempt fired in a blocked hour doesn't just fail — it's not
              legally executable at all. Every hour below is either a legal
              slot or a wasted one.
            </p>
          </div>
          <ConstraintDiagram />
          <p className="mt-4 text-[11px] text-text-muted">
            Illustrative 24-hour window based on NPCI's published non-peak
            execution rules (before ~10:00, 13:00–17:00, after ~21:30). Exact
            minute boundaries vary slightly across public sources — MandateOps
            documents which version it encodes and cites it in the README.
          </p>
        </Card>
      </section>

      {/* How it works — 4 layers */}
      <section>
        <div className="mb-5">
          <h2 className="text-xl font-bold text-text-primary">
            Four layers, each doing only what it's good at
          </h2>
          <p className="mt-1 text-sm text-text-secondary">
            The single most important design decision in this system: money
            never moves because a model said so.
          </p>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          {HOW_IT_WORKS.map(({ icon: Icon, title, body, tag, tagColor }, i) => (
            <Card key={title} delay={i * 0.06}>
              <div className="flex items-start gap-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-ai-500/10 text-ai-400">
                  <Icon size={19} />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between gap-2">
                    <h3 className="text-sm font-semibold text-text-primary">{title}</h3>
                    <span className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-medium ${tagColor}`}>
                      {tag}
                    </span>
                  </div>
                  <p className="mt-1.5 text-sm text-text-secondary">{body}</p>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </section>

      {/* Credibility strip */}
      <section>
        <Card className="flex flex-col items-center gap-3 text-center sm:flex-row sm:justify-center sm:gap-4 sm:text-left">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-success-500/10 text-success-500">
            <Smartphone size={18} />
          </div>
          <p className="text-sm text-text-secondary">
            We've already shipped the consumer half of this problem —{" "}
            <a
              href="https://play.google.com/store/apps/details?id=com.airolabs.autopayy"
              target="_blank"
              rel="noreferrer"
              className="link-underline font-semibold text-ai-400"
            >
              AutoPay
            </a>
            , a UPI mandate manager with 740+ users in its first 20 days on
            the Play Store. MandateOps is the same domain expertise, pointed
            at the merchant's side of the same broken rail.
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
              className="link-underline text-sm font-medium text-ai-400"
            >
              See exactly where AI is used — and where it deliberately isn't →
            </Link>
          </div>
        </Card>
      </section>

      {/* Sources */}
      <section>
        <div className="mb-4">
          <h2 className="text-lg font-bold text-text-primary">Sources &amp; citations</h2>
          <p className="mt-1 text-sm text-text-secondary">
            Every claim on this page is sourced. No number here is invented —
            consistent with how MandateOps treats AI everywhere else in this
            product.
          </p>
        </div>
        <Card>
          <SourcesFooter />
        </Card>
      </section>
    </div>
  );
}
