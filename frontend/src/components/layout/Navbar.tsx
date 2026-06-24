import { Link, useLocation } from 'react-router-dom'
import { Zap } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'

export default function Navbar() {
  const location = useLocation()

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-transparent">
      <div className="max-w-[1280px] mx-auto px-6 h-14 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="w-8 h-8 flex items-center justify-center rounded-lg shadow-sm group-hover:scale-105 transition-transform overflow-hidden border border-slate-200">
            <img
              src="/assets/Gemini_Generated_Image_k1ssfbk1ssfbk1ss.png"
              alt="QueryBridge Logo"
              className="w-full h-full object-cover"
            />
          </div>

        </Link>

        <div className="flex items-center gap-1">
          <Link to="/">
            <Button
              variant="ghost"
              size="sm"
              className={cn(location.pathname === '/' && 'bg-slate-100 text-slate-900')}
            >
              Home
            </Button>
          </Link>
          <Link to="/query">
            <Button
              variant={location.pathname === '/query' ? 'primary' : 'ghost'}
              size="sm"
              className="gap-1.5"
            >
              <Zap className="w-3.5 h-3.5" />
              Query Builder
            </Button>
          </Link>
        </div>
      </div>
    </nav>
  )
}