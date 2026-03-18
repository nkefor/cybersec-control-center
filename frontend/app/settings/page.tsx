import { TopNav } from '@/components/layout/TopNav'
import Link from 'next/link'
import { Plug, Bell, Shield, Users, Key } from 'lucide-react'

const settingsSections = [
  {
    href: '/settings/integrations',
    icon: Plug,
    title: 'Integrations',
    description: 'Connect Microsoft 365 and Google Workspace for automatic user and device sync.',
    status: 'Configure',
  },
  {
    href: '#',
    icon: Bell,
    title: 'Alert Notifications',
    description: 'Set up email or Slack alerts for critical incidents and security events.',
    status: 'Coming soon',
    disabled: true,
  },
  {
    href: '#',
    icon: Shield,
    title: 'Security Policies',
    description: 'Define MFA requirements, device compliance thresholds, and backup schedules.',
    status: 'Coming soon',
    disabled: true,
  },
  {
    href: '#',
    icon: Users,
    title: 'Team Members',
    description: 'Add administrators and assign roles for managing the security dashboard.',
    status: 'Coming soon',
    disabled: true,
  },
  {
    href: '#',
    icon: Key,
    title: 'API Access',
    description: 'Generate API keys for integrating with other security tools.',
    status: 'Coming soon',
    disabled: true,
  },
]

export default function SettingsPage() {
  return (
    <div>
      <TopNav title="Settings" subtitle="Configure CyberShield for your organization" />

      <div className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl">
          {settingsSections.map((section) => {
            const Icon = section.icon
            const content = (
              <div
                className={`bg-white rounded-2xl border border-gray-200 p-5 flex items-start gap-4 transition-all ${
                  section.disabled
                    ? 'opacity-60 cursor-not-allowed'
                    : 'hover:shadow-md hover:border-blue-200 cursor-pointer'
                }`}
              >
                <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center shrink-0">
                  <Icon size={20} className="text-blue-600" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-gray-800">{section.title}</h3>
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                        section.disabled
                          ? 'text-gray-400 bg-gray-100'
                          : 'text-blue-600 bg-blue-50'
                      }`}
                    >
                      {section.status}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">{section.description}</p>
                </div>
              </div>
            )

            return section.disabled ? (
              <div key={section.title}>{content}</div>
            ) : (
              <Link key={section.title} href={section.href}>
                {content}
              </Link>
            )
          })}
        </div>
      </div>
    </div>
  )
}
