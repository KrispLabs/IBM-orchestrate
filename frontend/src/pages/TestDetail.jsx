import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, FileCode, CheckCircle, XCircle, RefreshCw } from 'lucide-react'
import Layout from '../components/Layout'
import { aiAPI } from '../services/api'

export default function TestDetail() {
  const { testId } = useParams()

  const { data: testFile, isLoading } = useQuery({
    queryKey: ['testFile', testId],
    queryFn: () => aiAPI.getTestFile(testId).then(res => res.data),
  })

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link
              to={`/repo/${testFile?.code_file?.repo?.id}`}
              className="text-slate-400 hover:text-white"
            >
              <ArrowLeft size={24} />
            </Link>
            <div>
              <h1 className="text-3xl font-bold text-white">
                {testFile?.code_file?.file_path}
              </h1>
              <p className="text-slate-400 mt-1">
                {testFile?.generated_by_ai ? 'AI Generated Test' : 'Manual Test'}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            {testFile?.is_passing ? (
              <div className="flex items-center space-x-2 px-4 py-2 bg-green-500/10 border border-green-500 rounded-lg">
                <CheckCircle className="text-green-500" size={20} />
                <span className="text-green-500 font-medium">Passing</span>
              </div>
            ) : (
              <div className="flex items-center space-x-2 px-4 py-2 bg-red-500/10 border border-red-500 rounded-lg">
                <XCircle className="text-red-500" size={20} />
                <span className="text-red-500 font-medium">Failing</span>
              </div>
            )}
            <button className="btn-secondary flex items-center space-x-2">
              <RefreshCw size={18} />
              <span>Regenerate</span>
            </button>
          </div>
        </div>

        {/* Metadata */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card">
            <p className="text-slate-400 text-sm">Last Updated</p>
            <p className="text-white font-medium mt-2">
              {new Date(testFile?.last_updated).toLocaleString()}
            </p>
          </div>

          <div className="card">
            <p className="text-slate-400 text-sm">Language</p>
            <p className="text-white font-medium mt-2">
              {testFile?.code_file?.language || 'Python'}
            </p>
          </div>

          <div className="card">
            <p className="text-slate-400 text-sm">Created</p>
            <p className="text-white font-medium mt-2">
              {new Date(testFile?.created_at).toLocaleString()}
            </p>
          </div>
        </div>

        {/* Code Comparison */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Source Code */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Source Code</h3>
              <FileCode className="text-blue-500" size={20} />
            </div>
            <div className="bg-slate-900 rounded-lg p-4 border border-slate-700 overflow-x-auto">
              <pre className="text-sm text-slate-300">
                <code>{testFile?.code_file?.file_content || 'No source code available'}</code>
              </pre>
            </div>
          </div>

          {/* Test Code */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Generated Tests</h3>
              <FileCode className="text-green-500" size={20} />
            </div>
            <div className="bg-slate-900 rounded-lg p-4 border border-slate-700 overflow-x-auto">
              <pre className="text-sm text-slate-300">
                <code>{testFile?.test_content || 'No test code available'}</code>
              </pre>
            </div>
          </div>
        </div>

        {/* Change History */}
        <div className="card">
          <h3 className="text-lg font-semibold text-white mb-4">Change History</h3>
          {testFile?.code_file?.change_events && testFile.code_file.change_events.length > 0 ? (
            <div className="space-y-3">
              {testFile.code_file.change_events.map((event) => (
                <div
                  key={event.id}
                  className="p-4 bg-slate-900 rounded-lg border border-slate-700"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-white font-medium">{event.commit_message}</p>
                      <p className="text-slate-400 text-sm mt-1">
                        Commit: {event.commit_hash?.substring(0, 8)}
                      </p>
                    </div>
                    <div className="text-right">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium ${
                          event.status === 'completed'
                            ? 'bg-green-500/10 text-green-500'
                            : event.status === 'processing'
                            ? 'bg-yellow-500/10 text-yellow-500'
                            : event.status === 'failed'
                            ? 'bg-red-500/10 text-red-500'
                            : 'bg-slate-500/10 text-slate-500'
                        }`}
                      >
                        {event.status}
                      </span>
                      <p className="text-slate-500 text-xs mt-2">
                        {new Date(event.detected_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-slate-400 text-center py-8">No change history available</p>
          )}
        </div>
      </div>
    </Layout>
  )
}

// Made with Bob
