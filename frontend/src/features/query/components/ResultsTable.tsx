import { useState, useMemo } from 'react'
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  type SortingState,
  type ColumnDef,
  flexRender,
} from '@tanstack/react-table'
import { motion } from 'framer-motion'
import { ArrowUpDown, ArrowUp, ArrowDown, TableIcon } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { cn, formatNumber } from '@/lib/utils'
import type { ExecuteResponse } from '../types'

interface ResultsTableProps {
  data: ExecuteResponse
}

export default function ResultsTable({ data }: ResultsTableProps) {
  const [sorting, setSorting] = useState<SortingState>([])

  const columns = useMemo<ColumnDef<Record<string, unknown>>[]>(
    () =>
      data.columns.map((col) => ({
        accessorKey: col,
        header: ({ column }) => (
          <button
            className="flex items-center gap-1 text-left font-semibold text-slate-700 text-xs uppercase tracking-wider hover:text-slate-900 transition-colors"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            {col}
            {column.getIsSorted() === 'asc' ? (
              <ArrowUp className="w-3 h-3" />
            ) : column.getIsSorted() === 'desc' ? (
              <ArrowDown className="w-3 h-3" />
            ) : (
              <ArrowUpDown className="w-3 h-3 text-slate-300" />
            )}
          </button>
        ),
        cell: ({ getValue }) => {
          const val = getValue()
          if (val === null || val === undefined) {
            return <span className="text-slate-300 italic text-xs">null</span>
          }
          if (typeof val === 'number') {
            return <span className="font-mono text-sm tabular-nums">{formatNumber(val)}</span>
          }
          return <span className="text-sm text-slate-700">{String(val)}</span>
        },
      })),
    [data.columns]
  )

  const table = useReactTable({
    data: data.rows,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  })

  if (data.row_count === 0) {
    return (
      <Card className="shadow-none">
        <CardContent className="py-12 flex flex-col items-center gap-2">
          <TableIcon className="w-8 h-8 text-slate-200" />
          <p className="text-sm text-slate-400">No results returned</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
    >
      <Card className="shadow-none overflow-hidden">
        <CardHeader className="py-3 px-5 border-b border-slate-100 flex-row items-center justify-between space-y-0">
          <div className="flex items-center gap-2">
            <CardTitle className="text-sm">Results</CardTitle>
            <Badge variant="secondary">{data.row_count} rows</Badge>
          </div>
          <span className="text-xs text-slate-400">{data.execution_time_ms.toFixed(0)}ms</span>
        </CardHeader>
        <CardContent className="p-0">
          <ScrollArea className="max-h-[400px]">
            <table className="w-full min-w-max caption-bottom text-sm">
              <thead className="sticky top-0 bg-slate-50 border-b border-slate-200 z-10">
                {table.getHeaderGroups().map((hg) => (
                  <tr key={hg.id}>
                    {hg.headers.map((header) => (
                      <th key={header.id} className="px-4 py-2.5 text-left">
                        {flexRender(header.column.columnDef.header, header.getContext())}
                      </th>
                    ))}
                  </tr>
                ))}
              </thead>
              <tbody>
                {table.getRowModel().rows.map((row, i) => (
                  <motion.tr
                    key={row.id}
                    initial={{ opacity: 0, y: 4 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.02, duration: 0.15 }}
                    className={cn(
                      'border-b border-slate-100 hover:bg-slate-50 transition-colors',
                      i % 2 === 0 ? 'bg-white' : 'bg-slate-50/50'
                    )}
                  >
                    {row.getVisibleCells().map((cell) => (
                      <td key={cell.id} className="px-4 py-3 whitespace-nowrap">
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </td>
                    ))}
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </ScrollArea>
        </CardContent>
      </Card>
    </motion.div>
  )
}
