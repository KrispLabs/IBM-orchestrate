import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  GitBranch, Trash2, Plus, Copy, Check,
  AlertTriangle, Loader2, RefreshCw, CheckCircle2, RotateCw,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import { githubAPI } from '../services/api'

function relativeTime(iso) {
  if (!iso) return 'never'
  const then = new Date(iso).getTime()
  const diff = Math.max(0, Date.now() - then)
  const s = Math.floor(diff / 1000)
  if (s < 60) return `${s}s ago`
  const m = Math.floor(s / 60)
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  const d = Math.floor(h / 24)
  return `${d}d ago`
}

function RepoCard({ repo, onView, onDelete, onRescan, isRescanning }) {
  const isScanning = repo.scan_status === 'pending' || repo.scan_status === 'scanning'
  const isFailed = repo.scan_status === 'failed'
  const isCompleted = repo.scan_status === 'completed'

  return (
    <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-slate-900 rounded-lg border border-gray-200 dark:border-slate-700">
      <div className="flex items-center space-x-3 min-w-0 flex-1">
        <GitBranch className="text-blue-500 shrink-0" size={20} />
        <div className="min-w-0 flex-1">
          <p className="text-gray-900 dark:text-white font-medium truncate">{repo.repo_name}</p>

          {isScanning && (
            <div className="flex items-center space-x-2 mt-1">
              <Loader2 className="text-blue-500 animate-spin" size={14} />
              <p className="text-blue-600 dark:text-blue-400 text-sm">
                Zero Touch is generating tests...
              </p>
            </div>
          )}

          {isCompleted && (
            <div className="flex items-center space-x-2 mt-1">
              <CheckCircle2 className="text-green-500" size={14} />
              <p className="text-gray-500 dark:text-slate-400 text-sm">
                {repo.test_count || 0} tests · {repo.passing_count || 0} passing
              </p>
              <span className="text-gray-400 dark:text-slate-500 text-xs">
                · Last scanned {relativeTime(repo.last_scanned_at)}
              </span>
            </div>
          )}

          {isFailed && (
            <div className="flex items-center space-x-2 mt-1">
              <AlertTriangle className="text-amber-500" size={14} />
              <p className="text-amber-600 dark:text-amber-400 text-sm">Scan failed</p>
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center space-x-3 shrink-0">
        {isFailed && (
          <button
            className="btn-secondary text-sm flex items-center space-x-2"
            onClick={() => onRescan(repo.id)}
            disabled={isRescanning}
          >
            <RefreshCw size={14} className={isRescanning ? 'animate-spin' : ''} />
            <span>Retry Scan</span>
          </button>
        )}
        {!isScanning && !isFailed && (
          <button
            className="btn-secondary text-sm flex items-center space-x-2"
            onClick={() => onRescan(repo.id)}
            disabled={isRescanning}
            title="Re-run tests"
          >
            <RotateCw size={14} className={isRescanning ? 'animate-spin' : ''} />
            <span>Re-run Tests</span>
          </button>
        )}
        <button
          className="btn-secondary text-sm"
          onClick={() => onView(repo.id)}
        >
          View
        </button>
        <button
          className="p-2 text-gray-400 dark:text-slate-400 hover:text-red-500 dark:hover:text-red-400 transition-colors"
          onClick={() => onDelete(repo)}
          aria-label="Remove repository"
        >
          <Trash2 size={16} />
        </button>
      </div>
    </div>
  )
}

export default function Repositories() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [fullName, setFullName] = useState('')
  const [formError, setFormError] = useState('')
  const [newRepoSecret, setNewRepoSecret] = useState(null)
  const [copiedSecret, setCopiedSecret] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(null)
  const [rescanningIds, setRescanningIds] = useState(new Set())

  const { data: repos, isLoading } = useQuery({
    queryKey: ['repos-list'],
    queryFn: () => githubAPI.listRepos().then(r => r.data),
    refetchInterval: (q) => {
      const list = q.state.data || []
      const anyScanning = list.some(
        r => r.scan_status === 'pending' || r.scan_status === 'scanning'
      )
      return anyScanning ? 3000 : false
    },
  })

  const connectMutation = useMutation({
    mutationFn: (data) => githubAPI.connectRepo(data),
    onSuccess: (res) => {
      setNewRepoSecret(res.data)
      setFullName('')
      setFormError('')
      queryClient.invalidateQueries({ queryKey: ['repos-list'] })
      queryClient.invalidateQueries({ queryKey: ['repos'] })
    },
    onError: (err) => {
      const msg = err.response?.data?.error || 'Failed to connect repository'
      if (err.response?.status === 409) {
        setFormError('This repository is already connected')
      } else if (err.response?.status === 400) {
        setFormError('Invalid format — use owner/repository-name')
      } else if (err.response?.status === 404) {
        setFormError(msg)
      } else {
        setFormError(msg)
      }
    },
  })

  const disconnectMutation = useMutation({
    mutationFn: (repoId) => githubAPI.disconnectRepo(repoId),
    onSuccess: () => {
      setConfirmDelete(null)
      queryClient.invalidateQueries({ queryKey: ['repos-list'] })
      queryClient.invalidateQueries({ queryKey: ['repos'] })
    },
  })

  const rescanMutation = useMutation({
    mutationFn: (repoId) => githubAPI.rescanRepo(repoId),
    onMutate: (repoId) => {
      setRescanningIds(prev => new Set(prev).add(repoId))
    },
    onSettled: (_data, _err, repoId) => {
      setRescanningIds(prev => {
        const next = new Set(prev)
        next.delete(repoId)
        return next
      })
      queryClient.invalidateQueries({ queryKey: ['repos-list'] })
    },
  })

  const rescanAllMutation = useMutation({
    mutationFn: () => githubAPI.rescanAll(),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['repos-list'] })
    },
  })

  function handleConnect(e) {
    e.preventDefault()
    setFormError('')
    setNewRepoSecret(null)
    if (fullName.split('/').filter(Boolean).length !== 2) {
      setFormError('Invalid format — use owner/repository-name')
      return
    }
    connectMutation.mutate({ full_name: fullName.trim() })
  }

  function handleCopySecret(secret) {
    navigator.clipboard.writeText(secret)
    setCopiedSecret(true)
    setTimeout(() => setCopiedSecret(false), 2000)
  }

  const activeRepos = (repos || []).filter(r => r.is_active !== false)
  const anyScanning = activeRepos.some(
    r => r.scan_status === 'pending' || r.scan_status === 'scanning'
  )

  return (
    <Layout>
      <div className="space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Repositories</h1>
            <p className="text-gray-500 dark:text-slate-400 mt-1">Manage connected GitHub repositories</p>
          </div>
          {activeRepos.length > 0 && (
            <button
              className="btn-secondary flex items-center space-x-2"
              onClick={() => rescanAllMutation.mutate()}
              disabled={rescanAllMutation.isPending || anyScanning}
            >
              <RotateCw
                size={16}
                className={rescanAllMutation.isPending || anyScanning ? 'animate-spin' : ''}
              />
              <span>Re-run All Tests</span>
            </button>
          )}
        </div>

        {/* Section A — Connected repos */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Connected Repositories</h2>
          {isLoading ? (
            <div className="flex items-center justify-center h-24">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
            </div>
          ) : activeRepos.length > 0 ? (
            <div className="space-y-3">
              {activeRepos.map((repo) => (
                <RepoCard
                  key={repo.id}
                  repo={repo}
                  onView={(id) => navigate(`/repo/${id}`)}
                  onDelete={(r) => setConfirmDelete(r)}
                  onRescan={(id) => rescanMutation.mutate(id)}
                  isRescanning={rescanningIds.has(repo.id)}
                />
              ))}
            </div>
          ) : (
            <p className="text-gray-500 dark:text-slate-400 text-center py-8">No repositories connected yet</p>
          )}
        </div>

        {/* Confirm delete dialog */}
        {confirmDelete && (
          <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
            <div className="card max-w-md w-full mx-4">
              <div className="flex items-center space-x-3 mb-4">
                <AlertTriangle className="text-amber-500 dark:text-amber-400" size={24} />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Remove Repository?</h3>
              </div>
              <p className="text-gray-600 dark:text-slate-400 mb-2">
                Remove <span className="text-gray-900 dark:text-white font-medium">{confirmDelete.repo_name}</span>?
              </p>
              <p className="text-gray-500 dark:text-slate-500 text-sm mb-6">Test history is kept. You can reconnect at any time.</p>
              <div className="flex space-x-3">
                <button
                  className="btn-primary flex-1 bg-red-600 hover:bg-red-700"
                  onClick={() => disconnectMutation.mutate(confirmDelete.id)}
                  disabled={disconnectMutation.isPending}
                >
                  {disconnectMutation.isPending ? 'Removing...' : 'Remove'}
                </button>
                <button className="btn-secondary flex-1" onClick={() => setConfirmDelete(null)}>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Section B — Add new repo */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Connect a Repository</h2>
          <form onSubmit={handleConnect} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-600 dark:text-slate-400 mb-2">
                GitHub Repository
              </label>
              <div className="flex space-x-3">
                <input
                  type="text"
                  className="input flex-1"
                  placeholder="owner/repository-name"
                  value={fullName}
                  onChange={e => { setFullName(e.target.value); setFormError('') }}
                />
                <button
                  type="submit"
                  className="btn-primary flex items-center space-x-2 whitespace-nowrap"
                  disabled={connectMutation.isPending}
                >
                  <Plus size={18} />
                  <span>{connectMutation.isPending ? 'Connecting...' : 'Connect Repository'}</span>
                </button>
              </div>
              {formError && (
                <p className="text-red-500 dark:text-red-400 text-sm mt-2">{formError}</p>
              )}
            </div>
          </form>

          {/* Webhook secret reveal */}
          {newRepoSecret && (
            <div className="mt-6 p-4 bg-gray-50 dark:bg-slate-900 rounded-lg border border-blue-400/50 dark:border-blue-500/50">
              <p className="text-gray-900 dark:text-white font-medium mb-1">Repository connected!</p>
              <p className="text-gray-600 dark:text-slate-400 text-sm mb-3">
                Zero Touch is now scanning the repo. Add this secret to your GitHub webhook settings:
              </p>
              <div className="flex items-center space-x-3">
                <code className="flex-1 text-blue-600 dark:text-blue-400 text-sm bg-white dark:bg-slate-800 px-3 py-2 rounded font-mono truncate border border-gray-200 dark:border-slate-700">
                  {newRepoSecret.webhook_secret}
                </code>
                <button
                  className="btn-secondary flex items-center space-x-2 shrink-0"
                  onClick={() => handleCopySecret(newRepoSecret.webhook_secret)}
                >
                  {copiedSecret ? <Check size={16} className="text-green-500" /> : <Copy size={16} />}
                  <span>{copiedSecret ? 'Copied' : 'Copy'}</span>
                </button>
              </div>
              <p className="text-gray-500 dark:text-slate-500 text-xs mt-2">
                Webhook URL: <span className="text-gray-600 dark:text-slate-400">POST /api/github/webhook/</span>
              </p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}
