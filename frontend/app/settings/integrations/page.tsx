'use client'

import { useState, useEffect } from 'react'
import { integrationsApi } from '@/lib/api'
import { TopNav } from '@/components/layout/TopNav'
import { timeAgo } from '@/lib/utils'
import {
  CheckCircle2,
  XCircle,
  ExternalLink,
  RefreshCw,
  Unlink,
  Info,
  Building2,
  Globe,
} from 'lucide-react'
import type { IntegrationStatus } from '@/lib/types'

export default function IntegrationsPage() {
  const [status, setStatus] = useState<IntegrationStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [connecting, setConnecting] = useState<string | null>(null)
  const [disconnecting, setDisconnecting] = useState<string | null>(null)
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null)

  useEffect(() => {
    fetchStatus()
    // Check for connection success from OAuth callback
    const params = new URLSearchParams(window.location.search)
    const connected = params.get('connected')
    if (connected) {
      setMessage({ text: `${connected === 'microsoft' ? 'Microsoft 365' : 'Google Workspace'} connected successfully!`, type: 'success' })
      window.history.replaceState({}, '', '/settings/integrations')
    }
  }, [])

  const fetchStatus = async () => {
    try {
      const data = await integrationsApi.getStatus()
      setStatus(data)
    } catch {
      // API might not be running
    } finally {
      setLoading(false)
    }
  }

  const connectMicrosoft = async () => {
    if (!status?.microsoft365.configured) {
      setMessage({ text: 'Microsoft 365 is not configured. Set MICROSOFT_CLIENT_ID and MICROSOFT_CLIENT_SECRET environment variables.', type: 'error' })
      return
    }
    setConnecting('microsoft')
    try {
      const { authorization_url } = await integrationsApi.getMicrosoftAuthUrl()
      window.location.href = authorization_url
    } catch (e: any) {
      setMessage({ text: e.message || 'Failed to get authorization URL', type: 'error' })
      setConnecting(null)
    }
  }

  const connectGoogle = async () => {
    if (!status?.google.configured) {
      setMessage({ text: 'Google Workspace is not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables.', type: 'error' })
      return
    }
    setConnecting('google')
    try {
      const { authorization_url } = await integrationsApi.getGoogleAuthUrl()
      window.location.href = authorization_url
    } catch (e: any) {
      setMessage({ text: e.message || 'Failed to get authorization URL', type: 'error' })
      setConnecting(null)
    }
  }

  const disconnectMicrosoft = async () => {
    setDisconnecting('microsoft')
    await integrationsApi.disconnectMicrosoft()
    await fetchStatus()
    setDisconnecting(null)
    setMessage({ text: 'Microsoft 365 disconnected.', type: 'success' })
  }

  const disconnectGoogle = async () => {
    setDisconnecting('google')
    await integrationsApi.disconnectGoogle()
    await fetchStatus()
    setDisconnecting(null)
    setMessage({ text: 'Google Workspace disconnected.', type: 'success' })
  }

  return (
    <div>
      <TopNav title="Integrations" subtitle="Connect your identity providers for automatic sync" />

      <div className="p-6 space-y-6 max-w-3xl">
        {message && (
          <div
            className={`flex items-start gap-3 p-4 rounded-xl border text-sm ${
              message.type === 'success'
                ? 'bg-green-50 border-green-200 text-green-800'
                : 'bg-red-50 border-red-200 text-red-800'
            }`}
          >
            {message.type === 'success' ? <CheckCircle2 size={18} /> : <XCircle size={18} />}
            <p>{message.text}</p>
            <button onClick={() => setMessage(null)} className="ml-auto shrink-0 opacity-60 hover:opacity-100">✕</button>
          </div>
        )}

        {/* Info banner */}
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 flex items-start gap-3">
          <Info size={18} className="text-blue-600 shrink-0 mt-0.5" />
          <div className="text-sm text-blue-800">
            <p className="font-semibold mb-1">How integrations work</p>
            <p className="text-blue-700">
              Connecting your identity provider enables CyberShield to automatically sync users, MFA status,
              sign-in activity, and device posture every {30} minutes. No data is shared outside your network.
            </p>
          </div>
        </div>

        {/* Microsoft 365 */}
        <IntegrationCard
          title="Microsoft 365"
          subtitle="Azure Active Directory / Microsoft Entra ID"
          icon={<Building2 size={24} className="text-blue-600" />}
          iconBg="bg-blue-50"
          connected={status?.microsoft365.connected ?? false}
          configured={status?.microsoft365.configured ?? false}
          lastSync={status?.microsoft365.last_sync ?? null}
          tenantId={status?.microsoft365.tenant_id ?? null}
          loading={loading}
          connecting={connecting === 'microsoft'}
          disconnecting={disconnecting === 'microsoft'}
          onConnect={connectMicrosoft}
          onDisconnect={disconnectMicrosoft}
          scopes={[
            'User.Read.All — Read all user profiles and activity',
            'AuditLog.Read.All — Access sign-in and audit logs',
            'UserAuthenticationMethod.Read.All — Read MFA registration details',
            'IdentityRiskyUser.Read.All — Read risky sign-in events',
          ]}
        />

        {/* Google Workspace */}
        <IntegrationCard
          title="Google Workspace"
          subtitle="Google Admin SDK / Directory API"
          icon={<Globe size={24} className="text-red-500" />}
          iconBg="bg-red-50"
          connected={status?.google.connected ?? false}
          configured={status?.google.configured ?? false}
          lastSync={status?.google.last_sync ?? null}
          tenantId={status?.google.domain ?? null}
          loading={loading}
          connecting={connecting === 'google'}
          disconnecting={disconnecting === 'google'}
          onConnect={connectGoogle}
          onDisconnect={disconnectGoogle}
          scopes={[
            'admin.directory.user.readonly — Read user accounts',
            'admin.reports.audit.readonly — Read login activity',
            'admin.directory.device.chromeos.readonly — Read device info',
          ]}
        />

        {/* Manual entry note */}
        <div className="bg-gray-50 border border-gray-200 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-gray-700 mb-1">Manual Data Entry</h3>
          <p className="text-sm text-gray-500">
            No cloud identity provider? You can manually add users, devices, and backup jobs through the
            respective pages. The security score will be calculated based on manually entered data.
          </p>
        </div>
      </div>
    </div>
  )
}

function IntegrationCard({
  title,
  subtitle,
  icon,
  iconBg,
  connected,
  configured,
  lastSync,
  tenantId,
  loading,
  connecting,
  disconnecting,
  onConnect,
  onDisconnect,
  scopes,
}: {
  title: string
  subtitle: string
  icon: React.ReactNode
  iconBg: string
  connected: boolean
  configured: boolean
  lastSync: string | null
  tenantId: string | null
  loading: boolean
  connecting: boolean
  disconnecting: boolean
  onConnect: () => void
  onDisconnect: () => void
  scopes: string[]
}) {
  return (
    <div className={`bg-white rounded-2xl border-2 p-6 transition-colors ${connected ? 'border-green-300' : 'border-gray-200'}`}>
      <div className="flex items-start justify-between mb-5">
        <div className="flex items-center gap-3">
          <div className={`w-12 h-12 rounded-xl ${iconBg} flex items-center justify-center`}>
            {icon}
          </div>
          <div>
            <h3 className="text-base font-semibold text-gray-900">{title}</h3>
            <p className="text-xs text-gray-500">{subtitle}</p>
          </div>
        </div>

        {loading ? (
          <div className="w-24 h-7 bg-gray-100 rounded-full animate-pulse" />
        ) : connected ? (
          <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-green-700 bg-green-100 px-3 py-1.5 rounded-full">
            <CheckCircle2 size={13} /> Connected
          </span>
        ) : (
          <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-gray-500 bg-gray-100 px-3 py-1.5 rounded-full">
            <XCircle size={13} /> Not Connected
          </span>
        )}
      </div>

      {connected && (
        <div className="bg-green-50 rounded-xl p-3 mb-4 text-xs text-green-700 space-y-1">
          {tenantId && <p><strong>Tenant/Domain:</strong> {tenantId}</p>}
          {lastSync && <p><strong>Last synced:</strong> {timeAgo(lastSync)}</p>}
        </div>
      )}

      {!configured && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 mb-4 text-xs text-amber-700">
          <strong>Configuration required.</strong> Set the OAuth credentials in your <code>.env</code> file to enable this integration.
        </div>
      )}

      <div className="mb-5">
        <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Required Permissions</p>
        <ul className="space-y-1">
          {scopes.map((scope) => (
            <li key={scope} className="flex items-start gap-2 text-xs text-gray-500">
              <span className="mt-1 w-1.5 h-1.5 rounded-full bg-gray-300 shrink-0" />
              {scope}
            </li>
          ))}
        </ul>
      </div>

      <div className="flex gap-3">
        {connected ? (
          <>
            <button
              onClick={onDisconnect}
              disabled={disconnecting}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-red-600 bg-red-50 hover:bg-red-100 rounded-lg transition-colors disabled:opacity-50"
            >
              <Unlink size={15} />
              {disconnecting ? 'Disconnecting...' : 'Disconnect'}
            </button>
          </>
        ) : (
          <button
            onClick={onConnect}
            disabled={connecting || !configured}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50"
          >
            <ExternalLink size={15} />
            {connecting ? 'Redirecting...' : 'Connect'}
          </button>
        )}
      </div>
    </div>
  )
}
