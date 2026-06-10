import { useState, useRef } from 'react'
import { BarChart2, RefreshCw } from 'lucide-react'
import UploadCard from './components/UploadCard'
import SummaryDashboard from './components/SummaryDashboard'
import TransactionTable from './components/TransactionTable'
import CategoryChart from './components/CategoryChart'
import DownloadButton from './components/DownloadButton'
import { uploadStatement } from './utils/api'

export default function App() {
  const [status, setStatus] = useState('idle')   // idle | uploading | done | error
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const resultsRef = useRef(null)

  const handleUpload = async (file) => {
    setStatus('uploading')
    setProgress(0)
    setError(null)
    setResult(null)

    // Simulate progress stages
    const progressTimer = setInterval(() => {
      setProgress(prev => {
        if (prev >= 85) { clearInterval(progressTimer); return prev }
        return prev + Math.random() * 8
      })
    }, 400)

    try {
      const data = await uploadStatement(file, setProgress)
      clearInterval(progressTimer)
      setProgress(100)
      setResult(data)
      setStatus('done')

      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }, 300)
    } catch (err) {
      clearInterval(progressTimer)
      setStatus('error')
      const msg = err.response?.data?.detail || err.message || 'An unexpected error occurred.'
      setError(msg)
    }
  }

  const handleReset = () => {
    setStatus('idle')
    setProgress(0)
    setError(null)
    setResult(null)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* ── Navbar ──────────────────────────────────────────────────────── */}
      <nav className="sticky top-0 z-50 border-b border-white/10 bg-navy-950/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-brand">
              <BarChart2 className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-white text-lg tracking-tight">StatementIQ</span>
            <span className="hidden sm:block px-1.5 py-0.5 text-xs font-medium rounded bg-brand/20 text-brand border border-brand/30">
              HDFC
            </span>
          </div>
          <div className="flex items-center gap-3">
            {result && (
              <button onClick={handleReset} className="btn-secondary text-sm py-2">
                <RefreshCw className="w-4 h-4" /> New Analysis
              </button>
            )}
          </div>
        </div>
      </nav>

      {/* ── Hero ────────────────────────────────────────────────────────── */}
      <section className="flex flex-col items-center justify-center px-4 pt-16 pb-12 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand/10 border border-brand/20 text-brand text-xs font-medium mb-6">
          <span className="w-1.5 h-1.5 rounded-full bg-brand animate-pulse" />
          Supports HDFC Bank PDF statements
        </div>
        <h1 className="text-4xl sm:text-5xl font-extrabold text-white tracking-tight leading-tight max-w-2xl">
          Instant Bank Statement
          <span className="block text-transparent bg-clip-text bg-gradient-to-r from-brand to-blue-300">
            Intelligence
          </span>
        </h1>
        <p className="mt-4 text-base text-slate-400 max-w-lg leading-relaxed">
          Upload your HDFC Bank PDF statement and get a full transaction breakdown,
          smart categorization, and a downloadable Excel report — in seconds.
        </p>

        {/* Feature pills */}
        <div className="flex flex-wrap justify-center gap-2 mt-6">
          {['Zero transactions dropped', 'Auto-categorization', '3-sheet Excel export', 'Salary & EMI detection'].map(f => (
            <span key={f} className="text-xs px-3 py-1 rounded-full bg-white/5 border border-white/10 text-slate-300">
              ✓ {f}
            </span>
          ))}
        </div>
      </section>

      {/* ── Upload Section ──────────────────────────────────────────────── */}
      <section className="px-4 sm:px-6 pb-12 flex justify-center">
        <div className="w-full max-w-2xl">
          <UploadCard
            onUpload={handleUpload}
            loading={status === 'uploading'}
            progress={Math.round(progress)}
            error={status === 'error' ? error : null}
            onClearError={() => { setStatus('idle'); setError(null) }}
          />
        </div>
      </section>

      {/* ── Results Section ─────────────────────────────────────────────── */}
      {result && (
        <div ref={resultsRef} className="flex-1 px-4 sm:px-6 pb-16 max-w-7xl mx-auto w-full space-y-8 animate-fade-in">
          {/* Divider */}
          <div className="flex items-center gap-4">
            <div className="flex-1 h-px bg-white/10" />
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Analysis Complete</span>
            <div className="flex-1 h-px bg-white/10" />
          </div>

          {/* Summary Dashboard */}
          <div>
            <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <span className="w-1 h-5 rounded-full bg-brand inline-block" />
              Account Overview
            </h2>
            <SummaryDashboard
              account={result.account}
              totalTransactions={result.total_transactions}
              pctCategorized={result.pct_categorized}
              parseWarnings={result.parse_warnings}
            />
          </div>

          {/* Chart + Download side-by-side on large screens */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <span className="w-1 h-5 rounded-full bg-violet-500 inline-block" />
                Spending Breakdown
              </h2>
              <CategoryChart categorySummary={result.category_summary} />
            </div>

            <div className="flex flex-col gap-6">
              {/* Category list */}
              <div>
                <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <span className="w-1 h-5 rounded-full bg-emerald-500 inline-block" />
                  Category Summary
                </h2>
                <div className="glass-card divide-y divide-white/5 overflow-hidden">
                  {result.category_summary
                    .sort((a, b) => (b.total_debit + b.total_credit) - (a.total_debit + a.total_credit))
                    .slice(0, 8)
                    .map(cat => (
                      <div key={cat.category} className="flex items-center gap-3 px-4 py-3 hover:bg-white/5 transition-colors">
                        <div
                          className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                          style={{ backgroundColor: `var(--cat-${cat.category.replace(/[\s/]/g, '-')})` || '#94A3B8' }}
                        />
                        <span className="flex-1 text-sm text-white">{cat.category}</span>
                        <span className="text-xs text-slate-400">{cat.count} txns</span>
                        {cat.total_debit > 0 && (
                          <span className="text-xs text-red-400 font-mono">
                            −₹{(cat.total_debit / 1000).toFixed(1)}K
                          </span>
                        )}
                        {cat.total_credit > 0 && (
                          <span className="text-xs text-emerald-400 font-mono">
                            +₹{(cat.total_credit / 1000).toFixed(1)}K
                          </span>
                        )}
                      </div>
                    ))}
                </div>
              </div>
            </div>
          </div>

          {/* Download CTA */}
          <div>
            <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <span className="w-1 h-5 rounded-full bg-amber-500 inline-block" />
              Export Report
            </h2>
            <DownloadButton
              sessionId={result.session_id}
              totalTransactions={result.total_transactions}
            />
          </div>

          {/* Transaction Table */}
          <div>
            <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <span className="w-1 h-5 rounded-full bg-cyan-500 inline-block" />
              Transactions Preview
            </h2>
            <TransactionTable
              transactions={result.transactions}
              totalTransactions={result.total_transactions}
            />
          </div>

          {/* Second Download */}
          <div className="text-center py-4">
            <p className="text-slate-400 text-sm mb-4">
              Full data including all {result.total_transactions} transactions is available in the Excel report.
            </p>
            <DownloadButton
              sessionId={result.session_id}
              totalTransactions={result.total_transactions}
            />
          </div>
        </div>
      )}

      {/* ── Footer ──────────────────────────────────────────────────────── */}
      <footer className="border-t border-white/10 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          <p className="text-xs text-slate-500">
            StatementIQ — HDFC Bank Statement Analyzer
          </p>
          <p className="text-xs text-slate-500">
            Built with ReactJS + FastAPI
          </p>
        </div>
      </footer>
    </div>
  )
}
