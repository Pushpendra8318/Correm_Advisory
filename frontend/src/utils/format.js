export function formatCurrency(amount) {
  if (amount == null || amount === '') return '—'
  const num = Number(amount)
  if (isNaN(num)) return '—'
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(num)
}

export function formatNumber(num) {
  if (num == null) return '0'
  return new Intl.NumberFormat('en-IN').format(num)
}

export function truncate(str, max = 40) {
  if (!str) return ''
  return str.length > max ? str.slice(0, max) + '…' : str
}

export const CATEGORY_COLORS = {
  'Salary': '#10B981',
  'EMI / Loan': '#EF4444',
  'Food & Dining': '#F59E0B',
  'Travel': '#6366F1',
  'Shopping': '#EC4899',
  'Utilities': '#6B7280',
  'Telecom': '#06B6D4',
  'Entertainment': '#8B5CF6',
  'Healthcare': '#14B8A6',
  'Education': '#F97316',
  'Investments': '#22C55E',
  'Insurance': '#A855F7',
  'Cash Withdrawal': '#EAB308',
  'UPI / Transfer': '#3B82F6',
  'Rent': '#D946EF',
  'Other': '#94A3B8',
}

export const CATEGORY_BG = {
  'Salary': 'bg-emerald-500/20 text-emerald-300',
  'EMI / Loan': 'bg-red-500/20 text-red-300',
  'Food & Dining': 'bg-amber-500/20 text-amber-300',
  'Travel': 'bg-indigo-500/20 text-indigo-300',
  'Shopping': 'bg-pink-500/20 text-pink-300',
  'Utilities': 'bg-gray-500/20 text-gray-300',
  'Telecom': 'bg-cyan-500/20 text-cyan-300',
  'Entertainment': 'bg-violet-500/20 text-violet-300',
  'Healthcare': 'bg-teal-500/20 text-teal-300',
  'Education': 'bg-orange-500/20 text-orange-300',
  'Investments': 'bg-green-500/20 text-green-300',
  'Insurance': 'bg-purple-500/20 text-purple-300',
  'Cash Withdrawal': 'bg-yellow-500/20 text-yellow-300',
  'UPI / Transfer': 'bg-blue-500/20 text-blue-300',
  'Rent': 'bg-fuchsia-500/20 text-fuchsia-300',
  'Other': 'bg-slate-500/20 text-slate-300',
}
