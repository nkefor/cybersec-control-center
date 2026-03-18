import { Suspense } from 'react'
import { dashboardApi, incidentsApi, tasksApi } from '@/lib/api'
import { TopNav } from '@/components/layout/TopNav'
import { SecurityScoreCard } from '@/components/dashboard/SecurityScoreCard'
import { MFACoverageWidget } from '@/components/dashboard/MFACoverageWidget'
import { RiskyLoginsWidget } from '@/components/dashboard/RiskyLoginsWidget'
import { BackupStatusWidget } from '@/components/dashboard/BackupStatusWidget'
import { DevicePostureWidget } from '@/components/dashboard/DevicePostureWidget'
import { IncidentTimeline } from '@/components/dashboard/IncidentTimeline'
import { AlertBanner } from '@/components/layout/AlertBanner'
import Link from 'next/link'
import {
  ClipboardList,
  AlertTriangle,
  RefreshCw,
  Plus,
} from 'lucide-react'
import { timeAgo } from '@/lib/utils'

async function DashboardContent() {
  const [summary, incidents, tasks] = await Promise.all([
    dashboardApi.getSummary().catch(() => null),
    incidentsApi.getIncidents({ status: 'open', page_size: 8 }).catch(() => null),
    tasksApi.getTasks({ status: 'todo' }).catch(() => null),
  ])

  if (!summary) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        <div className="text-center">
          <AlertTriangle size={36} className="mx-auto text-amber-400 mb-2" />
          <p className="font-medium">Could not load dashboard</p>
          <p className="text-sm text-gray-400 mt-1">Make sure the API is running</p>
        </div>
      </div>
    )
  }

  const hasCritical = summary.critical_incidents > 0

  return (
    <div className="animate-fade-in">
      {hasCritical && (
        <AlertBanner
          message={`${summary.critical_incidents} critical incident${summary.critical_incidents > 1 ? 's' : ''} require immediate attention.`}
          severity="critical"
        />
      )}

      <TopNav
        title={summary.tenant_name}
        subtitle={summary.last_synced ? `Last synced ${timeAgo(summary.last_synced)}` : 'Never synced'}
      />

      <div className="p-6 space-y-6">
        {/* Row 1: Score + 4 metric widgets */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-4">
          <div className="xl:col-span-1">
            <SecurityScoreCard
              score={summary.security_score}
              change7d={summary.score_change_7d}
              lastSynced={summary.last_synced}
            />
          </div>
          <div className="xl:col-span-1">
            <MFACoverageWidget coverage={summary.mfa_coverage} />
          </div>
          <div className="xl:col-span-1">
            <RiskyLoginsWidget
              count={summary.risky_logins_24h}
              recentIncidents={incidents?.items?.filter(i => i.category === 'risky_login').slice(0, 3) ?? []}
            />
          </div>
          <div className="xl:col-span-1">
            <DevicePostureWidget devices={summary.devices} />
          </div>
          <div className="xl:col-span-1">
            <BackupStatusWidget summary={summary.backups} />
          </div>
        </div>

        {/* Row 2: Quick stats bar */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <QuickStat
            label="Open Tasks"
            value={summary.open_tasks}
            href="/dashboard/tasks"
            color="text-blue-600"
            bg="bg-blue-50"
          />
          <QuickStat
            label="Critical Incidents"
            value={summary.critical_incidents}
            href="/dashboard/incidents?severity=critical"
            color="text-red-600"
            bg="bg-red-50"
          />
          <QuickStat
            label="Users Without MFA"
            value={summary.mfa_coverage.total - summary.mfa_coverage.enabled}
            href="/dashboard/identity?mfa_enabled=false"
            color="text-amber-600"
            bg="bg-amber-50"
          />
          <QuickStat
            label="Non-compliant Devices"
            value={summary.devices.noncompliant}
            href="/dashboard/devices?is_compliant=false"
            color="text-purple-600"
            bg="bg-purple-50"
          />
        </div>

        {/* Row 3: Incident timeline + Open tasks */}
        <div className="grid grid-cols-1 xl:grid-cols-5 gap-4">
          <div className="xl:col-span-3">
            <IncidentTimeline incidents={incidents?.items ?? []} />
          </div>
          <div className="xl:col-span-2">
            <OpenTasksSummary
              tasks={tasks?.items ?? []}
              total={summary.open_tasks}
            />
          </div>
        </div>

        {/* Quick actions */}
        <div className="flex flex-wrap gap-3">
          <Link href="/dashboard/tasks" className="btn-primary flex items-center gap-2">
            <Plus size={16} />
            Create Task
          </Link>
          <Link href="/dashboard/incidents" className="btn-secondary flex items-center gap-2">
            <AlertTriangle size={16} />
            View Incidents
          </Link>
          <Link href="/settings/integrations" className="btn-secondary flex items-center gap-2">
            <RefreshCw size={16} />
            Configure Integrations
          </Link>
        </div>
      </div>
    </div>
  )
}

function QuickStat({
  label,
  value,
  href,
  color,
  bg,
}: {
  label: string
  value: number
  href: string
  color: string
  bg: string
}) {
  return (
    <Link
      href={href}
      className={`${bg} rounded-xl p-4 hover:shadow-sm transition-shadow border border-transparent hover:border-gray-200`}
    >
      <p className={`text-3xl font-bold ${color}`}>{value}</p>
      <p className="text-xs text-gray-600 mt-1 font-medium">{label}</p>
    </Link>
  )
}

function OpenTasksSummary({
  tasks,
  total,
}: {
  tasks: import('@/lib/types').Task[]
  total: number
}) {
  const priorityOrder = ['critical', 'high', 'medium', 'low']
  const sorted = [...tasks].sort(
    (a, b) => priorityOrder.indexOf(a.priority) - priorityOrder.indexOf(b.priority)
  )

  const priorityColors: Record<string, string> = {
    critical: 'bg-red-500',
    high: 'bg-orange-500',
    medium: 'bg-amber-500',
    low: 'bg-green-500',
  }

  return (
    <div className="bg-white rounded-2xl border border-gray-200 p-6 h-full">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <ClipboardList size={18} className="text-blue-500" />
          <h3 className="text-sm font-semibold text-gray-700">Open Tasks</h3>
          <span className="text-xs text-white bg-blue-600 px-1.5 py-0.5 rounded-full font-semibold">
            {total}
          </span>
        </div>
        <Link href="/dashboard/tasks" className="text-xs font-semibold text-blue-600 hover:text-blue-700">
          View board
        </Link>
      </div>

      <div className="space-y-2">
        {sorted.slice(0, 6).map((task) => (
          <div key={task.id} className="flex items-center gap-2.5 p-2.5 rounded-lg hover:bg-gray-50">
            <span
              className={`w-2 h-2 rounded-full shrink-0 ${priorityColors[task.priority] ?? 'bg-gray-400'}`}
            />
            <p className="text-sm text-gray-700 flex-1 truncate">{task.title}</p>
            {task.assigned_to && (
              <span className="text-xs text-gray-400 shrink-0">{task.assigned_to.split('.')[0]}</span>
            )}
          </div>
        ))}
        {total > 6 && (
          <p className="text-xs text-gray-400 text-center pt-1">
            +{total - 6} more tasks
          </p>
        )}
      </div>
    </div>
  )
}

export default function DashboardPage() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center h-full">
          <div className="animate-spin w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full" />
        </div>
      }
    >
      <DashboardContent />
    </Suspense>
  )
}
