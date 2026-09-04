import type { ReactNode } from "react";
import { motion } from "framer-motion";

interface CardProps {
  children: ReactNode;
  className?: string;
  delay?: number;
}

/** The base surface used across every panel in the dashboard. Fades/slides
 * in on mount per BUILD-BLUEPRINT.md's motion guidance — subtle, under
 * 300ms, staggered by `delay` when rendered in a list of cards.
 */
export function Card({ children, className = "", delay = 0 }: CardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay, ease: "easeOut" }}
      className={`card p-5 ${className}`}
    >
      {children}
    </motion.div>
  );
}

export function CardHeader({ children }: { children: ReactNode }) {
  return (
    <div className="mb-4 flex items-center justify-between gap-3">{children}</div>
  );
}

export function CardTitle({ children }: { children: ReactNode }) {
  return <h3 className="text-sm font-semibold text-text-primary">{children}</h3>;
}
