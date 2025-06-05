import React, { useState, useEffect } from 'react';
import { 
  Database, 
  Download, 
  Upload, 
  RefreshCw, 
  AlertCircle, 
  CheckCircle,
  Trash2,
  FileJson,
  Filter
} from 'lucide-react';

const JobStorage = ({ onJobsLoaded, onStorageUpdate }) => {
  const [jobs, setJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    total: 0,
    bySource: {},
    lastUpdated: null,
    duplicates: 0
  });

  // Local Storage Management
  const STORAGE_KEY = 'jobbot_collected_jobs';
  const METADATA_KEY = 'jobbot_job_metadata';

  useEffect(() => {
    loadJobsFromStorage();
  }, []);

  const loadJobsFromStorage = () => {
    try {
      setIsLoading(true);
      const storedJobs = localStorage.getItem(STORAGE_KEY);
      const storedMetadata = localStorage.getItem(METADATA_KEY);
      
      if (storedJobs) {
        const parsedJobs = JSON.parse(storedJobs);
        const parsedMetadata = storedMetadata ? JSON.parse(storedMetadata) : {};
        
        setJobs(parsedJobs);
        updateStats(parsedJobs);
        
        if (onJobsLoaded) {
          onJobsLoaded(parsedJobs);
        }
      }
    } catch (err) {
      setError('Failed to load jobs from storage');
      console.error('Storage load error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const saveJobsToStorage = (jobsToSave) => {
    try {
      const metadata = {
        lastUpdated: new Date().toISOString(),
        totalJobs: jobsToSave.length,
        sources: [...new Set(jobsToSave.map(job => job.source).filter(Boolean))]
      };

      localStorage.setItem(STORAGE_KEY, JSON.stringify(jobsToSave));
      localStorage.setItem(METADATA_KEY, JSON.stringify(metadata));
      
      setJobs(jobsToSave);
      updateStats(jobsToSave);
      
      if (onStorageUpdate) {
        onStorageUpdate({ jobs: jobsToSave, metadata });
      }
      
      return true;
    } catch (err) {
      setError('Failed to save jobs to storage');
      console.error('Storage save error:', err);
      return false;
    }
  };

  const updateStats = (jobList) => {
    const bySource = {};
    let duplicateCount = 0;
    const seen = new Set();

    jobList.forEach(job => {
      // Count by source
      const source = job.source || 'unknown';
      bySource[source] = (bySource[source] || 0) + 1;

      // Count duplicates
      const identifier = job.url || `${job.title}_${job.company}`.toLowerCase();
      if (seen.has(identifier)) {
        duplicateCount++;
      } else {
        seen.add(identifier);
      }
    });

    setStats({
      total: jobList.length,
      bySource,
      lastUpdated: new Date().toISOString(),
      duplicates: duplicateCount
    });
  };

  const handleFileImport = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsLoading(true);
    setError(null);

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const importedData = JSON.parse(e.target.result);
        
        // Handle different import formats
        let importedJobs = [];
        
        if (Array.isArray(importedData)) {
          importedJobs = importedData;
        } else if (importedData.jobs && Array.isArray(importedData.jobs)) {
          importedJobs = importedData.jobs;
        } else if (importedData.data && Array.isArray(importedData.data)) {
          importedJobs = importedData.data;
        } else {
          throw new Error('Invalid job data format');
        }

        // Merge with existing jobs (avoiding duplicates)
        const mergedJobs = mergeJobs(jobs, importedJobs);
        
        if (saveJobsToStorage(mergedJobs)) {
          setError(null);
          if (onJobsLoaded) {
            onJobsLoaded(mergedJobs);
          }
        }
      } catch (err) {
        setError(`Failed to import file: ${err.message}`);
        console.error('Import error:', err);
      } finally {
        setIsLoading(false);
        event.target.value = ''; // Reset file input
      }
    };

    reader.readAsText(file);
  };

  const mergeJobs = (existingJobs, newJobs) => {
    const merged = [...existingJobs];
    const existingUrls = new Set(existingJobs.map(job => job.url).filter(Boolean));
    const existingTitles = new Set(existingJobs.map(job => 
      `${job.title}_${job.company}`.toLowerCase()
    ));

    let addedCount = 0;
    
    newJobs.forEach(newJob => {
      const isDuplicate = newJob.url ? 
        existingUrls.has(newJob.url) :
        existingTitles.has(`${newJob.title}_${newJob.company}`.toLowerCase());

      if (!isDuplicate) {
        // Add import timestamp
        merged.push({
          ...newJob,
          importedAt: new Date().toISOString(),
          jobId: newJob.jobId || generateJobId(newJob)
        });
        addedCount++;
      }
    });

    console.log(`Merged ${addedCount} new jobs (${newJobs.length - addedCount} duplicates skipped)`);
    return merged;
  };

  const generateJobId = (job) => {
    const identifier = job.url || `${job.title}_${job.company}_${job.location}`;
    return btoa(identifier).replace(/[^a-zA-Z0-9]/g, '').substring(0, 16);
  };

  const handleExport = () => {
    try {
      const exportData = {
        metadata: {
          exportedAt: new Date().toISOString(),
          totalJobs: jobs.length,
          sources: Object.keys(stats.bySource),
          version: '1.0'
        },
        jobs: jobs
      };

      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
      });
      
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `jobbot_export_${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to export jobs');
      console.error('Export error:', err);
    }
  };

  const handleClearStorage = () => {
    if (window.confirm('Are you sure you want to clear all stored jobs? This cannot be undone.')) {
      localStorage.removeItem(STORAGE_KEY);
      localStorage.removeItem(METADATA_KEY);
      setJobs([]);
      updateStats([]);
      if (onJobsLoaded) {
        onJobsLoaded([]);
      }
    }
  };

  const removeDuplicates = () => {
    setIsLoading(true);
    
    try {
      const unique = [];
      const seen = new Set();
      
      jobs.forEach(job => {
        const identifier = job.url || `${job.title}_${job.company}`.toLowerCase();
        if (!seen.has(identifier)) {
          seen.add(identifier);
          unique.push(job);
        }
      });

      if (saveJobsToStorage(unique)) {
        console.log(`Removed ${jobs.length - unique.length} duplicate jobs`);
        if (onJobsLoaded) {
          onJobsLoaded(unique);
        }
      }
    } catch (err) {
      setError('Failed to remove duplicates');
      console.error('Deduplication error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Job Storage</h2>
          <p className="text-gray-600">Manage your collected job data</p>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={loadJobsFromStorage}
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

      {/* Storage Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center">
            <Database className="h-8 w-8 text-blue-500 mr-3" />
            <div>
              <div className="text-2xl font-bold text-blue-900">{stats.total}</div>
              <div className="text-sm text-blue-700">Total Jobs</div>
            </div>
          </div>
        </div>

        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center">
            <CheckCircle className="h-8 w-8 text-green-500 mr-3" />
            <div>
              <div className="text-2xl font-bold text-green-900">
                {Object.keys(stats.bySource).length}
              </div>
              <div className="text-sm text-green-700">Sources</div>
            </div>
          </div>
        </div>

        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center">
            <Filter className="h-8 w-8 text-yellow-500 mr-3" />
            <div>
              <div className="text-2xl font-bold text-yellow-900">{stats.duplicates}</div>
              <div className="text-sm text-yellow-700">Duplicates</div>
            </div>
          </div>
        </div>

        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <div className="flex items-center">
            <RefreshCw className="h-8 w-8 text-purple-500 mr-3" />
            <div>
              <div className="text-sm font-medium text-purple-900">
                {stats.lastUpdated ? 
                  new Date(stats.lastUpdated).toLocaleDateString() : 
                  'Never'
                }
              </div>
              <div className="text-sm text-purple-700">Last Updated</div>
            </div>
          </div>
        </div>
      </div>

      {/* Source Breakdown */}
      {Object.keys(stats.bySource).length > 0 && (
        <div className="bg-white border rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Jobs by Source</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(stats.bySource).map(([source, count]) => (
              <div key={source} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="font-medium capitalize">{source}</span>
                <span className="text-lg font-bold text-blue-600">{count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Storage Actions */}
      <div className="bg-white border rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Storage Actions</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Import Jobs */}
          <div>
            <label className="btn btn-primary w-full cursor-pointer">
              <Upload className="h-4 w-4 mr-2" />
              Import Jobs
              <input
                type="file"
                accept=".json"
                onChange={handleFileImport}
                className="hidden"
                disabled={isLoading}
              />
            </label>
            <p className="text-xs text-gray-500 mt-1">Import from JSON file</p>
          </div>

          {/* Export Jobs */}
          <div>
            <button
              onClick={handleExport}
              disabled={jobs.length === 0}
              className="btn btn-secondary w-full"
            >
              <Download className="h-4 w-4 mr-2" />
              Export Jobs
            </button>
            <p className="text-xs text-gray-500 mt-1">Export to JSON file</p>
          </div>

          {/* Remove Duplicates */}
          <div>
            <button
              onClick={removeDuplicates}
              disabled={isLoading || stats.duplicates === 0}
              className="btn btn-warning w-full"
            >
              <Filter className="h-4 w-4 mr-2" />
              Remove Duplicates
            </button>
            <p className="text-xs text-gray-500 mt-1">
              {stats.duplicates} duplicates found
            </p>
          </div>

          {/* Clear Storage */}
          <div>
            <button
              onClick={handleClearStorage}
              disabled={jobs.length === 0}
              className="btn btn-danger w-full"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Clear All
            </button>
            <p className="text-xs text-gray-500 mt-1">Permanently delete all jobs</p>
          </div>
        </div>
      </div>

      {/* Data Format Help */}
      <div className="bg-gray-50 border rounded-lg p-4">
        <div className="flex items-start">
          <FileJson className="h-5 w-5 text-gray-500 mr-2 mt-0.5" />
          <div>
            <h4 className="font-medium text-gray-900">Import Data Format</h4>
            <p className="text-sm text-gray-600 mt-1">
              Import JSON files containing job arrays. Supported formats:
            </p>
            <ul className="text-xs text-gray-500 mt-2 space-y-1">
              <li>• Direct array: <code>[{job1}, {job2}, ...]</code></li>
              <li>• Object with jobs: <code>{jobs: [{job1}, {job2}, ...]}</code></li>
              <li>• Object with data: <code>{data: [{job1}, {job2}, ...]}</code></li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobStorage;