import { ArrowRight } from "lucide-react";
import { Card } from "../ui/Card";
import { CountUp } from "../ui/CountUp";
import { formatRupees } from "../../lib/format";
import type { StrategySummary } from "../../lib/types";

interface ComparisonHeroProps {
  naive: StrategySummary | null;
  mandateops: StrategySummary | null;
}

export function ComparisonHero({ naive, mandateops }: ComparisonHeroProps) {
  const naiveRupees = naive?.recovered_rupees ?? 0;
  const mandateopsRupees = mandateops?.recovered_rupees ?? 0;
  const delta = mandateopsRupees - naiveRupees;

  return (
    <Card>
      <div className="grid grid-cols-1 items-center gap-6 sm:grid-cols-3">
        <div className="text-center sm:text-left">
          <div className="text-xs font-medium uppercase tracking-wide text-text-muted">
            Naive Retry (next-day)
          </div>
          <div className="mt-2 text-3xl font-bold text-text-secondary">
            <CountUp value={naiveRupees} format={(n) => formatRupees(n)} />
          </div>
          <div className="mt-1 text-xs text-text-muted">
            {naive ? `${(naive.recovery_rate * 100).toFixed(1)}% recovery rate` : "—"}
          </div>
        </div>

        <div className="flex flex-col items-center gap-1">
          <ArrowRight className="text-ai-400" size={22} />
          <div className="rounded-full bg-success-500/10 px-3 py-1 text-xs font-semibold text-success-400 font-mono-num">
            +{formatRupees(delta > 0 ? delta : 0)}
          </div>
        </div>

        <div className="text-center sm:text-right">
          <div className="text-xs font-medium uppercase tracking-wide text-ai-400">
            MandateOps
          </div>
          <div className="mt-2 text-3xl font-bold text-success-400">
            <CountUp value={mandateopsRupees} format={(n) => formatRupees(n)} />
          </div>
          <div className="mt-1 text-xs text-text-muted">
            {mandateops
              ? `${(mandateops.recovery_rate * 100).toFixed(1)}% recovery rate`
              : "—"}
          </div>
        </div>
      </div>
    </Card>
  );
}
