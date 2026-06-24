import { motion } from 'framer-motion'
import { MessageSquare, Code2, ShieldCheck, Zap, Database, Clock } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'

const features = [
  {
    icon: MessageSquare,
    title: 'Natural Language',
    description: 'Write questions in plain English. No SQL knowledge required. Just describe what you want to know.',
    color: 'text-blue-500',
    bg: 'bg-blue-50',
  },
  {
    icon: Code2,
    title: 'Instant SQL',
    description: 'Get production-ready SQL in seconds. Powered by Mistral AI with proper JOINs, aliases, and optimizations.',
    color: 'text-violet-500',
    bg: 'bg-violet-50',
  },
  {
    icon: ShieldCheck,
    title: 'Safe Execution',
    description: 'Read-only queries only. No data modification allowed. SELECT statements only, with built-in validation.',
    color: 'text-emerald-500',
    bg: 'bg-emerald-50',
  },
  {
    icon: Database,
    title: 'Schema Aware',
    description: 'Automatically extracts your database schema including tables, columns, types, and foreign key relationships.',
    color: 'text-amber-500',
    bg: 'bg-amber-50',
  },
  {
    icon: Zap,
    title: 'Self-Correcting',
    description: 'If the generated SQL fails, the AI automatically detects the error and generates a corrected query.',
    color: 'text-orange-500',
    bg: 'bg-orange-50',
  },
  {
    icon: Clock,
    title: 'Query History',
    description: 'Every query is saved locally. Revisit and re-run previous queries with a single click.',
    color: 'text-slate-500',
    bg: 'bg-slate-100',
  },
]

export default function Features() {
  return (
    <section id="features" className="py-24 bg-white">
      <div className="max-w-[1280px] mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl font-bold text-slate-900 tracking-tight mb-4">
            Everything you need to query smarter
          </h2>
          <p className="text-slate-500 text-lg max-w-xl mx-auto">
            A complete Text-to-SQL solution built for developers and analysts.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.07, duration: 0.4 }}
            >
              <Card className="h-full hover:shadow-md hover:-translate-y-0.5 transition-all duration-200">
                <CardContent className="p-6">
                  <div className={`w-10 h-10 ${feature.bg} rounded-xl flex items-center justify-center mb-4`}>
                    <feature.icon className={`w-5 h-5 ${feature.color}`} />
                  </div>
                  <h3 className="font-semibold text-slate-900 mb-2">{feature.title}</h3>
                  <p className="text-sm text-slate-500 leading-relaxed">{feature.description}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
