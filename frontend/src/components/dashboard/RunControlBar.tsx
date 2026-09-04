import { useEffect, useState } from "react";
import { Loader2, Play } from "lucide-react";
import { Card } from "../ui/Card";

interface RunControlBarProps {
  onRun: (cohortSize: number, seed: number) => void;
  isRunning: boolean;
}

const PROCESSING_STEPS = [
  "Generating synthetic cohort…",
  "Running naive retry strategy…",
  "Running MandateOps strategy…",
  "Writing audit trail…",
];

export function RunControlBar({ onRun, isRunning }: RunControlBarProps) {
  const [cohortSize, setCohortSize] = useState(50);
  const [seed, setSeed] = useState(2026);
  const [stepIndex, setStepIndex] = useState(0);

  // Cycle through the processing steps while the run is in flight, purely
  // cosmetic — it gives the (intentionally brief) minimum run duration a
  // sense of actual work happening rather than an unexplained pause.
  useEffect(() => {
    if (!isRunning) {
      setStepIndex(0);
      return;
    }
    const interval = setInterval(() => {
      setStepIndex((i) => Math.min(i + 1, PROCESSING_STEPS.length - 1));
    }, 700);
    return () => clearInterval(interval);
  }, [isRunning]);

  return (
    <Card className="flex flex-wrap items-center gap-4">
      <div className="flex items-center gap-2">
        <label className="text-xs text-text-muted" htmlFor="cohort-size">
          Cohort size
        </label>
        <input
          id="cohort-size"
          type="number"
          min={10}
          max={20000}
          step={100}
          value={cohortSize}
          onChange={(e) => setCohortSize(Number(e.target.value))}
          disabled={isRunning}
          className="w-28 rounded-md border border-border bg-bg px-2 py-1.5 text-sm font-mono-num text-text-primary outline-none focus:border-ai-500 disabled:opacity-60"
        />
      </div>
      <div className="flex items-center gap-2">
        <label className="text-xs text-text-muted" htmlFor="seed">
          Seed
        </label>
        <input
          id="seed"
          type="number"
          value={seed}
          onChange={(e) => setSeed(Number(e.target.value))}
          disabled={isRunning}
          className="w-24 rounded-md border border-border bg-bg px-2 py-1.5 text-sm font-mono-num text-text-primary outline-none focus:border-ai-500 disabled:opacity-60"
        />
      </div>
      <button
        onClick={() => onRun(cohortSize, seed)}
        disabled={isRunning}
        className="inline-flex items-center gap-2 rounded-lg bg-ai-500 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-ai-600 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isRunning ? (
          <>
            <Loader2 size={16} className="animate-spin" />
            Running batch…
          </>
        ) : (
          <>
            <Play size={16} />
            Run Batch
          </>
        )}
      </button>
      {isRunning && (
        <span className="font-mono-num text-xs text-text-muted transition-opacity">
          {PROCESSING_STEPS[stepIndex]}
        </span>
      )}
    </Card>
  );
}
