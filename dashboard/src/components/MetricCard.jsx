import React from 'react'
import { TrendingUp, TrendingDown } from 'lucide-react'

function MetricCard({ 
  title, 
  value, 
  subtitle, 
  change, 
  changeLabel, 
  icon: Icon, 
  color = 'blue',
  trend = null 
}) {
  const colorClasses = {
    blue: 'text-blue-600 bg-blue-50',
    green: 'text-green-600 bg-green-50',
    purple: 'text-purple-600 bg-purple-50',
    orange: 'text-orange-600 bg-orange-50',
    red: 'text-red-600 bg-red-50',
  }

  const getTrendIcon = () => {
    if (trend === null && change === undefined) return null
    
    const isPositive = trend === 'up' || (trend === null && change > 0)
    const TrendIcon = isPositive ? TrendingUp : TrendingDown
    const trendColor = isPositive ? 'text-green-600' : 'text-red-600'
    
    return <TrendIcon className={`h-4 w-4 ${trendColor}`} />
  }

  const formatValue = (val) => {
    if (typeof val === 'number' && val >= 1000) {
      if (val >= 1000000) {
        return `${(val / 1000000).toFixed(1)}M`
      }
      return `${(val / 1000).toFixed(1)}K`
    }
    return val
  }

  return (
    <div className="card">
      <div className="card-content">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
            <div className="flex items-baseline space-x-2">
              <p className="text-2xl font-bold text-gray-900">
                {formatValue(value)}
              </p>
              {getTrendIcon()}
            </div>
            
            {subtitle && (
              <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
            )}
            
            {(change !== undefined && changeLabel) && (
              <div className="flex items-center mt-2 text-sm">
                <span className={`font-medium ${
                  change > 0 ? 'text-green-600' : 
                  change < 0 ? 'text-red-600' : 'text-gray-600'
                }`}>
                  {change > 0 ? '+' : ''}{formatValue(change)}
                </span>
                <span className="text-gray-500 ml-1">{changeLabel}</span>
              </div>
            )}
          </div>
          
          {Icon && (
            <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
              <Icon className="h-6 w-6" />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default MetricCard