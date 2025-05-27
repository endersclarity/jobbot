import React, { useState, useEffect } from 'react'
import { 
  Target, 
  Clock, 
  DollarSign, 
  TrendingUp, 
  CheckCircle,
  AlertCircle,
  Play,
  Pause,
  Edit,
  Trash2,
  Plus
} from 'lucide-react'
import { useQuery } from '@tanstack/react-query'

function OpportunityPipeline() {
  const [selectedStage, setSelectedStage] = useState('all')
  const [sortBy, setSortBy] = useState('score')

  // Fetch opportunities data
  const { data: opportunities, isLoading } = useQuery({
    queryKey: ['opportunities', selectedStage, sortBy],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (selectedStage !== 'all') params.append('stage', selectedStage)
      params.append('sort_by', sortBy)
      
      const response = await fetch(`/api/v1/business/opportunities?${params}`)
      return response.json()
    }
  })

  const stages = [
    { id: 'discovery', name: 'Discovery', color: 'blue', count: opportunities?.stages?.discovery || 0 },
    { id: 'analysis', name: 'Analysis', color: 'yellow', count: opportunities?.stages?.analysis || 0 },
    { id: 'demo_creation', name: 'Demo Creation', color: 'purple', count: opportunities?.stages?.demo_creation || 0 },
    { id: 'outreach', name: 'Outreach', color: 'green', count: opportunities?.stages?.outreach || 0 },
    { id: 'negotiation', name: 'Negotiation', color: 'orange', count: opportunities?.stages?.negotiation || 0 },
    { id: 'closed', name: 'Closed', color: 'gray', count: opportunities?.stages?.closed || 0 }
  ]

  const handleCreateOpportunity = async () => {
    // Open modal or redirect to opportunity creation
    console.log('Create new opportunity')
  }

  if (isLoading) {
    return (
      <div className="loading">
        <Target className="h-6 w-6 animate-spin mr-2" />
        Loading pipeline...
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Opportunity Pipeline</h1>
          <p className="text-gray-600 mt-1">Track and manage business opportunities through the sales process</p>
        </div>
        <button 
          onClick={handleCreateOpportunity}
          className="btn btn-primary flex items-center space-x-2"
        >
          <Plus className="h-4 w-4" />
          <span>Create Opportunity</span>
        </button>
      </div>

      {/* Pipeline Overview */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-medium text-gray-900">Pipeline Overview</h2>
          <div className="flex items-center space-x-4">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="score">Sort by Score</option>
              <option value="value">Sort by Value</option>
              <option value="created_at">Sort by Date</option>
              <option value="priority">Sort by Priority</option>
            </select>
          </div>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
          {stages.map((stage) => (
            <div 
              key={stage.id}
              onClick={() => setSelectedStage(selectedStage === stage.id ? 'all' : stage.id)}
              className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                selectedStage === stage.id 
                  ? `border-${stage.color}-500 bg-${stage.color}-50` 
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="text-center">
                <div className={`text-2xl font-bold text-${stage.color}-600`}>
                  {stage.count}
                </div>
                <div className="text-sm text-gray-600 mt-1">{stage.name}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Pipeline Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <Target className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Opportunities</p>
              <p className="text-2xl font-bold text-gray-900">{opportunities?.total || 0}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <DollarSign className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Pipeline Value</p>
              <p className="text-2xl font-bold text-gray-900">
                ${(opportunities?.total_value || 0).toLocaleString()}
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-purple-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Win Rate</p>
              <p className="text-2xl font-bold text-gray-900">{opportunities?.win_rate || 0}%</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <Clock className="h-8 w-8 text-orange-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Avg. Cycle Time</p>
              <p className="text-2xl font-bold text-gray-900">{opportunities?.avg_cycle_days || 0}d</p>
            </div>
          </div>
        </div>
      </div>

      {/* Opportunities List */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">
            {selectedStage === 'all' ? 'All Opportunities' : `${stages.find(s => s.id === selectedStage)?.name} Opportunities`}
          </h2>
        </div>
        
        <div className="divide-y divide-gray-200">
          {opportunities?.items?.map((opportunity) => (
            <div key={opportunity.id} className="p-6 hover:bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 mt-1">
                    <div className={`w-3 h-3 rounded-full bg-${
                      opportunity.priority === 'high' ? 'red' :
                      opportunity.priority === 'medium' ? 'yellow' : 'green'
                    }-500`}></div>
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <h3 className="text-lg font-medium text-gray-900">{opportunity.title}</h3>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        opportunity.stage === 'discovery' ? 'bg-blue-100 text-blue-800' :
                        opportunity.stage === 'analysis' ? 'bg-yellow-100 text-yellow-800' :
                        opportunity.stage === 'demo_creation' ? 'bg-purple-100 text-purple-800' :
                        opportunity.stage === 'outreach' ? 'bg-green-100 text-green-800' :
                        opportunity.stage === 'negotiation' ? 'bg-orange-100 text-orange-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {stages.find(s => s.id === opportunity.stage)?.name}
                      </span>
                    </div>
                    
                    <p className="text-sm text-gray-600 mt-1">{opportunity.company_name}</p>
                    <p className="text-sm text-gray-500 mt-2 line-clamp-2">{opportunity.description}</p>
                    
                    <div className="flex items-center space-x-6 mt-3 text-sm text-gray-500">
                      <span className="flex items-center">
                        <DollarSign className="h-4 w-4 mr-1" />
                        ${(opportunity.estimated_value || 0).toLocaleString()}
                      </span>
                      <span className="flex items-center">
                        <Target className="h-4 w-4 mr-1" />
                        Score: {opportunity.score || 0}%
                      </span>
                      <span className="flex items-center">
                        <Clock className="h-4 w-4 mr-1" />
                        {opportunity.days_in_stage || 0} days in stage
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  {opportunity.status === 'active' ? (
                    <button className="p-2 text-green-600 hover:bg-green-50 rounded-md">
                      <Play className="h-4 w-4" />
                    </button>
                  ) : (
                    <button className="p-2 text-orange-600 hover:bg-orange-50 rounded-md">
                      <Pause className="h-4 w-4" />
                    </button>
                  )}
                  
                  <button className="p-2 text-blue-600 hover:bg-blue-50 rounded-md">
                    <Edit className="h-4 w-4" />
                  </button>
                  
                  <button className="p-2 text-red-600 hover:bg-red-50 rounded-md">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
              
              {opportunity.next_action && (
                <div className="mt-4 p-3 bg-yellow-50 rounded-md">
                  <div className="flex items-center">
                    <AlertCircle className="h-4 w-4 text-yellow-600 mr-2" />
                    <span className="text-sm font-medium text-yellow-800">Next Action:</span>
                  </div>
                  <p className="text-sm text-yellow-700 mt-1">{opportunity.next_action}</p>
                  {opportunity.next_action_date && (
                    <p className="text-xs text-yellow-600 mt-1">
                      Due: {new Date(opportunity.next_action_date).toLocaleDateString()}
                    </p>
                  )}
                </div>
              )}
            </div>
          )) || (
            <div className="p-12 text-center">
              <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No opportunities found</h3>
              <p className="text-gray-500">Create your first opportunity to start building your pipeline.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default OpportunityPipeline