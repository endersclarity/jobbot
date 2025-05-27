import { useState, useEffect, useMemo } from 'react'
import { 
  BarChart, Bar, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell,
  Area, AreaChart
} from 'recharts'
import { 
  TrendingUp, DollarSign, Target, Users, Award
} from 'lucide-react'
import PredictiveModeling from './PredictiveModeling'
import ROIAnalytics from './ROIAnalytics'
import LeadScoringAnalytics from './LeadScoringAnalytics'

const AdvancedAnalytics = () => {
  const [timeRange, setTimeRange] = useState('30d')
  const [analyticsData, setAnalyticsData] = useState(null)
  const [loading, setLoading] = useState(true)

  // Mock data - replace with API calls
  useEffect(() => {
    const fetchAnalyticsData = async () => {
      setLoading(true)
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      const mockData = {
        overview: {
          totalRevenue: 125000,
          revenueGrowth: 23.5,
          totalLeads: 1247,
          leadGrowth: 18.2,
          conversionRate: 12.8,
          conversionGrowth: 5.3,
          avgDealSize: 8500,
          dealSizeGrowth: 15.7
        },
        revenueTimeline: [
          { month: 'Jan', revenue: 85000, leads: 180, deals: 12 },
          { month: 'Feb', revenue: 92000, leads: 195, deals: 14 },
          { month: 'Mar', revenue: 98000, leads: 210, deals: 16 },
          { month: 'Apr', revenue: 105000, leads: 225, deals: 18 },
          { month: 'May', revenue: 115000, leads: 240, deals: 20 },
          { month: 'Jun', revenue: 125000, leads: 260, deals: 22 }
        ],
        conversionFunnel: [
          { stage: 'Prospects', count: 1000, percentage: 100 },
          { stage: 'Qualified', count: 450, percentage: 45 },
          { stage: 'Proposals', count: 200, percentage: 20 },
          { stage: 'Negotiations', count: 80, percentage: 8 },
          { stage: 'Closed Won', count: 45, percentage: 4.5 }
        ],
        leadSources: [
          { source: 'Automated Discovery', value: 40, color: '#8884d8' },
          { source: 'Referrals', value: 25, color: '#82ca9d' },
          { source: 'Inbound', value: 20, color: '#ffc658' },
          { source: 'Outreach', value: 15, color: '#ff7300' }
        ],
        performanceMetrics: {
          responseRate: 15.2,
          meetingRate: 8.7,
          proposalRate: 4.3,
          winRate: 22.5,
          avgSalesCycle: 45,
          customerLifetimeValue: 125000
        }
      }

      setAnalyticsData(mockData)
      setLoading(false)
    }

    fetchAnalyticsData()
  }, [timeRange])

  const kpiCards = useMemo(() => [
    {
      title: 'Total Revenue',
      value: analyticsData?.overview.totalRevenue,
      format: 'currency',
      growth: analyticsData?.overview.revenueGrowth,
      icon: DollarSign,
      color: 'text-green-600'
    },
    {
      title: 'Total Leads',
      value: analyticsData?.overview.totalLeads,
      format: 'number',
      growth: analyticsData?.overview.leadGrowth,
      icon: Users,
      color: 'text-blue-600'
    },
    {
      title: 'Conversion Rate',
      value: analyticsData?.overview.conversionRate,
      format: 'percentage',
      growth: analyticsData?.overview.conversionGrowth,
      icon: Target,
      color: 'text-purple-600'
    },
    {
      title: 'Avg Deal Size',
      value: analyticsData?.overview.avgDealSize,
      format: 'currency',
      growth: analyticsData?.overview.dealSizeGrowth,
      icon: Award,
      color: 'text-orange-600'
    }
  ], [analyticsData])

  const formatValue = (value, format) => {
    if (!value) return '...'
    
    switch (format) {
      case 'currency':
        return new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD',
          minimumFractionDigits: 0
        }).format(value)
      case 'percentage':
        return `${value}%`
      case 'number':
        return new Intl.NumberFormat('en-US').format(value)
      default:
        return value
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Advanced Analytics</h1>
              <p className="text-gray-600 mt-2">Comprehensive business intelligence and predictive insights</p>
            </div>
            <div className="flex gap-4">
              <select 
                value={timeRange} 
                onChange={(e) => setTimeRange(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="7d">Last 7 days</option>
                <option value="30d">Last 30 days</option>
                <option value="90d">Last 90 days</option>
                <option value="1y">Last year</option>
              </select>
            </div>
          </div>
        </div>

        {/* KPI Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {kpiCards.map((kpi, index) => (
            <div key={index} className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{kpi.title}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-2">
                    {formatValue(kpi.value, kpi.format)}
                  </p>
                  {kpi.growth && (
                    <div className="flex items-center mt-2">
                      <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
                      <span className="text-sm text-green-600">+{kpi.growth}%</span>
                      <span className="text-sm text-gray-500 ml-1">vs last period</span>
                    </div>
                  )}
                </div>
                <div className={`p-3 rounded-full bg-gray-100 ${kpi.color}`}>
                  <kpi.icon className="h-6 w-6" />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Revenue Timeline */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Revenue & Performance Timeline</h2>
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={analyticsData.revenueTimeline}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip 
                formatter={(value, name) => [
                  name === 'revenue' ? formatValue(value, 'currency') : value,
                  name === 'revenue' ? 'Revenue' : name === 'leads' ? 'Leads' : 'Deals'
                ]}
              />
              <Legend />
              <Area 
                type="monotone" 
                dataKey="revenue" 
                stackId="1" 
                stroke="#8884d8" 
                fill="#8884d8"
                name="Revenue"
              />
              <Bar dataKey="leads" fill="#82ca9d" name="Leads" />
              <Line 
                type="monotone" 
                dataKey="deals" 
                stroke="#ff7300" 
                strokeWidth={3}
                name="Deals Closed"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Conversion Funnel & Lead Sources */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Conversion Funnel */}
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Conversion Funnel</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analyticsData.conversionFunnel} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis type="category" dataKey="stage" />
                <Tooltip formatter={(value) => [value, 'Count']} />
                <Bar dataKey="count" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Lead Sources */}
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Lead Sources</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={analyticsData.leadSources}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {analyticsData.leadSources.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Key Performance Metrics</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {Object.entries(analyticsData.performanceMetrics).map(([key, value]) => (
              <div key={key} className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-2xl font-bold text-gray-900">
                  {key.includes('Rate') || key === 'winRate' ? `${value}%` : 
                   key === 'customerLifetimeValue' ? formatValue(value, 'currency') :
                   key === 'avgSalesCycle' ? `${value} days` : value}
                </p>
                <p className="text-sm text-gray-600 capitalize">
                  {key.replace(/([A-Z])/g, ' $1').trim()}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Advanced Components */}
        <div className="space-y-8">
          <PredictiveModeling data={analyticsData} />
          <ROIAnalytics data={analyticsData} />
          <LeadScoringAnalytics />
        </div>
      </div>
    </div>
  )
}

export default AdvancedAnalytics