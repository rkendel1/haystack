import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import { QueryResponse, PipelineMode } from '@/types';

interface QueryParams {
  query: string;
  pipeline?: PipelineMode;
  top_k?: number;
}

export const useHaystackQuery = (params: QueryParams, enabled = false) => {
  return useQuery({
    queryKey: ['haystack-query', params],
    queryFn: async () => {
      if (!params.query) return null;
      const { data } = await api.post<QueryResponse>('/query', {
        query: params.query,
        pipeline: params.pipeline || 'rag',
        top_k: params.top_k || 5,
      });
      return data;
    },
    enabled: enabled && !!params.query,
    retry: 1,
  });
};
