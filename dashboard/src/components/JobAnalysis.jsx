import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Database, 
  RefreshCw,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import JobAnalyzer from './JobAnalyzer';
import JobStorage from './JobStorage';

const JobAnalysis = () => {
  const [activeTab, setActiveTab] = useState('analyzer');
  const [jobs, setJobs] = useState([]);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const tabs = [
    {
      id: 'analyzer',
      label: 'Job Analyzer',
      icon: FileText,
      description: 'Analyze and filter collected job data'
    },
    {
      id: 'storage', 
      label: 'Data Storage',
      icon: Database,
      description: 'Manage job data storage and imports'
    }
  ];

  // Load jobs from storage on component mount
  useEffect(() => {
    loadJobsFromStorage();
  }, []);

  const loadJobsFromStorage = () => {
    try {
      setIsLoading(true);
      const storedJobs = localStorage.getItem('jobbot_collected_jobs');
      
      if (storedJobs) {
        const parsedJobs = JSON.parse(storedJobs);
        setJobs(parsedJobs);
        setLastUpdate(new Date().toISOString());
        setError(null);
      } else {
        setJobs([]);
      }
    } catch (err) {
      setError('Failed to load jobs from storage');
      console.error('Job loading error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleJobsLoaded = (loadedJobs) => {
    setJobs(loadedJobs);
    setLastUpdate(new Date().toISOString());
    setError(null);
  };

  const handleStorageUpdate = ({ jobs: updatedJobs, metadata }) => {
    setJobs(updatedJobs);
    setLastUpdate(metadata.lastUpdated);
    setError(null);
  };

  const handleRefresh = () => {
    loadJobsFromStorage();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Job Analysis Center</h1>
          <p className="text-gray-600 mt-1">
            Analyze, filter, and manage your collected job opportunities
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          {/* Status Indicator */}
          <div className="flex items-center space-x-2">
            {error ? (
              <div className="flex items-center text-red-600">
                <AlertCircle className="h-4 w-4 mr-1" />
                <span className="text-sm">Error</span>
              </div>
            ) : (
              <div className="flex items-center text-green-600">
                <CheckCircle className="h-4 w-4 mr-1" />
                <span className="text-sm">{jobs.length} jobs loaded</span>
              </div>
            )}
          </div>

          {/* Refresh Button */}
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className="btn btn-secondary"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
            <span className="text-red-700">{error}</span>
          </div>
        </div>
      )}

      {/* Statistics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center">
            <Database className="h-8 w-8 text-blue-500 mr-3" />
            <div>
              <div className="text-2xl font-bold text-blue-900">{jobs.length}</div>
              <div className="text-sm text-blue-700">Total Jobs</div>
            </div>
          </div>
        </div>

        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center">
            <CheckCircle className="h-8 w-8 text-green-500 mr-3" />
            <div>
              <div className="text-2xl font-bold text-green-900">
                {jobs.filter(job => job.salary).length}
              </div>
              <div className="text-sm text-green-700">With Salary</div>
            </div>
          </div>
        </div>

        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <div className="flex items-center">
            <FileText className="h-8 w-8 text-purple-500 mr-3" />
            <div>
              <div className="text-2xl font-bold text-purple-900">
                {[...new Set(jobs.map(job => job.source).filter(Boolean))].length}
              </div>
              <div className="text-sm text-purple-700">Sources</div>
            </div>
          </div>
        </div>

        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center">
            <RefreshCw className="h-8 w-8 text-yellow-500 mr-3" />
            <div>
              <div className="text-sm font-medium text-yellow-900">
                {lastUpdate ? 
                  new Date(lastUpdate).toLocaleDateString() : 
                  'Never'
                }
              </div>
              <div className="text-sm text-yellow-700">Last Updated</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`group inline-flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                  isActive
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className={`mr-2 h-5 w-5 ${
                  isActive 
                    ? 'text-blue-500' 
                    : 'text-gray-400 group-hover:text-gray-500'
                }`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="mt-6">
        {activeTab === 'analyzer' && (
          <JobAnalyzer 
            jobs={jobs}
            onJobsUpdate={handleJobsLoaded}
          />
        )}
        
        {activeTab === 'storage' && (
          <JobStorage 
            onJobsLoaded={handleJobsLoaded}
            onStorageUpdate={handleStorageUpdate}
          />
        )}
      </div>

      {/* Help Section */}
      {jobs.length === 0 && (
        <div className="bg-gray-50 border rounded-lg p-6">
          <div className="text-center">
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Job Data Found</h3>
            <p className="text-gray-600 mb-4">
              Get started by importing job data or running a scraping session.
            </p>
            <div className="flex justify-center space-x-4">
              <button 
                onClick={() => setActiveTab('storage')}
                className="btn btn-secondary"
              >
                Import Job Data
              </button>
              <button 
                onClick={() => window.location.href = '/scrape'}
                className="btn btn-primary"
              >
                Start Scraping
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default JobAnalysis;