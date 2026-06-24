import { Database } from 'lucide-react'
import { cn } from '@/lib/utils'

export default function Logo({ className }: { className?: string }) {
  return (
    <div className={cn('flex items-center gap-2', className)}>
      <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center shadow-sm">
        <Database className="w-4 h-4 text-white" />
      </div>
      <span className="font-bold text-slate-900">QueryBridge</span>
    </div>
  )
}
