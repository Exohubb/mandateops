import { motion } from "framer-motion";

const WINDOWS = [
  { label: "12 AM", start: 0, legal: true },
  { label: "6 AM", start: 6, legal: true },
  { label: "10 AM", start: 10, legal: false },
  { label: "1 PM", start: 13, legal: true },
  { label: "5 PM", start: 17, legal: false },
  { label: "9:30 PM", start: 21.5, legal: true },
  { label: "12 AM", start: 24, legal: true },
];

/** A 24-hour bar visualizing NPCI's non-peak execution windows: green
 * segments are legal for an AutoPay debit attempt, red segments are peak
 * hours where execution is blocked entirely.
 */
export function ConstraintDiagram() {
  const segments: { from: number; to: number; legal: boolean }[] = [];
  for (let i = 0; i < WINDOWS.length - 1; i++) {
    segments.push({
      from: WINDOWS[i].start,
      to: WINDOWS[i + 1].start,
      legal: WINDOWS[i].legal,
    });
  }

  return (
    <div>
      <div className="mb-2 flex h-8 overflow-hidden rounded-lg border border-border">
        {segments.map((seg, i) => {
          const widthPct = ((seg.to - seg.from) / 24) * 100;
          return (
            <motion.div
              key={i}
              initial={{ scaleX: 0 }}
              animate={{ scaleX: 1 }}
              transition={{ duration: 0.5, delay: i * 0.06, ease: "easeOut" }}
              style={{ width: `${widthPct}%`, transformOrigin: "left" }}
              className={seg.legal ? "bg-success-500/70" : "bg-danger-500/70"}
              title={seg.legal ? "Non-peak — attempts allowed" : "Peak — attempts blocked"}
            />
          );
        })}
      </div>
      <div className="flex justify-between text-[10px] text-text-muted">
        {WINDOWS.map((w, i) => (
          <span key={i}>{w.label}</span>
        ))}
      </div>
      <div className="mt-3 flex items-center gap-4 text-xs">
        <span className="flex items-center gap-1.5 text-text-secondary">
          <span className="h-2.5 w-2.5 rounded-sm bg-success-500/70" /> Non-peak — legal
        </span>
        <span className="flex items-center gap-1.5 text-text-secondary">
          <span className="h-2.5 w-2.5 rounded-sm bg-danger-500/70" /> Peak — blocked
        </span>
      </div>
    </div>
  );
}
