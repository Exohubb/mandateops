// Shared React Query hooks for data that's read from multiple pages.
//
// The batches list is the clearest example of a cross-page staleness bug:
// Dashboard, Mandate Explorer, Ask Nira, and Audit Trail each independently
// query it. With the app-wide default staleTime (30s) and React Router
// unmounting/remounting page components on navigation, a page visited
// right after a new batch was created elsewhere could sit there showing
// the OLD cached list (or an empty one, if it mounted before any batch
// existed) until the 30s staleness window passed — which reads as "I have
// to reload the page to see the new data." Two fixes, applied here once
// instead of per-page:
//   1. `staleTime: 0` + `refetchOnMount: "always"` — every time a page
//      mounts, it fetches fresh rather than trusting a stale cache entry.
//   2. A single shared query key builder, so every page reading the same
//      underlying list actually shares one cache entry (previously some
//      pages used a different `limit` while all writing to the identical
//      key string, causing cache collisions between unrelated limits).

import { useQuery, type QueryClient } from "@tanstack/react-query";
import { api } from "./api";

export function batchesListQueryKey(limit: number) {
  return ["batches-list", limit] as const;
}

export function useBatchesList(limit = 20) {
  return useQuery({
    queryKey: batchesListQueryKey(limit),
    queryFn: () => api.listBatches(limit),
    staleTime: 0,
    refetchOnMount: "always",
  });
}

/** Call after any mutation that changes which batches exist (create,
 * delete) so every page's batches-list query — regardless of which
 * `limit` it was fetched with — refetches on its next mount/focus rather
 * than serving a snapshot from before the mutation.
 */
export function invalidateBatchesList(queryClient: QueryClient) {
  return queryClient.invalidateQueries({
    predicate: (query) => query.queryKey[0] === "batches-list",
  });
}
