'use client'

import { Bell, RefreshCw, Search } from 'lucide-react'
import { useState } from 'react'
import { identityApi } from '@/lib/api'

interface TopNavProps {
  title: string
  subtitle?: string
}

export function TopNav({ title, subtitle }: TopNavProps) {
  const [syncing, setSyncing] = useState(false)
  const [syncMsg, setSyncMsg] = useState<string | null>(null)

  const handleSync = async () => {
    setSyncing(true)
    setSyncMsg(null)
    try {
      const result = await identityApi.triggerSync()
      setSyncMsg(result.message)
    } catch {
      setSyncMsg('Sync failed. Check integrations.')
    } finally {
      setSyncing(false)
      setTimeout(() => setSyncMsg(null), 4000)
    }
  }

  return (
    <header className="sticky top-0 z-20 bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-gray-900">{title}</h1>
          {subtitle && <p className="text-sm text-gray-500 mt-0.5">{subtitle}</p>}
        </div>

        <div className="flex items-center gap-3">
          {syncMsg && (
            <span className="text-xs text-green-600 bg-green-50 px-3 py-1.5 rounded-full border border-green-200">
              {syncMsg}
            </span>
          )}

          <button
            onClick={handleSync}
            disabled={syncing}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            <RefreshCw size={15} className={syncing ? 'animate-spin' : ''} />
            {syncing ? 'Syncing...' : 'Sync Now'}
          </button>

          <button className="relative p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
            <Bell size={18} />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
          </button>
        </div>
      </div>
    </header>
  )
}
