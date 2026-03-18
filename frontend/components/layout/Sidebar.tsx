'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard,
  Users,
  Monitor,
  Database,
  AlertTriangle,
  ClipboardList,
  Settings,
  Plug,
  Shield,
  ChevronRight,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const navItems = [
  { href: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { href: '/dashboard/identity', icon: Users, label: 'Identity' },
  { href: '/dashboard/devices', icon: Monitor, label: 'Devices' },
  { href: '/dashboard/backups', icon: Database, label: 'Backups' },
  { href: '/dashboard/incidents', icon: AlertTriangle, label: 'Incidents' },
  { href: '/dashboard/tasks', icon: ClipboardList, label: 'Tasks' },
]

const settingsItems = [
  { href: '/settings', icon: Settings, label: 'Settings' },
  { href: '/settings/integrations', icon: Plug, label: 'Integrations' },
]

interface NavItemProps {
  href: string
  icon: React.ElementType
  label: string
  active: boolean
}

function NavItem({ href, icon: Icon, label, active }: NavItemProps) {
  return (
    <Link
      href={href}
      className={cn(
        'flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-150',
        active
          ? 'bg-blue-600 text-white shadow-sm'
          : 'text-slate-400 hover:text-white hover:bg-slate-800'
      )}
    >
      <Icon size={18} className="shrink-0" />
      <span>{label}</span>
      {active && <ChevronRight size={14} className="ml-auto opacity-70" />}
    </Link>
  )
}

export function Sidebar({
  tenantName = 'Your Organization',
  plan = 'Professional Plan',
}: {
  tenantName?: string
  plan?: string
}) {
  const pathname = usePathname()

  const isActive = (href: string) => {
    if (href === '/dashboard') return pathname === '/dashboard'
    return pathname.startsWith(href)
  }

  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-slate-900 border-r border-slate-800 flex flex-col z-30">
      {/* Logo */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-slate-800">
        <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center shrink-0">
          <Shield size={20} className="text-white" />
        </div>
        <div>
          <p className="text-white font-bold text-base leading-tight">CyberShield</p>
          <p className="text-slate-500 text-xs">Control Center</p>
        </div>
      </div>

      {/* Main nav */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <p className="px-4 text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2">
          Security
        </p>
        {navItems.map((item) => (
          <NavItem
            key={item.href}
            href={item.href}
            icon={item.icon}
            label={item.label}
            active={isActive(item.href)}
          />
        ))}

        <div className="pt-4 mt-4 border-t border-slate-800">
          <p className="px-4 text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2">
            Configuration
          </p>
          {settingsItems.map((item) => (
            <NavItem
              key={item.href}
              href={item.href}
              icon={item.icon}
              label={item.label}
              active={isActive(item.href)}
            />
          ))}
        </div>
      </nav>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-slate-800">
        <div className="flex items-center gap-3 px-2">
          <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-xs font-bold">
            AL
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-white text-sm font-medium truncate">{tenantName}</p>
            <p className="text-slate-500 text-xs">{plan}</p>
          </div>
        </div>
      </div>
    </aside>
  )
}
