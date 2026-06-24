import { Skeleton } from '@/components/ui/skeleton'

export function QueryPageSkeleton() {
  return (
    <div className="space-y-4 p-6">
      <Skeleton className="h-32 w-full" />
      <Skeleton className="h-48 w-full" />
      <Skeleton className="h-64 w-full" />
    </div>
  )
}

export function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-2 p-4">
      <Skeleton className="h-8 w-full" />
      {Array.from({ length: rows }).map((_, i) => (
        <Skeleton key={i} className="h-12 w-full" style={{ animationDelay: `${i * 0.05}s` }} />
      ))}
    </div>
  )
}
