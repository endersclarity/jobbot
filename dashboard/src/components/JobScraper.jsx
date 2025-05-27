import React, { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { 
  Search, 
  MapPin, 
  Building, 
  Play,
  Loader2,
  CheckCircle,
  XCircle,
  Globe
} from 'lucide-react'
import { scrapingApi } from '../services/api'

function JobScraper() {
  const [formData, setFormData] = useState({
    search_term: 'software engineer',
    location: 'Grass Valley, CA',
    max_jobs: 50,
    job_site: 'indeed'
  })
  
  const [results, setResults] = useState(null)

  // Mutation for scraping jobs
  const scrapeMutation = useMutation({
    mutationFn: (data) => scrapingApi.scrapeJobs(data),
    onSuccess: (response) => {
      setResults(response.data)
      console.log('Scraping success:', response.data)
    },
    onError: (error) => {
      console.error('Scraping error:', error)
      setResults({ 
        success: false, 
        error: error.response?.data?.detail || error.message 
      })
    }
  })

  // Mutation for background scraping
  const backgroundScrapeMutation = useMutation({
    mutationFn: (data) => scrapingApi.scrapeJobsBackground(data),
    onSuccess: (response) => {
      setResults(response.data)
      console.log('Background scraping started:', response.data)
    },
    onError: (error) => {
      console.error('Background scraping error:', error)
      setResults({ 
        success: false, 
        error: error.response?.data?.detail || error.message 
      })
    }
  })

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: name === 'max_jobs' ? parseInt(value) : value
    }))
  }

  const handleScrape = async () => {
    setResults(null)
    scrapeMutation.mutate(formData)
  }

  const handleBackgroundScrape = async () => {
    setResults(null)
    backgroundScrapeMutation.mutate(formData)
  }

  const isLoading = scrapeMutation.isPending || backgroundScrapeMutation.isPending

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Job Scraper</h1>
        <p className="text-gray-600">Scrape jobs from various job boards using our Crawlee infrastructure</p>
      </div>

      {/* Scraping Form */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">🔥 Scrape Jobs</h3>
        </div>
        <div className="card-content">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Left Column - Form */}
            <div className="space-y-4">
              {/* Search Term */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Search className="inline h-4 w-4 mr-1" />
                  Job Search Keywords
                </label>
                <input
                  type="text"
                  name="search_term"
                  value={formData.search_term}
                  onChange={handleInputChange}
                  placeholder="e.g., software engineer, data scientist, marketing manager"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              {/* Location */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <MapPin className="inline h-4 w-4 mr-1" />
                  Location
                </label>
                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleInputChange}
                  placeholder="e.g., San Francisco, CA or Remote"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              {/* Job Site */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Building className="inline h-4 w-4 mr-1" />
                  Job Site
                </label>
                <select
                  name="job_site"
                  value={formData.job_site}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="indeed">Indeed</option>
                  <option value="linkedin">LinkedIn (Coming Soon)</option>
                  <option value="glassdoor">Glassdoor (Coming Soon)</option>
                </select>
              </div>

              {/* Max Jobs */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Maximum Jobs to Scrape
                </label>
                <select
                  name="max_jobs"
                  value={formData.max_jobs}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value={10}>10 jobs (Quick test)</option>
                  <option value={25}>25 jobs</option>
                  <option value={50}>50 jobs (Recommended)</option>
                  <option value={100}>100 jobs</option>
                  <option value={200}>200 jobs (Max)</option>
                </select>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-3 pt-4">
                <button
                  onClick={handleScrape}
                  disabled={isLoading}
                  className="flex-1 btn btn-primary flex items-center justify-center space-x-2"
                >
                  {scrapeMutation.isPending ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Play className="h-4 w-4" />
                  )}
                  <span>Scrape Now</span>
                </button>
                
                <button
                  onClick={handleBackgroundScrape}
                  disabled={isLoading}
                  className="flex-1 btn btn-secondary flex items-center justify-center space-x-2"
                >
                  {backgroundScrapeMutation.isPending ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Globe className="h-4 w-4" />
                  )}
                  <span>Background</span>
                </button>
              </div>
            </div>

            {/* Right Column - Info */}
            <div className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 mb-2">🚀 What happens when you scrape:</h4>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>• Uses our enterprise Crawlee infrastructure</li>
                  <li>• Anti-detection measures bypass 403 errors</li>
                  <li>• Intelligent rate limiting respects target sites</li>
                  <li>• Extracts structured job data automatically</li>
                  <li>• Saves to database with duplicate detection</li>
                </ul>
              </div>

              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h4 className="font-medium text-green-900 mb-2">💰 Economic Impact:</h4>
                <ul className="text-sm text-green-700 space-y-1">
                  <li>• Our cost: $0.00 (unlimited scraping)</li>
                  <li>• Apify equivalent: $30+ per 1,000 jobs</li>
                  <li>• <strong>WE EAT THEIR LUNCH! 🔥</strong></li>
                </ul>
              </div>

              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-2">Scraping Options:</h4>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li>• <strong>Scrape Now:</strong> Real-time results, wait for completion</li>
                  <li>• <strong>Background:</strong> Fire-and-forget for large jobs</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Results */}
      {results && (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title flex items-center space-x-2">
              {results.success ? (
                <CheckCircle className="h-5 w-5 text-green-600" />
              ) : (
                <XCircle className="h-5 w-5 text-red-600" />
              )}
              <span>Scraping Results</span>
            </h3>
          </div>
          <div className="card-content">
            {results.success ? (
              <div className="space-y-4">
                {/* Success Message */}
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <p className="text-green-800 font-medium">{results.message}</p>
                </div>

                {/* Results Summary */}
                {results.summary && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">{results.summary.jobs_found}</div>
                      <div className="text-sm text-gray-600">Jobs Found</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">{results.summary.jobs_saved}</div>
                      <div className="text-sm text-gray-600">Jobs Saved</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-orange-600">{results.summary.duplicates_skipped}</div>
                      <div className="text-sm text-gray-600">Duplicates Skipped</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-red-600">{results.summary.save_errors}</div>
                      <div className="text-sm text-gray-600">Errors</div>
                    </div>
                  </div>
                )}

                {/* Task ID for background jobs */}
                {results.task_id && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-blue-800">
                      <strong>Background Task Started!</strong><br />
                      Task ID: <code className="bg-blue-100 px-2 py-1 rounded">{results.task_id}</code><br />
                      Estimated duration: {results.estimated_duration}
                    </p>
                  </div>
                )}

                {/* Scraping Details */}
                {results.scraping && (
                  <div>
                    <h4 className="font-medium mb-2">Scraping Details:</h4>
                    <div className="bg-gray-50 rounded-lg p-3">
                      <pre className="text-sm text-gray-700">
                        {JSON.stringify(results.scraping, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-800">
                  <strong>Scraping Failed:</strong><br />
                  {results.error}
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default JobScraper