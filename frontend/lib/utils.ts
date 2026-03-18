import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { formatDistanceToNow, format, parseISO } from 'date-fns'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function timeAgo(dateStr: string | null | undefined): string {
  if (!dateStr) return 'Never'
  try {
    return formatDistanceToNow(parseISO(dateStr), { addSuffix: true })
  } catch {
    return 'Unknown'
  }
}

export function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return '—'
  try {
    return format(parseISO(dateStr), 'MMM d, yyyy HH:mm')
  } catch {
    return '—'
  }
}

export function formatBytes(gb: number | null | undefined): string {
  if (gb == null) return '—'
  if (gb < 1) return `${Math.round(gb * 1024)} MB`
  if (gb >= 1024) return `${(gb / 1024).toFixed(1)} TB`
  return `${gb.toFixed(1)} GB`
}

export function severityColor(severity: string): string {
  const map: Record<string, string> = {
    critical: 'text-red-600 bg-red-50 border-red-200',
    high: 'text-orange-600 bg-orange-50 border-orange-200',
    medium: 'text-amber-600 bg-amber-50 border-amber-200',
    low: 'text-green-600 bg-green-50 border-green-200',
    info: 'text-blue-600 bg-blue-50 border-blue-200',
  }
  return map[severity] ?? 'text-gray-600 bg-gray-50 border-gray-200'
}

export function severityDot(severity: string): string {
  const map: Record<string, string> = {
    critical: 'bg-red-500',
    high: 'bg-orange-500',
    medium: 'bg-amber-500',
    low: 'bg-green-500',
    info: 'bg-blue-500',
  }
  return map[severity] ?? 'bg-gray-400'
}

export function priorityColor(priority: string): string {
  const map: Record<string, string> = {
    critical: 'text-red-700 bg-red-100',
    high: 'text-orange-700 bg-orange-100',
    medium: 'text-amber-700 bg-amber-100',
    low: 'text-green-700 bg-green-100',
  }
  return map[priority] ?? 'text-gray-600 bg-gray-100'
}

export function statusColor(status: string): string {
  const map: Record<string, string> = {
    healthy: 'text-green-700 bg-green-100',
    warning: 'text-amber-700 bg-amber-100',
    critical: 'text-red-700 bg-red-100',
    unknown: 'text-gray-600 bg-gray-100',
    open: 'text-red-700 bg-red-100',
    acknowledged: 'text-amber-700 bg-amber-100',
    resolved: 'text-green-700 bg-green-100',
    todo: 'text-blue-700 bg-blue-100',
    in_progress: 'text-purple-700 bg-purple-100',
    done: 'text-green-700 bg-green-100',
    dismissed: 'text-gray-600 bg-gray-100',
  }
  return map[status] ?? 'text-gray-600 bg-gray-100'
}

export function scoreColor(score: number): { text: string; stroke: string; bg: string } {
  if (score >= 76) return { text: 'text-green-600', stroke: '#16A34A', bg: 'bg-green-50' }
  if (score >= 51) return { text: 'text-amber-600', stroke: '#D97706', bg: 'bg-amber-50' }
  return { text: 'text-red-600', stroke: '#DC2626', bg: 'bg-red-50' }
}

export function categoryLabel(category: string): string {
  const map: Record<string, string> = {
    risky_login: 'Risky Sign-in',
    mfa_bypass: 'MFA Bypass',
    inactive_account: 'Inactive Account',
    device_noncompliance: 'Device Non-compliance',
    backup_failure: 'Backup Failure',
    phishing: 'Phishing',
    other: 'Other',
  }
  return map[category] ?? category
}

export function osIcon(osType: string): string {
  const map: Record<string, string> = {
    windows: 'Windows',
    macos: 'macOS',
    linux: 'Linux',
    ios: 'iOS',
    android: 'Android',
    other: 'Other',
  }
  return map[osType] ?? osType
}
