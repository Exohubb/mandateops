import { useEffect, useRef, useState } from "react";
import { animate } from "framer-motion";

interface CountUpProps {
  value: number;
  format?: (n: number) => string;
  durationSec?: number;
  className?: string;
}

/** Animated count-up for headline numbers (recovered rupees, attempts
 * saved, mandates processed) per BUILD-BLUEPRINT.md section 6.1. Restarts
 * the animation whenever `value` changes, so it also works for live
 * WebSocket-driven counters that update repeatedly.
 */
export function CountUp({
  value,
  format = (n) => Math.round(n).toLocaleString("en-IN"),
  durationSec = 0.9,
  className = "",
}: CountUpProps) {
  const [display, setDisplay] = useState(0);
  const previousValue = useRef(0);

  useEffect(() => {
    const controls = animate(previousValue.current, value, {
      duration: durationSec,
      ease: "easeOut",
      onUpdate: (v) => setDisplay(v),
    });
    previousValue.current = value;
    return () => controls.stop();
  }, [value, durationSec]);

  return <span className={`font-mono-num ${className}`}>{format(display)}</span>;
}
