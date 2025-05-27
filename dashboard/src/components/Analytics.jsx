import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts'
import { 
  TrendingUp, 
  Calendar, 
  Globe, 
  Target,
  Download
} from 'lucide-react'
import { monitoringApi, jobsApi } from '../services/api'
import MetricCard from './MetricCard'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']

function Analytics() {
  const [timeRange, setTimeRange] = useState('7d')

  // Fetch analytics data
  const { data: sessionMetrics, isLoading: sessionLoading } = useQuery({
    queryKey: ['sessionMetrics', timeRange],
    queryFn: () => monitoringApi.getPerformanceMetrics(timeRange),
    select: (response) => response.data,
  })

  // Generate mock analytics data for demonstration
  const generateAnalyticsData = () => {
    const sites = ['indeed', 'linkedin', 'glassdoor']
    const days = Array.from({ length: 7 }, (_, i) => {
      const date = new Date()
      date.setDate(date.getDate() - (6 - i))
      return date.toISOString().split('T')[0]
    })

    return {
      dailyJobs: days.map(date => ({
        date,
        indeed: Math.floor(Math.random() * 100) + 50,
        linkedin: Math.floor(Math.random() * 80) + 30,
        glassdoor: Math.floor(Math.random() * 60) + 20,
        total: 0
      })).map(item => ({
        ...item,
        total: item.indeed + item.linkedin + item.glassdoor
      })),
      
      siteDistribution: sites.map(site => ({
        name: site,
        value: Math.floor(Math.random() * 1000) + 500,
        percentage: Math.floor(Math.random() * 30) + 20
      })),
      
      topLocations: [
        { name: 'San Francisco, CA', jobs: 1250, growth: 12 },
        { name: 'New York, NY', jobs: 1100, growth: 8 },
        { name: 'Seattle, WA', jobs: 950, growth: 15 },
        { name: 'Austin, TX', jobs: 800, growth: 22 },
        { name: 'Remote', jobs: 2100, growth: 35 }
      ],
      
      topCompanies: [
        { name: 'Google', jobs: 45, growth: 5 },
        { name: 'Microsoft', jobs: 38, growth: 12 },
        { name: 'Amazon', jobs: 52, growth: -3 },
        { name: 'Apple', jobs: 29, growth: 18 },
        { name: 'Meta', jobs: 23, growth: 8 }
      ],
      
      jobTypes: [
        { name: 'Full-time', value: 75, color: '#3b82f6' },
        { name: 'Contract', value: 15, color: '#10b981' },
        { name: 'Part-time', value: 7, color: '#f59e0b' },
        { name: 'Internship', value: 3, color: '#ef4444' }
      ],
      
      salaryRanges: [
        { range: '$50K-$75K', count: 250 },
        { range: '$75K-$100K', count: 420 },
        { range: '$100K-$125K', count: 380 },
        { range: '$125K-$150K', count: 290 },
        { range: '$150K+', count: 180 }
      ]
    }
  }

  const analyticsData = generateAnalyticsData()
  const isLoading = jobStatsLoading || siteStatsLoading || performanceLoading

  const handleExportReport = () => {
    const reportData = {
      generated_at: new Date().toISOString(),
      time_range: timeRange,
      summary: {
        total_jobs: analyticsData.dailyJobs.reduce((acc, day) => acc + day.total, 0),
        avg_daily_jobs: Math.round(analyticsData.dailyJobs.reduce((acc, day) => acc + day.total, 0) / 7),
        top_site: analyticsData.siteDistribution.reduce((a, b) => a.value > b.value ? a : b).name,
        top_location: analyticsData.topLocations[0].name
      },
      daily_breakdown: analyticsData.dailyJobs,
      site_stats: analyticsData.siteDistribution,
      top_locations: analyticsData.topLocations,
      top_companies: analyticsData.topCompanies
    }

    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `jobbot_analytics_${timeRange}_${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  if (isLoading) {
    return (
      <div className="loading">
        <BarChart className="h-6 w-6 animate-pulse mr-2" />
        Loading analytics...
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="text-gray-600">Insights and trends from scraping operations</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
          >
            <option value="1d">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
          </select>
          <button 
            onClick={handleExportReport}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <Download className="h-4 w-4" />
            <span>Export Report</span>
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Jobs Scraped"
          value={analyticsData.dailyJobs.reduce((acc, day) => acc + day.total, 0)}
          change={12}
          changeLabel="vs last period"
          icon={Target}
          color="blue"
        />
        
        <MetricCard
          title="Avg Daily Jobs"
          value={Math.round(analyticsData.dailyJobs.reduce((acc, day) => acc + day.total, 0) / 7)}
          change={8}
          changeLabel="vs last period"
          icon={TrendingUp}
          color="green"
        />
        
        <MetricCard
          title="Top Location"
          value={analyticsData.topLocations[0].jobs}
          subtitle={analyticsData.topLocations[0].name}
          icon={Globe}
          color="purple"
        />
        
        <MetricCard
          title="Success Rate"
          value="94%"
          change={2}
          changeLabel="vs last period"
          icon={Calendar}
          color="orange"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Daily Jobs Trend */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Daily Jobs by Site</h3>
          </div>
          <div className="card-content">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analyticsData.dailyJobs}>
                <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="indeed" stackId="a" fill="#3b82f6" name="Indeed" />
                <Bar dataKey="linkedin" stackId="a" fill="#10b981" name="LinkedIn" />
                <Bar dataKey="glassdoor" stackId="a" fill="#f59e0b" name="Glassdoor" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Site Distribution */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Jobs by Site</h3>
          </div>
          <div className="card-content">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={analyticsData.siteDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percentage }) => `${name}: ${percentage}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {analyticsData.siteDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Location and Company Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Locations */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Top Locations</h3>
          </div>
          <div className="card-content">
            <div className="space-y-3">
              {analyticsData.topLocations.map((location, index) => (
                <div key={location.name} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <span className="flex items-center justify-center w-6 h-6 bg-blue-100 text-blue-600 rounded-full text-sm font-bold">
                      {index + 1}
                    </span>
                    <div>
                      <p className="font-medium">{location.name}</p>
                      <p className="text-sm text-gray-600">{location.jobs} jobs</p>
                    </div>
                  </div>
                  <div className={`flex items-center space-x-1 text-sm ${
                    location.growth > 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    <TrendingUp className="h-4 w-4" />
                    <span>{location.growth}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Top Companies */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Top Companies</h3>
          </div>
          <div className="card-content">
            <div className="space-y-3">
              {analyticsData.topCompanies.map((company, index) => (
                <div key={company.name} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <span className="flex items-center justify-center w-6 h-6 bg-green-100 text-green-600 rounded-full text-sm font-bold">
                      {index + 1}
                    </span>
                    <div>
                      <p className="font-medium">{company.name}</p>
                      <p className="text-sm text-gray-600">{company.jobs} jobs</p>
                    </div>
                  </div>
                  <div className={`flex items-center space-x-1 text-sm ${
                    company.growth > 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    <TrendingUp className="h-4 w-4" />
                    <span>{company.growth > 0 ? '+' : ''}{company.growth}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Additional Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Job Types */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Job Types Distribution</h3>
          </div>
          <div className="card-content">
            <div className="space-y-3">
              {analyticsData.jobTypes.map((type) => (
                <div key={type.name} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div 
                      className="w-4 h-4 rounded"
                      style={{ backgroundColor: type.color }}
                    />
                    <span className="font-medium">{type.name}</span>
                  </div>
                  <span className="text-sm text-gray-600">{type.value}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Salary Ranges */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Salary Ranges</h3>
          </div>
          <div className="card-content">
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={analyticsData.salaryRanges} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" tick={{ fontSize: 12 }} />
                <YAxis dataKey="range" type="category" tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#8b5cf6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Analytics