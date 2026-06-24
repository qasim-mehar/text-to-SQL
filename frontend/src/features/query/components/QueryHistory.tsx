import { useState } from 'react'
import { History, ChevronDown, ChevronUp, Clock, Trash2 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { useLocalStorage } from '@/hooks/useLocalStorage'
import { QUERY_HISTORY_KEY } from '@/lib/constants'
import { truncate } from '@/lib/utils'
import type { QueryHistoryItem } from '../types'

interface QueryHistoryProps {
  onSelect: (item: QueryHistoryItem) => void
}

export default function QueryHistory({ onSelect }: QueryHistoryProps) {
  const [open, setOpen] = useState(false)
  const [history, setHistory] = useLocalStorage<QueryHistoryItem[]>(QUERY_HISTORY_KEY, [])

  const clearHistory = (e: React.MouseEvent) => {
    e.stopPropagation()
    setHistory([])
  }

  if (history.length === 0) return null

  return (
    <Card className="shadow-none">
      <CardHeader
        className="py-3 px-5 border-b border-slate-100 flex-row items-center justify-between space-y-0 cursor-pointer hover:bg-slate-50 transition-colors rounded-t-xl"
        onClick={() => setOpen(!open)}
      >
        <div className="flex items-center gap-2">
          <History className="w-4 h-4 text-slate-400" />
          <CardTitle className="text-sm">Query History</CardTitle>
          <Badge variant="secondary">{history.length}</Badge>
        </div>
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="icon" className="h-6 w-6" onClick={clearHistory}>
            <Trash2 className="w-3 h-3 text-slate-400" />
          </Button>
          {open ? (
            <ChevronUp className="w-4 h-4 text-slate-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-slate-400" />
          )}
        </div>
      </CardHeader>
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.15 }}
            className="overflow-hidden"
          >
            <CardContent className="p-0">
              <ScrollArea className="max-h-[200px]">
                {history.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => onSelect(item)}
                    className="w-full flex items-start gap-3 px-5 py-3 text-left hover:bg-slate-50 border-b border-slate-100 last:border-0 transition-colors"
                  >
                    <Clock className="w-3.5 h-3.5 text-slate-300 mt-0.5 shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-slate-700 truncate">{item.question}</p>
                      <p className="text-xs text-slate-400 font-mono mt-0.5 truncate">
                        {truncate(item.sql, 60)}
                      </p>
                    </div>
                    {item.row_count !== undefined && (
                      <Badge variant="outline" className="text-[10px] shrink-0">
                        {item.row_count}r
                      </Badge>
                    )}
                  </button>
                ))}
              </ScrollArea>
            </CardContent>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  )
}
