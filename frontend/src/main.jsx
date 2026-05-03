import React, { Suspense, lazy, useEffect } from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './index.css'
import LoadingSkeleton from './components/LoadingSkeleton'
import { useThemeStore } from './store/themeStore'

// Lazy load pages
const Dashboard = lazy(() => import('./pages/Dashboard'))
const RepositoryDetail = lazy(() => import('./pages/RepositoryDetail'))
const TestDetail = lazy(() => import('./pages/TestDetail'))
const Login = lazy(() => import('./pages/Login'))
const Repositories = lazy(() => import('./pages/Repositories'))

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000,
    },
  },
})

function ThemeManager() {
  const theme = useThemeStore((s) => s.theme)

  useEffect(() => {
    const html = document.documentElement
    if (theme === 'dark') {
      html.classList.add('dark')
    } else if (theme === 'light') {
      html.classList.remove('dark')
    } else {
      const mq = window.matchMedia('(prefers-color-scheme: dark)')
      const apply = (e) => {
        if (e.matches) html.classList.add('dark')
        else html.classList.remove('dark')
      }
      apply(mq)
      mq.addEventListener('change', apply)
      return () => mq.removeEventListener('change', apply)
    }
  }, [theme])

  return null
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeManager />
      <BrowserRouter>
        <Suspense fallback={<LoadingSkeleton />}>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Navigate to="/" replace />} />
            <Route path="/repo/:repoId" element={<RepositoryDetail />} />
            <Route path="/test/:testId" element={<TestDetail />} />
            <Route path="/repositories" element={<Repositories />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)

// Made with Bob
