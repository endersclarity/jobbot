import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
  Search, 
  Filter, 
  Plus, 
  RefreshCw,
  Download,
  Play,
  Square
} from 'lucide-react'
import { monitoringApi } from '../services/api'
import SessionsList from './SessionsList'
import { useScrapingSession } from '../hooks/useRealTimeMetrics'

function ScrapingSessions() {
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [siteFilter, setSiteFilter] = useState('all')
  const [selectedSession, setSelectedSession] = useState(null)

  const { data: sessions, isLoading, error, refetch } = useQuery({
    queryKey: ['scrapingSessions', { search: searchTerm, status: statusFilter, site: siteFilter }],
    queryFn: () => monitoringApi.getScrapingSessions({
      search: searchTerm || undefined,
      status: statusFilter !== 'all' ? statusFilter : undefined,
      site: siteFilter !== 'all' ? siteFilter : undefined,
      limit: 50,
      sort: 'created_at:desc'
    }),
    select: (response) => response.data,
    refetchInterval: 10000, // Refresh every 10 seconds
  })

  const { session: sessionDetails, updates } = useScrapingSession(selectedSession)

  const filteredSessions = sessions?.sessions || []

  const handleStartNewSession = () => {
    // In a real implementation, this would open a modal or navigate to a form
    console.log('Start new scraping session')
  }

  const handleExportSessions = () => {
    // Export sessions data as CSV or JSON
    const csvData = filteredSessions.map(session => ({
      id: session.id,
      site: session.site,
      search_term: session.search_term,
      location: session.location,
      status: session.status,
      jobs_found: session.jobs_found,
      started_at: session.started_at,
      completed_at: session.completed_at,
    }))
    
    const csv = [
      Object.keys(csvData[0]).join(','),
      ...csvData.map(row => Object.values(row).join(','))
    ].join('\n')
    
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `scraping_sessions_${new Date().toISOString().split('T')[0]}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  if (error) {
    return (
      <div className="error">
        Failed to load scraping sessions: {error.message}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Scraping Sessions</h1>
          <p className="text-gray-600">Monitor and manage all scraping operations</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <button 
            onClick={handleExportSessions}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <Download className="h-4 w-4" />
            <span>Export</span>
          </button>
          <button 
            onClick={refetch}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Refresh</span>
          </button>
          <button 
            onClick={handleStartNewSession}
            className="btn btn-primary flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>New Session</span>
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="card-content">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search sessions..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Statuses</option>
              <option value="running">Running</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
              <option value="pending">Pending</option>
            </select>

            {/* Site Filter */}
            <select
              value={siteFilter}
              onChange={(e) => setSiteFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Sites</option>
              <option value="indeed">Indeed</option>
              <option value="linkedin">LinkedIn</option>
              <option value="glassdoor">Glassdoor</option>
              <option value="multi-site">Multi-Site</option>
            </select>

            {/* Quick Actions */}
            <div className="flex space-x-2">
              <button className="btn btn-secondary flex-1 flex items-center justify-center space-x-1">
                <Play className="h-4 w-4" />
                <span>Start</span>
              </button>
              <button className="btn btn-secondary flex-1 flex items-center justify-center space-x-1">
                <Square className="h-4 w-4" />
                <span>Stop</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Sessions List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sessions List */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">
              Sessions ({filteredSessions.length})
              {isLoading && (
                <RefreshCw className="inline h-4 w-4 ml-2 animate-spin" />
              )}
            </h3>
          </div>
          <div className="card-content">
            {isLoading ? (
              <div className="loading">Loading sessions...</div>
            ) : (
              <div className="max-h-96 overflow-y-auto">
                <SessionsList 
                  sessions={filteredSessions} 
                  showDetails={true}
                  onSessionSelect={setSelectedSession}
                  selectedSession={selectedSession}
                />
              </div>
            )}
          </div>
        </div>

        {/* Session Details */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">
              {selectedSession ? 'Session Details' : 'Select a Session'}
            </h3>
          </div>
          <div className="card-content">
            {selectedSession ? (
              <div className="space-y-4">
                {/* Session Info */}
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-600">Session ID</p>
                    <p className="font-medium">{sessionDetails.id}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Site</p>
                    <p className="font-medium capitalize">{sessionDetails.site}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Search Term</p>
                    <p className="font-medium">{sessionDetails.search_term || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Location</p>
                    <p className="font-medium">{sessionDetails.location || 'N/A'}</p>
                  </div>
                </div>

                {/* Real-time Updates */}
                {updates.length > 0 && (
                  <div>
                    <h4 className="font-medium mb-2">Recent Updates</h4>
                    <div className="max-h-40 overflow-y-auto space-y-2">
                      {updates.slice(0, 10).map((update, index) => (
                        <div key={index} className="text-xs p-2 bg-gray-50 rounded">
                          <div className="flex justify-between items-start">
                            <span className="font-medium">{update.type || 'Update'}</span>
                            <span className="text-gray-500">
                              {new Date(update.timestamp).toLocaleTimeString()}
                            </span>
                          </div>
                          {update.message && (
                            <p className="text-gray-600 mt-1">{update.message}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Session Progress */}
                {sessionDetails.status === 'running' && sessionDetails.progress && (
                  <div>
                    <h4 className="font-medium mb-2">Progress</h4>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div 
                        className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                        style={{ width: `${sessionDetails.progress * 100}%` }}
                      />
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      {Math.round(sessionDetails.progress * 100)}% complete
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Filter className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>Select a session to view details</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="card-content metric-card">
            <div className="metric-value text-blue-600">
              {filteredSessions.filter(s => s.status === 'running').length}
            </div>
            <div className="metric-label">Active Sessions</div>
          </div>
        </div>
        <div className="card">
          <div className="card-content metric-card">
            <div className="metric-value text-green-600">
              {filteredSessions.filter(s => s.status === 'completed').length}
            </div>
            <div className="metric-label">Completed Today</div>
          </div>
        </div>
        <div className="card">
          <div className="card-content metric-card">
            <div className="metric-value text-orange-600">
              {filteredSessions.reduce((acc, s) => acc + (s.jobs_found || 0), 0)}
            </div>
            <div className="metric-label">Total Jobs Found</div>
          </div>
        </div>
        <div className="card">
          <div className="card-content metric-card">
            <div className="metric-value text-purple-600">
              {Math.round(
                (filteredSessions.filter(s => s.status === 'completed').length / 
                 Math.max(filteredSessions.length, 1)) * 100
              )}%
            </div>
            <div className="metric-label">Success Rate</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ScrapingSessions