import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function CTA() {
  return (
    <section className="py-24 bg-slate-900">
      <div className="max-w-[1280px] mx-auto px-6 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-3xl font-bold text-white tracking-tight mb-4">
            Ready to query your database?
          </h2>
          <p className="text-slate-400 text-lg mb-8 max-w-md mx-auto">
            Start translating plain English into SQL queries in seconds.
          </p>
          <Link to="/query">
            <Button id="cta-try-btn" size="lg" variant="primary" className="gap-2 group">
              Open Query Builder
              <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
            </Button>
          </Link>
        </motion.div>
      </div>
    </section>
  )
}
