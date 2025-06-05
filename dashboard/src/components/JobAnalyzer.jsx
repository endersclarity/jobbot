import React, { useState, useMemo } from 'react';
import { 
  Search, 
  Filter, 
  Star, 
  MapPin, 
  DollarSign, 
  Building, 
  Calendar,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Heart,
  Eye,
  Archive
} from 'lucide-react';

const JobAnalyzer = ({ jobs = [] }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFilters, setSelectedFilters] = useState({
    source: 'all',
    location: 'all',
    salaryMin: '',
    salaryMax: '',
    dateRange: 'all',
    desirabilityScore: 'all'
  });
  const [sortBy, setSortBy] = useState('desirability');
  const [sortOrder, setSortOrder] = useState('desc');
  const [viewMode, setViewMode] = useState('detailed'); // detailed, compact, grid
  const [selectedJobs, setSelectedJobs] = useState(new Set());
  const [showFilters, setShowFilters] = useState(false);

  // Job desirability scoring algorithm
  const calculateDesirabilityScore = (job) => {
    let score = 0;
    const factors = [];

    // Salary factor (30% weight)
    if (job.salary) {
      const salaryMatch = job.salary.match(/\$?(\d+(?:,\d+)*)/g);
      if (salaryMatch) {
        const salaryNum = parseInt(salaryMatch[0].replace(/\$|,/g, ''));
        if (salaryNum >= 120000) {
          score += 30;
          factors.push('High salary range');
        } else if (salaryNum >= 80000) {
          score += 20;
          factors.push('Good salary range');
        } else if (salaryNum >= 60000) {
          score += 10;
          factors.push('Fair salary range');
        }
      }
    }

    // Company factor (25% weight)
    const desirableCompanies = [
      'google', 'microsoft', 'apple', 'amazon', 'meta', 'netflix',
      'stripe', 'airbnb', 'uber', 'spotify', 'github', 'slack'
    ];
    if (job.company && desirableCompanies.some(company => 
      job.company.toLowerCase().includes(company)
    )) {
      score += 25;
      factors.push('Top-tier company');
    }

    // Title/Role factor (20% weight)
    const seniorRoles = ['senior', 'lead', 'principal', 'staff', 'architect'];
    const techRoles = ['engineer', 'developer', 'programmer', 'architect'];
    
    if (job.title) {
      const titleLower = job.title.toLowerCase();
      if (seniorRoles.some(role => titleLower.includes(role))) {
        score += 15;
        factors.push('Senior-level position');
      }
      if (techRoles.some(role => titleLower.includes(role))) {
        score += 10;
        factors.push('Technical role match');
      }
    }

    // Location factor (15% weight)
    const preferredLocations = ['remote', 'san francisco', 'seattle', 'new york', 'austin'];
    if (job.location && preferredLocations.some(loc => 
      job.location.toLowerCase().includes(loc)
    )) {
      score += 15;
      factors.push('Preferred location');
    }

    // Recency factor (10% weight)
    if (job.extractedAt) {
      const daysSincePosted = (Date.now() - new Date(job.extractedAt)) / (1000 * 60 * 60 * 24);
      if (daysSincePosted <= 7) {
        score += 10;
        factors.push('Recently posted');
      } else if (daysSincePosted <= 14) {
        score += 5;
        factors.push('Posted within 2 weeks');
      }
    }

    return { score: Math.min(score, 100), factors };
  };

  // Enhanced job data with desirability scores
  const enhancedJobs = useMemo(() => {
    return jobs.map(job => {
      const desirability = calculateDesirabilityScore(job);
      return {
        ...job,
        desirabilityScore: desirability.score,
        desirabilityFactors: desirability.factors,
        id: job.jobId || `${job.title}-${job.company}`.replace(/\s+/g, '-')
      };
    });
  }, [jobs]);

  // Filter and sort jobs
  const filteredAndSortedJobs = useMemo(() => {
    let filtered = enhancedJobs.filter(job => {
      // Search term filter
      if (searchTerm) {
        const searchLower = searchTerm.toLowerCase();
        const searchFields = [job.title, job.company, job.location, job.summary].join(' ').toLowerCase();
        if (!searchFields.includes(searchLower)) return false;
      }

      // Source filter
      if (selectedFilters.source !== 'all' && job.source !== selectedFilters.source) {
        return false;
      }

      // Location filter
      if (selectedFilters.location !== 'all') {
        if (!job.location || !job.location.toLowerCase().includes(selectedFilters.location.toLowerCase())) {
          return false;
        }
      }

      // Salary filter
      if (selectedFilters.salaryMin || selectedFilters.salaryMax) {
        const salaryMatch = job.salary?.match(/\$?(\d+(?:,\d+)*)/g);
        if (salaryMatch) {
          const salary = parseInt(salaryMatch[0].replace(/\$|,/g, ''));
          if (selectedFilters.salaryMin && salary < parseInt(selectedFilters.salaryMin)) return false;
          if (selectedFilters.salaryMax && salary > parseInt(selectedFilters.salaryMax)) return false;
        } else if (selectedFilters.salaryMin || selectedFilters.salaryMax) {
          return false; // Filter out jobs without salary if salary filter is active
        }
      }

      // Desirability score filter
      if (selectedFilters.desirabilityScore !== 'all') {
        const scoreThreshold = parseInt(selectedFilters.desirabilityScore);
        if (job.desirabilityScore < scoreThreshold) return false;
      }

      return true;
    });

    // Sort jobs
    filtered.sort((a, b) => {
      let aValue, bValue;
      
      switch (sortBy) {
        case 'desirability':
          aValue = a.desirabilityScore;
          bValue = b.desirabilityScore;
          break;
        case 'date':
          aValue = new Date(a.extractedAt || 0);
          bValue = new Date(b.extractedAt || 0);
          break;
        case 'salary':
          aValue = a.salary ? parseInt((a.salary.match(/\d+/g) || ['0'])[0]) : 0;
          bValue = b.salary ? parseInt((b.salary.match(/\d+/g) || ['0'])[0]) : 0;
          break;
        case 'company':
          aValue = a.company || '';
          bValue = b.company || '';
          break;
        default:
          aValue = a.title || '';
          bValue = b.title || '';
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    return filtered;
  }, [enhancedJobs, searchTerm, selectedFilters, sortBy, sortOrder]);

  // Get unique values for filter dropdowns
  const filterOptions = useMemo(() => {
    const sources = [...new Set(enhancedJobs.map(job => job.source).filter(Boolean))];
    const locations = [...new Set(enhancedJobs.map(job => job.location).filter(Boolean))];
    
    return { sources, locations };
  }, [enhancedJobs]);

  const handleJobSelection = (jobId, isSelected) => {
    const newSelection = new Set(selectedJobs);
    if (isSelected) {
      newSelection.add(jobId);
    } else {
      newSelection.delete(jobId);
    }
    setSelectedJobs(newSelection);
  };

  const handleBulkAction = (action) => {
    console.log(`Performing ${action} on ${selectedJobs.size} jobs`);
    // Implement bulk actions here
    setSelectedJobs(new Set());
  };

  const getDesirabilityColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    if (score >= 40) return 'text-orange-600';
    return 'text-red-600';
  };

  const getDesirabilityBadge = (score) => {
    if (score >= 80) return 'bg-green-100 text-green-800';
    if (score >= 60) return 'bg-yellow-100 text-yellow-800';
    if (score >= 40) return 'bg-orange-100 text-orange-800';
    return 'bg-red-100 text-red-800';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Job Analysis</h2>
          <p className="text-gray-600">
            {filteredAndSortedJobs.length} jobs • {selectedJobs.size} selected
          </p>
        </div>
        
        {selectedJobs.size > 0 && (
          <div className="flex items-center space-x-2">
            <button 
              onClick={() => handleBulkAction('favorite')}
              className="btn btn-sm btn-secondary"
            >
              <Heart className="h-4 w-4 mr-1" />
              Favorite ({selectedJobs.size})
            </button>
            <button 
              onClick={() => handleBulkAction('archive')}
              className="btn btn-sm btn-secondary"
            >
              <Archive className="h-4 w-4 mr-1" />
              Archive
            </button>
          </div>
        )}
      </div>

      {/* Search and Filters */}
      <div className="space-y-4">
        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search jobs by title, company, location..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input pl-10 w-full"
          />
        </div>

        {/* Filter Toggle */}
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="btn btn-secondary flex items-center space-x-2"
        >
          <Filter className="h-4 w-4" />
          <span>Filters</span>
          {showFilters ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </button>

        {/* Filters Panel */}
        {showFilters && (
          <div className="bg-gray-50 p-4 rounded-lg grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {/* Source Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Source</label>
              <select
                value={selectedFilters.source}
                onChange={(e) => setSelectedFilters(prev => ({ ...prev, source: e.target.value }))}
                className="input"
              >
                <option value="all">All Sources</option>
                {filterOptions.sources.map(source => (
                  <option key={source} value={source}>{source}</option>
                ))}
              </select>
            </div>

            {/* Location Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
              <select
                value={selectedFilters.location}
                onChange={(e) => setSelectedFilters(prev => ({ ...prev, location: e.target.value }))}
                className="input"
              >
                <option value="all">All Locations</option>
                <option value="remote">Remote</option>
                <option value="san francisco">San Francisco</option>
                <option value="new york">New York</option>
                <option value="seattle">Seattle</option>
                <option value="austin">Austin</option>
              </select>
            </div>

            {/* Salary Range */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Salary Min</label>
              <input
                type="number"
                placeholder="60000"
                value={selectedFilters.salaryMin}
                onChange={(e) => setSelectedFilters(prev => ({ ...prev, salaryMin: e.target.value }))}
                className="input"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Salary Max</label>
              <input
                type="number"
                placeholder="200000"
                value={selectedFilters.salaryMax}
                onChange={(e) => setSelectedFilters(prev => ({ ...prev, salaryMax: e.target.value }))}
                className="input"
              />
            </div>

            {/* Desirability Score */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Min Score</label>
              <select
                value={selectedFilters.desirabilityScore}
                onChange={(e) => setSelectedFilters(prev => ({ ...prev, desirabilityScore: e.target.value }))}
                className="input"
              >
                <option value="all">Any Score</option>
                <option value="80">Excellent (80+)</option>
                <option value="60">Good (60+)</option>
                <option value="40">Fair (40+)</option>
              </select>
            </div>
          </div>
        )}

        {/* Sort and View Controls */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-gray-700">Sort by:</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="input input-sm"
              >
                <option value="desirability">Desirability Score</option>
                <option value="date">Date Posted</option>
                <option value="salary">Salary</option>
                <option value="company">Company</option>
                <option value="title">Job Title</option>
              </select>
            </div>
            
            <button
              onClick={() => setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')}
              className="btn btn-sm btn-secondary"
            >
              {sortOrder === 'asc' ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </button>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setViewMode('compact')}
              className={`btn btn-sm ${viewMode === 'compact' ? 'btn-primary' : 'btn-secondary'}`}
            >
              Compact
            </button>
            <button
              onClick={() => setViewMode('detailed')}
              className={`btn btn-sm ${viewMode === 'detailed' ? 'btn-primary' : 'btn-secondary'}`}
            >
              Detailed
            </button>
          </div>
        </div>
      </div>

      {/* Jobs List */}
      <div className="space-y-4">
        {filteredAndSortedJobs.length === 0 ? (
          <div className="text-center py-12">
            <Search className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No jobs found</h3>
            <p className="text-gray-600">Try adjusting your search criteria or filters.</p>
          </div>
        ) : (
          filteredAndSortedJobs.map((job) => (
            <JobCard
              key={job.id}
              job={job}
              viewMode={viewMode}
              isSelected={selectedJobs.has(job.id)}
              onSelect={(isSelected) => handleJobSelection(job.id, isSelected)}
              getDesirabilityColor={getDesirabilityColor}
              getDesirabilityBadge={getDesirabilityBadge}
            />
          ))
        )}
      </div>
    </div>
  );
};

// Job Card Component
const JobCard = ({ job, viewMode, isSelected, onSelect, getDesirabilityColor, getDesirabilityBadge }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (viewMode === 'compact') {
    return (
      <div className={`border rounded-lg p-4 hover:bg-gray-50 ${isSelected ? 'ring-2 ring-blue-500' : ''}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={isSelected}
              onChange={(e) => onSelect(e.target.checked)}
              className="h-4 w-4 text-blue-600"
            />
            <div className="flex-1">
              <h3 className="font-medium text-gray-900">{job.title}</h3>
              <p className="text-sm text-gray-600">{job.company} • {job.location}</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {job.salary && (
              <span className="text-sm font-medium text-green-600">{job.salary}</span>
            )}
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDesirabilityBadge(job.desirabilityScore)}`}>
              {job.desirabilityScore}%
            </span>
            {job.url && (
              <a
                href={job.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800"
              >
                <ExternalLink className="h-4 w-4" />
              </a>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`border rounded-lg p-6 hover:bg-gray-50 ${isSelected ? 'ring-2 ring-blue-500' : ''}`}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start space-x-3">
          <input
            type="checkbox"
            checked={isSelected}
            onChange={(e) => onSelect(e.target.checked)}
            className="h-4 w-4 text-blue-600 mt-1"
          />
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900">{job.title}</h3>
            <div className="flex items-center space-x-4 mt-1">
              <div className="flex items-center text-gray-600">
                <Building className="h-4 w-4 mr-1" />
                {job.company}
              </div>
              {job.location && (
                <div className="flex items-center text-gray-600">
                  <MapPin className="h-4 w-4 mr-1" />
                  {job.location}
                </div>
              )}
              {job.salary && (
                <div className="flex items-center text-green-600">
                  <DollarSign className="h-4 w-4 mr-1" />
                  {job.salary}
                </div>
              )}
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <div className="text-right">
            <div className={`text-2xl font-bold ${getDesirabilityColor(job.desirabilityScore)}`}>
              {job.desirabilityScore}%
            </div>
            <div className="text-xs text-gray-500">Desirability</div>
          </div>
          {job.url && (
            <a
              href={job.url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-sm btn-secondary"
            >
              <ExternalLink className="h-4 w-4 mr-1" />
              View Job
            </a>
          )}
        </div>
      </div>

      {job.summary && (
        <div className="mb-4">
          <p className="text-gray-700 text-sm line-clamp-2">{job.summary}</p>
        </div>
      )}

      {/* Desirability Factors */}
      {job.desirabilityFactors && job.desirabilityFactors.length > 0 && (
        <div className="mb-4">
          <div className="flex items-center space-x-2 mb-2">
            <Star className="h-4 w-4 text-yellow-500" />
            <span className="text-sm font-medium text-gray-700">Why this job scored well:</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {job.desirabilityFactors.map((factor, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
              >
                {factor}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Job Metadata */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center space-x-4">
          <span>Source: {job.source}</span>
          {job.extractedAt && (
            <div className="flex items-center">
              <Calendar className="h-3 w-3 mr-1" />
              {new Date(job.extractedAt).toLocaleDateString()}
            </div>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          <button 
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-blue-600 hover:text-blue-800"
          >
            <Eye className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Expanded Details */}
      {isExpanded && job.summary && (
        <div className="mt-4 pt-4 border-t">
          <h4 className="font-medium text-gray-900 mb-2">Job Description</h4>
          <p className="text-sm text-gray-700 whitespace-pre-line">{job.summary}</p>
        </div>
      )}
    </div>
  );
};

export default JobAnalyzer;