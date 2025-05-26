import { io } from 'socket.io-client'

class WebSocketService {
  constructor() {
    this.socket = null
    this.listeners = new Map()
    this.isConnected = false
  }

  connect(url = 'ws://172.22.206.209:8000') {
    if (this.socket?.connected) {
      return this.socket
    }

    this.socket = io(url, {
      transports: ['websocket'],
      autoConnect: true,
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
    })

    this.socket.on('connect', () => {
      console.log('WebSocket connected')
      this.isConnected = true
      this.emit('connection_status', { connected: true })
    })

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason)
      this.isConnected = false
      this.emit('connection_status', { connected: false, reason })
    })

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error)
      this.emit('connection_error', { error: error.message })
    })

    // Real-time monitoring events
    this.socket.on('scraping_update', (data) => {
      this.emit('scraping_update', data)
    })

    this.socket.on('session_update', (data) => {
      this.emit('session_update', data)
    })

    this.socket.on('metrics_update', (data) => {
      this.emit('metrics_update', data)
    })

    this.socket.on('error_alert', (data) => {
      this.emit('error_alert', data)
    })

    this.socket.on('orchestrator_update', (data) => {
      this.emit('orchestrator_update', data)
    })

    return this.socket
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
      this.isConnected = false
    }
  }

  // Event listener management
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event).add(callback)

    // Return unsubscribe function
    return () => {
      const eventListeners = this.listeners.get(event)
      if (eventListeners) {
        eventListeners.delete(callback)
        if (eventListeners.size === 0) {
          this.listeners.delete(event)
        }
      }
    }
  }

  off(event, callback) {
    const eventListeners = this.listeners.get(event)
    if (eventListeners) {
      eventListeners.delete(callback)
      if (eventListeners.size === 0) {
        this.listeners.delete(event)
      }
    }
  }

  emit(event, data) {
    const eventListeners = this.listeners.get(event)
    if (eventListeners) {
      eventListeners.forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`Error in WebSocket event listener for ${event}:`, error)
        }
      })
    }
  }

  // Send data to server
  send(event, data) {
    if (this.socket?.connected) {
      this.socket.emit(event, data)
    } else {
      console.warn('WebSocket not connected, cannot send:', event, data)
    }
  }

  // Monitoring-specific methods
  subscribeToSession(sessionId) {
    this.send('subscribe_session', { sessionId })
  }

  unsubscribeFromSession(sessionId) {
    this.send('unsubscribe_session', { sessionId })
  }

  subscribeToMetrics() {
    this.send('subscribe_metrics', {})
  }

  unsubscribeFromMetrics() {
    this.send('unsubscribe_metrics', {})
  }

  requestOrchestratorStatus() {
    this.send('get_orchestrator_status', {})
  }

  getConnectionStatus() {
    return {
      connected: this.isConnected,
      socket: this.socket,
    }
  }
}

// Create singleton instance
const wsService = new WebSocketService()

export default wsService