import { Component, type ReactNode } from 'react'
import { AlertTriangle } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface Props { children: ReactNode }
interface State { hasError: boolean; error?: Error }

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center h-64 gap-4">
          <div className="w-12 h-12 rounded-full bg-red-50 flex items-center justify-center">
            <AlertTriangle className="w-6 h-6 text-red-500" />
          </div>
          <div className="text-center">
            <h3 className="font-semibold text-slate-900">Something went wrong</h3>
            <p className="text-sm text-slate-500 mt-1">{this.state.error?.message}</p>
          </div>
          <Button onClick={() => this.setState({ hasError: false })} variant="outline" size="sm">
            Try again
          </Button>
        </div>
      )
    }
    return this.props.children
  }
}
