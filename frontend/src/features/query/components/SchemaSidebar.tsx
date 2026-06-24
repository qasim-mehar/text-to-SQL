import { useState } from 'react'
import { ChevronRight, ChevronDown, Table2, KeyRound, AlertCircle } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { useSchema } from '../hooks/useSchema'
import { cn } from '@/lib/utils'
import type { TableInfo } from '../types'

function TableRow({ table }: { table: TableInfo }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="border-b border-slate-100 last:border-0">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-2 px-4 py-2.5 text-sm hover:bg-slate-50 transition-colors text-left"
      >
        {open ? (
          <ChevronDown className="w-3.5 h-3.5 text-slate-400 shrink-0" />
        ) : (
          <ChevronRight className="w-3.5 h-3.5 text-slate-400 shrink-0" />
        )}
        <Table2 className="w-3.5 h-3.5 text-blue-500 shrink-0" />
        <span className="font-medium text-slate-800 flex-1">{table.name}</span>
        <span className="text-xs text-slate-400">{table.columns.length}</span>
      </button>
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.15 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-2 space-y-0.5 pl-10">
              {table.columns.map((col) => (
                <div key={col.name} className="flex items-center justify-between py-1 gap-2">
                  <span className="text-xs text-slate-600 font-mono">{col.name}</span>
                  <Badge variant="outline" className="text-[10px] font-mono px-1.5 py-0">
                    {col.type.toLowerCase()}
                  </Badge>
                </div>
              ))}
              {table.foreign_keys.length > 0 && (
                <div className="mt-2 pt-2 border-t border-slate-100">
                  <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1 flex items-center gap-1">
                    <KeyRound className="w-2.5 h-2.5" /> Relations
                  </p>
                  {table.foreign_keys.map((fk, i) => (
                    <div key={i} className="text-[10px] text-slate-400 font-mono">
                      {fk.from_col} → {fk.to_table}.{fk.to_column}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default function SchemaSidebar() {
  const { data, isLoading, isError } = useSchema()

  return (
    <aside className="w-[280px] shrink-0 border-r border-slate-200 bg-white flex flex-col h-full">
      <div className="px-4 py-3 border-b border-slate-200">
        <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
          Database Schema
        </h2>
      </div>
      <ScrollArea className="flex-1">
        {isLoading && (
          <div className="p-4 space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <Skeleton key={i} className="h-9 w-full" />
            ))}
          </div>
        )}
        {isError && (
          <div className="p-4 flex flex-col items-center gap-2 text-center">
            <AlertCircle className="w-6 h-6 text-red-400" />
            <p className="text-xs text-slate-500">
              Could not load schema.
              <br />
              Is the backend running?
            </p>
          </div>
        )}
        {data && (
          <div>
            {data.tables.map((table) => (
              <TableRow key={table.name} table={table} />
            ))}
          </div>
        )}
      </ScrollArea>
      {data && (
        <div className="px-4 py-2 border-t border-slate-100">
          <p className="text-[10px] text-slate-400">{data.tables.length} tables</p>
        </div>
      )}
    </aside>
  )
}
