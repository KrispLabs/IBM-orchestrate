import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, FileCode, CheckCircle, XCircle, Clock } from 'lucide-react'
import Layout from '../components/Layout'
import AIOverview from '../components/AIOverview'
import { githubAPI, aiAPI, insightsAPI } from '../services/api'

export default function RepositoryDetail() {
  const { repoId } = useParams()

  const { data: repo, isLoading: repoLoading } = useQuery({
    queryKey: ['repo', repoId],
    queryFn: () => githubAPI.getRepo(repoId).then(res => res.data),
  })

  const { data: testFiles, isLoading: testsLoading } = useQuery({
    queryKey: ['testFiles', repoId],
    queryFn: () => aiAPI.listTestFiles(repoId).then(res => res.data),
  })

  const { data: timeline } = useQuery({
    queryKey: ['timeline', repoId],
    queryFn: () => insightsAPI.getTimeline(repoId).then(res => res.data),
  })

  const { data: testHealth } = useQuery({
    queryKey: ['testHealth', repoId],
    queryFn: () => insightsAPI.getTestHealth(repoId).then(res => res.data),
  })

  if (repoLoading || testsLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      </Layout>
    )
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'passing':
        return <CheckCircle className="text-green-500" size={20} />
      case 'failing':
        return <XCircle className="text-red-500" size={20} />
      default:
        return <Clock className="text-yellow-500" size={20} />
    }
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center space-x-4">
          <Link to="/" className="text-gray-500 dark:text-slate-400 hover:text-gray-900 dark:hover:text-white">
            <ArrowLeft size={24} />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">{repo?.repo_name}</h1>
            <a
              href={repo?.repo_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-500 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 text-sm"
            >
              {repo?.repo_url}
            </a>
          </div>
        </div>

        {/* Test Health Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 dark:text-slate-400 text-sm">Total Tests</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                  {testHealth?.total_tests || 0}
                </p>
              </div>
              <FileCode className="text-blue-500" size={32} />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 dark:text-slate-400 text-sm">Passing</p>
                <p className="text-3xl font-bold text-green-500 mt-2">
                  {testHealth?.passing || 0}
                </p>
              </div>
              <CheckCircle className="text-green-500" size={32} />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 dark:text-slate-400 text-sm">Coverage</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                  {testHealth?.coverage || 0}%
                </p>
              </div>
              <div className="w-12 h-12 rounded-full border-4 border-blue-500 flex items-center justify-center">
                <span className="text-blue-500 text-xs font-bold">
                  {testHealth?.coverage || 0}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* AI Overview */}
        <AIOverview repoId={repoId} />

        {/* Recent Activity Timeline */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recent Activity</h3>
          {timeline && timeline.length > 0 ? (
            <div className="space-y-4">
              {timeline.map((event, index) => (
                <div
                  key={index}
                  className="flex items-start space-x-4 p-4 bg-gray-50 dark:bg-slate-900 rounded-lg border border-gray-200 dark:border-slate-700"
                >
                  <div className="mt-1">{getStatusIcon(event.status)}</div>
                  <div className="flex-1">
                    <p className="text-gray-900 dark:text-white font-medium">{event.title}</p>
                    <p className="text-gray-500 dark:text-slate-400 text-sm mt-1">{event.description}</p>
                    <p className="text-gray-400 dark:text-slate-500 text-xs mt-2">
                      {new Date(event.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 dark:text-slate-400 text-center py-8">No recent activity</p>
          )}
        </div>

        {/* Test Files */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Generated Test Files</h3>
          {testFiles && testFiles.length > 0 ? (
            <div className="space-y-3">
              {testFiles.map((test) => (
                <Link
                  key={test.id}
                  to={`/test/${test.id}`}
                  className="block p-4 bg-gray-50 dark:bg-slate-900 rounded-lg border border-gray-200 dark:border-slate-700 hover:border-gray-300 dark:hover:border-slate-600 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <FileCode className="text-blue-500" size={20} />
                      <div>
                        <p className="text-gray-900 dark:text-white font-medium">{test.code_file?.file_path}</p>
                        <p className="text-gray-500 dark:text-slate-400 text-sm">
                          {test.generated_by_ai ? 'AI Generated' : 'Manual'}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      {getStatusIcon(test.is_passing ? 'passing' : 'failing')}
                      <span className="text-gray-500 dark:text-slate-400 text-sm">
                        {new Date(test.last_updated).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <FileCode className="mx-auto text-gray-400 dark:text-slate-600" size={48} />
              <p className="text-gray-500 dark:text-slate-400 mt-4">No test files generated yet</p>
              <p className="text-gray-400 dark:text-slate-500 text-sm mt-2">
                Push code changes to trigger automatic test generation
              </p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}

// Made with Bob
