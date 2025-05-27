import React, { useState, useMemo } from 'react'
import { 
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts'
import { DollarSign, TrendingUp, Calculator, Award, Clock, Target } from 'lucide-react'

const ROIAnalytics = ({ data }) => {
  const [timeFrame, setTimeFrame] = useState('monthly')
  const [selectedCampaign, setSelectedCampaign] = useState('all')

  // Mock ROI data - replace with actual API calls
  const roiData = useMemo(() => ({
    campaigns: [
      {
        id: 'automated_discovery',
        name: 'Automated Discovery',
        investment: 15000,
        revenue: 85000,
        roi: 466.7,
        leads: 120,
        conversions: 15,
        avgDealSize: 5667,
        costPerLead: 125,
        costPerAcquisition: 1000
      },
      {
        id: 'ai_outreach',
        name: 'AI-Powered Outreach',
        investment: 8000,
        revenue: 45000,
        roi: 462.5,
        leads: 80,
        conversions: 8,
        avgDealSize: 5625,
        costPerLead: 100,
        costPerAcquisition: 1000
      },
      {
        id: 'demo_automation',
        name: 'Demo Automation',
        investment: 12000,
        revenue: 65000,
        roi: 441.7,
        leads: 60,
        conversions: 12,
        avgDealSize: 5417,
        costPerLead: 200,
        costPerAcquisition: 1000
      }
    ],
    monthlyROI: [
      { month: 'Jan', roi: 320, investment: 10000, revenue: 32000 },
      { month: 'Feb', roi: 385, investment: 11000, revenue: 42350 },
      { month: 'Mar', roi: 420, investment: 12000, revenue: 50400 },
      { month: 'Apr', roi: 445, investment: 13000, revenue: 57850 },
      { month: 'May', roi: 460, investment: 14000, revenue: 64400 },
      { month: 'Jun', roi: 478, investment: 15000, revenue: 71700 }
    ],
    costBreakdown: [
      { category: 'Technology', amount: 25000, percentage: 45.5 },
      { category: 'Personnel', amount: 18000, percentage: 32.7 },
      { category: 'Marketing', amount: 8000, percentage: 14.5 },
      { category: 'Operations', amount: 4000, percentage: 7.3 }
    ],
    customerLifetimeValue: {
      avgLifetime: 24, // months
      avgMonthlyValue: 5200,
      totalCLV: 124800,
      acquisitionCost: 1000,
      ltvsToCAC: 124.8
    }
  }), [])

  const selectedCampaignData = useMemo(() => {
    if (selectedCampaign === 'all') {
      return {
        investment: roiData.campaigns.reduce((sum, c) => sum + c.investment, 0),
        revenue: roiData.campaigns.reduce((sum, c) => sum + c.revenue, 0),
        leads: roiData.campaigns.reduce((sum, c) => sum + c.leads, 0),
        conversions: roiData.campaigns.reduce((sum, c) => sum + c.conversions, 0)
      }
    }
    return roiData.campaigns.find(c => c.id === selectedCampaign) || roiData.campaigns[0]
  }, [selectedCampaign, roiData])

  const formatCurrency = (value) => new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0
  }).format(value)

  const formatPercentage = (value) => `${value.toFixed(1)}%`

  const kpiMetrics = useMemo(() => [
    {
      title: 'Total ROI',
      value: selectedCampaignData.revenue && selectedCampaignData.investment ? 
        ((selectedCampaignData.revenue - selectedCampaignData.investment) / selectedCampaignData.investment * 100) : 0,
      format: 'percentage',
      icon: TrendingUp,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    {
      title: 'Revenue Generated',
      value: selectedCampaignData.revenue || 0,
      format: 'currency',
      icon: DollarSign,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      title: 'Total Investment',
      value: selectedCampaignData.investment || 0,
      format: 'currency',
      icon: Calculator,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50'
    },
    {
      title: 'Customer LTV:CAC',
      value: roiData.customerLifetimeValue.ltvsToCAC,
      format: 'ratio',
      icon: Award,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50'
    }
  ], [selectedCampaignData, roiData])

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <DollarSign className="h-6 w-6 text-green-600 mr-2" />
          <h2 className="text-xl font-semibold text-gray-900">ROI Analytics</h2>
        </div>
        <div className="flex gap-4">
          <select 
            value={selectedCampaign} 
            onChange={(e) => setSelectedCampaign(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
          >
            <option value="all">All Campaigns</option>
            {roiData.campaigns.map(campaign => (
              <option key={campaign.id} value={campaign.id}>{campaign.name}</option>
            ))}
          </select>
          <select 
            value={timeFrame} 
            onChange={(e) => setTimeFrame(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
          >
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
            <option value="quarterly">Quarterly</option>
          </select>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {kpiMetrics.map((metric, index) => (
          <div key={index} className={`${metric.bgColor} rounded-lg p-4`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{metric.title}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {metric.format === 'currency' ? formatCurrency(metric.value) :
                   metric.format === 'percentage' ? formatPercentage(metric.value) :
                   metric.format === 'ratio' ? `${metric.value.toFixed(1)}:1` :
                   metric.value}
                </p>
              </div>
              <metric.icon className={`h-8 w-8 ${metric.color}`} />
            </div>
          </div>
        ))}
      </div>

      {/* ROI Trend Chart */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">ROI Trend Over Time</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={roiData.monthlyROI}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip 
              formatter={(value, name) => [
                name === 'roi' ? `${value}%` : formatCurrency(value),
                name === 'roi' ? 'ROI' : name === 'investment' ? 'Investment' : 'Revenue'
              ]}
            />
            <Legend />
            <Bar dataKey="investment" fill="#8884d8" name="Investment" />
            <Bar dataKey="revenue" fill="#82ca9d" name="Revenue" />
            <Line 
              type="monotone" 
              dataKey="roi" 
              stroke="#ff7300" 
              strokeWidth={3}
              name="ROI %"
              yAxisId="right"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Campaign Performance & Cost Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Campaign Performance */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Campaign Performance</h3>
          <div className="space-y-4">
            {roiData.campaigns.map((campaign) => (
              <div key={campaign.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <h4 className="font-medium text-gray-900">{campaign.name}</h4>
                  <span className="text-lg font-bold text-green-600">
                    {formatPercentage(campaign.roi)}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Investment:</span>
                    <span className="ml-2 font-medium">{formatCurrency(campaign.investment)}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Revenue:</span>
                    <span className="ml-2 font-medium">{formatCurrency(campaign.revenue)}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Leads:</span>
                    <span className="ml-2 font-medium">{campaign.leads}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Conversions:</span>
                    <span className="ml-2 font-medium">{campaign.conversions}</span>
                  </div>
                </div>
                <div className="mt-2 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-600 h-2 rounded-full" 
                    style={{ width: `${Math.min(100, campaign.roi / 5)}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Cost Breakdown */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Cost Breakdown</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={roiData.costBreakdown}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percentage }) => `${name}: ${percentage}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="amount"
              >
                {roiData.costBreakdown.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={
                    ['#8884d8', '#82ca9d', '#ffc658', '#ff7300'][index % 4]
                  } />
                ))}
              </Pie>
              <Tooltip formatter={(value) => formatCurrency(value)} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Customer Lifetime Value Analysis */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Customer Lifetime Value Analysis</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900">
              {roiData.customerLifetimeValue.avgLifetime} months
            </p>
            <p className="text-sm text-gray-600">Average Customer Lifetime</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900">
              {formatCurrency(roiData.customerLifetimeValue.avgMonthlyValue)}
            </p>
            <p className="text-sm text-gray-600">Average Monthly Value</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900">
              {formatCurrency(roiData.customerLifetimeValue.totalCLV)}
            </p>
            <p className="text-sm text-gray-600">Total Customer LTV</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-green-600">
              {roiData.customerLifetimeValue.ltvsToCAC.toFixed(1)}:1
            </p>
            <p className="text-sm text-gray-600">LTV:CAC Ratio</p>
          </div>
        </div>
        
        <div className="mt-4 p-4 bg-green-50 rounded-lg">
          <div className="flex items-center">
            <Target className="h-5 w-5 text-green-600 mr-2" />
            <span className="text-sm font-medium text-green-800">
              Excellent LTV:CAC ratio! Industry benchmark is 3:1, you're achieving {roiData.customerLifetimeValue.ltvsToCAC.toFixed(1)}:1
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ROIAnalytics