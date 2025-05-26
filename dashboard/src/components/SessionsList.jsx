import React from 'react'
import { format } from 'date-fns'
import { 
  Clock, 
  CheckCircle, 
  XCircle, 
  Activity,
  Database,
  Globe
} from 'lucide-react'

function SessionsList({ sessions = [], showDetails = true }) {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-600" />
      case 'running':
        return <Activity className="h-4 w-4 text-blue-600 animate-pulse" />
      default:
        return <Clock className="h-4 w-4 text-gray-400" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'status-success'
      case 'failed':
        return 'status-error'
      case 'running':
        return 'status-info'
      default:
        return 'status-warning'
    }
  }

  const getSiteIcon = (site) => {
    switch (site?.toLowerCase()) {
      case 'indeed':
        return <Database className="h-4 w-4 text-blue-600" />
      case 'linkedin':
        return <Globe className="h-4 w-4 text-blue-700" />
      case 'glassdoor':
        return <Activity className="h-4 w-4 text-green-600" />
      default:
        return <Globe className="h-4 w-4 text-gray-600" />
    }
  }

  const formatDuration = (start, end) => {
    if (!start) return 'N/A'
    const startTime = new Date(start)
    const endTime = end ? new Date(end) : new Date()
    const durationMs = endTime - startTime
    const minutes = Math.floor(durationMs / 60000)
    const seconds = Math.floor((durationMs % 60000) / 1000)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  if (!sessions || sessions.length === 0) {
    return (
      <div className="text-center py-6 text-gray-500">
        <Activity className="h-8 w-8 mx-auto mb-2 opacity-50" />
        <p>No sessions found</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {sessions.map((session) => (
        <div key={session.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-3">
              {getSiteIcon(session.site)}
              <div>
                <h4 className="font-medium text-sm">
                  {session.search_term || session.job_title || 'Scraping Session'}
                </h4>
                <p className="text-xs text-gray-600">
                  {session.site ? session.site.charAt(0).toUpperCase() + session.site.slice(1) : 'Multi-site'}
                  {session.location && ` • ${session.location}`}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              {getStatusIcon(session.status)}
              <span className={`status-badge ${getStatusColor(session.status)}`}>
                {session.status}
              </span>
            </div>
          </div>

          {showDetails && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-3 pt-3 border-t text-sm">
              <div>
                <p className="text-gray-600">Jobs Found</p>
                <p className="font-medium">{session.jobs_found || 0}</p>
              </div>
              <div>
                <p className="text-gray-600">Duration</p>
                <p className="font-medium">
                  {formatDuration(session.started_at, session.completed_at)}
                </p>
              </div>
              <div>
                <p className="text-gray-600">Success Rate</p>
                <p className="font-medium">
                  {session.success_rate ? `${Math.round(session.success_rate * 100)}%` : 'N/A'}
                </p>
              </div>
              <div>
                <p className="text-gray-600">Started</p>
                <p className="font-medium">
                  {session.started_at ? 
                    format(new Date(session.started_at), 'HH:mm') : 
                    'N/A'
                  }
                </p>
              </div>
            </div>
          )}

          {!showDetails && (
            <div className="flex items-center justify-between mt-2 text-sm">
              <span className="text-gray-600">
                {session.jobs_found || 0} jobs • {formatDuration(session.started_at, session.completed_at)}
              </span>
              <span className="text-gray-500">
                {session.started_at ? 
                  format(new Date(session.started_at), 'HH:mm') : 
                  'N/A'
                }
              </span>
            </div>
          )}

          {session.error_message && (
            <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
              <strong>Error:</strong> {session.error_message}
            </div>
          )}

          {session.status === 'running' && session.progress && (
            <div className="mt-2">
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-gray-600">Progress</span>
                <span className="font-medium">{Math.round(session.progress * 100)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${session.progress * 100}%` }}
                />
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

export default SessionsList