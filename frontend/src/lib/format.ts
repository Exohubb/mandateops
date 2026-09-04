// Small formatting helpers shared across pages. Centralized here so
// "how a rupee amount looks" and "what color a state gets" stay consistent
// across every chart/table per the BUILD-BLUEPRINT design system.

export function formatRupees(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatCompactRupees(amount: number): string {
  if (amount >= 100000) {
    return `₹${(amount / 100000).toFixed(2)}L`;
  }
  if (amount >= 1000) {
    return `₹${(amount / 1000).toFixed(1)}K`;
  }
  return `₹${amount.toFixed(0)}`;
}

export function formatPercent(fraction: number): string {
  return `${(fraction * 100).toFixed(1)}%`;
}

export function paiseToRupees(paise: number): number {
  return paise / 100;
}

/** Nira's system prompt forbids markdown, but this is a safety net: strip
 * stray markdown syntax (bold/italic asterisks, bullet dashes, header
 * hashes) so a rare slip-up never renders as literal asterisks in the UI.
 */
export function cleanAiText(text: string): string {
  return text
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/\*(.*?)\*/g, "$1")
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/^[-*]\s+/gm, "")
    .trim();
}

// Color system: every state maps to exactly one semantic color, matching
// index.css's palette. Used for badges, chart series, and event feed rows.
export const STATE_COLOR: Record<string, string> = {
  RECOVERED: "text-success-400 bg-success-500/10 border-success-500/30",
  EXHAUSTED: "text-danger-400 bg-danger-500/10 border-danger-500/30",
  FROZEN_REVOKED: "text-warning-400 bg-warning-500/10 border-warning-500/30",
  FROZEN_PAUSED: "text-warning-400 bg-warning-500/10 border-warning-500/30",
  FROZEN_NOTIFICATION_FAILED:
    "text-warning-400 bg-warning-500/10 border-warning-500/30",
  PENDING: "text-text-secondary bg-white/5 border-border",
};

export const ACTOR_LAYER_COLOR: Record<string, string> = {
  deterministic: "text-text-secondary bg-white/5 border-border",
  statistical: "text-ai-400 bg-ai-500/10 border-ai-500/30",
  ai: "text-ai-400 bg-ai-500/10 border-ai-500/30",
};

export const ACTOR_LAYER_LABEL: Record<string, string> = {
  deterministic: "Deterministic",
  statistical: "Statistical",
  ai: "Nira (AI)",
};

export function declineCategoryLabel(category: string): string {
  const labels: Record<string, string> = {
    insufficient_funds: "Insufficient Funds",
    bank_down: "Bank Down",
    mandate_paused: "Mandate Paused",
    mandate_revoked: "Mandate Revoked",
    other: "Other",
    unclassified: "Unclassified",
  };
  return labels[category] ?? category;
}
