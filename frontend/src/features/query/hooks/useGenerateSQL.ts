import { useMutation } from '@tanstack/react-query'
import { toast } from 'sonner'
import api from '@/lib/api'
import { API_ENDPOINTS } from '@/lib/constants'
import type { GenerateRequest, GenerateResponse } from '../types'

export function useGenerateSQL() {
  return useMutation<GenerateResponse, Error, GenerateRequest>({
    mutationFn: async (data) => {
      const response = await api.post<GenerateResponse>(API_ENDPOINTS.GENERATE, data)
      return response.data
    },
    onSuccess: () => {
      toast.success('SQL generated successfully')
    },
    onError: (error) => {
      toast.error(`Generation failed: ${error.message}`)
    },
  })
}
