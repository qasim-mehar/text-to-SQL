import { useState } from 'react'
import { Copy, Check, Play, Loader2 } from 'lucide-react'
import { motion } from 'framer-motion'
import SyntaxHighlighter from 'react-syntax-highlighter'
import { atomOneDark } from 'react-syntax-highlighter/dist/esm/styles/hljs'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tooltip, TooltipContent, TooltipTrigger, TooltipProvider } from '@/components/ui/tooltip'

interface SQLPreviewProps {
  sql: string
  onExecute: () => void
  isExecuting: boolean
  retryCount?: number
}

export default function SQLPreview({ sql, onExecute, isExecuting, retryCount }: SQLPreviewProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(sql)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
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
            <CardTitle className="text-sm">Generated SQL</CardTitle>
            {retryCount !== undefined && retryCount > 0 && (
              <Badge variant="warning" className="text-[10px]">
                Self-corrected
              </Badge>
            )}
          </div>
          <div className="flex items-center gap-2">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    id="copy-sql-btn"
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7"
                    onClick={handleCopy}
                  >
                    {copied ? (
                      <Check className="w-3.5 h-3.5 text-emerald-500" />
                    ) : (
                      <Copy className="w-3.5 h-3.5" />
                    )}
                  </Button>
                </TooltipTrigger>
                <TooltipContent>{copied ? 'Copied!' : 'Copy SQL'}</TooltipContent>
              </Tooltip>
            </TooltipProvider>
            <Button
              id="execute-sql-btn"
              variant="primary"
              size="sm"
              onClick={onExecute}
              disabled={isExecuting}
              className="gap-2 h-7 text-xs"
            >
              {isExecuting ? (
                <>
                  <Loader2 className="w-3 h-3 animate-spin" /> Running...
                </>
              ) : (
                <>
                  <Play className="w-3 h-3" /> Execute
                </>
              )}
            </Button>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <SyntaxHighlighter
            language="sql"
            style={atomOneDark}
            customStyle={{
              margin: 0,
              borderRadius: 0,
              fontSize: '13px',
              lineHeight: '1.6',
              padding: '16px 20px',
              background: '#1a1f2e',
              minHeight: '80px',
            }}
            showLineNumbers={false}
          >
            {sql}
          </SyntaxHighlighter>
        </CardContent>
      </Card>
    </motion.div>
  )
}
