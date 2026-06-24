import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Zap,
  Database,
  Code2,
  Shield,
  ArrowRight,
  ChevronRight,
  Sparkles,
  BarChart3,
  Users,
  TrendingUp,
} from 'lucide-react'
import Navbar from '@/components/layout/Navbar'
import Footer from '@/components/layout/Footer'
import Container from '@/components/layout/Container'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { EXAMPLE_QUESTIONS } from '@/lib/constants'

const FEATURES = [
  {
    icon: Sparkles,
    title: 'AI-Powered Translation',
    description:
      'Mistral AI understands your natural language and generates precise, optimized SQL queries every time.',
    color: 'text-violet-500',
    bg: 'bg-violet-50',
  },
  {
    icon: Zap,
    title: 'Instant Execution',
    description:
      'Run generated queries directly against your company analytics database with one click.',
    color: 'text-amber-500',
    bg: 'bg-amber-50',
  },
  {
    icon: Shield,
    title: 'Self-Correcting',
    description:
      'Built-in validation loop automatically detects and fixes SQL errors before you see them.',
    color: 'text-emerald-500',
    bg: 'bg-emerald-50',
  },
  {
    icon: Code2,
    title: 'Schema-Aware',
    description:
      'The AI always knows your full schema — tables, columns, types, and relationships.',
    color: 'text-blue-500',
    bg: 'bg-blue-50',
  },
  {
    icon: BarChart3,
    title: 'Rich Results',
    description:
      'Sortable, scrollable data tables with execution time and row count metadata.',
    color: 'text-pink-500',
    bg: 'bg-pink-50',
  },
  {
    icon: Database,
    title: 'Query History',
    description:
      'Every query is saved locally so you can revisit, re-run, or build on previous work.',
    color: 'text-indigo-500',
    bg: 'bg-indigo-50',
  },
]

const TABLES = [
  { name: 'employees', icon: Users, count: '5 cols', color: 'text-blue-500' },
  { name: 'departments', icon: Database, count: '4 cols', color: 'text-violet-500' },
  { name: 'projects', icon: Code2, count: '6 cols', color: 'text-emerald-500' },
  { name: 'sales', icon: TrendingUp, count: '5 cols', color: 'text-amber-500' },
  { name: 'expenses', icon: BarChart3, count: '5 cols', color: 'text-pink-500' },
]

const SQL_DEMO = `SELECT
  d.name AS department,
  COUNT(e.id) AS headcount,
  AVG(e.salary) AS avg_salary
FROM departments d
JOIN employees e ON e.department_id = d.id
GROUP BY d.name
ORDER BY headcount DESC;`

const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.07 } },
}

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4 } },
}

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />

      {/* ── Hero ─────────────────────────────────────────────────────────── */}
      <section className="relative pt-28 pb-20 grid-bg overflow-hidden">
        {/* Decorative blobs */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[700px] h-[400px] bg-blue-500/5 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute top-20 right-0 w-[400px] h-[400px] bg-violet-500/5 rounded-full blur-3xl pointer-events-none" />

        <Container className="relative">
          <motion.div
            initial="hidden"
            animate="show"
            variants={stagger}
            className="max-w-3xl mx-auto text-center"
          >


            <motion.h1
              variants={fadeUp}
              className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 leading-tight tracking-tight mb-6"
            >
              Turn{' '}
              <span className="text-blue-500">plain English</span>
              <br />
              into SQL instantly
            </motion.h1>

            <motion.p
              variants={fadeUp}
              className="text-lg text-slate-500 mb-10 max-w-xl mx-auto leading-relaxed"
            >
              QueryBridge bridges the gap between your question and your data. No SQL knowledge
              required. Just ask, and get results.
            </motion.p>

            <motion.div variants={fadeUp} className="flex items-center justify-center gap-3">
              <Link to="/query">
                <Button variant="primary" size="lg" className="gap-2 shadow-lg shadow-blue-500/20">
                  <Zap className="w-4 h-4" />
                  Try Query Builder
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
              <a href="#features">
                <Button variant="outline" size="lg">
                  See Features
                </Button>
              </a>
            </motion.div>

            {/* Example pill questions */}
            <motion.div
              variants={fadeUp}
              className="mt-10 flex flex-wrap items-center justify-center gap-2"
            >
              {EXAMPLE_QUESTIONS.map((q) => (
                <Link key={q} to="/query">
                  <span className="inline-flex items-center gap-1.5 text-xs px-3 py-1.5 bg-white rounded-full border border-slate-200 text-slate-600 hover:border-blue-300 hover:text-blue-700 hover:bg-blue-50 transition-colors shadow-sm cursor-pointer">
                    <ChevronRight className="w-3 h-3 text-slate-400" />
                    {q}
                  </span>
                </Link>
              ))}
            </motion.div>
          </motion.div>

          {/* Demo card */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="mt-16 max-w-2xl mx-auto"
          >
            <div className="rounded-2xl border border-slate-200 bg-white shadow-xl shadow-slate-200/60 overflow-hidden">
              {/* Traffic lights */}
              <div className="flex items-center gap-1.5 px-4 py-3 bg-slate-50 border-b border-slate-200">
                <div className="w-3 h-3 rounded-full bg-red-400" />
                <div className="w-3 h-3 rounded-full bg-amber-400" />
                <div className="w-3 h-3 rounded-full bg-emerald-400" />
                <span className="ml-2 text-xs text-slate-400 font-mono">querybridge — sql preview</span>
              </div>
              {/* Question bubble */}
              <div className="px-6 pt-5 pb-3">
                <div className="flex items-start gap-2 mb-4">
                  <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center shrink-0 mt-0.5">
                    <Sparkles className="w-3 h-3 text-blue-500" />
                  </div>
                  <div className="bg-blue-50 rounded-xl rounded-tl-none px-4 py-2.5 text-sm text-blue-800 border border-blue-100">
                    How many employees are in each department with avg salary?
                  </div>
                </div>
              </div>
              {/* SQL */}
              <div className="bg-[#1a1f2e] px-6 py-4 font-mono text-[13px] leading-relaxed">
                {SQL_DEMO.split('\n').map((line, i) => (
                  <div key={i} className="flex gap-4">
                    <span className="text-slate-600 select-none w-4 text-right shrink-0">
                      {i + 1}
                    </span>
                    <span
                      className={
                        line.match(/^(SELECT|FROM|JOIN|WHERE|GROUP|ORDER|ON|AS|BY|DESC|AVG|COUNT)/)
                          ? 'text-blue-400'
                          : line.match(/[a-z]+\.[a-z]+/)
                          ? 'text-emerald-400'
                          : 'text-slate-300'
                      }
                    >
                      {line || '\u00A0'}
                    </span>
                  </div>
                ))}
              </div>
              {/* Bottom status */}
              <div className="px-6 py-3 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
                <Badge variant="success" className="gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                  Generated
                </Badge>
                <span className="text-xs text-slate-400">5 rows · 42ms</span>
              </div>
            </div>
          </motion.div>
        </Container>
      </section>

      {/* ── Schema Overview ───────────────────────────────────────────────── */}
      <section className="py-16 bg-white border-y border-slate-200">
        <Container>
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4 }}
            className="text-center mb-10"
          >
            <h2 className="text-2xl font-bold text-slate-900 mb-2">Company Analytics Database</h2>
            <p className="text-slate-500 text-sm">5 interconnected tables ready to query</p>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="show"
            viewport={{ once: true }}
            variants={stagger}
            className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4"
          >
            {TABLES.map(({ name, icon: Icon, count, color }) => (
              <motion.div key={name} variants={fadeUp}>
                <Card className="shadow-none hover:shadow-md hover:border-slate-300 transition-all duration-200 cursor-default">
                  <CardContent className="p-5 flex flex-col items-center text-center gap-3">
                    <div className={`w-10 h-10 rounded-lg bg-slate-50 flex items-center justify-center`}>
                      <Icon className={`w-5 h-5 ${color}`} />
                    </div>
                    <div>
                      <p className="font-semibold text-slate-800 text-sm">{name}</p>
                      <p className="text-xs text-slate-400 mt-0.5">{count}</p>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        </Container>
      </section>

      {/* ── Features ─────────────────────────────────────────────────────── */}
      <section id="features" className="py-20 bg-slate-50">
        <Container>
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4 }}
            className="text-center mb-14"
          >
            <Badge variant="secondary" className="mb-4">Features</Badge>
            <h2 className="text-3xl font-bold text-slate-900 mb-3">
              Everything you need to query data
            </h2>
            <p className="text-slate-500 max-w-lg mx-auto">
              A complete AI-powered SQL interface built for analysts, developers, and anyone who
              works with data.
            </p>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="show"
            viewport={{ once: true }}
            variants={stagger}
            className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5"
          >
            {FEATURES.map(({ icon: Icon, title, description, color, bg }) => (
              <motion.div key={title} variants={fadeUp}>
                <Card className="shadow-none h-full hover:shadow-md hover:border-slate-300 transition-all duration-200">
                  <CardContent className="p-6">
                    <div className={`w-10 h-10 ${bg} rounded-xl flex items-center justify-center mb-4`}>
                      <Icon className={`w-5 h-5 ${color}`} />
                    </div>
                    <h3 className="font-semibold text-slate-900 mb-2">{title}</h3>
                    <p className="text-sm text-slate-500 leading-relaxed">{description}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        </Container>
      </section>

      {/* ── How It Works ─────────────────────────────────────────────────── */}
      <section className="py-20 bg-white">
        <Container>
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4 }}
            className="text-center mb-14"
          >
            <Badge variant="secondary" className="mb-4">How it works</Badge>
            <h2 className="text-3xl font-bold text-slate-900">Three steps to your answer</h2>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="show"
            viewport={{ once: true }}
            variants={stagger}
            className="grid md:grid-cols-3 gap-8 max-w-3xl mx-auto"
          >
            {[
              {
                step: '01',
                title: 'Ask your question',
                desc: 'Type any question about your data in plain English — no SQL syntax needed.',
                color: 'bg-blue-500',
              },
              {
                step: '02',
                title: 'AI generates SQL',
                desc: 'Mistral AI reads your schema and crafts a precise, optimized SQL query.',
                color: 'bg-violet-500',
              },
              {
                step: '03',
                title: 'See your results',
                desc: 'Execute the query and view results in an interactive, sortable table.',
                color: 'bg-emerald-500',
              },
            ].map(({ step, title, desc, color }) => (
              <motion.div key={step} variants={fadeUp} className="text-center">
                <div
                  className={`w-12 h-12 ${color} rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-md`}
                >
                  <span className="text-white font-bold text-sm">{step}</span>
                </div>
                <h3 className="font-semibold text-slate-900 mb-2">{title}</h3>
                <p className="text-sm text-slate-500 leading-relaxed">{desc}</p>
              </motion.div>
            ))}
          </motion.div>
        </Container>
      </section>

      {/* ── CTA ──────────────────────────────────────────────────────────── */}
      <section className="py-20 bg-slate-900">
        <Container>
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4 }}
            className="text-center"
          >
            <h2 className="text-3xl font-bold text-white mb-4">
              Ready to bridge the gap?
            </h2>
            <p className="text-slate-400 mb-8 max-w-md mx-auto">
              Start querying your company database with natural language in seconds.
            </p>
            <Link to="/query">
              <Button size="lg" variant="primary" className="gap-2 shadow-lg shadow-blue-500/30">
                <Zap className="w-4 h-4" />
                Open Query Builder
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </motion.div>
        </Container>
      </section>

      <Footer />
    </div>
  )
}
