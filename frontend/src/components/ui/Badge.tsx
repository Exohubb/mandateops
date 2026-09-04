import type { ReactNode } from "react";

interface BadgeProps {
  children: ReactNode;
  className?: string;
}

/** A small pill badge. Callers pass the semantic color classes from
 * lib/format.ts (STATE_COLOR / ACTOR_LAYER_COLOR) so color meaning stays
 * centralized in one place rather than scattered across components.
 */
export function Badge({ children, className = "" }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium font-mono-num ${className}`}
    >
      {children}
    </span>
  );
}
