import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid
} from 'recharts'
import { CATEGORY_COLORS, formatCurrency } from '../utils/format'
import { useState } from 'react'

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  const data = payload[0].payload
  return (
    <div className="glass-card p-3 text-sm shadow-xl border border-white/20">
      <p className="font-semibold text-white">{data.name}</p>
      <p className="text-emerald-400 mt-1">Credits: {formatCurrency(data.total_credit)}</p>
      <p className="text-red-400">Debits: {formatCurrency(data.total_debit)}</p>
      <p className="text-slate-300">Count: {data.count}</p>
    </div>
  )
}

export default function CategoryChart({ categorySummary }) {
  const [view, setView] = useState('pie')

  const data = categorySummary
    .filter(c => c.total_debit > 0 || c.total_credit > 0)
    .map(c => ({
      name: c.category,
      total_credit: c.total_credit,
      total_debit: c.total_debit,
      count: c.count,
      value: c.total_debit || c.total_credit,
    }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 12)

  const RADIAN = Math.PI / 180
  const renderCustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
    if (percent < 0.04) return null
    const r = innerRadius + (outerRadius - innerRadius) * 0.5
    const x = cx + r * Math.cos(-midAngle * RADIAN)
    const y = cy + r * Math.sin(-midAngle * RADIAN)
    return (
      <text x={x} y={y} fill="white" textAnchor="middle" dominantBaseline="central" fontSize={11} fontWeight={600}>
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    )
  }

  return (
    <div className="glass-card p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="section-title mb-0">Spending by Category</h3>
        <div className="flex gap-1 bg-white/5 rounded-lg p-1">
          {['pie', 'bar'].map(v => (
            <button
              key={v}
              onClick={() => setView(v)}
              className={`px-3 py-1 text-xs font-medium rounded-md transition-all
                ${view === v ? 'bg-brand text-white' : 'text-slate-400 hover:text-white'}`}
            >
              {v.charAt(0).toUpperCase() + v.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {view === 'pie' ? (
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={renderCustomLabel}
              outerRadius={120}
              dataKey="value"
            >
              {data.map((entry) => (
                <Cell
                  key={entry.name}
                  fill={CATEGORY_COLORS[entry.name] || '#94A3B8'}
                  stroke="rgba(255,255,255,0.1)"
                  strokeWidth={1}
                />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend
              formatter={(value) => (
                <span style={{ color: '#CBD5E1', fontSize: 12 }}>{value}</span>
              )}
            />
          </PieChart>
        </ResponsiveContainer>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data} margin={{ top: 5, right: 10, left: 10, bottom: 60 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis
              dataKey="name"
              tick={{ fill: '#94A3B8', fontSize: 10 }}
              angle={-35}
              textAnchor="end"
              interval={0}
            />
            <YAxis
              tick={{ fill: '#94A3B8', fontSize: 10 }}
              tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}K`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="total_debit" fill="#EF4444" radius={[4, 4, 0, 0]} name="Debit" />
            <Bar dataKey="total_credit" fill="#10B981" radius={[4, 4, 0, 0]} name="Credit" />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
