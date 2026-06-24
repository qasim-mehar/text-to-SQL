import { useMutation } from '@tanstack/react-query'
import { toast } from 'sonner'
import api from '@/lib/api'
import { API_ENDPOINTS } from '@/lib/constants'
import type { ExecuteRequest, ExecuteResponse } from '../types'

export function useExecuteQuery() {
  return useMutation<ExecuteResponse, Error, ExecuteRequest>({
    mutationFn: async (data) => {
      const response = await api.post<ExecuteResponse>(API_ENDPOINTS.EXECUTE, data)
      return response.data
    },
    onSuccess: (data) => {
      toast.success(`Query executed — ${data.row_count} row${data.row_count !== 1 ? 's' : ''} returned`)
    },
    onError: (error) => {
      toast.error(`Execution failed: ${error.message}`)
    },
  })
}
