'use client'

import Link from 'next/link'
import { Monitor, ArrowRight } from 'lucide-react'
import type { DeviceSummary } from '@/lib/types'

interface DevicePostureWidgetProps {
  devices: DeviceSummary
}

export function DevicePostureWidget({ devices }: DevicePostureWidgetProps) {
  const pct = devices.total > 0
    ? Math.round((devices.compliant / devices.total) * 100)
    : 0

  return (
    <div className="bg-white rounded-2xl border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Monitor size={18} className="text-purple-500" />
          <h3 className="text-sm font-semibold text-gray-700">Device Compliance</h3>
        </div>
        <span
          className={`text-2xl font-bold ${
            pct >= 90 ? 'text-green-600' : pct >= 70 ? 'text-amber-600' : 'text-red-600'
          }`}
        >
          {pct}%
        </span>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-gray-100 rounded-full h-3 mb-4">
        <div
          className={`h-3 rounded-full transition-all duration-700 ${
            pct >= 90 ? 'bg-green-500' : pct >= 70 ? 'bg-amber-500' : 'bg-red-500'
          }`}
          style={{ width: `${pct}%` }}
        />
      </div>

      <div className="grid grid-cols-3 gap-3 text-center">
        <Stat label="Total" value={devices.total} color="text-gray-800" />
        <Stat label="Compliant" value={devices.compliant} color="text-green-600" />
        <Stat label="Non-compliant" value={devices.noncompliant} color="text-red-600" />
      </div>

      {devices.noncompliant > 0 && (
        <Link
          href="/dashboard/devices?is_compliant=false"
          className="flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-700 mt-3"
        >
          View {devices.noncompliant} non-compliant <ArrowRight size={12} />
        </Link>
      )}
    </div>
  )
}

function Stat({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div>
      <p className={`text-xl font-bold ${color}`}>{value}</p>
      <p className="text-xs text-gray-400 mt-0.5">{label}</p>
    </div>
  )
}
