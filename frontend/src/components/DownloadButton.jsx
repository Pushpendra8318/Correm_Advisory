import { useState } from 'react'
import { Download, CheckCircle, Loader2, FileSpreadsheet } from 'lucide-react'
import { getDownloadUrl } from '../utils/api'

export default function DownloadButton({ sessionId, totalTransactions }) {
  const [state, setState] = useState('idle') // idle | downloading | success

  const handleDownload = async () => {
    if (!sessionId || state === 'downloading') return
    setState('downloading')

    try {
      const url = getDownloadUrl(sessionId)
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `HDFC_Statement_${sessionId.slice(0, 8)}.xlsx`)
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      setTimeout(() => setState('success'), 800)
      setTimeout(() => setState('idle'), 4000)
    } catch {
      setState('idle')
    }
  }

  return (
    <div className="glass-card p-6 flex flex-col sm:flex-row items-center gap-6">
      <div className="flex items-center gap-4 flex-1">
        <div className="flex items-center justify-center w-14 h-14 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex-shrink-0">
          <FileSpreadsheet className="w-7 h-7 text-emerald-400" />
        </div>
        <div>
          <p className="font-semibold text-white">Download Excel Report</p>
          <p className="text-sm text-slate-400 mt-0.5">
            3-sheet report · {totalTransactions} transactions · Categories & Analytics
          </p>
          <div className="flex gap-2 mt-2">
            {['Account Details', 'Transaction Ledger', 'Analytics'].map(sheet => (
              <span key={sheet} className="text-xs px-2 py-0.5 rounded border border-emerald-500/30 text-emerald-400 bg-emerald-500/10">
                {sheet}
              </span>
            ))}
          </div>
        </div>
      </div>

      <button
        onClick={handleDownload}
        disabled={state === 'downloading'}
        className={`flex-shrink-0 btn-primary py-3.5 px-8 text-base
          ${state === 'success'
            ? 'bg-emerald-600 hover:bg-emerald-700'
            : state === 'downloading'
            ? 'opacity-75 cursor-not-allowed'
            : ''
          }`}
      >
        {state === 'idle' && <><Download className="w-5 h-5" /> Download .xlsx</>}
        {state === 'downloading' && <><Loader2 className="w-5 h-5 animate-spin-slow" /> Preparing…</>}
        {state === 'success' && <><CheckCircle className="w-5 h-5" /> Downloaded!</>}
      </button>
    </div>
  )
}
