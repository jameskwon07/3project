import { useState, useEffect } from 'react'
import axios from 'axios'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'

const API_BASE = 'http://localhost:8000/api'

function App() {
  const [currentSection, setCurrentSection] = useState('releases')
  const [health, setHealth] = useState({ status: 'unknown', agents_count: 0 })
  const [releases, setReleases] = useState([])
  const [agents, setAgents] = useState([])
  const [deployments, setDeployments] = useState([])

  // Load data
  useEffect(() => {
    updateHealth()
    loadReleases()
    loadAgents()
    loadDeployments()

    const interval = setInterval(() => {
      updateHealth()
      if (currentSection === 'releases') loadReleases()
      if (currentSection === 'agents') loadAgents()
      if (currentSection === 'deployments') loadDeployments()
    }, 5000)

    return () => clearInterval(interval)
  }, [currentSection])

  async function updateHealth() {
    try {
      const response = await axios.get(`${API_BASE}/health`)
      setHealth({ status: 'healthy', agents_count: response.data.agents_count })
    } catch (error) {
      setHealth({ status: 'error', agents_count: 0 })
    }
  }

  async function loadReleases() {
    try {
      const response = await axios.get(`${API_BASE}/releases`)
      setReleases(response.data)
    } catch (error) {
      console.error('Failed to load releases:', error)
    }
  }

  async function loadAgents() {
    try {
      const response = await axios.get(`${API_BASE}/agents`)
      setAgents(response.data)
    } catch (error) {
      console.error('Failed to load agents:', error)
    }
  }

  async function loadDeployments() {
    try {
      const response = await axios.get(`${API_BASE}/deployments/history`)
      setDeployments(response.data)
    } catch (error) {
      console.error('Failed to load deployments:', error)
    }
  }

  const sections = [
    { id: 'releases', icon: '📦', label: 'Release Management' },
    { id: 'agents', icon: '🤖', label: 'Agent Management' },
    { id: 'deployments', icon: '🚀', label: 'Deployment' },
    { id: 'settings', icon: '⚙️', label: 'Settings' },
  ]

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-primary">🔧 Master Agent Manager</h1>
          <div className="flex items-center gap-4">
            <span className={`text-sm ${health.status === 'healthy' ? 'text-green-600' : 'text-red-600'}`}>
              ● {health.status === 'healthy' ? 'Healthy' : 'Error'}
            </span>
            <span className="text-sm text-muted-foreground">Agents: {health.agents_count}</span>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6 flex gap-6">
        {/* Sidebar */}
        <aside className="w-64 flex-shrink-0">
          <nav className="space-y-1">
            {sections.map((section) => (
              <button
                key={section.id}
                onClick={() => setCurrentSection(section.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-md text-left transition-colors ${
                  currentSection === section.id
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-accent text-muted-foreground hover:text-foreground'
                }`}
              >
                <span className="text-xl">{section.icon}</span>
                <span>{section.label}</span>
              </button>
            ))}
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 min-w-0">
          {currentSection === 'releases' && (
            <div>
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold">Release Management</h2>
                <Button>Add Release</Button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {releases.length === 0 ? (
                  <p className="text-muted-foreground">No releases added</p>
                ) : (
                  releases.map((release) => (
                    <Card key={release.id}>
                      <CardHeader>
                        <CardTitle>{release.name}</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-muted-foreground">Version: {release.version}</p>
                      </CardContent>
                    </Card>
                  ))
                )}
              </div>
            </div>
          )}

          {currentSection === 'agents' && (
            <div>
              <h2 className="text-2xl font-bold mb-6">Agent Management</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {agents.length === 0 ? (
                  <p className="text-muted-foreground">No agents registered</p>
                ) : (
                  agents.map((agent) => (
                    <Card key={agent.id}>
                      <CardHeader>
                        <CardTitle>{agent.name}</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-muted-foreground">Platform: {agent.platform}</p>
                        <p className="text-sm text-muted-foreground">Status: {agent.status}</p>
                      </CardContent>
                    </Card>
                  ))
                )}
              </div>
            </div>
          )}

          {currentSection === 'deployments' && (
            <div>
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold">Deployment</h2>
                <Button>New Deployment</Button>
              </div>
              <div className="space-y-4">
                {deployments.length === 0 ? (
                  <p className="text-muted-foreground">No deployments yet</p>
                ) : (
                  deployments.map((deployment) => (
                    <Card key={deployment.id}>
                      <CardHeader>
                        <CardTitle>Deployment to {deployment.agent_name}</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-muted-foreground">Status: {deployment.status}</p>
                      </CardContent>
                    </Card>
                  ))
                )}
              </div>
            </div>
          )}

          {currentSection === 'settings' && (
            <div>
              <h2 className="text-2xl font-bold mb-6">Settings</h2>
              <p className="text-muted-foreground">Settings section (to be implemented)</p>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

export default App

