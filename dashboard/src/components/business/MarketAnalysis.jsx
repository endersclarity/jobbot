import React, { useState, useEffect } from 'react'
import { 
  TrendingUp, 
  PieChart, 
  BarChart3, 
  Globe, 
  Users, 
  DollarSign,
  Activity,
  Building,
  Zap,
  Target,
  ArrowUp,
  ArrowDown
} from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart as RechartsPieChart,
  Cell,
  BarChart,
  Bar
} from 'recharts'

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4']

function MarketAnalysis() {
  const [timeRange, setTimeRange] = useState('30d')
  const [selectedRegion, setSelectedRegion] = useState('all')

  // Fetch market analysis data
  const { data: marketData, isLoading } = useQuery({
    queryKey: ['market-analysis', timeRange, selectedRegion],
    queryFn: async () => {
      const params = new URLSearchParams()
      params.append('time_range', timeRange)
      if (selectedRegion !== 'all') params.append('region', selectedRegion)
      
      const response = await fetch(`/api/v1/business/market-analysis?${params}`)
      return response.json()
    }
  })

  if (isLoading) {
    return (
      <div className="loading">
        <TrendingUp className="h-6 w-6 animate-spin mr-2" />
        Loading market analysis...
      </div>
    )
  }

  const opportunityTrends = marketData?.opportunity_trends || []
  const industryDistribution = marketData?.industry_distribution || []
  const regionData = marketData?.region_data || []
  const competitorAnalysis = marketData?.competitor_analysis || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Market Analysis</h1>
          <p className="text-gray-600 mt-1">Analyze market trends and business opportunities</p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={selectedRegion}
            onChange={(e) => setSelectedRegion(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Regions</option>
            <option value="north_america">North America</option>
            <option value="europe">Europe</option>
            <option value="asia_pacific">Asia Pacific</option>
          </select>
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Market Opportunity</p>
              <p className="text-2xl font-bold text-gray-900">
                ${(marketData?.total_market_value || 0).toLocaleString()}
              </p>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <DollarSign className="h-6 w-6 text-blue-600" />
            </div>
          </div>
          <div className="mt-2 flex items-center text-sm">
            <ArrowUp className="h-4 w-4 text-green-500 mr-1" />
            <span className="text-green-600 font-medium">
              {marketData?.market_growth_rate || 0}%
            </span>
            <span className="text-gray-500 ml-1">vs last period</span>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Companies</p>
              <p className="text-2xl font-bold text-gray-900">{marketData?.active_companies || 0}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <Building className="h-6 w-6 text-green-600" />
            </div>
          </div>
          <div className="mt-2 flex items-center text-sm">
            <ArrowUp className="h-4 w-4 text-green-500 mr-1" />
            <span className="text-green-600 font-medium">+{marketData?.new_companies || 0}</span>
            <span className="text-gray-500 ml-1">new this period</span>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Automation Score</p>
              <p className="text-2xl font-bold text-gray-900">{marketData?.automation_score || 0}%</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-full">
              <Zap className="h-6 w-6 text-purple-600" />
            </div>
          </div>
          <div className="mt-2 flex items-center text-sm">
            <ArrowUp className="h-4 w-4 text-green-500 mr-1" />
            <span className="text-green-600 font-medium">High potential</span>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Competition Level</p>
              <p className="text-2xl font-bold text-gray-900">{marketData?.competition_level || 'Low'}</p>
            </div>
            <div className="p-3 bg-orange-100 rounded-full">
              <Target className="h-6 w-6 text-orange-600" />
            </div>
          </div>
          <div className="mt-2 flex items-center text-sm">
            <span className="text-orange-600 font-medium">
              {marketData?.competitors_count || 0} direct competitors
            </span>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Opportunity Trends */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Opportunity Trends</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={opportunityTrends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="date" 
                tickFormatter={(date) => new Date(date).toLocaleDateString()}
              />
              <YAxis />
              <Tooltip 
                labelFormatter={(date) => new Date(date).toLocaleDateString()}
                formatter={(value, name) => [value, name === 'opportunities' ? 'Opportunities' : 'Value ($)']}
              />
              <Area 
                type="monotone" 
                dataKey="opportunities" 
                stackId="1"
                stroke="#3B82F6" 
                fill="#3B82F6" 
                fillOpacity={0.6}
              />
              <Area 
                type="monotone" 
                dataKey="value" 
                stackId="2"
                stroke="#10B981" 
                fill="#10B981" 
                fillOpacity={0.6}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Industry Distribution */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Industry Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <RechartsPieChart>
              <Pie
                data={industryDistribution}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={120}
                paddingAngle={5}
                dataKey="value"
              >
                {industryDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value, name) => [`${value}%`, name]} />
            </RechartsPieChart>
          </ResponsiveContainer>
          <div className="mt-4 grid grid-cols-2 gap-2">
            {industryDistribution.map((industry, index) => (
              <div key={industry.name} className="flex items-center text-sm">
                <div 
                  className="w-3 h-3 rounded-full mr-2"
                  style={{ backgroundColor: COLORS[index % COLORS.length] }}
                ></div>
                <span className="text-gray-600">{industry.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Regional Analysis */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Regional Analysis</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={regionData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="region" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="companies" fill="#3B82F6" name="Companies" />
            <Bar dataKey="opportunities" fill="#10B981" name="Opportunities" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Competitor Analysis */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Competitor Analysis</h3>
        </div>
        <div className="divide-y divide-gray-200">
          {competitorAnalysis.map((competitor, index) => (
            <div key={index} className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    <Building className="h-10 w-10 text-gray-400" />
                  </div>
                  <div>
                    <h4 className="text-lg font-medium text-gray-900">{competitor.name}</h4>
                    <p className="text-sm text-gray-500">{competitor.description}</p>
                    <div className="flex items-center space-x-4 mt-2">
                      <span className="flex items-center text-sm text-gray-500">
                        <Users className="h-4 w-4 mr-1" />
                        {competitor.market_share}% market share
                      </span>
                      <span className="flex items-center text-sm text-gray-500">
                        <Globe className="h-4 w-4 mr-1" />
                        {competitor.coverage} coverage
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="text-right">
                  <div className={`text-sm font-medium ${
                    competitor.threat_level === 'high' ? 'text-red-600' :
                    competitor.threat_level === 'medium' ? 'text-yellow-600' : 'text-green-600'
                  }`}>
                    {competitor.threat_level.charAt(0).toUpperCase() + competitor.threat_level.slice(1)} Threat
                  </div>
                  <div className="text-xs text-gray-500">
                    {competitor.strengths?.length || 0} key strengths
                  </div>
                </div>
              </div>
              
              {competitor.strengths && competitor.strengths.length > 0 && (
                <div className="mt-4">
                  <h5 className="text-sm font-medium text-gray-900 mb-2">Key Strengths:</h5>
                  <div className="flex flex-wrap gap-2">
                    {competitor.strengths.map((strength, idx) => (
                      <span key={idx} className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-md">
                        {strength}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              {competitor.opportunities && competitor.opportunities.length > 0 && (
                <div className="mt-3">
                  <h5 className="text-sm font-medium text-gray-900 mb-2">Our Opportunities:</h5>
                  <div className="flex flex-wrap gap-2">
                    {competitor.opportunities.map((opportunity, idx) => (
                      <span key={idx} className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-md">
                        {opportunity}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )) || (
            <div className="p-12 text-center">
              <TrendingUp className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h4 className="text-lg font-medium text-gray-900 mb-2">No competitor data</h4>
              <p className="text-gray-500">Market analysis will be updated as more data becomes available.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default MarketAnalysis