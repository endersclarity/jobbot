import React, { useState, useEffect } from 'react'
import { 
  Building, 
  Search, 
  MapPin, 
  Globe, 
  Users, 
  TrendingUp,
  Plus,
  Filter,
  Download,
  Eye,
  Star,
  Clock
} from 'lucide-react'
import { useQuery } from '@tanstack/react-query'

function CompanyDiscovery() {
  const [searchTerm, setSearchTerm] = useState('')
  const [locationFilter, setLocationFilter] = useState('')
  const [industryFilter, setIndustryFilter] = useState('')

  // Fetch companies data
  const { data: companies, isLoading } = useQuery({
    queryKey: ['companies', searchTerm, locationFilter, industryFilter],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (searchTerm) params.append('search', searchTerm)
      if (locationFilter) params.append('location', locationFilter)
      if (industryFilter) params.append('industry', industryFilter)
      
      const response = await fetch(`/api/v1/business/companies?${params}`)
      return response.json()
    }
  })

  const handleStartDiscovery = async () => {
    try {
      const response = await fetch('/api/v1/business/discovery/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          search_terms: [searchTerm],
          location: locationFilter,
          industry: industryFilter
        })
      })
      
      if (response.ok) {
        // Trigger data refresh
        window.location.reload()
      }
    } catch (error) {
      console.error('Failed to start discovery:', error)
    }
  }

  if (isLoading) {
    return (
      <div className="loading">
        <Building className="h-6 w-6 animate-spin mr-2" />
        Loading companies...
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Company Discovery</h1>
          <p className="text-gray-600 mt-1">Discover and analyze potential business opportunities</p>
        </div>
        <button 
          onClick={handleStartDiscovery}
          className="btn btn-primary flex items-center space-x-2"
        >
          <Plus className="h-4 w-4" />
          <span>Start Discovery</span>
        </button>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Companies
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Company name or technology..."
                className="pl-10 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Location
            </label>
            <div className="relative">
              <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                value={locationFilter}
                onChange={(e) => setLocationFilter(e.target.value)}
                placeholder="City, State"
                className="pl-10 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Industry
            </label>
            <select
              value={industryFilter}
              onChange={(e) => setIndustryFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Industries</option>
              <option value="technology">Technology</option>
              <option value="healthcare">Healthcare</option>
              <option value="finance">Finance</option>
              <option value="retail">Retail</option>
              <option value="manufacturing">Manufacturing</option>
            </select>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <Building className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Companies</p>
              <p className="text-2xl font-bold text-gray-900">{companies?.total || 0}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <Star className="h-8 w-8 text-yellow-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">High Priority</p>
              <p className="text-2xl font-bold text-gray-900">{companies?.high_priority || 0}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Growth Companies</p>
              <p className="text-2xl font-bold text-gray-900">{companies?.growth_companies || 0}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <Clock className="h-8 w-8 text-purple-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Recently Added</p>
              <p className="text-2xl font-bold text-gray-900">{companies?.recent || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Companies List */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-medium text-gray-900">Discovered Companies</h2>
            <div className="flex items-center space-x-2">
              <button className="btn btn-secondary btn-sm flex items-center space-x-1">
                <Filter className="h-4 w-4" />
                <span>Filter</span>
              </button>
              <button className="btn btn-secondary btn-sm flex items-center space-x-1">
                <Download className="h-4 w-4" />
                <span>Export</span>
              </button>
            </div>
          </div>
        </div>
        
        <div className="divide-y divide-gray-200">
          {companies?.items?.map((company) => (
            <div key={company.id} className="p-6 hover:bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    <Building className="h-10 w-10 text-gray-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">{company.name}</h3>
                    <p className="text-sm text-gray-500">{company.industry} • {company.location}</p>
                    <div className="flex items-center space-x-4 mt-1">
                      <span className="flex items-center text-sm text-gray-500">
                        <Users className="h-4 w-4 mr-1" />
                        {company.employee_count || 'Unknown'} employees
                      </span>
                      <span className="flex items-center text-sm text-gray-500">
                        <Globe className="h-4 w-4 mr-1" />
                        {company.website || 'No website'}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  <div className="text-right">
                    <div className={`text-sm font-medium ${
                      company.opportunity_score >= 80 ? 'text-green-600' :
                      company.opportunity_score >= 60 ? 'text-yellow-600' : 'text-red-600'
                    }`}>
                      Score: {company.opportunity_score || 0}%
                    </div>
                    <div className="text-xs text-gray-500">
                      {company.automation_opportunities || 0} opportunities
                    </div>
                  </div>
                  <button className="btn btn-primary btn-sm flex items-center space-x-1">
                    <Eye className="h-4 w-4" />
                    <span>View Details</span>
                  </button>
                </div>
              </div>
              
              {company.description && (
                <p className="mt-3 text-sm text-gray-600 line-clamp-2">{company.description}</p>
              )}
              
              {company.tech_stack && company.tech_stack.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {company.tech_stack.slice(0, 5).map((tech, index) => (
                    <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-md">
                      {tech}
                    </span>
                  ))}
                  {company.tech_stack.length > 5 && (
                    <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-md">
                      +{company.tech_stack.length - 5} more
                    </span>
                  )}
                </div>
              )}
            </div>
          )) || (
            <div className="p-12 text-center">
              <Building className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No companies found</h3>
              <p className="text-gray-500">Start a discovery process to find potential business opportunities.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default CompanyDiscovery