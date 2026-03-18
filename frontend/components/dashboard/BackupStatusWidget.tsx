'use client'

import Link from 'next/link'
import { HardDrive, ArrowRight, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react'
import type { BackupSummary } from '@/lib/types'

interface BackupStatusWidgetProps {
  summary: BackupSummary
}

export function BackupStatusWidget({ summary }: BackupStatusWidgetProps) {
  const total = summary.healthy + summary.warning + summary.critical + summary.unknown

  return (
    <div className="bg-white rounded-2xl border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <HardDrive size={18} className="text-indigo-500" />
          <h3 className="text-sm font-semibold text-gray-700">Backup Health</h3>
        </div>
        <span className="text-2xl font-bold text-gray-800">{total}</span>
      </div>

      {summary.critical > 0 && (
        <div className="flex items-center gap-2 bg-red-50 border border-red-200 text-red-700 rounded-lg px-3 py-2 mb-3 text-xs font-medium">
          <XCircle size={14} />
          <span>{summary.critical} backup{summary.critical > 1 ? 's' : ''} in critical state!</span>
        </div>
      )}

      <div className="space-y-2">
        <StatusRow
          icon={<CheckCircle2 size={15} className="text-green-500" />}
          label="Healthy"
          count={summary.healthy}
          color="text-green-600"
          total={total}
        />
        <StatusRow
          icon={<AlertTriangle size={15} className="text-amber-500" />}
          label="Warning"
          count={summary.warning}
          color="text-amber-600"
          total={total}
        />
        <StatusRow
          icon={<XCircle size={15} className="text-red-500" />}
          label="Critical"
          count={summary.critical}
          color="text-red-600"
          total={total}
        />
      </div>

      <Link
        href="/dashboard/backups"
        className="flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-700 mt-3"
      >
        View backup jobs <ArrowRight size={12} />
      </Link>
    </div>
  )
}

function StatusRow({
  icon,
  label,
  count,
  color,
  total,
}: {
  icon: React.ReactNode
  label: string
  count: number
  color: string
  total: number
}) {
  const pct = total > 0 ? (count / total) * 100 : 0
  return (
    <div className="flex items-center gap-2">
      {icon}
      <span className="text-xs text-gray-600 w-14">{label}</span>
      <div className="flex-1 bg-gray-100 rounded-full h-1.5">
        <div
          className={`h-1.5 rounded-full transition-all duration-500 ${
            color.includes('green') ? 'bg-green-500' :
            color.includes('amber') ? 'bg-amber-500' :
            color.includes('red') ? 'bg-red-500' : 'bg-gray-400'
          }`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className={`text-xs font-semibold ${color} w-4 text-right`}>{count}</span>
    </div>
  )
}
