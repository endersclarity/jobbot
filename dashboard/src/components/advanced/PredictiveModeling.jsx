import React, { useState, useEffect, useMemo } from 'react'
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, 
  Legend, ResponsiveContainer, ScatterChart, Scatter, Area, AreaChart
} from 'recharts'
import { Brain, TrendingUp, AlertTriangle, Target, Calendar } from 'lucide-react'

const PredictiveModeling = ({ data }) => {
  const [selectedModel, setSelectedModel] = useState('revenue')
  const [confidence, setConfidence] = useState(85)
  const [predictions, setPredictions] = useState(null)
  const [loading, setLoading] = useState(false)

  // Simple linear regression for predictions
  const generatePredictions = (historicalData, type) => {
    if (!historicalData || historicalData.length === 0) return []

    const n = historicalData.length
    const xValues = historicalData.map((_, index) => index)
    const yValues = historicalData.map(item => {
      switch (type) {
        case 'revenue': return item.revenue
        case 'leads': return item.leads
        case 'deals': return item.deals
        default: return item.revenue
      }
    })

    // Calculate linear regression
    const sumX = xValues.reduce((sum, x) => sum + x, 0)
    const sumY = yValues.reduce((sum, y) => sum + y, 0)
    const sumXY = xValues.reduce((sum, x, i) => sum + x * yValues[i], 0)
    const sumXX = xValues.reduce((sum, x) => sum + x * x, 0)

    const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX)
    const intercept = (sumY - slope * sumX) / n

    // Generate future predictions (next 6 months)
    const futureMonths = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    const predictions = []

    // Add historical data
    historicalData.forEach((item, index) => {
      predictions.push({
        ...item,
        predicted: Math.round(slope * index + intercept),
        type: 'historical'
      })
    })

    // Add future predictions
    futureMonths.forEach((month, index) => {
      const x = n + index
      const predicted = Math.round(slope * x + intercept)
      const variance = Math.random() * 0.1 - 0.05 // ±5% variance
      
      predictions.push({
        month,
        [type]: null,
        predicted: Math.round(predicted * (1 + variance)),
        upperBound: Math.round(predicted * 1.15),
        lowerBound: Math.round(predicted * 0.85),
        type: 'prediction'
      })
    })

    return predictions
  }

  useEffect(() => {
    if (data?.revenueTimeline) {
      setLoading(true)
      
      // Simulate ML model processing time
      setTimeout(() => {
        const revenueData = generatePredictions(data.revenueTimeline, 'revenue')
        const leadsData = generatePredictions(data.revenueTimeline, 'leads')
        const dealsData = generatePredictions(data.revenueTimeline, 'deals')

        setPredictions({
          revenue: revenueData,
          leads: leadsData,
          deals: dealsData
        })
        setLoading(false)
      }, 1500)
    }
  }, [data])

  const currentPredictions = predictions?.[selectedModel] || []
  
  const nextMonthPrediction = useMemo(() => {
    if (!currentPredictions.length) return null
    
    const futureData = currentPredictions.filter(item => item.type === 'prediction')
    if (!futureData.length) return null
    
    return futureData[0]
  }, [currentPredictions])

  const modelAccuracy = useMemo(() => {
    if (!currentPredictions.length) return null

    const historical = currentPredictions.filter(item => item.type === 'historical')
    if (historical.length === 0) return null

    const errors = historical.map(item => {
      const actual = item[selectedModel]
      const predicted = item.predicted
      return Math.abs((actual - predicted) / actual)
    })

    const mape = errors.reduce((sum, error) => sum + error, 0) / errors.length
    return Math.max(0, Math.min(100, (1 - mape) * 100))
  }, [currentPredictions, selectedModel])

  const insights = useMemo(() => {
    if (!nextMonthPrediction) return []

    const insights = []
    const growth = ((nextMonthPrediction.predicted - (currentPredictions[currentPredictions.length - 7]?.[selectedModel] || 0)) / (currentPredictions[currentPredictions.length - 7]?.[selectedModel] || 1)) * 100

    if (growth > 10) {
      insights.push({
        type: 'positive',
        message: `Strong ${selectedModel} growth predicted (+${growth.toFixed(1)}%)`
      })
    } else if (growth < -5) {
      insights.push({
        type: 'warning',
        message: `Declining ${selectedModel} trend detected (${growth.toFixed(1)}%)`
      })
    }

    if (modelAccuracy > 90) {
      insights.push({
        type: 'info',
        message: `High model confidence (${modelAccuracy.toFixed(1)}% accuracy)`
      })
    } else if (modelAccuracy < 70) {
      insights.push({
        type: 'warning',
        message: `Model accuracy needs improvement (${modelAccuracy.toFixed(1)}%)`
      })
    }

    return insights
  }, [nextMonthPrediction, currentPredictions, selectedModel, modelAccuracy])

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <div className="flex items-center mb-4">
          <Brain className="h-6 w-6 text-purple-600 mr-2" />
          <h2 className="text-xl font-semibold text-gray-900">Predictive Modeling</h2>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Training ML models...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <Brain className="h-6 w-6 text-purple-600 mr-2" />
          <h2 className="text-xl font-semibold text-gray-900">Predictive Modeling</h2>
        </div>
        <div className="flex gap-4">
          <select 
            value={selectedModel} 
            onChange={(e) => setSelectedModel(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
          >
            <option value="revenue">Revenue Forecast</option>
            <option value="leads">Lead Generation</option>
            <option value="deals">Deal Pipeline</option>
          </select>
        </div>
      </div>

      {/* Model Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-purple-50 rounded-lg p-4">
          <div className="flex items-center">
            <Target className="h-5 w-5 text-purple-600 mr-2" />
            <span className="text-sm font-medium text-purple-900">Model Accuracy</span>
          </div>
          <p className="text-2xl font-bold text-purple-900 mt-1">
            {modelAccuracy ? `${modelAccuracy.toFixed(1)}%` : '...'}
          </p>
        </div>
        
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="flex items-center">
            <Calendar className="h-5 w-5 text-blue-600 mr-2" />
            <span className="text-sm font-medium text-blue-900">Next Month Prediction</span>
          </div>
          <p className="text-2xl font-bold text-blue-900 mt-1">
            {nextMonthPrediction ? 
              (selectedModel === 'revenue' ? 
                new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0 }).format(nextMonthPrediction.predicted) :
                new Intl.NumberFormat('en-US').format(nextMonthPrediction.predicted)
              ) : '...'
            }
          </p>
        </div>
        
        <div className="bg-green-50 rounded-lg p-4">
          <div className="flex items-center">
            <TrendingUp className="h-5 w-5 text-green-600 mr-2" />
            <span className="text-sm font-medium text-green-900">Confidence Interval</span>
          </div>
          <p className="text-2xl font-bold text-green-900 mt-1">{confidence}%</p>
        </div>
      </div>

      {/* Prediction Chart */}
      <div className="mb-6">
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={currentPredictions}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip 
              formatter={(value, name) => [
                selectedModel === 'revenue' && value ? 
                  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0 }).format(value) :
                  value,
                name === selectedModel ? 'Actual' : 
                name === 'predicted' ? 'Predicted' :
                name === 'upperBound' ? 'Upper Bound' : 'Lower Bound'
              ]}
            />
            <Legend />
            
            {/* Historical actual data */}
            <Area
              type="monotone"
              dataKey={selectedModel}
              stroke="#8884d8"
              fill="#8884d8"
              fillOpacity={0.3}
              connectNulls={false}
              name="Actual"
            />
            
            {/* Predicted data */}
            <Area
              type="monotone"
              dataKey="predicted"
              stroke="#ff7300"
              fill="#ff7300"
              fillOpacity={0.2}
              strokeDasharray="5 5"
              connectNulls={false}
              name="Predicted"
            />
            
            {/* Confidence bounds */}
            <Area
              type="monotone"
              dataKey="upperBound"
              stroke="#82ca9d"
              fill="none"
              strokeDasharray="2 2"
              connectNulls={false}
              name="Upper Bound"
            />
            <Area
              type="monotone"
              dataKey="lowerBound"
              stroke="#82ca9d"
              fill="none"
              strokeDasharray="2 2"
              connectNulls={false}
              name="Lower Bound"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* AI Insights */}
      {insights.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-gray-900">AI Insights</h3>
          {insights.map((insight, index) => (
            <div key={index} className={`flex items-start p-3 rounded-lg ${
              insight.type === 'positive' ? 'bg-green-50 text-green-800' :
              insight.type === 'warning' ? 'bg-yellow-50 text-yellow-800' :
              'bg-blue-50 text-blue-800'
            }`}>
              {insight.type === 'warning' ? (
                <AlertTriangle className="h-5 w-5 mr-2 mt-0.5" />
              ) : (
                <TrendingUp className="h-5 w-5 mr-2 mt-0.5" />
              )}
              <span className="text-sm font-medium">{insight.message}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default PredictiveModeling