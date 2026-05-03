import { Link, useLocation } from 'react-router-dom'
import { Home, GitBranch, LogOut, Monitor, Sun, Moon } from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import { useThemeStore } from '../store/themeStore'

export default function Layout({ children }) {
  const location = useLocation()
  const { user, clearAuth } = useAuthStore()
  const { theme, setTheme } = useThemeStore()

  const handleLogout = () => {
    clearAuth()
    window.location.href = '/login'
  }

  const cycleTheme = () => {
    const next = theme === 'system' ? 'light' : theme === 'light' ? 'dark' : 'system'
    setTheme(next)
  }

  const ThemeIcon = theme === 'light' ? Sun : theme === 'dark' ? Moon : Monitor
  const themeLabel = theme === 'system' ? 'System theme' : theme === 'light' ? 'Light theme' : 'Dark theme'

  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/repositories', icon: GitBranch, label: 'Repositories' },
  ]

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-900">
      {/* Header */}
      <header className="bg-white dark:bg-slate-800 border-b border-gray-200 dark:border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-8">
              <Link to="/" className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold">ZT</span>
                </div>
                <span className="text-gray-900 dark:text-white font-semibold text-lg">Zero Touch</span>
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
                          ? 'bg-gray-100 text-gray-900 dark:bg-slate-700 dark:text-white'
                          : 'text-gray-500 dark:text-slate-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-slate-700'
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
              <button
                onClick={cycleTheme}
                title={themeLabel}
                aria-label={themeLabel}
                className="p-2 rounded-lg text-gray-500 dark:text-slate-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-slate-700 transition-colors"
              >
                <ThemeIcon size={18} />
              </button>
              {user && (
                <div className="flex items-center space-x-3">
                  <span className="text-gray-500 dark:text-slate-400 text-sm">{user.email || user.username}</span>
                  <button
                    onClick={handleLogout}
                    className="flex items-center space-x-2 text-gray-500 dark:text-slate-400 hover:text-gray-900 dark:hover:text-white transition-colors"
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
