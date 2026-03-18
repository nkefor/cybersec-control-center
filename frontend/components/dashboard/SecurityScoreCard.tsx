'use client'

import { TrendingUp, TrendingDown, Clock } from 'lucide-react'
import { scoreColor, timeAgo } from '@/lib/utils'

interface SecurityScoreCardProps {
  score: number
  change7d: number
  lastSynced: string | null
}

export function SecurityScoreCard({ score, change7d, lastSynced }: SecurityScoreCardProps) {
  const colors = scoreColor(score)
  const radius = 54
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (score / 100) * circumference

  const label = score >= 76 ? 'Good' : score >= 51 ? 'Fair' : 'Poor'

  return (
    <div className="bg-white rounded-2xl border border-gray-200 p-6 flex flex-col items-center">
      <p className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
        Security Score
      </p>

      {/* Circular gauge */}
      <div className="relative w-40 h-40 mb-4">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 128 128">
          {/* Track */}
          <circle
            cx="64"
            cy="64"
            r={radius}
            fill="none"
            stroke="#F1F5F9"
            strokeWidth="12"
          />
          {/* Score arc */}
          <circle
            cx="64"
            cy="64"
            r={radius}
            fill="none"
            stroke={colors.stroke}
            strokeWidth="12"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-4xl font-bold ${colors.text}`}>{score}</span>
          <span className="text-xs text-gray-400 font-medium mt-0.5">{label}</span>
        </div>
      </div>

      {/* 7-day delta */}
      <div className="flex items-center gap-1.5">
        {change7d >= 0 ? (
          <TrendingUp size={16} className="text-green-500" />
        ) : (
          <TrendingDown size={16} className="text-red-500" />
        )}
        <span
          className={`text-sm font-semibold ${
            change7d >= 0 ? 'text-green-600' : 'text-red-600'
          }`}
        >
          {change7d >= 0 ? '+' : ''}
          {change7d} pts this week
        </span>
      </div>

      {lastSynced && (
        <div className="flex items-center gap-1.5 mt-2 text-xs text-gray-400">
          <Clock size={12} />
          <span>Synced {timeAgo(lastSynced)}</span>
        </div>
      )}
    </div>
  )
}
