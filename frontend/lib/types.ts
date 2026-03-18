// Shared TypeScript types matching backend Pydantic schemas

export type RiskLevel = 'none' | 'low' | 'medium' | 'high'
export type UserSource = 'microsoft365' | 'google' | 'manual'
export type OsType = 'windows' | 'macos' | 'linux' | 'ios' | 'android' | 'other'
export type BackupStatus = 'healthy' | 'warning' | 'critical' | 'unknown'
export type IncidentSeverity = 'info' | 'low' | 'medium' | 'high' | 'critical'
export type IncidentCategory =
  | 'risky_login'
  | 'mfa_bypass'
  | 'inactive_account'
  | 'device_noncompliance'
  | 'backup_failure'
  | 'phishing'
  | 'other'
export type IncidentStatus = 'open' | 'acknowledged' | 'resolved'
export type TaskPriority = 'low' | 'medium' | 'high' | 'critical'
export type TaskStatus = 'todo' | 'in_progress' | 'done' | 'dismissed'

// Dashboard
export interface MFACoverage {
  enabled: number
  total: number
  percentage: number
}

export interface DeviceSummary {
  compliant: number
  noncompliant: number
  total: number
}

export interface BackupSummary {
  healthy: number
  warning: number
  critical: number
  unknown: number
}

export interface DashboardSummary {
  security_score: number
  score_change_7d: number
  mfa_coverage: MFACoverage
  risky_logins_24h: number
  devices: DeviceSummary
  backups: BackupSummary
  open_tasks: number
  critical_incidents: number
  last_synced: string | null
  tenant_name: string
}

// Users
export interface User {
  id: string
  tenant_id: string
  email: string
  display_name: string
  mfa_enabled: boolean
  mfa_methods: string[] | null
  last_sign_in: string | null
  is_active: boolean
  risk_level: RiskLevel
  source: UserSource
  created_at: string
  updated_at: string
}

export interface UserListResponse {
  items: User[]
  total: number
  page: number
  page_size: number
}

export interface MFASummary {
  total_users: number
  mfa_enabled: number
  mfa_disabled: number
  coverage_percentage: number
  methods_breakdown: Record<string, number>
}

export interface InactiveUser {
  id: string
  email: string
  display_name: string
  last_sign_in: string | null
  days_inactive: number
  risk_level: RiskLevel
}

// Devices
export interface Device {
  id: string
  tenant_id: string
  device_name: string
  owner_email: string | null
  os_type: OsType
  os_version: string | null
  is_compliant: boolean
  encryption_enabled: boolean
  last_seen: string | null
  compliance_issues: string[] | null
  risk_score: number
  source: UserSource
  created_at: string
}

export interface DeviceListResponse {
  items: Device[]
  total: number
  page: number
  page_size: number
}

export interface DevicePostureSummary {
  total: number
  compliant: number
  noncompliant: number
  compliance_rate: number
  encrypted: number
  encryption_rate: number
  by_os: Record<string, number>
}

// Backups
export interface BackupJob {
  id: string
  tenant_id: string
  name: string
  target_description: string
  last_backup_at: string | null
  next_backup_at: string | null
  status: BackupStatus
  backup_size_gb: number | null
  retention_days: number
  provider: string
  notes: string | null
  created_at: string
}

export interface BackupListResponse {
  items: BackupJob[]
  total: number
}

// Incidents
export interface Incident {
  id: string
  tenant_id: string
  title: string
  description: string
  severity: IncidentSeverity
  category: IncidentCategory
  user_email: string | null
  device_id: string | null
  status: IncidentStatus
  detected_at: string
  resolved_at: string | null
  source_data: Record<string, unknown> | null
  created_at: string
}

export interface IncidentListResponse {
  items: Incident[]
  total: number
  page: number
  page_size: number
}

// Tasks
export interface Task {
  id: string
  tenant_id: string
  title: string
  description: string | null
  priority: TaskPriority
  status: TaskStatus
  assigned_to: string | null
  related_incident_id: string | null
  due_date: string | null
  completed_at: string | null
  created_at: string
  updated_at: string
}

export interface TaskListResponse {
  items: Task[]
  total: number
}

export interface BackupJobCreate {
  name: string
  target_description: string
  provider: string
  retention_days?: number
  notes?: string
}

export interface TaskCreate {
  title: string
  description?: string
  priority?: TaskPriority
  assigned_to?: string
  due_date?: string
}

export interface TaskUpdate {
  title?: string
  description?: string
  priority?: TaskPriority
  status?: TaskStatus
  assigned_to?: string
  due_date?: string
}

// Integrations
export interface IntegrationStatus {
  microsoft365: {
    connected: boolean
    tenant_id: string | null
    last_sync: string | null
    configured: boolean
  }
  google: {
    connected: boolean
    domain: string | null
    last_sync: string | null
    configured: boolean
  }
}
