'use client'

import Link from 'next/link'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'
import { ShieldCheck, ShieldAlert, ArrowRight } from 'lucide-react'
import type { MFACoverage } from '@/lib/types'

interface MFACoverageWidgetProps {
  coverage: MFACoverage
}

export function MFACoverageWidget({ coverage }: MFACoverageWidgetProps) {
  const disabled = coverage.total - coverage.enabled
  const data = [
    { name: 'MFA Enabled', value: coverage.enabled, color: '#16A34A' },
    { name: 'No MFA', value: disabled, color: '#DC2626' },
  ]
  const pct = coverage.percentage

  return (
    <div className="bg-white rounded-2xl border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <ShieldCheck size={18} className="text-blue-600" />
          <h3 className="text-sm font-semibold text-gray-700">MFA Coverage</h3>
        </div>
        <span
          className={`text-2xl font-bold ${
            pct >= 90 ? 'text-green-600' : pct >= 70 ? 'text-amber-600' : 'text-red-600'
          }`}
        >
          {pct.toFixed(0)}%
        </span>
      </div>

      {coverage.total > 0 ? (
        <ResponsiveContainer width="100%" height={120}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={35}
              outerRadius={55}
              dataKey="value"
              startAngle={90}
              endAngle={-270}
            >
              {data.map((entry, index) => (
                <Cell key={index} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              formatter={(value: number, name: string) => [value + ' users', name]}
            />
          </PieChart>
        </ResponsiveContainer>
      ) : (
        <div className="h-[120px] flex items-center justify-center text-gray-400 text-sm">
          No data
        </div>
      )}

      <div className="flex items-center justify-between mt-3">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <span className="w-2.5 h-2.5 rounded-full bg-red-500 inline-block" />
          <span>{disabled} users without MFA</span>
        </div>
        {disabled > 0 && (
          <Link
            href="/dashboard/identity?mfa_enabled=false"
            className="flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-700"
          >
            Fix Now <ArrowRight size={12} />
          </Link>
        )}
      </div>
    </div>
  )
}
