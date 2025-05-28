import { Link, useLocation } from 'react-router-dom'
import { 
  Activity, 
  Database, 
  BarChart3, 
  Brain,
  Settings, 
  Zap, 
  Wifi, 
  WifiOff,
  Building,
  Target,
  TrendingUp,
  Mail,
  Search
} from 'lucide-react'
import { useRealTimeMetrics } from '../hooks/useRealTimeMetrics'

function Layout({ children }) {
  const location = useLocation()
  const { connectionStatus } = useRealTimeMetrics()

  const navigation = [
    { name: 'Dashboard', href: '/', icon: Activity },
    { name: 'Job Scraper', href: '/scrape', icon: Search },
    { name: 'Sessions', href: '/sessions', icon: Database },
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
    { name: 'Advanced Analytics', href: '/advanced-analytics', icon: Brain },
    { name: 'Companies', href: '/companies', icon: Building },
    { name: 'Opportunities', href: '/opportunities', icon: Target },
    { name: 'Market Analysis', href: '/market', icon: TrendingUp },
    { name: 'Outreach', href: '/outreach', icon: Mail },
    { name: 'Settings', href: '/settings', icon: Settings },
  ]

  const isActive = (href) => {
    if (href === '/') {
      return location.pathname === '/'
    }
    return location.pathname.startsWith(href) && location.pathname !== '/'
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <Zap className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">JobBot Dashboard</h1>
                <p className="text-sm text-gray-500">Enterprise Scraping Monitor</p>
              </div>
            </div>

            {/* Connection Status */}
            <div className="flex items-center space-x-2">
              {connectionStatus.connected ? (
                <div className="flex items-center space-x-2 text-green-600">
                  <Wifi className="h-4 w-4" />
                  <span className="text-sm font-medium">Live</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2 text-red-600">
                  <WifiOff className="h-4 w-4" />
                  <span className="text-sm font-medium">Offline</span>
                </div>
              )}
              <div 
                className="status-badge status-info" 
                role="status" 
                aria-label="Current phase indicator"
              >
                Phase 7
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <nav className="w-64 bg-white shadow-sm min-h-[calc(100vh-4rem)]">
          <div className="p-4">
            <ul className="space-y-2">
              {navigation.map((item) => {
                const Icon = item.icon
                return (
                  <li key={item.name}>
                    <Link
                      to={item.href}
                      className={`flex items-center space-x-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                        isActive(item.href)
                          ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                      }`}
                    >
                      <Icon className="h-5 w-5" />
                      <span>{item.name}</span>
                    </Link>
                  </li>
                )
              })}
            </ul>
          </div>

          {/* Status Panel */}
          <div className="p-4 border-t">
            <h3 className="text-sm font-medium text-gray-900 mb-3">System Status</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">WebSocket</span>
                <span className={`status-badge ${connectionStatus.connected ? 'status-success' : 'status-error'}`}>
                  {connectionStatus.connected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">API</span>
                <span className="status-badge status-success">Online</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Database</span>
                <span className="status-badge status-success">Healthy</span>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="flex-1 p-6">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}

export default Layout