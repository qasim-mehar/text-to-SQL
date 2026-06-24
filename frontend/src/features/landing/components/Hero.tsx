import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowRight, Zap } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function Hero() {
  return (
    <section className="relative overflow-hidden pt-32 pb-24 grid-bg">
      {/* Gradient Orbs */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-blue-500/8 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute top-20 right-1/4 w-[300px] h-[300px] bg-violet-500/6 rounded-full blur-3xl pointer-events-none" />

      <div className="max-w-[1280px] mx-auto px-6 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-3xl mx-auto text-center"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1, duration: 0.3 }}
            className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-medium mb-6"
          >
            <Zap className="w-3 h-3" />
            Powered by Mistral AI + LangChain
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15, duration: 0.5 }}
            className="text-5xl sm:text-6xl font-bold text-slate-900 leading-tight tracking-tight mb-6"
          >
            Ask Questions in English,{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-violet-600">
              Get SQL Instantly
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="text-lg text-slate-500 leading-relaxed mb-10 max-w-xl mx-auto"
          >
            QueryBridge translates natural language into executable database queries using AI.
            No SQL knowledge required.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25, duration: 0.5 }}
            className="flex items-center justify-center gap-4"
          >
            <Link to="/query">
              <Button id="hero-cta-btn" variant="primary" size="lg" className="gap-2 group">
                Try It Free
                <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
              </Button>
            </Link>
            <a href="#features">
              <Button variant="outline" size="lg">See Features</Button>
            </a>
          </motion.div>
        </motion.div>

        {/* Demo Card */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.6 }}
          className="mt-16 max-w-2xl mx-auto"
        >
          <div className="rounded-2xl border border-slate-200 bg-white shadow-xl shadow-slate-200/60 overflow-hidden">
            <div className="px-4 py-2.5 bg-slate-50 border-b border-slate-200 flex items-center gap-2">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-red-400" />
                <div className="w-3 h-3 rounded-full bg-amber-400" />
                <div className="w-3 h-3 rounded-full bg-emerald-400" />
              </div>
              <span className="text-xs text-slate-400 font-mono ml-2">QueryBridge</span>
            </div>
            <div className="p-5">
              <div className="text-sm text-slate-500 mb-2">Question:</div>
              <div className="text-slate-900 font-medium mb-4">"Who are the top 3 highest paid employees?"</div>
              <div className="text-sm text-slate-500 mb-2">Generated SQL:</div>
              <div className="bg-[#1a1f2e] rounded-lg p-4 font-mono text-sm leading-relaxed">
                <span className="text-blue-400">SELECT</span>{' '}
                <span className="text-slate-300">e.first_name, e.last_name, e.salary, d.department_name</span>
                <br />
                <span className="text-blue-400">FROM</span>{' '}
                <span className="text-slate-300">employees e</span>
                <br />
                <span className="text-blue-400">JOIN</span>{' '}
                <span className="text-slate-300">departments d ON e.department_id = d.department_id</span>
                <br />
                <span className="text-blue-400">ORDER BY</span>{' '}
                <span className="text-slate-300">e.salary</span>{' '}
                <span className="text-blue-400">DESC</span>
                <br />
                <span className="text-blue-400">LIMIT</span>{' '}
                <span className="text-amber-400">3</span>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
