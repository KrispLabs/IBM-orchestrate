import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Sparkles, ShieldCheck, AlertTriangle, Lightbulb, RefreshCw } from 'lucide-react'
import { repoOverviewAPI } from '../services/api'

function SkeletonCard() {
  return (
    <div className="p-4 bg-gray-100 dark:bg-slate-900 rounded-lg border border-gray-200 dark:border-slate-700 animate-pulse space-y-3">
      <div className="h-4 bg-gray-200 dark:bg-slate-700 rounded w-1/3" />
      <div className="h-3 bg-gray-200 dark:bg-slate-700 rounded w-full" />
      <div className="h-3 bg-gray-200 dark:bg-slate-700 rounded w-5/6" />
    </div>
  )
}

export default function AIOverview({ repoId }) {
  const queryClient = useQueryClient()

  const { data, isLoading, isError, refetch, isFetching } = useQuery({
    queryKey: ['repo-overview', repoId],
    queryFn: () => repoOverviewAPI.getOverview(repoId).then(r => r.data),
    staleTime: 5 * 60 * 1000,
    retry: 1,
  })

  function handleRefresh() {
    queryClient.invalidateQueries({ queryKey: ['repo-overview', repoId] })
    refetch()
  }

  return (
    <div className="card space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">AI Analysis</h3>
          <span className="px-2 py-0.5 rounded text-xs font-medium text-white"
            style={{ backgroundColor: '#0F62FE' }}>
            Powered by IBM WatsonX
          </span>
        </div>
        <button
          onClick={handleRefresh}
          disabled={isFetching}
          className="flex items-center space-x-2 text-gray-500 dark:text-slate-400 hover:text-gray-900 dark:hover:text-white transition-colors disabled:opacity-50"
        >
          <RefreshCw size={16} className={isFetching ? 'animate-spin' : ''} />
          <span className="text-sm">Refresh Analysis</span>
        </button>
      </div>

      {isLoading || isFetching ? (
        <div className="space-y-3">
          <p className="text-gray-500 dark:text-slate-400 text-sm animate-pulse">
            IBM WatsonX is analyzing your repository...
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </div>
        </div>
      ) : isError ? (
        <div className="text-center py-6">
          <p className="text-gray-500 dark:text-slate-400">WatsonX analysis unavailable — showing cached data</p>
          <button onClick={handleRefresh} className="btn-secondary mt-3 text-sm">Retry</button>
        </div>
      ) : data ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Card 1 — Summary */}
          <div className="p-4 bg-gray-50 dark:bg-slate-900 rounded-lg border border-gray-200 dark:border-slate-700">
            <div className="flex items-center space-x-2 mb-3">
              <Sparkles className="text-blue-500 dark:text-blue-400" size={18} />
              <p className="text-gray-900 dark:text-white font-medium text-sm">Repository Summary</p>
            </div>
            <p className="text-gray-600 dark:text-slate-400 text-sm leading-relaxed">{data.summary}</p>
          </div>

          {/* Card 2 — Coverage */}
          <div className="p-4 bg-gray-50 dark:bg-slate-900 rounded-lg border border-gray-200 dark:border-slate-700">
            <div className="flex items-center space-x-2 mb-3">
              <ShieldCheck className="text-green-500 dark:text-green-400" size={18} />
              <p className="text-gray-900 dark:text-white font-medium text-sm">Coverage Assessment</p>
            </div>
            <p className="text-gray-600 dark:text-slate-400 text-sm leading-relaxed">{data.coverage_assessment}</p>
          </div>

          {/* Card 3 — Risk Areas */}
          <div className="p-4 bg-gray-50 dark:bg-slate-900 rounded-lg border border-amber-400/50 dark:border-amber-500/30">
            <div className="flex items-center space-x-2 mb-3">
              <AlertTriangle className="text-amber-500 dark:text-amber-400" size={18} />
              <p className="text-gray-900 dark:text-white font-medium text-sm">Risk Areas</p>
            </div>
            <p className="text-gray-600 dark:text-slate-400 text-sm leading-relaxed">{data.risk_areas}</p>
          </div>

          {/* Card 4 — Recommendations */}
          <div className="p-4 bg-gray-50 dark:bg-slate-900 rounded-lg border border-gray-200 dark:border-slate-700">
            <div className="flex items-center space-x-2 mb-3">
              <Lightbulb className="text-yellow-500 dark:text-yellow-400" size={18} />
              <p className="text-gray-900 dark:text-white font-medium text-sm">Recommendations</p>
            </div>
            <ol className="space-y-2">
              {(data.recommendations || []).map((rec, i) => (
                <li key={i} className="flex items-start space-x-2 text-sm text-gray-600 dark:text-slate-400">
                  <span className="text-yellow-500 dark:text-yellow-400 font-bold shrink-0">{i + 1}.</span>
                  <span className="leading-relaxed">{rec}</span>
                </li>
              ))}
            </ol>
          </div>
        </div>
      ) : null}
    </div>
  )
}
