import { useState, useRef, useEffect } from 'react'
import { Sparkles, Send, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { EXAMPLE_QUESTIONS } from '@/lib/constants'
import { cn } from '@/lib/utils'

interface QueryInputProps {
  onSubmit: (question: string) => void
  isLoading: boolean
}

export default function QueryInput({ onSubmit, isLoading }: QueryInputProps) {
  const [question, setQuestion] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSubmit = () => {
    if (question.trim() && !isLoading) {
      onSubmit(question.trim())
    }
  }

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        handleSubmit()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [question, isLoading])

  return (
    <Card className="shadow-none">
      <CardContent className="p-5">
        <div className="flex items-start gap-2 mb-3">
          <Sparkles className="w-4 h-4 text-blue-500 mt-0.5 shrink-0" />
          <h3 className="text-sm font-semibold text-slate-900">Ask in Natural Language</h3>
        </div>
        <textarea
          ref={textareaRef}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g., How many employees are in each department?"
          rows={3}
          className={cn(
            'w-full resize-none rounded-lg border border-slate-200 bg-slate-50 px-4 py-3',
            'text-sm text-slate-900 placeholder:text-slate-400',
            'focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-300 focus:bg-white',
            'transition-all duration-150'
          )}
          disabled={isLoading}
        />
        <div className="flex items-center justify-between mt-3">
          <div className="flex flex-wrap gap-1.5">
            {EXAMPLE_QUESTIONS.slice(0, 3).map((q) => (
              <button
                key={q}
                onClick={() => setQuestion(q)}
                disabled={isLoading}
                className="text-xs px-2.5 py-1 rounded-full bg-slate-100 hover:bg-blue-50 hover:text-blue-700 text-slate-600 transition-colors border border-slate-200 hover:border-blue-200 disabled:opacity-50"
              >
                {q.length > 35 ? q.slice(0, 35) + '…' : q}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400 hidden sm:block">Ctrl+Enter</span>
            <Button
              id="generate-sql-btn"
              variant="primary"
              size="sm"
              onClick={handleSubmit}
              disabled={!question.trim() || isLoading}
              className="gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" /> Generating...
                </>
              ) : (
                <>
                  <Send className="w-3.5 h-3.5" /> Generate SQL
                </>
              )}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
