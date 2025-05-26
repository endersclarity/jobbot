import React from 'react'
import { 
  CheckCircle, 
  AlertTriangle, 
  XCircle, 
  Activity, 
  Database, 
  Globe,
  Wifi,
  WifiOff
} from 'lucide-react'

function SystemStatus({ connectionStatus, orchestratorStatus, systemMetrics }) {
  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
      case 'connected':
      case 'active':
      case 'running':
        return 'text-green-600 bg-green-50'
      case 'warning':
      case 'degraded':
        return 'text-yellow-600 bg-yellow-50'
      case 'error':
      case 'failed':
      case 'disconnected':
        return 'text-red-600 bg-red-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
      case 'connected':
      case 'active':
      case 'running':
        return <CheckCircle className="h-5 w-5" />
      case 'warning':
      case 'degraded':
        return <AlertTriangle className="h-5 w-5" />
      case 'error':
      case 'failed':
      case 'disconnected':
        return <XCircle className="h-5 w-5" />
      default:
        return <Activity className="h-5 w-5" />
    }
  }

  const systemComponents = [
    {
      name: 'WebSocket Connection',
      status: connectionStatus.connected ? 'connected' : 'disconnected',
      icon: connectionStatus.connected ? <Wifi className="h-5 w-5" /> : <WifiOff className="h-5 w-5" />,
      details: connectionStatus.connected ? 'Real-time updates active' : 'Using polling fallback',
    },
    {
      name: 'Multi-Site Orchestrator',
      status: orchestratorStatus.status || 'unknown',
      icon: <Globe className="h-5 w-5" />,
      details: orchestratorStatus.active_scrapers ? 
        `${orchestratorStatus.active_scrapers} scrapers active` : 
        'No active scrapers',
    },
    {
      name: 'Database',
      status: systemMetrics.database_status || 'healthy',
      icon: <Database className="h-5 w-5" />,
      details: systemMetrics.total_jobs ? 
        `${systemMetrics.total_jobs} jobs stored` : 
        'Database operational',
    },
    {
      name: 'API Server',
      status: 'healthy',
      icon: <Activity className="h-5 w-5" />,
      details: `Response time: ${systemMetrics.avg_response_time || '<100'}ms`,
    },
  ]

  const overallStatus = systemComponents.every(c => 
    ['healthy', 'connected', 'active', 'running'].includes(c.status)
  ) ? 'healthy' : 
    systemComponents.some(c => 
      ['error', 'failed', 'disconnected'].includes(c.status)
    ) ? 'error' : 'warning'

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center justify-between">
          <h3 className="card-title">System Status</h3>
          <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(overallStatus)}`}>
            {getStatusIcon(overallStatus)}
            <span className="capitalize">{overallStatus}</span>
          </div>
        </div>
      </div>
      <div className="card-content">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {systemComponents.map((component) => (
            <div key={component.name} className="border rounded-lg p-4">
              <div className="flex items-center space-x-3 mb-2">
                <div className={`p-2 rounded-lg ${getStatusColor(component.status)}`}>
                  {component.icon}
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-sm">{component.name}</h4>
                  <p className={`text-xs font-medium capitalize ${getStatusColor(component.status).split(' ')[0]}`}>
                    {component.status.replace('_', ' ')}
                  </p>
                </div>
              </div>
              <p className="text-xs text-gray-600">{component.details}</p>
            </div>
          ))}
        </div>

        {/* System Metrics Summary */}
        {systemMetrics && Object.keys(systemMetrics).length > 0 && (
          <div className="mt-6 pt-4 border-t">
            <h4 className="text-sm font-medium text-gray-900 mb-3">Performance Metrics</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <p className="text-lg font-bold text-gray-900">
                  {systemMetrics.cpu_usage ? `${Math.round(systemMetrics.cpu_usage)}%` : 'N/A'}
                </p>
                <p className="text-xs text-gray-600">CPU Usage</p>
              </div>
              <div className="text-center">
                <p className="text-lg font-bold text-gray-900">
                  {systemMetrics.memory_usage ? `${Math.round(systemMetrics.memory_usage)}%` : 'N/A'}
                </p>
                <p className="text-xs text-gray-600">Memory Usage</p>
              </div>
              <div className="text-center">
                <p className="text-lg font-bold text-gray-900">
                  {systemMetrics.active_connections || 0}
                </p>
                <p className="text-xs text-gray-600">Active Connections</p>
              </div>
              <div className="text-center">
                <p className="text-lg font-bold text-gray-900">
                  {systemMetrics.requests_per_minute || 0}
                </p>
                <p className="text-xs text-gray-600">Requests/min</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default SystemStatus