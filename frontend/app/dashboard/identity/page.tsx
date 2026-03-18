import { Suspense } from 'react'
import { identityApi } from '@/lib/api'
import { TopNav } from '@/components/layout/TopNav'
import { timeAgo, severityColor, statusColor } from '@/lib/utils'
import { ShieldCheck, ShieldX, UserX, AlertTriangle, Users } from 'lucide-react'
import type { User, InactiveUser } from '@/lib/types'

async function IdentityContent({ searchParams }: { searchParams: Record<string, string> }) {
  const mfaFilter = searchParams.mfa_enabled
  const [users, mfaSummary, inactiveUsers] = await Promise.all([
    identityApi.getUsers({
      page: Number(searchParams.page ?? 1),
      page_size: 25,
      ...(mfaFilter !== undefined ? { mfa_enabled: mfaFilter } : {}),
      ...(searchParams.risk_level ? { risk_level: searchParams.risk_level } : {}),
    }).catch(() => ({ items: [], total: 0, page: 1, page_size: 25 })),
    identityApi.getMFASummary().catch(() => null),
    identityApi.getInactiveUsers(30).catch(() => []),
  ])

  return (
    <div className="animate-fade-in">
      <TopNav title="Identity & Access" subtitle="User accounts, MFA status, and access risks" />

      <div className="p-6 space-y-6">
        {/* MFA summary bar */}
        {mfaSummary && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <SummaryCard
              icon={<Users size={18} className="text-blue-500" />}
              label="Total Users"
              value={mfaSummary.total_users}
              sub="Active accounts"
              color="text-blue-600"
              bg="bg-blue-50"
            />
            <SummaryCard
              icon={<ShieldCheck size={18} className="text-green-500" />}
              label="MFA Enabled"
              value={mfaSummary.mfa_enabled}
              sub={`${mfaSummary.coverage_percentage.toFixed(0)}% coverage`}
              color="text-green-600"
              bg="bg-green-50"
            />
            <SummaryCard
              icon={<ShieldX size={18} className="text-red-500" />}
              label="No MFA"
              value={mfaSummary.mfa_disabled}
              sub="Require immediate action"
              color="text-red-600"
              bg="bg-red-50"
            />
            <SummaryCard
              icon={<UserX size={18} className="text-amber-500" />}
              label="Inactive (30d)"
              value={inactiveUsers.length}
              sub="No sign-in in 30 days"
              color="text-amber-600"
              bg="bg-amber-50"
            />
          </div>
        )}

        {/* MFA Coverage Progress */}
        {mfaSummary && (
          <div className="bg-white rounded-2xl border border-gray-200 p-5">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-semibold text-gray-700">MFA Coverage</h3>
              <span className="text-sm font-bold text-gray-800">
                {mfaSummary.mfa_enabled} / {mfaSummary.total_users} users
              </span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-4">
              <div
                className={`h-4 rounded-full transition-all duration-700 ${
                  mfaSummary.coverage_percentage >= 90
                    ? 'bg-green-500'
                    : mfaSummary.coverage_percentage >= 70
                    ? 'bg-amber-500'
                    : 'bg-red-500'
                }`}
                style={{ width: `${mfaSummary.coverage_percentage}%` }}
              />
            </div>
            {mfaSummary.methods_breakdown && Object.keys(mfaSummary.methods_breakdown).length > 0 && (
              <div className="flex flex-wrap gap-3 mt-3">
                {Object.entries(mfaSummary.methods_breakdown).map(([method, count]) => (
                  <span key={method} className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                    {method}: <strong>{count}</strong>
                  </span>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Inactive users alert */}
        {inactiveUsers.length > 0 && (
          <div className="bg-amber-50 border border-amber-200 rounded-2xl p-5">
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle size={18} className="text-amber-600" />
              <h3 className="text-sm font-semibold text-amber-800">
                {inactiveUsers.length} Inactive Account{inactiveUsers.length > 1 ? 's' : ''}
              </h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-2">
              {inactiveUsers.slice(0, 6).map((u: InactiveUser) => (
                <div key={u.id} className="flex items-center gap-2 bg-white rounded-lg p-2.5 border border-amber-100">
                  <div className="w-8 h-8 rounded-full bg-amber-100 flex items-center justify-center text-amber-700 text-xs font-bold shrink-0">
                    {u.display_name.charAt(0)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-gray-800 truncate">{u.display_name}</p>
                    <p className="text-xs text-gray-400">{u.days_inactive} days inactive</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* User table */}
        <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
            <h3 className="text-sm font-semibold text-gray-700">
              All Users ({users.total})
            </h3>
            <div className="flex gap-2">
              <MFAFilterBadge active={mfaFilter === 'false'} label="No MFA" href="/dashboard/identity?mfa_enabled=false" />
              <MFAFilterBadge active={mfaFilter === 'true'} label="With MFA" href="/dashboard/identity?mfa_enabled=true" />
              <MFAFilterBadge active={!mfaFilter} label="All" href="/dashboard/identity" />
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-100">
                  <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">User</th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">MFA Status</th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Last Sign-in</th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Risk</th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Source</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {users.items.map((user: User) => (
                  <tr key={user.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 text-xs font-bold shrink-0">
                          {user.display_name.charAt(0)}
                        </div>
                        <div>
                          <p className="font-medium text-gray-800">{user.display_name}</p>
                          <p className="text-xs text-gray-400">{user.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-3.5">
                      {user.mfa_enabled ? (
                        <span className="inline-flex items-center gap-1 text-xs font-medium text-green-700 bg-green-100 px-2.5 py-1 rounded-full">
                          <ShieldCheck size={12} /> Enabled
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-xs font-medium text-red-700 bg-red-100 px-2.5 py-1 rounded-full">
                          <ShieldX size={12} /> Not Set
                        </span>
                      )}
                    </td>
                    <td className="px-5 py-3.5 text-sm text-gray-600">
                      {timeAgo(user.last_sign_in)}
                    </td>
                    <td className="px-5 py-3.5">
                      <RiskBadge level={user.risk_level} />
                    </td>
                    <td className="px-5 py-3.5 text-xs text-gray-500">
                      {user.source === 'microsoft365' ? 'Microsoft 365' : user.source === 'google' ? 'Google' : 'Manual'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {users.items.length === 0 && (
              <div className="py-12 text-center text-gray-400">
                <Users size={36} className="mx-auto mb-2 text-gray-200" />
                <p>No users found</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function SummaryCard({ icon, label, value, sub, color, bg }: {
  icon: React.ReactNode
  label: string
  value: number
  sub: string
  color: string
  bg: string
}) {
  return (
    <div className={`${bg} rounded-xl p-4 border border-transparent`}>
      <div className="flex items-center gap-2 mb-1">
        {icon}
        <span className="text-xs font-medium text-gray-600">{label}</span>
      </div>
      <p className={`text-3xl font-bold ${color}`}>{value}</p>
      <p className="text-xs text-gray-500 mt-0.5">{sub}</p>
    </div>
  )
}

function RiskBadge({ level }: { level: string }) {
  const colors: Record<string, string> = {
    none: 'text-gray-500 bg-gray-100',
    low: 'text-green-700 bg-green-100',
    medium: 'text-amber-700 bg-amber-100',
    high: 'text-red-700 bg-red-100',
  }
  if (level === 'none') return <span className="text-xs text-gray-400">—</span>
  return (
    <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${colors[level]}`}>
      {level}
    </span>
  )
}

function MFAFilterBadge({ active, label, href }: { active: boolean; label: string; href: string }) {
  return (
    <a
      href={href}
      className={`text-xs px-3 py-1 rounded-lg font-medium transition-colors ${
        active
          ? 'bg-blue-600 text-white'
          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
      }`}
    >
      {label}
    </a>
  )
}

export default function IdentityPage({
  searchParams,
}: {
  searchParams: Record<string, string>
}) {
  return (
    <Suspense fallback={<LoadingState />}>
      <IdentityContent searchParams={searchParams} />
    </Suspense>
  )
}

function LoadingState() {
  return (
    <div>
      <TopNav title="Identity & Access" />
      <div className="p-6 space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-24 bg-gray-100 rounded-2xl animate-pulse" />
        ))}
      </div>
    </div>
  )
}
