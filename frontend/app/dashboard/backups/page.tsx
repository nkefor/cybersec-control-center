import { Suspense } from 'react'
import { backupsApi } from '@/lib/api'
import { TopNav } from '@/components/layout/TopNav'
import { timeAgo, formatDate, formatBytes } from '@/lib/utils'
import {
  HardDrive,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  HelpCircle,
  Clock,
  Calendar,
} from 'lucide-react'
import type { BackupJob } from '@/lib/types'

const statusConfig = {
  healthy: { icon: CheckCircle2, color: 'text-green-600', bg: 'bg-green-100', border: 'border-green-200' },
  warning: { icon: AlertTriangle, color: 'text-amber-600', bg: 'bg-amber-100', border: 'border-amber-200' },
  critical: { icon: XCircle, color: 'text-red-600', bg: 'bg-red-100', border: 'border-red-200' },
  unknown: { icon: HelpCircle, color: 'text-gray-500', bg: 'bg-gray-100', border: 'border-gray-200' },
}

async function BackupsContent() {
  const backups = await backupsApi.getBackups().catch(() => ({ items: [], total: 0 }))

  const stats = backups.items.reduce(
    (acc: Record<string, number>, job: BackupJob) => {
      acc[job.status] = (acc[job.status] || 0) + 1
      return acc
    },
    {}
  )

  const criticalJobs = backups.items.filter((j: BackupJob) => j.status === 'critical' || j.status === 'warning')

  return (
    <div className="animate-fade-in">
      <TopNav title="Backup Health" subtitle="Status and coverage of all backup jobs" />

      <div className="p-6 space-y-6">
        {/* Summary stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {(['healthy', 'warning', 'critical', 'unknown'] as const).map((status) => {
            const cfg = statusConfig[status]
            const Icon = cfg.icon
            return (
              <div key={status} className={`${cfg.bg} border ${cfg.border} rounded-xl p-4`}>
                <div className="flex items-center gap-2 mb-1">
                  <Icon size={18} className={cfg.color} />
                  <span className="text-xs font-medium text-gray-600 capitalize">{status}</span>
                </div>
                <p className={`text-3xl font-bold ${cfg.color}`}>{stats[status] ?? 0}</p>
                <p className="text-xs text-gray-400 mt-0.5">backup jobs</p>
              </div>
            )
          })}
        </div>

        {/* Alert for warning/critical */}
        {criticalJobs.length > 0 && (
          <div className="bg-amber-50 border border-amber-200 rounded-2xl p-5">
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle size={18} className="text-amber-600" />
              <h3 className="text-sm font-semibold text-amber-800">
                {criticalJobs.length} backup{criticalJobs.length > 1 ? 's' : ''} need attention
              </h3>
            </div>
            <div className="space-y-2">
              {criticalJobs.map((job: BackupJob) => (
                <div key={job.id} className="bg-white rounded-lg p-3 border border-amber-100">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-800">{job.name}</p>
                      {job.notes && <p className="text-xs text-gray-500 mt-0.5">{job.notes}</p>}
                    </div>
                    <StatusBadge status={job.status} />
                  </div>
                  <p className="text-xs text-gray-400 mt-1.5">
                    Last backup: {job.last_backup_at ? timeAgo(job.last_backup_at) : 'Never'}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Backup jobs grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {backups.items.map((job: BackupJob) => (
            <BackupCard key={job.id} job={job} />
          ))}
        </div>

        {backups.items.length === 0 && (
          <div className="bg-white rounded-2xl border border-gray-200 py-16 text-center text-gray-400">
            <HardDrive size={48} className="mx-auto mb-3 text-gray-200" />
            <p className="font-medium">No backup jobs configured</p>
            <p className="text-sm mt-1">Add backup jobs to track their health</p>
          </div>
        )}
      </div>
    </div>
  )
}

function BackupCard({ job }: { job: BackupJob }) {
  const cfg = statusConfig[job.status as keyof typeof statusConfig] ?? statusConfig.unknown
  const Icon = cfg.icon

  return (
    <div className={`bg-white rounded-2xl border-2 ${cfg.border} p-5 hover:shadow-sm transition-shadow`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className={`${cfg.bg} w-9 h-9 rounded-lg flex items-center justify-center`}>
            <HardDrive size={18} className={cfg.color} />
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-800 leading-tight">{job.name}</p>
            <p className="text-xs text-gray-400">{job.provider}</p>
          </div>
        </div>
        <StatusBadge status={job.status} />
      </div>

      <p className="text-xs text-gray-500 mb-3 line-clamp-2">{job.target_description}</p>

      <div className="space-y-2 text-xs text-gray-600">
        <div className="flex items-center justify-between">
          <span className="flex items-center gap-1 text-gray-400"><Clock size={12} /> Last backup</span>
          <span className="font-medium">{job.last_backup_at ? timeAgo(job.last_backup_at) : '—'}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="flex items-center gap-1 text-gray-400"><Calendar size={12} /> Next backup</span>
          <span className="font-medium">{job.next_backup_at ? timeAgo(job.next_backup_at) : '—'}</span>
        </div>
        {job.backup_size_gb != null && (
          <div className="flex items-center justify-between">
            <span className="text-gray-400">Size</span>
            <span className="font-medium">{formatBytes(job.backup_size_gb)}</span>
          </div>
        )}
        <div className="flex items-center justify-between">
          <span className="text-gray-400">Retention</span>
          <span className="font-medium">{job.retention_days} days</span>
        </div>
      </div>

      {job.notes && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <p className="text-xs text-amber-600 bg-amber-50 rounded p-2">{job.notes}</p>
        </div>
      )}
    </div>
  )
}

function StatusBadge({ status }: { status: string }) {
  const cfg = statusConfig[status as keyof typeof statusConfig] ?? statusConfig.unknown
  const Icon = cfg.icon
  return (
    <span className={`inline-flex items-center gap-1 text-xs font-medium px-2.5 py-1 rounded-full ${cfg.bg} ${cfg.color}`}>
      <Icon size={11} />
      {status}
    </span>
  )
}

export default function BackupsPage() {
  return (
    <Suspense fallback={<div className="p-6"><div className="h-64 bg-gray-100 rounded-2xl animate-pulse" /></div>}>
      <BackupsContent />
    </Suspense>
  )
}
