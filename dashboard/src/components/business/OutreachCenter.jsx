import React, { useState, useEffect } from 'react'
import { 
  Mail, 
  Send, 
  Users, 
  Calendar, 
  CheckCircle,
  Clock,
  AlertCircle,
  Eye,
  Edit,
  Trash2,
  Plus,
  BarChart3,
  TrendingUp,
  MessageSquare,
  Phone
} from 'lucide-react'
import { useQuery } from '@tanstack/react-query'

function OutreachCenter() {
  const [selectedCampaign, setSelectedCampaign] = useState(null)
  const [statusFilter, setStatusFilter] = useState('all')
  const [sortBy, setSortBy] = useState('created_at')

  // Fetch outreach data
  const { data: outreachData, isLoading } = useQuery({
    queryKey: ['outreach', statusFilter, sortBy],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (statusFilter !== 'all') params.append('status', statusFilter)
      params.append('sort_by', sortBy)
      
      const response = await fetch(`/api/v1/business/outreach?${params}`)
      return response.json()
    }
  })

  const handleCreateCampaign = async () => {
    // Open campaign creation modal
    console.log('Create new campaign')
  }

  const handleSendMessage = async (contactId, messageTemplate) => {
    try {
      const response = await fetch('/api/v1/business/outreach/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contact_id: contactId,
          message_template: messageTemplate
        })
      })
      
      if (response.ok) {
        // Refresh data
        window.location.reload()
      }
    } catch (error) {
      console.error('Failed to send message:', error)
    }
  }

  if (isLoading) {
    return (
      <div className="loading">
        <Mail className="h-6 w-6 animate-spin mr-2" />
        Loading outreach center...
      </div>
    )
  }

  const campaigns = outreachData?.campaigns || []
  const contacts = outreachData?.contacts || []
  const stats = outreachData?.stats || {}

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Outreach Center</h1>
          <p className="text-gray-600 mt-1">Manage personalized outreach campaigns and track responses</p>
        </div>
        <button 
          onClick={handleCreateCampaign}
          className="btn btn-primary flex items-center space-x-2"
        >
          <Plus className="h-4 w-4" />
          <span>New Campaign</span>
        </button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <Mail className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Sent</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total_sent || 0}</p>
            </div>
          </div>
          <div className="mt-2 text-sm text-gray-500">
            {stats.sent_this_week || 0} this week
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <Eye className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Open Rate</p>
              <p className="text-2xl font-bold text-gray-900">{stats.open_rate || 0}%</p>
            </div>
          </div>
          <div className="mt-2 text-sm text-gray-500">
            {stats.total_opens || 0} total opens
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <MessageSquare className="h-8 w-8 text-purple-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Response Rate</p>
              <p className="text-2xl font-bold text-gray-900">{stats.response_rate || 0}%</p>
            </div>
          </div>
          <div className="mt-2 text-sm text-gray-500">
            {stats.total_responses || 0} responses
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <CheckCircle className="h-8 w-8 text-orange-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Meeting Rate</p>
              <p className="text-2xl font-bold text-gray-900">{stats.meeting_rate || 0}%</p>
            </div>
          </div>
          <div className="mt-2 text-sm text-gray-500">
            {stats.total_meetings || 0} meetings booked
          </div>
        </div>
      </div>

      {/* Campaigns and Contacts Split View */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Active Campaigns */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-medium text-gray-900">Active Campaigns</h2>
              <button className="btn btn-secondary btn-sm">
                <BarChart3 className="h-4 w-4 mr-1" />
                Analytics
              </button>
            </div>
          </div>
          
          <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
            {campaigns.map((campaign) => (
              <div 
                key={campaign.id} 
                className={`p-4 cursor-pointer hover:bg-gray-50 ${
                  selectedCampaign?.id === campaign.id ? 'bg-blue-50 border-r-2 border-blue-500' : ''
                }`}
                onClick={() => setSelectedCampaign(campaign)}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-gray-900">{campaign.name}</h3>
                    <p className="text-sm text-gray-500 mt-1">{campaign.description}</p>
                    <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                      <span className="flex items-center">
                        <Users className="h-3 w-3 mr-1" />
                        {campaign.total_contacts || 0} contacts
                      </span>
                      <span className="flex items-center">
                        <Send className="h-3 w-3 mr-1" />
                        {campaign.sent_count || 0} sent
                      </span>
                      <span className="flex items-center">
                        <MessageSquare className="h-3 w-3 mr-1" />
                        {campaign.response_count || 0} responses
                      </span>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      campaign.status === 'active' ? 'bg-green-100 text-green-800' :
                      campaign.status === 'paused' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {campaign.status}
                    </span>
                    <div className="text-xs text-gray-500 mt-1">
                      {campaign.response_rate || 0}% response
                    </div>
                  </div>
                </div>
              </div>
            )) || (
              <div className="p-8 text-center">
                <Mail className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <p className="text-sm text-gray-500">No active campaigns</p>
              </div>
            )}
          </div>
        </div>

        {/* Recent Contacts */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-medium text-gray-900">Recent Contacts</h2>
              <div className="flex items-center space-x-2">
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="px-2 py-1 border border-gray-300 rounded text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="all">All Status</option>
                  <option value="pending">Pending</option>
                  <option value="sent">Sent</option>
                  <option value="opened">Opened</option>
                  <option value="responded">Responded</option>
                </select>
              </div>
            </div>
          </div>
          
          <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
            {contacts.map((contact) => (
              <div key={contact.id} className="p-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                        <Users className="h-4 w-4 text-gray-500" />
                      </div>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">{contact.name}</h4>
                      <p className="text-xs text-gray-500">{contact.title} at {contact.company}</p>
                      <p className="text-xs text-gray-400">{contact.email}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      contact.status === 'responded' ? 'bg-green-100 text-green-800' :
                      contact.status === 'opened' ? 'bg-blue-100 text-blue-800' :
                      contact.status === 'sent' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {contact.status}
                    </span>
                    
                    {contact.status === 'pending' && (
                      <button
                        onClick={() => handleSendMessage(contact.id, contact.message_template)}
                        className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                      >
                        <Send className="h-3 w-3" />
                      </button>
                    )}
                  </div>
                </div>
                
                {contact.last_message && (
                  <div className="mt-2 text-xs text-gray-600 bg-gray-50 p-2 rounded">
                    <span className="font-medium">Last message:</span> {contact.last_message.substring(0, 100)}...
                  </div>
                )}
                
                <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                  {contact.last_contact_date && (
                    <span className="flex items-center">
                      <Clock className="h-3 w-3 mr-1" />
                      {new Date(contact.last_contact_date).toLocaleDateString()}
                    </span>
                  )}
                  {contact.next_followup_date && (
                    <span className="flex items-center">
                      <Calendar className="h-3 w-3 mr-1" />
                      Follow up: {new Date(contact.next_followup_date).toLocaleDateString()}
                    </span>
                  )}
                </div>
              </div>
            )) || (
              <div className="p-8 text-center">
                <Users className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <p className="text-sm text-gray-500">No contacts found</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Campaign Details (if selected) */}
      {selectedCampaign && (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-medium text-gray-900">
                Campaign: {selectedCampaign.name}
              </h2>
              <div className="flex items-center space-x-2">
                <button className="btn btn-secondary btn-sm">
                  <Edit className="h-4 w-4 mr-1" />
                  Edit
                </button>
                <button className="btn btn-danger btn-sm">
                  <Trash2 className="h-4 w-4 mr-1" />
                  Delete
                </button>
              </div>
            </div>
          </div>
          
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <h3 className="text-sm font-medium text-gray-900 mb-3">Campaign Stats</h3>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Total Contacts:</span>
                    <span className="font-medium">{selectedCampaign.total_contacts || 0}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Messages Sent:</span>
                    <span className="font-medium">{selectedCampaign.sent_count || 0}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Open Rate:</span>
                    <span className="font-medium">{selectedCampaign.open_rate || 0}%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Response Rate:</span>
                    <span className="font-medium">{selectedCampaign.response_rate || 0}%</span>
                  </div>
                </div>
              </div>
              
              <div className="md:col-span-2">
                <h3 className="text-sm font-medium text-gray-900 mb-3">Message Template</h3>
                <div className="bg-gray-50 p-4 rounded-md">
                  <p className="text-sm text-gray-700 whitespace-pre-wrap">
                    {selectedCampaign.message_template || 'No template defined'}
                  </p>
                </div>
              </div>
            </div>
            
            {selectedCampaign.next_actions && selectedCampaign.next_actions.length > 0 && (
              <div className="mt-6">
                <h3 className="text-sm font-medium text-gray-900 mb-3">Pending Actions</h3>
                <div className="space-y-2">
                  {selectedCampaign.next_actions.map((action, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-yellow-50 rounded-md">
                      <div className="flex items-center">
                        <AlertCircle className="h-4 w-4 text-yellow-600 mr-2" />
                        <span className="text-sm text-yellow-800">{action.description}</span>
                      </div>
                      <button className="btn btn-primary btn-sm">
                        Execute
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default OutreachCenter