'use client'

import Link from 'next/link'
import {
  AlertTriangle,
  AlertOctagon,
  Info,
  CheckCircle2,
  Clock,
  UserX,
  HardDrive,
  Monitor,
  Mail,
} from 'lucide-react'
import { timeAgo, severityColor, statusColor } from '@/lib/utils'
import type { Incident } from '@/lib/types'

interface IncidentTimelineProps {
  incidents: Incident[]
}

const categoryIcons: Record<string, React.ElementType> = {
  risky_login: AlertOctagon,
  mfa_bypass: AlertTriangle,
  inactive_account: UserX,
  device_noncompliance: Monitor,
  backup_failure: HardDrive,
  phishing: Mail,
  other: Info,
}

const severityIcons: Record<string, React.ElementType> = {
  critical: AlertOctagon,
  high: AlertTriangle,
  medium: AlertTriangle,
  low: Info,
  info: Info,
}

export function IncidentTimeline({ incidents }: IncidentTimelineProps) {
  return (
    <div className="bg-white rounded-2xl border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-700">Recent Incidents</h3>
        <Link
          href="/dashboard/incidents"
          className="text-xs font-semibold text-blue-600 hover:text-blue-700"
        >
          View all
        </Link>
      </div>

      {incidents.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-10 text-gray-400">
          <CheckCircle2 size={36} className="text-green-300 mb-2" />
          <p className="text-sm">No incidents detected</p>
        </div>
      ) : (
        <div className="space-y-3">
          {incidents.map((incident, idx) => {
            const CategoryIcon = categoryIcons[incident.category] || Info
            return (
              <div
                key={incident.id}
                className={`flex items-start gap-3 p-3 rounded-xl border transition-colors hover:bg-gray-50 ${
                  incident.status === 'open' ? 'border-gray-200' : 'border-gray-100 opacity-70'
                }`}
              >
                {/* Severity icon */}
                <div
                  className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                    incident.severity === 'critical'
                      ? 'bg-red-100'
                      : incident.severity === 'high'
                      ? 'bg-orange-100'
                      : incident.severity === 'medium'
                      ? 'bg-amber-100'
                      : 'bg-blue-100'
                  }`}
                >
                  <CategoryIcon
                    size={15}
                    className={
                      incident.severity === 'critical'
                        ? 'text-red-600'
                        : incident.severity === 'high'
                        ? 'text-orange-600'
                        : incident.severity === 'medium'
                        ? 'text-amber-600'
                        : 'text-blue-600'
                    }
                  />
                </div>

                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-800 leading-snug truncate">
                    {incident.title}
                  </p>
                  {incident.user_email && (
                    <p className="text-xs text-gray-500 mt-0.5 truncate">{incident.user_email}</p>
                  )}
                  <div className="flex items-center gap-2 mt-1.5">
                    <span className={`text-xs px-1.5 py-0.5 rounded font-medium border ${severityColor(incident.severity)}`}>
                      {incident.severity}
                    </span>
                    <span className={`text-xs px-1.5 py-0.5 rounded font-medium ${statusColor(incident.status)}`}>
                      {incident.status}
                    </span>
                    <span className="flex items-center gap-1 text-xs text-gray-400">
                      <Clock size={10} />
                      {timeAgo(incident.detected_at)}
                    </span>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
