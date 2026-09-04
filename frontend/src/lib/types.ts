// Shared TypeScript types mirroring the backend's response shapes.
// Kept hand-written and minimal rather than codegen'd, since the API
// surface is small and stable for this hackathon build.

export type Strategy = "naive" | "mandateops";

export interface StrategySummary {
  strategy: Strategy;
  total_mandates: number;
  recovered_count: number;
  recovered_rupees: number;
  total_attempts_used: number;
  total_attempts_saved: number;
  recovery_rate: number;
}

export interface BatchRun {
  id: string;
  created_at: string;
  cohort_size: number;
  seed: number;
  status: "running" | "completed";
  naive_summary: StrategySummary | null;
  mandateops_summary: StrategySummary | null;
  executive_summary_text: string | null;
}

export interface MandateOutcome {
  batch_id: string;
  strategy: Strategy;
  mandate_id: string;
  cycle_id: string;
  subscriber_name: string;
  bank: string;
  decline_category: string;
  decline_raw_text: string;
  final_state: string;
  attempts_used: number;
  attempts_saved: number;
  recovered: number; // 0 or 1 from SQLite
  recovered_amount_paise: number;
  plan_amount_paise: number;
  classified_by: string;
}

export interface SimulationEventRow {
  id: number;
  batch_id: string;
  strategy: Strategy;
  sequence: number;
  timestamp: string;
  mandate_id: string;
  cycle_id: string;
  event_type: string;
  actor_layer: "deterministic" | "statistical" | "ai";
  detail: Record<string, unknown>;
}

export interface MandateDetail {
  naive: MandateOutcome | null;
  mandateops: MandateOutcome | null;
  events: SimulationEventRow[];
}

export interface AuditEventRow {
  id: string;
  sequence: number;
  timestamp: string;
  actor_layer: string;
  event_type: string;
  mandate_id: string | null;
  cycle_id: string | null;
  detail: Record<string, unknown>;
  prev_hash: string;
  this_hash: string;
}

export interface VerifyChainResult {
  batch_id: string;
  valid: boolean;
  total_events: number;
  first_invalid_sequence: number | null;
}

export interface CopilotAnswer {
  answer: string;
  grounded: boolean;
  used_fallback: boolean;
}

export interface HeatmapCell {
  bank_code: string;
  hour: number;
  shrunk_probability: number;
  observed_trials: number;
  sufficient_support: boolean;
}

export interface AiJudgmentRow {
  decision: string;
  made_by: string;
  why: string;
}

export interface HealthStatus {
  status: string;
  gemini_configured: boolean;
}
