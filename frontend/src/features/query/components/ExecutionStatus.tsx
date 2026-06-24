import { CheckCircle2, XCircle, Clock } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { formatMs } from '@/lib/utils'

interface ExecutionStatusProps {
  isSuccess?: boolean
  isError?: boolean
  executionTimeMs?: number
  rowCount?: number
  errorMessage?: string
}

export default function ExecutionStatus({
  isSuccess,
  isError,
  executionTimeMs,
  rowCount,
  errorMessage,
}: ExecutionStatusProps) {
  if (isSuccess) {
    return (
      <div className="flex items-center gap-3">
        <Badge variant="success" className="gap-1.5">
          <CheckCircle2 className="w-3 h-3" />
          Success
        </Badge>
        {rowCount !== undefined && (
          <span className="text-xs text-slate-500">{rowCount} rows</span>
        )}
        {executionTimeMs !== undefined && (
          <span className="flex items-center gap-1 text-xs text-slate-400">
            <Clock className="w-3 h-3" />
            {formatMs(executionTimeMs)}
          </span>
        )}
      </div>
    )
  }

  if (isError) {
    return (
      <div className="flex items-center gap-2">
        <Badge variant="destructive" className="gap-1.5">
          <XCircle className="w-3 h-3" />
          Error
        </Badge>
        {errorMessage && (
          <span className="text-xs text-red-500 truncate max-w-sm">{errorMessage}</span>
        )}
      </div>
    )
  }

  return null
}
