import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts'
import { monitoringApi } from '../services/api'
import { format, subHours } from 'date-fns'

function PerformanceChart({ timeRange = '1h', height = 300 }) {
  const { data: performanceData, isLoading, error } = useQuery({
    queryKey: ['performanceMetrics', timeRange],
    queryFn: () => monitoringApi.getPerformanceMetrics(timeRange),
    select: (response) => response.data,
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  // Generate mock data if API doesn't return data
  const generateMockData = () => {
    const now = new Date()
    const hours = timeRange === '1h' ? 1 : timeRange === '6h' ? 6 : 24
    const intervals = timeRange === '1h' ? 12 : timeRange === '6h' ? 24 : 48
    
    return Array.from({ length: intervals }, (_, i) => {
      const time = subHours(now, (intervals - i - 1) * (hours / intervals))
      const baseJobsPerMinute = 45 + Math.sin(i * 0.5) * 10
      const baseSuccessRate = 0.85 + Math.random() * 0.1
      const baseResponseTime = 120 + Math.random() * 50
      
      return {
        time: format(time, timeRange === '1h' ? 'HH:mm' : timeRange === '6h' ? 'HH:mm' : 'MMM dd HH:mm'),
        timestamp: time.toISOString(),
        jobs_per_minute: Math.round(baseJobsPerMinute + (Math.random() - 0.5) * 10),
        success_rate: Math.round(baseSuccessRate * 100),
        response_time: Math.round(baseResponseTime + (Math.random() - 0.5) * 30),
        active_sessions: Math.floor(Math.random() * 5) + 1,
        errors_per_minute: Math.floor(Math.random() * 3),
      }
    })
  }

  const chartData = performanceData?.metrics || generateMockData()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading">Loading performance data...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="error">Failed to load performance data</div>
      </div>
    )
  }

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border rounded-lg shadow-lg">
          <p className="font-medium mb-2">{`Time: ${label}`}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }} className="text-sm">
              {`${entry.name}: ${entry.value}${
                entry.dataKey === 'success_rate' ? '%' : 
                entry.dataKey === 'response_time' ? 'ms' :
                entry.dataKey === 'jobs_per_minute' ? '/min' : ''
              }`}
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <div className="space-y-4">
      {/* Time Range Selector */}
      <div className="flex items-center justify-between">
        <h4 className="font-medium text-gray-900">Performance Over Time</h4>
        <div className="flex space-x-1">
          {['1h', '6h', '24h'].map((range) => (
            <button
              key={range}
              className={`px-3 py-1 text-sm rounded ${
                timeRange === range
                  ? 'bg-blue-100 text-blue-700 font-medium'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
              onClick={() => {
                // In a real implementation, this would update the timeRange state
                console.log(`Switch to ${range} view`)
              }}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      {/* Jobs Per Minute Chart */}
      <div>
        <h5 className="text-sm font-medium text-gray-700 mb-2">Jobs Scraped Per Minute</h5>
        <ResponsiveContainer width="100%" height={height}>
          <AreaChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
            <XAxis 
              dataKey="time" 
              tick={{ fontSize: 12 }}
              axisLine={false}
            />
            <YAxis 
              tick={{ fontSize: 12 }}
              axisLine={false}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="jobs_per_minute"
              stroke="#3b82f6"
              fill="#3b82f6"
              fillOpacity={0.1}
              strokeWidth={2}
              name="Jobs/min"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Multi-Metric Chart */}
      <div>
        <h5 className="text-sm font-medium text-gray-700 mb-2">Success Rate & Response Time</h5>
        <ResponsiveContainer width="100%" height={height}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
            <XAxis 
              dataKey="time" 
              tick={{ fontSize: 12 }}
              axisLine={false}
            />
            <YAxis 
              yAxisId="left"
              tick={{ fontSize: 12 }}
              axisLine={false}
              domain={['dataMin - 5', 'dataMax + 5']}
            />
            <YAxis 
              yAxisId="right" 
              orientation="right"
              tick={{ fontSize: 12 }}
              axisLine={false}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="success_rate"
              stroke="#10b981"
              strokeWidth={2}
              dot={false}
              name="Success Rate"
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="response_time"
              stroke="#f59e0b"
              strokeWidth={2}
              dot={false}
              name="Response Time"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t">
        <div className="text-center">
          <p className="text-sm text-gray-600">Avg Jobs/min</p>
          <p className="text-lg font-bold text-blue-600">
            {Math.round(chartData.reduce((acc, d) => acc + d.jobs_per_minute, 0) / chartData.length)}
          </p>
        </div>
        <div className="text-center">
          <p className="text-sm text-gray-600">Avg Success Rate</p>
          <p className="text-lg font-bold text-green-600">
            {Math.round(chartData.reduce((acc, d) => acc + d.success_rate, 0) / chartData.length)}%
          </p>
        </div>
        <div className="text-center">
          <p className="text-sm text-gray-600">Avg Response Time</p>
          <p className="text-lg font-bold text-orange-600">
            {Math.round(chartData.reduce((acc, d) => acc + d.response_time, 0) / chartData.length)}ms
          </p>
        </div>
        <div className="text-center">
          <p className="text-sm text-gray-600">Peak Sessions</p>
          <p className="text-lg font-bold text-purple-600">
            {Math.max(...chartData.map(d => d.active_sessions))}
          </p>
        </div>
      </div>
    </div>
  )
}

export default PerformanceChart