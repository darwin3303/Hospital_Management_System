import { QueryClient } from '@tanstack/react-query';

/**
 * Single shared QueryClient instance. Pages don't use useQuery/useMutation
 * yet (still on direct useEffect + API calls) -- this just wires up the
 * provider so that migration can happen feature-by-feature later without
 * touching App bootstrapping again.
 */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});
