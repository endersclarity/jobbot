import { useState, useEffect, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import wsService from '../services/websocket'
import { monitoringApi } from '../services/api'

export function useRealTimeMetrics() {
  const [realTimeData, setRealTimeData] = useState(null)
  const [connectionStatus, setConnectionStatus] = useState({ connected: false })

  // Fetch initial metrics data
  const { data: initialMetrics, isLoading, error, refetch } = useQuery({
    queryKey: ['systemMetrics'],
    queryFn: () => monitoringApi.getSystemMetrics(),
    refetchInterval: 30000, // Fallback polling every 30 seconds
    select: (response) => response.data,
  })

  useEffect(() => {
    // For now, simulate connected status without WebSocket
    setConnectionStatus({ connected: true })
    
    // TODO: Re-enable WebSocket when backend supports it
    // wsService.connect()
    
    return () => {
      // Cleanup if needed
    }
  }, [])

  // Merge initial data with real-time updates
  const currentMetrics = realTimeData || initialMetrics || {}

  return {
    metrics: currentMetrics,
    isLoading,
    error,
    refetch,
    connectionStatus,
    isRealTime: connectionStatus.connected && realTimeData !== null,
  }
}

export function useScrapingSession(sessionId) {
  const [sessionData, setSessionData] = useState(null)
  const [updates, setUpdates] = useState([])

  // Fetch initial session data
  const { data: initialSession, isLoading, error } = useQuery({
    queryKey: ['scrapingSession', sessionId],
    queryFn: () => monitoringApi.getSessionDetails(sessionId),
    enabled: !!sessionId,
    select: (response) => response.data,
  })

  useEffect(() => {
    if (!sessionId) return

    // Subscribe to session updates
    wsService.subscribeToSession(sessionId)

    const unsubscribeSession = wsService.on('session_update', (data) => {
      if (data.sessionId === sessionId) {
        setSessionData(prev => ({
          ...prev,
          ...data,
          lastUpdate: new Date().toISOString(),
        }))
        
        // Add to updates log
        setUpdates(prev => [...prev, {
          timestamp: new Date().toISOString(),
          ...data,
        }].slice(-50)) // Keep last 50 updates
      }
    })

    const unsubscribeScraping = wsService.on('scraping_update', (data) => {
      if (data.sessionId === sessionId) {
        setUpdates(prev => [...prev, {
          timestamp: new Date().toISOString(),
          type: 'scraping_progress',
          ...data,
        }].slice(-50))
      }
    })

    return () => {
      unsubscribeSession()
      unsubscribeScraping()
      wsService.unsubscribeFromSession(sessionId)
    }
  }, [sessionId])

  const currentSession = sessionData || initialSession || {}

  return {
    session: currentSession,
    updates,
    isLoading,
    error,
  }
}

export function useOrchestratorStatus() {
  const [orchestratorData, setOrchestratorData] = useState(null)

  // Fetch initial orchestrator status
  const { data: initialStatus, isLoading, error, refetch } = useQuery({
    queryKey: ['orchestratorStatus'],
    queryFn: () => monitoringApi.getOrchestratorStatus(),
    refetchInterval: 10000, // Poll every 10 seconds
    select: (response) => response.data,
  })

  useEffect(() => {
    // Subscribe to orchestrator updates
    const unsubscribeOrchestrator = wsService.on('orchestrator_update', (data) => {
      setOrchestratorData(prev => ({
        ...prev,
        ...data,
        lastUpdate: new Date().toISOString(),
      }))
    })

    // Request current status when connected
    const unsubscribeConnection = wsService.on('connection_status', (status) => {
      if (status.connected) {
        wsService.requestOrchestratorStatus()
      }
    })

    return () => {
      unsubscribeOrchestrator()
      unsubscribeConnection()
    }
  }, [])

  const currentStatus = orchestratorData || initialStatus || {}

  return {
    status: currentStatus,
    isLoading,
    error,
    refetch,
    isRealTime: orchestratorData !== null,
  }
}