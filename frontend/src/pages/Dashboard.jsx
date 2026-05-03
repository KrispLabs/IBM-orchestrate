import { useQuery } from '@tanstack/react-query'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts'
import { CheckCircle, XCircle, Clock, TrendingUp, GitBranch, FileCode } from 'lucide-react'
import Layout from '../components/Layout'
import { insightsAPI, githubAPI } from '../services/api'

export default function Dashboard() {
  const { data: metrics, isLoading: metricsLoading } = useQuery({
    queryKey: ['metrics'],
    queryFn: () => insightsAPI.getMetrics().then(res => res.data),
  })

  const { data: repos, isLoading: reposLoading } = useQuery({
    queryKey: ['repos'],
    queryFn: () => githubAPI.listRepos().then(res => res.data),
  })

  const { data: productivity } = useQuery({
    queryKey: ['productivity'],
    queryFn: () => insightsAPI.getProductivityStats().then(res => res.data),
  })

  if (metricsLoading || reposLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      </Layout>
    )
  }

  const stats = [
    {
      label: 'Tests Generated',
      value: metrics?.total_tests || 0,
      icon: CheckCircle,
      color: 'text-green-500',
      bgColor: 'bg-green-500/10',
    },
    {
      label: 'Active Repos',
      value: repos?.length || 0,
      icon: GitBranch,
      color: 'text-blue-500',
      bgColor: 'bg-blue-500/10',
    },
    {
      label: 'Test Coverage',
      value: `${metrics?.coverage || 0}%`,
      icon: TrendingUp,
      color: 'text-purple-500',
      bgColor: 'bg-purple-500/10',
    },
    {
      label: 'Files Analyzed',
      value: metrics?.files_analyzed || 0,
      icon: FileCode,
      color: 'text-yellow-500',
      bgColor: 'bg-yellow-500/10',
    },
  ]

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-white">Dashboard</h1>
          <p className="text-slate-400 mt-1">Monitor your automated test generation</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat) => {
            const Icon = stat.icon
            return (
              <div key={stat.label} className="card">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-slate-400 text-sm">{stat.label}</p>
                    <p className="text-3xl font-bold text-white mt-2">{stat.value}</p>
                  </div>
                  <div className={`${stat.bgColor} p-3 rounded-lg`}>
                    <Icon className={stat.color} size={24} />
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Test Generation Timeline */}
          <div className="card">
            <h3 className="text-lg font-semibold text-white mb-4">Test Generation Timeline</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={productivity?.timeline || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="date" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                  labelStyle={{ color: '#94a3b8' }}
                />
                <Line type="monotone" dataKey="tests" stroke="#3b82f6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Test Status Distribution */}
          <div className="card">
            <h3 className="text-lg font-semibold text-white mb-4">Test Status</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={metrics?.test_status || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="status" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                  labelStyle={{ color: '#94a3b8' }}
                />
                <Bar dataKey="count" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recent Repositories */}
        <div className="card">
          <h3 className="text-lg font-semibold text-white mb-4">Connected Repositories</h3>
          {repos && repos.length > 0 ? (
            <div className="space-y-3">
              {repos.slice(0, 5).map((repo) => (
                <div
                  key={repo.id}
                  className="flex items-center justify-between p-4 bg-slate-900 rounded-lg border border-slate-700 hover:border-slate-600 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <GitBranch className="text-blue-500" size={20} />
                    <div>
                      <p className="text-white font-medium">{repo.repo_name}</p>
                      <p className="text-slate-400 text-sm">{repo.repo_url}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <p className="text-slate-400 text-sm">Last updated</p>
                      <p className="text-white text-sm">
                        {new Date(repo.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <button className="btn-secondary text-sm">View</button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <GitBranch className="mx-auto text-slate-600" size={48} />
              <p className="text-slate-400 mt-4">No repositories connected yet</p>
              <button className="btn-primary mt-4">Connect Repository</button>
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}

// Made with Bob
