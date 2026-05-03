import { Link, useLocation } from 'react-router-dom'
import { Home, GitBranch, Activity, LogOut } from 'lucide-react'
import { useAuthStore } from '../store/authStore'

export default function Layout({ children }) {
  const location = useLocation()
  const { user, clearAuth } = useAuthStore()

  const handleLogout = () => {
    clearAuth()
    window.location.href = '/login'
  }

  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/repos', icon: GitBranch, label: 'Repositories' },
    { path: '/activity', icon: Activity, label: 'Activity' },
  ]

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-8">
              <Link to="/" className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold">IB</span>
                </div>
                <span className="text-white font-semibold text-lg">IBM Orchestrate</span>
              </Link>
              
              <nav className="hidden md:flex space-x-4">
                {navItems.map((item) => {
                  const Icon = item.icon
                  const isActive = location.pathname === item.path
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                        isActive
                          ? 'bg-slate-700 text-white'
                          : 'text-slate-400 hover:text-white hover:bg-slate-700'
                      }`}
                    >
                      <Icon size={18} />
                      <span>{item.label}</span>
                    </Link>
                  )
                })}
              </nav>
            </div>

            <div className="flex items-center space-x-4">
              {user && (
                <div className="flex items-center space-x-3">
                  <span className="text-slate-400 text-sm">{user.email || user.username}</span>
                  <button
                    onClick={handleLogout}
                    className="flex items-center space-x-2 text-slate-400 hover:text-white transition-colors"
                  >
                    <LogOut size={18} />
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  )
}

// Made with Bob
