import { useState, useCallback } from 'react'
import { motion } from 'framer-motion'
import { AlertCircle } from 'lucide-react'
import Navbar from '@/components/layout/Navbar'
import { ErrorBoundary } from '@/components/shared/ErrorBoundary'
import SchemaSidebar from '../components/SchemaSidebar'
import QueryInput from '../components/QueryInput'
import SQLPreview from '../components/SQLPreview'
import ResultsTable from '../components/ResultsTable'
import QueryHistory from '../components/QueryHistory'
import ExecutionStatus from '../components/ExecutionStatus'
import { useGenerateSQL } from '../hooks/useGenerateSQL'
import { useExecuteQuery } from '../hooks/useExecuteQuery'
import { useLocalStorage } from '@/hooks/useLocalStorage'
import { QUERY_HISTORY_KEY, MAX_HISTORY_ITEMS } from '@/lib/constants'
import type { QueryHistoryItem, GenerateResponse, ExecuteResponse } from '../types'

export default function QueryPage() {
  const [currentSQL, setCurrentSQL] = useState<string | null>(null)
  const [currentQuestion, setCurrentQuestion] = useState<string>('')
  const [generateResult, setGenerateResult] = useState<GenerateResponse | null>(null)
  const [executeResult, setExecuteResult] = useState<ExecuteResponse | null>(null)
  const [executeError, setExecuteError] = useState<string | null>(null)

  const [history, setHistory] = useLocalStorage<QueryHistoryItem[]>(QUERY_HISTORY_KEY, [])

  const generateSQL = useGenerateSQL()
  const executeQuery = useExecuteQuery()

  const handleGenerate = useCallback(
    async (question: string) => {
      setCurrentQuestion(question)
      setExecuteResult(null)
      setExecuteError(null)
      setCurrentSQL(null)
      setGenerateResult(null)

      try {
        const result = await generateSQL.mutateAsync({ question })
        setGenerateResult(result)
        setCurrentSQL(result.sql)
      } catch {
        // error handled by hook
      }
    },
    [generateSQL]
  )

  const handleExecute = useCallback(async () => {
    if (!currentSQL) return
    setExecuteError(null)
    setExecuteResult(null)

    try {
      const result = await executeQuery.mutateAsync({ sql: currentSQL })
      setExecuteResult(result)

      // Save to history
      const historyItem: QueryHistoryItem = {
        id: Date.now().toString(),
        question: currentQuestion,
        sql: currentSQL,
        timestamp: Date.now(),
        row_count: result.row_count,
      }
      setHistory((prev) => [historyItem, ...prev].slice(0, MAX_HISTORY_ITEMS))
    } catch (err) {
      setExecuteError(err instanceof Error ? err.message : 'Execution failed')
    }
  }, [currentSQL, currentQuestion, executeQuery, setHistory])

  const handleHistorySelect = useCallback((item: QueryHistoryItem) => {
    setCurrentQuestion(item.question)
    setCurrentSQL(item.sql)
    setGenerateResult({ sql: item.sql, success: true })
    setExecuteResult(null)
    setExecuteError(null)
  }, [])

  return (
    <div className="flex flex-col min-h-screen bg-slate-50">
      <Navbar />

      <div className="flex flex-1 pt-14">
        {/* Schema Sidebar */}
        <div className="hidden lg:flex sticky top-14 h-[calc(100vh-3.5rem)]">
          <ErrorBoundary>
            <SchemaSidebar />
          </ErrorBoundary>
        </div>

        {/* Main content */}
        <main className="flex-1 overflow-auto">
          <div className="max-w-3xl mx-auto px-6 py-8 space-y-5">
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.25 }}
            >
              <h1 className="text-xl font-bold text-slate-900 mb-1">Query Builder</h1>
              <p className="text-sm text-slate-500">
                Type a question in plain English and get SQL instantly.
              </p>
            </motion.div>

            {/* Query Input */}
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.25, delay: 0.05 }}
            >
              <QueryInput onSubmit={handleGenerate} isLoading={generateSQL.isPending} />
            </motion.div>

            {/* History */}
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.25, delay: 0.1 }}
            >
              <QueryHistory onSelect={handleHistorySelect} />
            </motion.div>

            {/* SQL Preview */}
            {currentSQL && (
              <SQLPreview
                sql={currentSQL}
                onExecute={handleExecute}
                isExecuting={executeQuery.isPending}
                retryCount={generateResult?.retry_count}
              />
            )}

            {/* Execution status bar */}
            {(executeResult || executeError) && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-center px-1"
              >
                <ExecutionStatus
                  isSuccess={!!executeResult}
                  isError={!!executeError}
                  executionTimeMs={executeResult?.execution_time_ms}
                  rowCount={executeResult?.row_count}
                  errorMessage={executeError ?? undefined}
                />
              </motion.div>
            )}

            {/* Error display */}
            {executeError && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3"
              >
                <AlertCircle className="w-4 h-4 text-red-500 mt-0.5 shrink-0" />
                <div>
                  <p className="text-sm font-medium text-red-800">Query Execution Failed</p>
                  <p className="text-xs text-red-600 mt-0.5">{executeError}</p>
                </div>
              </motion.div>
            )}

            {/* Results Table */}
            {executeResult && <ResultsTable data={executeResult} />}
          </div>
        </main>
      </div>
    </div>
  )
}
