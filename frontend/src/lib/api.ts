// Thin fetch wrapper for the MandateOps API. Requests go to /api/*, which
// Vite's dev server proxies to the backend (see vite.config.ts); in
// production, nginx does the equivalent proxying.

import type {
  AiJudgmentRow,
  AuditEventRow,
  BatchRun,
  CopilotAnswer,
  HeatmapCell,
  HealthStatus,
  MandateDetail,
  MandateOutcome,
  Strategy,
  VerifyChainResult,
} from "./types";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const body = await response.text().catch(() => "");
    throw new Error(`API error ${response.status} on ${path}: ${body}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<HealthStatus>("/api/health"),

  runBatch: (cohortSize: number, seed: number) =>
    request<{ batch_id: string; status: string }>("/api/batches", {
      method: "POST",
      body: JSON.stringify({ cohort_size: cohortSize, seed }),
    }),

  listBatches: (limit = 20) => request<BatchRun[]>(`/api/batches?limit=${limit}`),

  getBatch: (batchId: string) => request<BatchRun>(`/api/batches/${batchId}`),

  deleteBatch: (batchId: string) =>
    request<{ batch_id: string; deleted: boolean }>(`/api/batches/${batchId}`, {
      method: "DELETE",
    }),

  getOutcomes: (batchId: string, strategy: Strategy, limit = 5000) =>
    request<MandateOutcome[]>(
      `/api/batches/${batchId}/outcomes/${strategy}?limit=${limit}`
    ),

  getMandateDetail: (batchId: string, mandateId: string) =>
    request<MandateDetail>(`/api/batches/${batchId}/mandate/${mandateId}`),

  getAuditTrail: (batchId: string, limit = 500) =>
    request<AuditEventRow[]>(`/api/audit/${batchId}?limit=${limit}`),

  verifyChain: (batchId: string) =>
    request<VerifyChainResult>(`/api/audit/${batchId}/verify`, { method: "POST" }),

  askCopilot: (
    batchId: string,
    question: string,
    history: { role: "user" | "nira"; text: string }[] = []
  ) =>
    request<CopilotAnswer>("/api/copilot/ask", {
      method: "POST",
      body: JSON.stringify({ batch_id: batchId, question, history }),
    }),

  getHeatmap: (declineCategory: string) =>
    request<HeatmapCell[]>(`/api/stats/heatmap/${declineCategory}`),

  getAiJudgmentTable: () => request<AiJudgmentRow[]>("/api/stats/ai-judgment-table"),
};
