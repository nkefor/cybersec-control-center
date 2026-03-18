import { Suspense } from 'react'
import { devicesApi } from '@/lib/api'
import { TopNav } from '@/components/layout/TopNav'
import { timeAgo, osIcon } from '@/lib/utils'
import {
  Monitor,
  CheckCircle2,
  XCircle,
  Lock,
  LockOpen,
  AlertTriangle,
} from 'lucide-react'
import type { Device } from '@/lib/types'

async function DevicesContent({ searchParams }: { searchParams: Record<string, string> }) {
  const [devices, posture] = await Promise.all([
    devicesApi.getDevices({
      page: Number(searchParams.page ?? 1),
      page_size: 25,
      ...(searchParams.is_compliant !== undefined ? { is_compliant: searchParams.is_compliant } : {}),
      ...(searchParams.os_type ? { os_type: searchParams.os_type } : {}),
    }).catch(() => ({ items: [], total: 0, page: 1, page_size: 25 })),
    devicesApi.getPostureSummary().catch(() => null),
  ])

  return (
    <div className="animate-fade-in">
      <TopNav title="Device Posture" subtitle="Compliance status across all managed endpoints" />

      <div className="p-6 space-y-6">
        {/* Posture summary */}
        {posture && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard
              icon={<Monitor size={18} className="text-blue-500" />}
              label="Total Devices"
              value={posture.total}
              bg="bg-blue-50"
              color="text-blue-600"
            />
            <StatCard
              icon={<CheckCircle2 size={18} className="text-green-500" />}
              label="Compliant"
              value={posture.compliant}
              sub={`${posture.compliance_rate.toFixed(0)}% compliance rate`}
              bg="bg-green-50"
              color="text-green-600"
            />
            <StatCard
              icon={<XCircle size={18} className="text-red-500" />}
              label="Non-compliant"
              value={posture.noncompliant}
              sub="Require attention"
              bg="bg-red-50"
              color="text-red-600"
            />
            <StatCard
              icon={<Lock size={18} className="text-purple-500" />}
              label="Encrypted"
              value={posture.encrypted}
              sub={`${posture.encryption_rate.toFixed(0)}% encrypted`}
              bg="bg-purple-50"
              color="text-purple-600"
            />
          </div>
        )}

        {/* OS breakdown */}
        {posture && Object.keys(posture.by_os).length > 0 && (
          <div className="bg-white rounded-2xl border border-gray-200 p-5">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Devices by OS</h3>
            <div className="flex flex-wrap gap-3">
              {Object.entries(posture.by_os).map(([os, count]) => (
                <div key={os} className="flex items-center gap-2 bg-gray-50 rounded-lg px-3 py-2">
                  <Monitor size={14} className="text-gray-400" />
                  <span className="text-sm text-gray-700 font-medium">{osIcon(os)}</span>
                  <span className="text-xs font-bold text-gray-500">{count}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Device table */}
        <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
            <h3 className="text-sm font-semibold text-gray-700">
              Devices ({devices.total})
            </h3>
            <div className="flex gap-2">
              <FilterBadge active={searchParams.is_compliant === 'false'} label="Non-compliant" href="/dashboard/devices?is_compliant=false" />
              <FilterBadge active={searchParams.is_compliant === 'true'} label="Compliant" href="/dashboard/devices?is_compliant=true" />
              <FilterBadge active={!searchParams.is_compliant} label="All" href="/dashboard/devices" />
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-100">
                  <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Device</th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Owner</th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">OS</th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Compliance</th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Encryption</th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Risk Score</th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Last Seen</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {devices.items.map((device: Device) => (
                  <tr key={device.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-2">
                        <Monitor size={16} className="text-gray-400 shrink-0" />
                        <div>
                          <p className="font-medium text-gray-800">{device.device_name}</p>
                          {device.compliance_issues && device.compliance_issues.length > 0 && (
                            <div className="flex flex-wrap gap-1 mt-1">
                              {device.compliance_issues.slice(0, 2).map((issue: string) => (
                                <span key={issue} className="text-xs text-red-600 bg-red-50 px-1.5 py-0.5 rounded">
                                  {issue}
                                </span>
                              ))}
                              {device.compliance_issues.length > 2 && (
                                <span className="text-xs text-gray-400">+{device.compliance_issues.length - 2} more</span>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-3.5 text-sm text-gray-600 truncate max-w-[150px]">
                      {device.owner_email ?? '—'}
                    </td>
                    <td className="px-5 py-3.5 text-sm text-gray-600">
                      {osIcon(device.os_type)} {device.os_version && <span className="text-xs text-gray-400">({device.os_version})</span>}
                    </td>
                    <td className="px-5 py-3.5">
                      {device.is_compliant ? (
                        <span className="inline-flex items-center gap-1 text-xs font-medium text-green-700 bg-green-100 px-2.5 py-1 rounded-full">
                          <CheckCircle2 size={12} /> Compliant
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-xs font-medium text-red-700 bg-red-100 px-2.5 py-1 rounded-full">
                          <XCircle size={12} /> Non-compliant
                        </span>
                      )}
                    </td>
                    <td className="px-5 py-3.5">
                      {device.encryption_enabled ? (
                        <span className="inline-flex items-center gap-1 text-xs font-medium text-green-600">
                          <Lock size={12} /> Enabled
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-xs font-medium text-red-600">
                          <LockOpen size={12} /> Disabled
                        </span>
                      )}
                    </td>
                    <td className="px-5 py-3.5">
                      <RiskScoreBadge score={device.risk_score} />
                    </td>
                    <td className="px-5 py-3.5 text-sm text-gray-500">
                      {timeAgo(device.last_seen)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {devices.items.length === 0 && (
              <div className="py-12 text-center text-gray-400">
                <Monitor size={36} className="mx-auto mb-2 text-gray-200" />
                <p>No devices found</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function StatCard({ icon, label, value, sub, bg, color }: {
  icon: React.ReactNode; label: string; value: number; sub?: string; bg: string; color: string
}) {
  return (
    <div className={`${bg} rounded-xl p-4`}>
      <div className="flex items-center gap-2 mb-1">{icon}<span className="text-xs font-medium text-gray-600">{label}</span></div>
      <p className={`text-3xl font-bold ${color}`}>{value}</p>
      {sub && <p className="text-xs text-gray-500 mt-0.5">{sub}</p>}
    </div>
  )
}

function RiskScoreBadge({ score }: { score: number }) {
  const color = score >= 70 ? 'text-red-700 bg-red-100' : score >= 40 ? 'text-amber-700 bg-amber-100' : 'text-green-700 bg-green-100'
  return (
    <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${color}`}>{score}</span>
  )
}

function FilterBadge({ active, label, href }: { active: boolean; label: string; href: string }) {
  return (
    <a href={href} className={`text-xs px-3 py-1 rounded-lg font-medium transition-colors ${active ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>
      {label}
    </a>
  )
}

export default function DevicesPage({ searchParams }: { searchParams: Record<string, string> }) {
  return (
    <Suspense fallback={<div className="p-6"><div className="h-24 bg-gray-100 rounded-2xl animate-pulse" /></div>}>
      <DevicesContent searchParams={searchParams} />
    </Suspense>
  )
}
