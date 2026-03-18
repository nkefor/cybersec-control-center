// API client with typed fetch wrapper

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
    message?: string
  ) {
    super(message || detail)
    this.name = 'ApiError'
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${path}`
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  }

  const response = await fetch(url, {
    ...options,
    headers,
    cache: 'no-store',
  })

  if (!response.ok) {
    let detail = `HTTP ${response.status}`
    try {
      const err = await response.json()
      detail = err.detail || err.message || detail
    } catch {
      // ignore JSON parse errors
    }
    throw new ApiError(response.status, detail)
  }

  if (response.status === 204) {
    return undefined as unknown as T
  }

  return response.json() as Promise<T>
}

// Dashboard
export const dashboardApi = {
  getSummary: () => request<import('./types').DashboardSummary>('/api/dashboard/summary'),
}

// Identity
export const identityApi = {
  getUsers: (params?: Record<string, string | number | boolean>) => {
    const qs = params ? '?' + new URLSearchParams(
      Object.fromEntries(Object.entries(params).map(([k, v]) => [k, String(v)]))
    ).toString() : ''
    return request<import('./types').UserListResponse>(`/api/identity/users${qs}`)
  },
  getMFASummary: () => request<import('./types').MFASummary>('/api/identity/mfa-summary'),
  getInactiveUsers: (days = 30) =>
    request<import('./types').InactiveUser[]>(`/api/identity/inactive-users?days=${days}`),
  triggerSync: () =>
    request<{ status: string; message: string }>('/api/identity/sync', { method: 'POST' }),
}

// Devices
export const devicesApi = {
  getDevices: (params?: Record<string, string | number | boolean>) => {
    const qs = params ? '?' + new URLSearchParams(
      Object.fromEntries(Object.entries(params).map(([k, v]) => [k, String(v)]))
    ).toString() : ''
    return request<import('./types').DeviceListResponse>(`/api/devices${qs}`)
  },
  getPostureSummary: () =>
    request<import('./types').DevicePostureSummary>('/api/devices/posture-summary'),
}

// Backups
export const backupsApi = {
  getBackups: (status?: string) =>
    request<import('./types').BackupListResponse>(
      `/api/backups${status ? `?status=${status}` : ''}`
    ),
  createBackup: (data: import('./types').BackupJobCreate) =>
    request<import('./types').BackupJob>('/api/backups', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  updateBackup: (id: string, data: Partial<import('./types').BackupJob>) =>
    request<import('./types').BackupJob>(`/api/backups/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  deleteBackup: (id: string) =>
    request<void>(`/api/backups/${id}`, { method: 'DELETE' }),
}

// Incidents
export const incidentsApi = {
  getIncidents: (params?: Record<string, string | number>) => {
    const qs = params ? '?' + new URLSearchParams(
      Object.fromEntries(Object.entries(params).map(([k, v]) => [k, String(v)]))
    ).toString() : ''
    return request<import('./types').IncidentListResponse>(`/api/incidents${qs}`)
  },
  acknowledgeIncident: (id: string) =>
    request<import('./types').Incident>(`/api/incidents/${id}/acknowledge`, { method: 'POST' }),
  resolveIncident: (id: string) =>
    request<import('./types').Incident>(`/api/incidents/${id}/resolve`, { method: 'POST' }),
}

// Tasks
export const tasksApi = {
  getTasks: (params?: Record<string, string>) => {
    const qs = params ? '?' + new URLSearchParams(params).toString() : ''
    return request<import('./types').TaskListResponse>(`/api/tasks${qs}`)
  },
  createTask: (data: import('./types').TaskCreate) =>
    request<import('./types').Task>('/api/tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  updateTask: (id: string, data: import('./types').TaskUpdate) =>
    request<import('./types').Task>(`/api/tasks/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  deleteTask: (id: string) =>
    request<void>(`/api/tasks/${id}`, { method: 'DELETE' }),
}

// Integrations
export const integrationsApi = {
  getStatus: () => request<import('./types').IntegrationStatus>('/api/integrations/status'),
  getMicrosoftAuthUrl: () =>
    request<{ authorization_url: string; state: string }>('/api/integrations/microsoft/authorize'),
  getGoogleAuthUrl: () =>
    request<{ authorization_url: string; state: string }>('/api/integrations/google/authorize'),
  disconnectMicrosoft: () =>
    request<{ status: string }>('/api/integrations/microsoft/disconnect', { method: 'DELETE' }),
  disconnectGoogle: () =>
    request<{ status: string }>('/api/integrations/google/disconnect', { method: 'DELETE' }),
}

export { ApiError }
