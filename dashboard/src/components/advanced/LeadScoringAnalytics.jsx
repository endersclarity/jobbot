import React, { useState, useEffect, useMemo } from 'react'
import { 
  BarChart, Bar, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer, LineChart, Line, Area, AreaChart
} from 'recharts'
import { Brain, Star, TrendingUp, Users, Target, AlertCircle, CheckCircle } from 'lucide-react'

const LeadScoringAnalytics = () => {
  const [scoringModel, setScoringModel] = useState('comprehensive')
  const [threshold, setThreshold] = useState(75)
  const [leadsData, setLeadsData] = useState(null)
  const [modelMetrics, setModelMetrics] = useState(null)
  const [loading, setLoading] = useState(true)

  // Mock lead scoring data
  useEffect(() => {
    const fetchLeadScoringData = async () => {
      setLoading(true)
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      const mockLeads = Array.from({ length: 100 }, (_, i) => {
        const companySize = Math.random() * 1000 + 10
        const industry = ['Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Retail'][Math.floor(Math.random() * 5)]
        const engagement = Math.random() * 100
        const budget = Math.random() * 500000 + 50000
        const timeline = Math.random() * 12 + 1
        
        // Calculate score based on multiple factors
        let score = 0
        score += companySize > 100 ? 25 : companySize > 50 ? 15 : 5
        score += ['Technology', 'Finance'].includes(industry) ? 20 : 10
        score += engagement > 70 ? 25 : engagement > 40 ? 15 : 5
        score += budget > 200000 ? 20 : budget > 100000 ? 15 : 5
        score += timeline < 6 ? 10 : timeline < 9 ? 5 : 0
        
        // Add some randomness
        score += Math.random() * 20 - 10
        score = Math.max(0, Math.min(100, score))
        
        return {
          id: `lead_${i + 1}`,
          companyName: `Company ${i + 1}`,
          score: Math.round(score),
          companySize,
          industry,
          engagement,
          budget,
          timeline,
          status: score > 75 ? 'hot' : score > 50 ? 'warm' : 'cold',
          converted: Math.random() > (score > 75 ? 0.2 : score > 50 ? 0.6 : 0.9)
        }
      })

      const scoreDistribution = [
        { range: '0-20', count: mockLeads.filter(l => l.score <= 20).length, color: '#dc2626' },
        { range: '21-40', count: mockLeads.filter(l => l.score > 20 && l.score <= 40).length, color: '#ea580c' },
        { range: '41-60', count: mockLeads.filter(l => l.score > 40 && l.score <= 60).length, color: '#ca8a04' },
        { range: '61-80', count: mockLeads.filter(l => l.score > 60 && l.score <= 80).length, color: '#16a34a' },
        { range: '81-100', count: mockLeads.filter(l => l.score > 80).length, color: '#059669' }
      ]

      const conversionByScore = [
        { scoreRange: '0-20', conversion: 2.1, leads: scoreDistribution[0].count },
        { scoreRange: '21-40', conversion: 8.5, leads: scoreDistribution[1].count },
        { scoreRange: '41-60', conversion: 15.2, leads: scoreDistribution[2].count },
        { scoreRange: '61-80', conversion: 32.7, leads: scoreDistribution[3].count },
        { scoreRange: '81-100', conversion: 78.9, leads: scoreDistribution[4].count }
      ]

      const metrics = {
        totalLeads: mockLeads.length,
        qualifiedLeads: mockLeads.filter(l => l.score >= threshold).length,
        conversionRate: mockLeads.filter(l => l.converted).length / mockLeads.length * 100,
        averageScore: mockLeads.reduce((sum, l) => sum + l.score, 0) / mockLeads.length,
        modelAccuracy: 87.3,
        precision: 82.1,
        recall: 89.7,
        f1Score: 85.7
      }

      setLeadsData({
        leads: mockLeads,
        scoreDistribution,
        conversionByScore
      })
      setModelMetrics(metrics)
      setLoading(false)
    }

    fetchLeadScoringData()
  }, [threshold])

  const scoringFactors = useMemo(() => [
    { factor: 'Company Size', weight: 25, description: 'Number of employees and revenue' },
    { factor: 'Industry Fit', weight: 20, description: 'Alignment with ideal customer profile' },
    { factor: 'Engagement Level', weight: 25, description: 'Website visits, email opens, content downloads' },
    { factor: 'Budget Authority', weight: 20, description: 'Decision-making power and budget size' },
    { factor: 'Timeline', weight: 10, description: 'Urgency and purchase timeline' }
  ], [])

  const topLeads = useMemo(() => {
    if (!leadsData) return []
    return leadsData.leads
      .filter(lead => lead.score >= threshold)
      .sort((a, b) => b.score - a.score)
      .slice(0, 10)
  }, [leadsData, threshold])

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <div className="flex items-center mb-4">
          <Brain className="h-6 w-6 text-blue-600 mr-2" />
          <h2 className="text-xl font-semibold text-gray-900">AI Lead Scoring Analytics</h2>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Analyzing lead scoring models...</p>
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
          <Brain className="h-6 w-6 text-blue-600 mr-2" />
          <h2 className="text-xl font-semibold text-gray-900">AI Lead Scoring Analytics</h2>
        </div>
        <div className="flex gap-4">
          <select 
            value={scoringModel} 
            onChange={(e) => setScoringModel(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="comprehensive">Comprehensive Model</option>
            <option value="engagement">Engagement-Based</option>
            <option value="firmographic">Firmographic</option>
            <option value="behavioral">Behavioral</option>
          </select>
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Threshold:</label>
            <input
              type="range"
              min="50"
              max="90"
              value={threshold}
              onChange={(e) => setThreshold(parseInt(e.target.value))}
              className="w-20"
            />
            <span className="text-sm font-medium text-gray-900">{threshold}</span>
          </div>
        </div>
      </div>

      {/* Model Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="flex items-center">
            <Target className="h-5 w-5 text-blue-600 mr-2" />
            <span className="text-sm font-medium text-blue-900">Model Accuracy</span>
          </div>
          <p className="text-2xl font-bold text-blue-900 mt-1">{modelMetrics.modelAccuracy}%</p>
        </div>
        
        <div className="bg-green-50 rounded-lg p-4">
          <div className="flex items-center">
            <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
            <span className="text-sm font-medium text-green-900">Qualified Leads</span>
          </div>
          <p className="text-2xl font-bold text-green-900 mt-1">{modelMetrics.qualifiedLeads}</p>
        </div>
        
        <div className="bg-purple-50 rounded-lg p-4">
          <div className="flex items-center">
            <TrendingUp className="h-5 w-5 text-purple-600 mr-2" />
            <span className="text-sm font-medium text-purple-900">Conversion Rate</span>
          </div>
          <p className="text-2xl font-bold text-purple-900 mt-1">{modelMetrics.conversionRate.toFixed(1)}%</p>
        </div>
        
        <div className="bg-orange-50 rounded-lg p-4">
          <div className="flex items-center">
            <Star className="h-5 w-5 text-orange-600 mr-2" />
            <span className="text-sm font-medium text-orange-900">Average Score</span>
          </div>
          <p className="text-2xl font-bold text-orange-900 mt-1">{modelMetrics.averageScore.toFixed(1)}</p>
        </div>
      </div>

      {/* Score Distribution & Conversion Rate */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Score Distribution */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Lead Score Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={leadsData.scoreDistribution}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="range" />
              <YAxis />
              <Tooltip formatter={(value) => [value, 'Leads']} />
              <Bar dataKey="count" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Conversion by Score */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Conversion Rate by Score Range</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={leadsData.conversionByScore}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="scoreRange" />
              <YAxis />
              <Tooltip formatter={(value, name) => [
                name === 'conversion' ? `${value}%` : value,
                name === 'conversion' ? 'Conversion Rate' : 'Leads'
              ]} />
              <Bar dataKey="leads" fill="#82ca9d" name="Leads" />
              <Line 
                type="monotone" 
                dataKey="conversion" 
                stroke="#ff7300" 
                strokeWidth={3}
                name="Conversion Rate"
                yAxisId="right"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Scoring Factors */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Scoring Model Factors</h3>
        <div className="space-y-4">
          {scoringFactors.map((factor, index) => (
            <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <h4 className="font-medium text-gray-900">{factor.factor}</h4>
                <p className="text-sm text-gray-600">{factor.description}</p>
              </div>
              <div className="text-right">
                <span className="text-lg font-bold text-gray-900">{factor.weight}%</span>
                <div className="mt-1 bg-gray-200 rounded-full h-2 w-20">
                  <div 
                    className="bg-blue-600 h-2 rounded-full" 
                    style={{ width: `${factor.weight * 4}%` }}
                  ></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Top Scoring Leads */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Scoring Leads</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Company
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Industry
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Company Size
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Engagement
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {topLeads.map((lead) => (
                <tr key={lead.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {lead.companyName}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className="text-sm font-bold text-gray-900 mr-2">{lead.score}</span>
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${
                            lead.score >= 80 ? 'bg-green-600' : 
                            lead.score >= 60 ? 'bg-yellow-600' : 'bg-red-600'
                          }`}
                          style={{ width: `${lead.score}%` }}
                        ></div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {lead.industry}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {Math.round(lead.companySize)} employees
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {lead.engagement.toFixed(1)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      lead.status === 'hot' ? 'bg-red-100 text-red-800' :
                      lead.status === 'warm' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {lead.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Model Performance Metrics */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Model Performance Metrics</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900">{modelMetrics.precision.toFixed(1)}%</p>
            <p className="text-sm text-gray-600">Precision</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900">{modelMetrics.recall.toFixed(1)}%</p>
            <p className="text-sm text-gray-600">Recall</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900">{modelMetrics.f1Score.toFixed(1)}%</p>
            <p className="text-sm text-gray-600">F1 Score</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LeadScoringAnalytics