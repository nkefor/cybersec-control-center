'use client'

import { AlertTriangle, X } from 'lucide-react'
import { useState } from 'react'

interface AlertBannerProps {
  message: string
  severity?: 'warning' | 'critical' | 'info'
  dismissible?: boolean
}

export function AlertBanner({ message, severity = 'warning', dismissible = true }: AlertBannerProps) {
  const [dismissed, setDismissed] = useState(false)

  if (dismissed) return null

  const styles = {
    warning: 'bg-amber-50 border-amber-200 text-amber-800',
    critical: 'bg-red-50 border-red-200 text-red-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800',
  }

  return (
    <div className={`flex items-center gap-3 px-4 py-3 border-b ${styles[severity]}`}>
      <AlertTriangle size={16} className="shrink-0" />
      <p className="text-sm flex-1">{message}</p>
      {dismissible && (
        <button
          onClick={() => setDismissed(true)}
          className="p-1 rounded hover:bg-black/10 transition-colors"
        >
          <X size={14} />
        </button>
      )}
    </div>
  )
}
