import { useState } from "react";
import { Loader2, Play } from "lucide-react";
import { Card } from "../ui/Card";

interface RunControlBarProps {
  onRun: (cohortSize: number, seed: number) => void;
  isRunning: boolean;
}

export function RunControlBar({ onRun, isRunning }: RunControlBarProps) {
  const [cohortSize, setCohortSize] = useState(5000);
  const [seed, setSeed] = useState(2026);

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
          className="w-28 rounded-md border border-border bg-bg px-2 py-1.5 text-sm font-mono-num text-text-primary outline-none focus:border-ai-500"
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
          className="w-24 rounded-md border border-border bg-bg px-2 py-1.5 text-sm font-mono-num text-text-primary outline-none focus:border-ai-500"
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
    </Card>
  );
}
