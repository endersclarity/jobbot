import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
  Activity, 
  Database, 
  Globe, 
  TrendingUp, 
  AlertTriangle,
  CheckCircle,
  Clock,
  Users
} from 'lucide-react'
import { useRealTimeMetrics, useOrchestratorStatus } from '../hooks/useRealTimeMetrics'
import { monitoringApi, jobsApi } from '../services/api'
import MetricCard from './MetricCard'
import SessionsList from './SessionsList'
import PerformanceChart from './PerformanceChart'
import SystemStatus from './SystemStatus'

function Dashboard() {
  const { metrics, isLoading: metricsLoading, connectionStatus, isRealTime } = useRealTimeMetrics()
  const { status: orchestratorStatus, isLoading: orchestratorLoading } = useOrchestratorStatus()

  // Fetch additional dashboard data
  const { data: jobStats, isLoading: jobStatsLoading, error: jobStatsError } = useQuery({
    queryKey: ['jobStats'],
    queryFn: () => jobsApi.getJobStats(),
    select: (response) => response.data,
    refetchInterval: 30000,
    retry: 3,
    retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000)
  })

  const { data: recentSessions, isLoading: sessionsLoading, error: sessionsError } = useQuery({
    queryKey: ['recentSessions'],
    queryFn: () => monitoringApi.getScrapingSessions({ limit: 5, sort: 'created_at:desc' }),
    select: (response) => response.data,
    refetchInterval: 10000,
    retry: 3,
    retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000)
  })

  const { data: siteStats, isLoading: siteStatsLoading, error: siteStatsError } = useQuery({
    queryKey: ['siteStats'],
    queryFn: () => monitoringApi.getSiteStats(),
    select: (response) => response.data,
    refetchInterval: 30000,
    retry: 3,
    retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000)
  })

  // Check for critical errors first
  if (jobStatsError || sessionsError || siteStatsError) {
    return (
      <div className="error-state">
        <AlertTriangle className="h-8 w-8 text-red-500 mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Dashboard Error</h3>
        <p className="text-gray-600 mb-4">
          Failed to load dashboard data. Please check your connection and try again.
        </p>
        <button 
          className="btn btn-primary"
          onClick={() => window.location.reload()}
        >
          Retry
        </button>
      </div>
    )
  }

  if (metricsLoading || jobStatsLoading || orchestratorLoading || siteStatsLoading) {
    return (
      <div className="loading">
        <Activity className="h-6 w-6 animate-spin mr-2" />
        Loading dashboard...
      </div>
    )
  }

  const systemMetrics = metrics || {}
  const jobMetrics = jobStats || {}
  const sessionMetrics = recentSessions || {}
  const orchestrator = orchestratorStatus || {}

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">JobBot Dashboard</h1>
          <p className="text-gray-600">
            Real-time monitoring for enterprise scraping operations
            {isRealTime && (
              <span className="ml-2 inline-flex items-center text-green-600">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse mr-1" />
                Live
              </span>
            )}
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <button 
            className="btn btn-primary"
            onClick={() => window.location.href = '/orchestrator/start'}
          >
            Start Multi-Site Scraping
          </button>
        </div>
      </div>

      {/* System Status Overview */}
      <SystemStatus 
        connectionStatus={connectionStatus}
        orchestratorStatus={orchestrator}
        systemMetrics={systemMetrics}
      />

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Jobs"
          value={jobMetrics.total_jobs || 0}
          change={jobMetrics.jobs_today || 0}
          changeLabel="today"
          icon={Database}
          color="blue"
        />
        
        <MetricCard
          title="Active Sessions"
          value={systemMetrics.active_sessions || 0}
          change={systemMetrics.sessions_today || 0}
          changeLabel="today"
          icon={Activity}
          color="green"
        />
        
        <MetricCard
          title="Sites Monitored"
          value={3}
          subtitle="Indeed, LinkedIn, Glassdoor"
          icon={Globe}
          color="purple"
        />
        
        <MetricCard
          title="Success Rate"
          value={`${Math.round((systemMetrics.success_rate || 0.85) * 100)}%`}
          change={systemMetrics.success_rate_change || 0}
          changeLabel="vs yesterday"
          icon={TrendingUp}
          color="orange"
        />
      </div>

      {/* Performance and Sessions Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance Chart */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Performance Metrics</h3>
          </div>
          <div className="card-content">
            <PerformanceChart />
          </div>
        </div>

        {/* Recent Sessions */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Recent Sessions</h3>
          </div>
          <div className="card-content">
            {sessionsLoading ? (
              <div className="loading">Loading sessions...</div>
            ) : (
              <SessionsList 
                sessions={sessionMetrics.sessions || []} 
                showDetails={false}
              />
            )}
          </div>
        </div>
      </div>

      {/* Site Statistics */}
      {!siteStatsLoading && siteStats && (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Site Performance</h3>
          </div>
          <div className="card-content">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {Object.entries(siteStats || {}).map(([site, stats]) => (
                <div key={site} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium capitalize">{site}</h4>
                    <span className={`status-badge ${
                      stats.status === 'active' ? 'status-success' : 
                      stats.status === 'error' ? 'status-error' : 'status-warning'
                    }`}>
                      {stats.status}
                    </span>
                  </div>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Jobs Scraped:</span>
                      <span className="font-medium">{stats.jobs_scraped || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Success Rate:</span>
                      <span className="font-medium">{Math.round((stats.success_rate || 0) * 100)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Last Updated:</span>
                      <span className="font-medium">
                        {stats.last_update ? new Date(stats.last_update).toLocaleTimeString() : 'Never'}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Quick Actions</h3>
        </div>
        <div className="card-content">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="btn btn-secondary flex items-center justify-center space-x-2 p-4">
              <Activity className="h-5 w-5" />
              <span>Start New Session</span>
            </button>
            <button className="btn btn-secondary flex items-center justify-center space-x-2 p-4">
              <Database className="h-5 w-5" />
              <span>View All Jobs</span>
            </button>
            <button className="btn btn-secondary flex items-center justify-center space-x-2 p-4">
              <AlertTriangle className="h-5 w-5" />
              <span>Check Errors</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard