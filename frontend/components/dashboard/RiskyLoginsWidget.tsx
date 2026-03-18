'use client'

import Link from 'next/link'
import { AlertOctagon, ArrowRight, User } from 'lucide-react'
import { timeAgo, severityColor } from '@/lib/utils'
import type { Incident } from '@/lib/types'

interface RiskyLoginsWidgetProps {
  count: number
  recentIncidents: Incident[]
}

export function RiskyLoginsWidget({ count, recentIncidents }: RiskyLoginsWidgetProps) {
  return (
    <div className="bg-white rounded-2xl border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <AlertOctagon size={18} className="text-red-500" />
          <h3 className="text-sm font-semibold text-gray-700">Risky Sign-ins</h3>
        </div>
        <span
          className={`text-2xl font-bold ${
            count === 0 ? 'text-green-600' : count <= 2 ? 'text-amber-600' : 'text-red-600'
          }`}
        >
          {count}
        </span>
      </div>

      <p className="text-xs text-gray-500 mb-3">Last 24 hours</p>

      {recentIncidents.length === 0 ? (
        <div className="flex items-center gap-2 text-sm text-green-600 bg-green-50 rounded-lg px-3 py-2">
          <span>No risky sign-ins detected</span>
        </div>
      ) : (
        <div className="space-y-2">
          {recentIncidents.slice(0, 3).map((inc) => (
            <div key={inc.id} className="flex items-start gap-2 p-2 rounded-lg bg-gray-50">
              <User size={14} className="text-gray-400 mt-0.5 shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-gray-700 truncate">{inc.user_email}</p>
                <p className="text-xs text-gray-400">{timeAgo(inc.detected_at)}</p>
              </div>
              <span
                className={`shrink-0 text-xs px-1.5 py-0.5 rounded font-medium border ${severityColor(
                  inc.severity
                )}`}
              >
                {inc.severity}
              </span>
            </div>
          ))}
        </div>
      )}

      <Link
        href="/dashboard/incidents?category=risky_login"
        className="flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-700 mt-3"
      >
        View all incidents <ArrowRight size={12} />
      </Link>
    </div>
  )
}
