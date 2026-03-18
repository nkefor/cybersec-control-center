'use client'

import { useState, useEffect, useCallback } from 'react'
import { tasksApi } from '@/lib/api'
import { TopNav } from '@/components/layout/TopNav'
import { priorityColor, statusColor, timeAgo, formatDate } from '@/lib/utils'
import {
  Plus,
  X,
  ClipboardList,
  AlertTriangle,
  Calendar,
  User,
  CheckCircle2,
  ArrowRight,
} from 'lucide-react'
import type { Task, TaskCreate, TaskStatus } from '@/lib/types'

const COLUMNS: { id: TaskStatus; label: string; color: string }[] = [
  { id: 'todo', label: 'To Do', color: 'bg-blue-500' },
  { id: 'in_progress', label: 'In Progress', color: 'bg-purple-500' },
  { id: 'done', label: 'Done', color: 'bg-green-500' },
]

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [priorityFilter, setPriorityFilter] = useState('')
  const [form, setForm] = useState<TaskCreate>({ title: '', priority: 'medium' })
  const [submitting, setSubmitting] = useState(false)

  const fetchTasks = useCallback(async () => {
    setLoading(true)
    try {
      const params: Record<string, string> = {}
      if (priorityFilter) params.priority = priorityFilter
      const data = await tasksApi.getTasks(params)
      setTasks(data.items)
    } finally {
      setLoading(false)
    }
  }, [priorityFilter])

  useEffect(() => { fetchTasks() }, [fetchTasks])

  const moveTask = async (taskId: string, newStatus: TaskStatus) => {
    await tasksApi.updateTask(taskId, { status: newStatus })
    setTasks(prev => prev.map(t => t.id === taskId ? { ...t, status: newStatus } : t))
  }

  const handleCreate = async () => {
    if (!form.title.trim()) return
    setSubmitting(true)
    try {
      const task = await tasksApi.createTask(form)
      setTasks(prev => [task, ...prev])
      setShowCreateModal(false)
      setForm({ title: '', priority: 'medium' })
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id: string) => {
    await tasksApi.deleteTask(id)
    setTasks(prev => prev.filter(t => t.id !== id))
  }

  const byStatus = (status: TaskStatus) =>
    tasks.filter(t => t.status === status && (!priorityFilter || t.priority === priorityFilter))

  const priorityColors: Record<string, string> = {
    critical: 'bg-red-500',
    high: 'bg-orange-500',
    medium: 'bg-amber-500',
    low: 'bg-green-500',
  }

  return (
    <div className="animate-fade-in h-full flex flex-col">
      <TopNav title="Remediation Tasks" subtitle="Track and manage security remediation work" />

      <div className="p-6 flex-1 flex flex-col space-y-4 overflow-hidden">
        {/* Toolbar */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <select
              value={priorityFilter}
              onChange={e => setPriorityFilter(e.target.value)}
              className="text-sm border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Priorities</option>
              {['critical', 'high', 'medium', 'low'].map(p => (
                <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
              ))}
            </select>
            <span className="text-sm text-gray-400">{tasks.length} tasks</span>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn-primary flex items-center gap-2"
          >
            <Plus size={16} />
            New Task
          </button>
        </div>

        {/* Kanban board */}
        {loading ? (
          <div className="flex gap-4 flex-1">
            {[1, 2, 3].map(i => (
              <div key={i} className="flex-1 bg-gray-100 rounded-2xl animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="flex gap-4 flex-1 overflow-hidden">
            {COLUMNS.map((col) => {
              const colTasks = byStatus(col.id)
              return (
                <div
                  key={col.id}
                  className="flex-1 flex flex-col bg-gray-50 rounded-2xl border border-gray-200 overflow-hidden"
                >
                  {/* Column header */}
                  <div className="px-4 py-3 bg-white border-b border-gray-200 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className={`w-2.5 h-2.5 rounded-full ${col.color}`} />
                      <h3 className="text-sm font-semibold text-gray-700">{col.label}</h3>
                    </div>
                    <span className="text-xs font-bold text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">
                      {colTasks.length}
                    </span>
                  </div>

                  {/* Task cards */}
                  <div className="flex-1 overflow-y-auto p-3 space-y-2">
                    {colTasks.map((task) => (
                      <TaskCard
                        key={task.id}
                        task={task}
                        onMove={moveTask}
                        onDelete={handleDelete}
                      />
                    ))}
                    {colTasks.length === 0 && (
                      <div className="text-center py-8 text-gray-300 text-xs">
                        <ClipboardList size={24} className="mx-auto mb-1" />
                        No tasks
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Create Task Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 animate-fade-in">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-lg font-semibold text-gray-900">New Task</h2>
              <button
                onClick={() => setShowCreateModal(false)}
                className="p-1 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X size={18} className="text-gray-500" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5">Title *</label>
                <input
                  type="text"
                  value={form.title}
                  onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
                  placeholder="e.g. Enable MFA for user..."
                  className="input"
                  autoFocus
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5">Description</label>
                <textarea
                  value={form.description ?? ''}
                  onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
                  placeholder="Steps to complete this task..."
                  rows={3}
                  className="input resize-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-gray-600 mb-1.5">Priority</label>
                  <select
                    value={form.priority ?? 'medium'}
                    onChange={e => setForm(f => ({ ...f, priority: e.target.value as Task['priority'] }))}
                    className="select"
                  >
                    {['critical', 'high', 'medium', 'low'].map(p => (
                      <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-600 mb-1.5">Assign To</label>
                  <input
                    type="text"
                    value={form.assigned_to ?? ''}
                    onChange={e => setForm(f => ({ ...f, assigned_to: e.target.value }))}
                    placeholder="Email or name"
                    className="input"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5">Due Date</label>
                <input
                  type="datetime-local"
                  value={form.due_date ?? ''}
                  onChange={e => setForm(f => ({ ...f, due_date: e.target.value }))}
                  className="input"
                />
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={handleCreate}
                disabled={submitting || !form.title.trim()}
                className="btn-primary flex-1 disabled:opacity-50"
              >
                {submitting ? 'Creating...' : 'Create Task'}
              </button>
              <button onClick={() => setShowCreateModal(false)} className="btn-secondary">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function TaskCard({
  task,
  onMove,
  onDelete,
}: {
  task: Task
  onMove: (id: string, status: TaskStatus) => void
  onDelete: (id: string) => void
}) {
  const nextStatus: Record<string, TaskStatus | null> = {
    todo: 'in_progress',
    in_progress: 'done',
    done: null,
  }

  const next = nextStatus[task.status]

  return (
    <div className="group bg-white rounded-xl border border-gray-200 p-3.5 shadow-sm hover:shadow-md transition-shadow">
      {/* Header row */}
      <div className="flex items-start justify-between gap-2 mb-2">
        <p className="text-sm font-medium text-gray-800 leading-snug flex-1">{task.title}</p>
        <button
          onClick={() => onDelete(task.id)}
          className="p-0.5 hover:bg-gray-100 rounded opacity-0 group-hover:opacity-100 transition-opacity"
          title="Delete task"
        >
          <X size={12} className="text-gray-400 hover:text-red-500" />
        </button>
      </div>

      {task.description && (
        <p className="text-xs text-gray-500 mb-2.5 line-clamp-2">{task.description}</p>
      )}

      {/* Meta */}
      <div className="flex flex-wrap gap-1.5 mb-3">
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${priorityColor(task.priority)}`}>
          {task.priority}
        </span>
        {task.assigned_to && (
          <span className="flex items-center gap-1 text-xs text-gray-500 bg-gray-50 px-2 py-0.5 rounded-full">
            <User size={10} />{task.assigned_to.split('@')[0]}
          </span>
        )}
        {task.due_date && (
          <span className="flex items-center gap-1 text-xs text-gray-500 bg-gray-50 px-2 py-0.5 rounded-full">
            <Calendar size={10} />{timeAgo(task.due_date)}
          </span>
        )}
      </div>

      {/* Move button */}
      {next && (
        <button
          onClick={() => onMove(task.id, next)}
          className="w-full flex items-center justify-center gap-1.5 text-xs font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 py-1.5 rounded-lg transition-colors"
        >
          Move to {next === 'in_progress' ? 'In Progress' : 'Done'}
          <ArrowRight size={11} />
        </button>
      )}
      {task.status === 'done' && task.completed_at && (
        <p className="flex items-center gap-1 text-xs text-green-600 mt-1">
          <CheckCircle2 size={11} /> Completed {timeAgo(task.completed_at)}
        </p>
      )}
    </div>
  )
}
