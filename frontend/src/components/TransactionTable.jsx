import { useState } from 'react'
import { Search, ChevronUp, ChevronDown, Filter } from 'lucide-react'
import { formatCurrency, truncate, CATEGORY_BG } from '../utils/format'

const ITEMS_PER_PAGE = 20

export default function TransactionTable({ transactions, totalTransactions }) {
  const [search, setSearch] = useState('')
  const [filterCategory, setFilterCategory] = useState('All')
  const [sortField, setSortField] = useState(null)
  const [sortDir, setSortDir] = useState('desc')

  const categories = ['All', ...new Set(transactions.map(t => t.category))]

  const filtered = transactions
    .filter(t => {
      const matchSearch = !search || t.description.toLowerCase().includes(search.toLowerCase())
      const matchCat = filterCategory === 'All' || t.category === filterCategory
      return matchSearch && matchCat
    })
    .sort((a, b) => {
      if (!sortField) return 0
      let va = a[sortField], vb = b[sortField]
      if (sortField === 'amount') {
        va = (a.credit || 0) - (a.debit || 0)
        vb = (b.credit || 0) - (b.debit || 0)
      }
      return sortDir === 'asc' ? (va > vb ? 1 : -1) : (va < vb ? 1 : -1)
    })

  const displayed = filtered.slice(0, ITEMS_PER_PAGE)

  const toggleSort = (field) => {
    if (sortField === field) {
      setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDir('desc')
    }
  }

  const SortIcon = ({ field }) => {
    if (sortField !== field) return <ChevronUp className="w-3 h-3 opacity-30" />
    return sortDir === 'asc'
      ? <ChevronUp className="w-3 h-3 text-brand" />
      : <ChevronDown className="w-3 h-3 text-brand" />
  }

  return (
    <div className="glass-card overflow-hidden">
      {/* Header */}
      <div className="p-5 border-b border-white/10">
        <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
          <div>
            <h3 className="section-title mb-0">Transaction Ledger</h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Showing {displayed.length} of {filtered.length} filtered
              {filtered.length !== totalTransactions && ` (${totalTransactions} total)`}
            </p>
          </div>
          <div className="flex gap-2 w-full sm:w-auto">
            {/* Search */}
            <div className="relative flex-1 sm:flex-none">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search description…"
                value={search}
                onChange={e => setSearch(e.target.value)}
                className="pl-9 pr-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm
                           text-white placeholder-slate-500 outline-none focus:border-brand/60
                           transition-colors w-full sm:w-52"
              />
            </div>
            {/* Category filter */}
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400 pointer-events-none" />
              <select
                value={filterCategory}
                onChange={e => setFilterCategory(e.target.value)}
                className="pl-8 pr-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm
                           text-white outline-none focus:border-brand/60 appearance-none cursor-pointer"
              >
                {categories.map(c => <option key={c} value={c} className="bg-navy-900">{c}</option>)}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-white/10 bg-white/3">
              {[
                { key: 'date', label: 'Date' },
                { key: 'description', label: 'Description' },
                { key: 'cheque_ref', label: 'Ref No.' },
                { key: 'amount', label: 'Amount' },
                { key: 'balance', label: 'Balance' },
                { key: 'category', label: 'Category' },
              ].map(col => (
                <th
                  key={col.key}
                  onClick={() => toggleSort(col.key)}
                  className="table-cell font-medium text-slate-400 text-left cursor-pointer hover:text-white select-none"
                >
                  <div className="flex items-center gap-1">
                    {col.label}
                    <SortIcon field={col.key} />
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {displayed.map((txn, i) => (
              <tr
                key={i}
                className={`border-b border-white/5 transition-colors hover:bg-white/5
                  ${txn.credit ? 'bg-emerald-500/3' : txn.debit ? 'bg-red-500/3' : ''}`}
              >
                <td className="table-cell text-slate-300 whitespace-nowrap">{txn.date}</td>
                <td className="table-cell text-white max-w-xs">
                  <span title={txn.description}>{truncate(txn.description, 45)}</span>
                </td>
                <td className="table-cell text-slate-400 font-mono text-xs">{txn.cheque_ref || '—'}</td>
                <td className="table-cell text-right font-mono font-medium whitespace-nowrap">
                  {txn.credit
                    ? <span className="text-emerald-400">+{formatCurrency(txn.credit)}</span>
                    : txn.debit
                    ? <span className="text-red-400">−{formatCurrency(txn.debit)}</span>
                    : '—'
                  }
                </td>
                <td className="table-cell text-slate-300 text-right font-mono whitespace-nowrap">
                  {formatCurrency(txn.balance)}
                </td>
                <td className="table-cell">
                  <span className={`badge ${CATEGORY_BG[txn.category] || 'bg-slate-500/20 text-slate-300'}`}>
                    {txn.category}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {displayed.length === 0 && (
        <div className="p-10 text-center text-slate-400">
          No transactions match your filters.
        </div>
      )}

      {filtered.length > ITEMS_PER_PAGE && (
        <div className="p-4 border-t border-white/10 text-center text-xs text-slate-400">
          Showing first {ITEMS_PER_PAGE} of {filtered.length} results.
          Full data is available in the Excel download.
        </div>
      )}
    </div>
  )
}
