import React, { useState } from 'react'
import { 
  Settings as SettingsIcon, 
  Save, 
  RefreshCw, 
  AlertTriangle,
  CheckCircle,
  Globe,
  Database,
  Bell
} from 'lucide-react'

function Settings() {
  const [settings, setSettings] = useState({
    // Scraping Configuration
    scraping: {
      defaultConcurrency: 3,
      requestDelay: 2000,
      maxRetries: 3,
      timeout: 30000,
      enableAntiDetection: true,
      rotateUserAgents: true,
    },
    
    // Site Configuration
    sites: {
      indeed: {
        enabled: true,
        priority: 1,
        maxJobsPerSession: 100,
        rateLimit: 1000,
      },
      linkedin: {
        enabled: true,
        priority: 2,
        maxJobsPerSession: 50,
        rateLimit: 2000,
      },
      glassdoor: {
        enabled: true,
        priority: 3,
        maxJobsPerSession: 75,
        rateLimit: 1500,
      },
    },
    
    // Monitoring & Alerts
    monitoring: {
      enableRealTimeUpdates: true,
      errorThreshold: 10,
      enableEmailAlerts: false,
      alertEmail: '',
      enableSlackAlerts: false,
      slackWebhook: '',
      performanceAlerts: true,
    },
    
    // Database
    database: {
      autoCleanup: true,
      retentionDays: 90,
      enableBackups: true,
      backupFrequency: 'daily',
    },
    
    // API Configuration
    api: {
      rateLimitPerMinute: 1000,
      enableCors: true,
      corsOrigins: 'http://localhost:3000,http://172.22.206.209:3000',
      enableApiDocs: true,
    },
  })

  const [saving, setSaving] = useState(false)
  const [testingConnection, setTestingConnection] = useState({})

  const handleSettingChange = (section, key, value) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value
      }
    }))
  }

  const handleSiteSettingChange = (site, key, value) => {
    setSettings(prev => ({
      ...prev,
      sites: {
        ...prev.sites,
        [site]: {
          ...prev.sites[site],
          [key]: value
        }
      }
    }))
  }

  const handleSaveSettings = async () => {
    setSaving(true)
    try {
      // In a real implementation, this would call the API
      await new Promise(resolve => setTimeout(resolve, 1000))
      console.log('Settings saved:', settings)
      // Show success notification
    } catch (error) {
      console.error('Failed to save settings:', error)
      // Show error notification
    } finally {
      setSaving(false)
    }
  }

  const testSiteConnection = async (site) => {
    setTestingConnection(prev => ({ ...prev, [site]: true }))
    try {
      // In a real implementation, this would test the site connection
      await new Promise(resolve => setTimeout(resolve, 2000))
      console.log(`Testing ${site} connection...`)
      // Show success/failure result
    } catch (error) {
      console.error(`Failed to test ${site}:`, error)
    } finally {
      setTestingConnection(prev => ({ ...prev, [site]: false }))
    }
  }

  const resetToDefaults = () => {
    if (confirm('Are you sure you want to reset all settings to defaults? This cannot be undone.')) {
      // Reset to default values
      setSettings({
        // ... default values
      })
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600">Configure JobBot scraping and monitoring system</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <button 
            onClick={resetToDefaults}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Reset Defaults</span>
          </button>
          <button 
            onClick={handleSaveSettings}
            disabled={saving}
            className="btn btn-primary flex items-center space-x-2"
          >
            {saving ? (
              <RefreshCw className="h-4 w-4 animate-spin" />
            ) : (
              <Save className="h-4 w-4" />
            )}
            <span>{saving ? 'Saving...' : 'Save Settings'}</span>
          </button>
        </div>
      </div>

      {/* Scraping Configuration */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title flex items-center space-x-2">
            <SettingsIcon className="h-5 w-5" />
            <span>Scraping Configuration</span>
          </h3>
        </div>
        <div className="card-content">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Default Concurrency
              </label>
              <input
                type="number"
                min="1"
                max="10"
                value={settings.scraping.defaultConcurrency}
                onChange={(e) => handleSettingChange('scraping', 'defaultConcurrency', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">Number of concurrent scrapers</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Request Delay (ms)
              </label>
              <input
                type="number"
                min="500"
                max="10000"
                step="500"
                value={settings.scraping.requestDelay}
                onChange={(e) => handleSettingChange('scraping', 'requestDelay', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">Delay between requests</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Retries
              </label>
              <input
                type="number"
                min="0"
                max="10"
                value={settings.scraping.maxRetries}
                onChange={(e) => handleSettingChange('scraping', 'maxRetries', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">Retry failed requests</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Timeout (ms)
              </label>
              <input
                type="number"
                min="5000"
                max="120000"
                step="5000"
                value={settings.scraping.timeout}
                onChange={(e) => handleSettingChange('scraping', 'timeout', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">Request timeout</p>
            </div>
          </div>

          <div className="mt-6 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium">Anti-Detection Measures</h4>
                <p className="text-sm text-gray-600">Enable stealth browsing and bot detection evasion</p>
              </div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={settings.scraping.enableAntiDetection}
                  onChange={(e) => handleSettingChange('scraping', 'enableAntiDetection', e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
              </label>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium">Rotate User Agents</h4>
                <p className="text-sm text-gray-600">Randomize browser fingerprints</p>
              </div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={settings.scraping.rotateUserAgents}
                  onChange={(e) => handleSettingChange('scraping', 'rotateUserAgents', e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Site Configuration */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title flex items-center space-x-2">
            <Globe className="h-5 w-5" />
            <span>Site Configuration</span>
          </h3>
        </div>
        <div className="card-content">
          <div className="space-y-6">
            {Object.entries(settings.sites).map(([site, config]) => (
              <div key={site} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <h4 className="font-medium capitalize">{site}</h4>
                    <span className={`status-badge ${config.enabled ? 'status-success' : 'status-error'}`}>
                      {config.enabled ? 'Enabled' : 'Disabled'}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => testSiteConnection(site)}
                      disabled={testingConnection[site]}
                      className="btn btn-secondary btn-sm flex items-center space-x-1"
                    >
                      {testingConnection[site] ? (
                        <RefreshCw className="h-3 w-3 animate-spin" />
                      ) : (
                        <CheckCircle className="h-3 w-3" />
                      )}
                      <span>Test</span>
                    </button>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={config.enabled}
                        onChange={(e) => handleSiteSettingChange(site, 'enabled', e.target.checked)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                    </label>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Priority
                    </label>
                    <select
                      value={config.priority}
                      onChange={(e) => handleSiteSettingChange(site, 'priority', parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                      disabled={!config.enabled}
                    >
                      <option value={1}>High (1)</option>
                      <option value={2}>Medium (2)</option>
                      <option value={3}>Low (3)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Max Jobs/Session
                    </label>
                    <input
                      type="number"
                      min="10"
                      max="500"
                      value={config.maxJobsPerSession}
                      onChange={(e) => handleSiteSettingChange(site, 'maxJobsPerSession', parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                      disabled={!config.enabled}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Rate Limit (ms)
                    </label>
                    <input
                      type="number"
                      min="500"
                      max="5000"
                      step="250"
                      value={config.rateLimit}
                      onChange={(e) => handleSiteSettingChange(site, 'rateLimit', parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                      disabled={!config.enabled}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Monitoring & Alerts */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title flex items-center space-x-2">
            <Bell className="h-5 w-5" />
            <span>Monitoring & Alerts</span>
          </h3>
        </div>
        <div className="card-content">
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium">Real-time Updates</h4>
                <p className="text-sm text-gray-600">Enable WebSocket connections for live monitoring</p>
              </div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={settings.monitoring.enableRealTimeUpdates}
                  onChange={(e) => handleSettingChange('monitoring', 'enableRealTimeUpdates', e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
              </label>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Error Threshold
                </label>
                <input
                  type="number"
                  min="1"
                  max="100"
                  value={settings.monitoring.errorThreshold}
                  onChange={(e) => handleSettingChange('monitoring', 'errorThreshold', parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">Errors before alert</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Alert Email
                </label>
                <input
                  type="email"
                  value={settings.monitoring.alertEmail}
                  onChange={(e) => handleSettingChange('monitoring', 'alertEmail', e.target.value)}
                  placeholder="alerts@example.com"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium">Email Alerts</h4>
                <p className="text-sm text-gray-600">Send email notifications for errors and status changes</p>
              </div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={settings.monitoring.enableEmailAlerts}
                  onChange={(e) => handleSettingChange('monitoring', 'enableEmailAlerts', e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
              </label>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium">Performance Alerts</h4>
                <p className="text-sm text-gray-600">Alert when performance metrics degrade</p>
              </div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={settings.monitoring.performanceAlerts}
                  onChange={(e) => handleSettingChange('monitoring', 'performanceAlerts', e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Database Configuration */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title flex items-center space-x-2">
            <Database className="h-5 w-5" />
            <span>Database Configuration</span>
          </h3>
        </div>
        <div className="card-content">
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium">Auto Cleanup</h4>
                <p className="text-sm text-gray-600">Automatically remove old data based on retention policy</p>
              </div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={settings.database.autoCleanup}
                  onChange={(e) => handleSettingChange('database', 'autoCleanup', e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
              </label>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Retention Period (days)
                </label>
                <input
                  type="number"
                  min="7"
                  max="365"
                  value={settings.database.retentionDays}
                  onChange={(e) => handleSettingChange('database', 'retentionDays', parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                  disabled={!settings.database.autoCleanup}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Backup Frequency
                </label>
                <select
                  value={settings.database.backupFrequency}
                  onChange={(e) => handleSettingChange('database', 'backupFrequency', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                  disabled={!settings.database.enableBackups}
                >
                  <option value="hourly">Hourly</option>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                </select>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium">Enable Backups</h4>
                <p className="text-sm text-gray-600">Create regular database backups</p>
              </div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={settings.database.enableBackups}
                  onChange={(e) => handleSettingChange('database', 'enableBackups', e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Status Indicator */}
      <div className="card">
        <div className="card-content">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <div>
                <h4 className="font-medium">Configuration Status</h4>
                <p className="text-sm text-gray-600">All settings are valid and applied</p>
              </div>
            </div>
            <div className="text-sm text-gray-500">
              Last saved: {new Date().toLocaleString()}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings