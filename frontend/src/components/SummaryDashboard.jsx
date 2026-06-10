import { formatCurrency, formatNumber } from '../utils/format'
import {
  User, Hash, Calendar, Building2, CreditCard,
  TrendingUp, TrendingDown, Activity, AlertTriangle
} from 'lucide-react'

function StatCard({ icon: Icon, label, value, sub, color = 'blue', trend }) {
  const colorMap = {
    blue: 'from-blue-500/20 to-blue-600/10 border-blue-500/20 text-blue-400',
    green: 'from-emerald-500/20 to-emerald-600/10 border-emerald-500/20 text-emerald-400',
    red: 'from-red-500/20 to-red-600/10 border-red-500/20 text-red-400',
    purple: 'from-violet-500/20 to-violet-600/10 border-violet-500/20 text-violet-400',
    amber: 'from-amber-500/20 to-amber-600/10 border-amber-500/20 text-amber-400',
  }

  return (
    <div className={`glass-card p-5 bg-gradient-to-br ${colorMap[color]} animate-slide-up`}>
      <div className="flex items-start justify-between mb-3">
        <div className={`p-2 rounded-lg bg-white/5 border border-white/10`}>
          <Icon className={`w-5 h-5 ${colorMap[color].split(' ').pop()}`} />
        </div>
        {trend !== undefined && (
          <span className={`text-xs font-medium ${trend >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            {trend >= 0 ? '+' : ''}{trend}%
          </span>
        )}
      </div>
      <p className="label-text mb-1">{label}</p>
      <p className="text-xl font-bold text-white leading-tight">{value}</p>
      {sub && <p className="text-xs text-slate-400 mt-1">{sub}</p>}
    </div>
  )
}

function InfoRow({ icon: Icon, label, value }) {
  return (
    <div className="flex items-center gap-3 py-3 border-b border-white/5 last:border-0">
      <div className="p-2 rounded-lg bg-white/5">
        <Icon className="w-4 h-4 text-blue-400" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="label-text">{label}</p>
        <p className="value-text truncate">{value || '—'}</p>
      </div>
    </div>
  )
}

export default function SummaryDashboard({ account, totalTransactions, pctCategorized, parseWarnings }) {
  const netFlow = (account.total_credit_amount || 0) - (account.total_debit_amount || 0)

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Parse warnings */}
      {parseWarnings?.length > 0 && (
        <div className="flex items-start gap-3 p-4 rounded-xl bg-amber-500/10 border border-amber-500/30">
          <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-amber-300">Parser Warnings</p>
            <ul className="mt-1 space-y-0.5">
              {parseWarnings.map((w, i) => (
                <li key={i} className="text-xs text-amber-400/80">{w}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Account Info */}
        <div className="glass-card p-5 lg:col-span-1">
          <h3 className="text-sm font-semibold text-blue-300 uppercase tracking-wider mb-3">
            Account Info
          </h3>
          <InfoRow icon={User} label="Account Holder" value={account.holder_name} />
          <InfoRow icon={Hash} label="Account Number" value={account.account_number} />
          <InfoRow icon={Building2} label="Branch" value={account.branch} />
          <InfoRow icon={CreditCard} label="IFSC Code" value={account.ifsc} />
          <InfoRow
            icon={Calendar}
            label="Statement Period"
            value={account.statement_from && account.statement_to
              ? `${account.statement_from} → ${account.statement_to}`
              : account.statement_from || '—'}
          />
        </div>

        {/* Stats Grid */}
        <div className="lg:col-span-2 grid grid-cols-2 gap-4">
          <StatCard
            icon={TrendingUp}
            label="Total Credits"
            value={formatCurrency(account.total_credit_amount)}
            sub={`${formatNumber(account.total_credit_count)} transactions`}
            color="green"
          />
          <StatCard
            icon={TrendingDown}
            label="Total Debits"
            value={formatCurrency(account.total_debit_amount)}
            sub={`${formatNumber(account.total_debit_count)} transactions`}
            color="red"
          />
          <StatCard
            icon={Activity}
            label="Net Flow"
            value={formatCurrency(Math.abs(netFlow))}
            sub={netFlow >= 0 ? 'Net positive' : 'Net negative'}
            color={netFlow >= 0 ? 'green' : 'red'}
          />
          <StatCard
            icon={CreditCard}
            label="Transactions"
            value={formatNumber(totalTransactions)}
            sub={`${pctCategorized}% categorized`}
            color="purple"
          />
          <StatCard
            icon={Building2}
            label="Opening Balance"
            value={formatCurrency(account.opening_balance)}
            color="blue"
          />
          <StatCard
            icon={Building2}
            label="Closing Balance"
            value={formatCurrency(account.closing_balance)}
            color="amber"
          />
        </div>
      </div>
    </div>
  )
}
