import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './components/Dashboard'
import ScrapingSessions from './components/ScrapingSessions'
import Analytics from './components/Analytics'
import Settings from './components/Settings'
import CompanyDiscovery from './components/business/CompanyDiscovery'
import OpportunityPipeline from './components/business/OpportunityPipeline'
import MarketAnalysis from './components/business/MarketAnalysis'
import OutreachCenter from './components/business/OutreachCenter'
import AdvancedAnalytics from './components/advanced/AdvancedAnalytics'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/sessions" element={<ScrapingSessions />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/advanced-analytics" element={<AdvancedAnalytics />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/companies" element={<CompanyDiscovery />} />
        <Route path="/opportunities" element={<OpportunityPipeline />} />
        <Route path="/market" element={<MarketAnalysis />} />
        <Route path="/outreach" element={<OutreachCenter />} />
      </Routes>
    </Layout>
  )
}

export default App