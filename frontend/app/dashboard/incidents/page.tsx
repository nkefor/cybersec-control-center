'use client'

import { useState, useEffect, useCallback } from 'react'
import { incidentsApi } from '@/lib/api'
import { TopNav } from '@/components/layout/TopNav'
import {
  timeAgo,
  severityColor,
  statusColor,
  categoryLabel,
  severityDot,
} from '@/lib/utils'
import {
  AlertOctagon,
  AlertTriangle,
  Info,
  CheckCircle2,
  UserX,
  HardDrive,
  Monitor,
  Mail,
  ChevronDown,
  ChevronUp,
} from 'lucide-react'
import type { Incident } from '@/lib/types'

const categoryIcons: Record<string, React.ElementType> = {
  risky_login: AlertOctagon,
  mfa_bypass: AlertTriangle,
  inactive_account: UserX,
  device_noncompliance: Monitor,
  backup_failure: HardDrive,
  phishing: Mail,
  other: Info,
}

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState<string | null>(null)
  const [severityFilter, setSeverityFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')

  const fetchIncidents = useCallback(async () => {
    setLoading(true)
    try {
      const params: Record<string, string | number> = { page_size: 50 }
      if (severityFilter) params.severity = severityFilter
      if (statusFilter) params.status = statusFilter
      if (categoryFilter) params.category = categoryFilter
      const data = await incidentsApi.getIncidents(params)
      setIncidents(data.items)
      setTotal(data.total)
    } catch {
      // Keep current state on error
    } finally {
      setLoading(false)
    }
  }, [severityFilter, statusFilter, categoryFilter])

  useEffect(() => {
    fetchIncidents()
  }, [fetchIncidents])

  const handleAcknowledge = async (id: string) => {
    await incidentsApi.acknowledgeIncident(id)
    fetchIncidents()
  }

  const handleResolve = async (id: string) => {
    await incidentsApi.resolveIncident(id)
    fetchIncidents()
  }

  const counts = {
    open: incidents.filter(i => i.status === 'open').length,
    acknowledged: incidents.filter(i => i.status === 'acknowledged').length,
    resolved: incidents.filter(i => i.status === 'resolved').length,
  }

  return (
    <div className="animate-fade-in">
      <TopNav title="Incidents" subtitle="Security alerts and threat timeline" />

      <div className="p-6 space-y-5">
        {/* Status summary */}
        <div className="grid grid-cols-3 gap-4">
          <StatusCard label="Open" count={counts.open} color="text-red-600" bg="bg-red-50" border="border-red-200" />
          <StatusCard label="Acknowledged" count={counts.acknowledged} color="text-amber-600" bg="bg-amber-50" border="border-amber-200" />
          <StatusCard label="Resolved" count={counts.resolved} color="text-green-600" bg="bg-green-50" border="border-green-200" />
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl border border-gray-200 p-4 flex flex-wrap gap-3 items-center">
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Filter:</span>

          <select
            value={severityFilter}
            onChange={e => setSeverityFilter(e.target.value)}
            className="text-sm border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Severities</option>
            {['critical', 'high', 'medium', 'low', 'info'].map(s => (
              <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
            ))}
          </select>

          <select
            value={statusFilter}
            onChange={e => setStatusFilter(e.target.value)}
            className="text-sm border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Statuses</option>
            {['open', 'acknowledged', 'resolved'].map(s => (
              <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
            ))}
          </select>

          <select
            value={categoryFilter}
            onChange={e => setCategoryFilter(e.target.value)}
            className="text-sm border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Categories</option>
            {['risky_login', 'mfa_bypass', 'inactive_account', 'device_noncompliance', 'backup_failure', 'phishing', 'other'].map(c => (
              <option key={c} value={c}>{categoryLabel(c)}</option>
            ))}
          </select>

          {(severityFilter || statusFilter || categoryFilter) && (
            <button
              onClick={() => { setSeverityFilter(''); setStatusFilter(''); setCategoryFilter('') }}
              className="text-xs text-blue-600 hover:text-blue-700 font-medium"
            >
              Clear filters
            </button>
          )}

          <span className="ml-auto text-xs text-gray-400">{total} incidents</span>
        </div>

        {/* Timeline */}
        {loading ? (
          <div className="space-y-3">
            {[1,2,3].map(i => <div key={i} className="h-24 bg-gray-100 rounded-2xl animate-pulse" />)}
          </div>
        ) : incidents.length === 0 ? (
          <div className="bg-white rounded-2xl border border-gray-200 py-16 text-center text-gray-400">
            <CheckCircle2 size={48} className="mx-auto mb-3 text-green-200" />
            <p className="font-medium text-gray-500">No incidents found</p>
          </div>
        ) : (
          <div className="space-y-3">
            {incidents.map((incident) => {
              const CategoryIcon = categoryIcons[incident.category] || Info
              const isExpanded = expanded === incident.id

              return (
                <div
                  key={incident.id}
                  className={`bg-white rounded-2xl border transition-all ${
                    incident.status === 'open' && incident.severity === 'critical'
                      ? 'border-red-300 shadow-sm'
                      : incident.status === 'open' && incident.severity === 'high'
                      ? 'border-orange-200'
                      : 'border-gray-200'
                  }`}
                >
                  <div
                    className="flex items-start gap-4 p-5 cursor-pointer"
                    onClick={() => setExpanded(isExpanded ? null : incident.id)}
                  >
                    {/* Severity dot */}
                    <div className={`w-2.5 h-2.5 rounded-full mt-1.5 shrink-0 ${severityDot(incident.severity)}`} />

                    {/* Icon */}
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
                      incident.severity === 'critical' ? 'bg-red-100' :
                      incident.severity === 'high' ? 'bg-orange-100' :
                      incident.severity === 'medium' ? 'bg-amber-100' : 'bg-blue-100'
                    }`}>
                      <CategoryIcon size={18} className={
                        incident.severity === 'critical' ? 'text-red-600' :
                        incident.severity === 'high' ? 'text-orange-600' :
                        incident.severity === 'medium' ? 'text-amber-600' : 'text-blue-600'
                      } />
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-3">
                        <p className="text-sm font-semibold text-gray-800 leading-snug">{incident.title}</p>
                        <div className="flex items-center gap-2 shrink-0">
                          <span className={`text-xs px-2 py-0.5 rounded border font-medium ${severityColor(incident.severity)}`}>
                            {incident.severity}
                          </span>
                          <span className={`text-xs px-2 py-0.5 rounded font-medium ${statusColor(incident.status)}`}>
                            {incident.status}
                          </span>
                          {isExpanded ? <ChevronUp size={14} className="text-gray-400" /> : <ChevronDown size={14} className="text-gray-400" />}
                        </div>
                      </div>
                      <div className="flex flex-wrap items-center gap-3 mt-1.5 text-xs text-gray-400">
                        <span className="bg-gray-100 px-2 py-0.5 rounded text-gray-600">{categoryLabel(incident.category)}</span>
                        {incident.user_email && <span>{incident.user_email}</span>}
                        <span>{timeAgo(incident.detected_at)}</span>
                      </div>
                    </div>
                  </div>

                  {/* Expanded details */}
                  {isExpanded && (
                    <div className="px-[3.5rem] pb-5 border-t border-gray-100 pt-4">
                      <p className="text-sm text-gray-600 leading-relaxed mb-4">{incident.description}</p>
                      {incident.status !== 'resolved' && (
                        <div className="flex gap-2">
                          {incident.status === 'open' && (
                            <button
                              onClick={() => handleAcknowledge(incident.id)}
                              className="px-4 py-1.5 text-xs font-medium text-amber-700 bg-amber-100 hover:bg-amber-200 rounded-lg transition-colors"
                            >
                              Acknowledge
                            </button>
                          )}
                          <button
                            onClick={() => handleResolve(incident.id)}
                            className="px-4 py-1.5 text-xs font-medium text-green-700 bg-green-100 hover:bg-green-200 rounded-lg transition-colors"
                          >
                            Mark Resolved
                          </button>
                        </div>
                      )}
                      {incident.status === 'resolved' && incident.resolved_at && (
                        <p className="text-xs text-green-600 flex items-center gap-1">
                          <CheckCircle2 size={12} /> Resolved {timeAgo(incident.resolved_at)}
                        </p>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}

function StatusCard({ label, count, color, bg, border }: {
  label: string; count: number; color: string; bg: string; border: string
}) {
  return (
    <div className={`${bg} border ${border} rounded-xl p-4 text-center`}>
      <p className={`text-3xl font-bold ${color}`}>{count}</p>
      <p className="text-xs text-gray-600 mt-1 font-medium">{label}</p>
    </div>
  )
}
