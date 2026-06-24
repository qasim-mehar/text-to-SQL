import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import { API_ENDPOINTS } from '@/lib/constants'
import type { SchemaResponse } from '../types'

export function useSchema() {
  return useQuery<SchemaResponse, Error>({
    queryKey: ['schema'],
    queryFn: async () => {
      const response = await api.get<SchemaResponse>(API_ENDPOINTS.SCHEMA)
      return response.data
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  })
}
