import { useState, useEffect, useMemo } from 'react'
import {
  useReactTable,
  getCoreRowModel,
  getFilteredRowModel,
  flexRender,
  createColumnHelper,
} from '@tanstack/react-table'
import axios from 'axios'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Eye, EyeOff } from 'lucide-react'

const API_BASE = 'http://localhost:8000/api'

function App() {
  // Load saved section from localStorage, default to 'releases'
  const [currentSection, setCurrentSection] = useState(() => {
    const saved = localStorage.getItem('selectedSection')
    return saved || 'releases'
  })
  const [health, setHealth] = useState({ status: 'unknown', agents_count: 0 })
  const [releases, setReleases] = useState([])
  const [agents, setAgents] = useState([])
  const [deployments, setDeployments] = useState([])
  const [releaseModalOpen, setReleaseModalOpen] = useState(false)
  const [deploymentModalOpen, setDeploymentModalOpen] = useState(false)
  const [selectedReleases, setSelectedReleases] = useState([])
  const [selectedVersions, setSelectedVersions] = useState({}) // { release_id: version_tag }
  const [releaseVersions, setReleaseVersions] = useState({}) // { release_id: [versions] }
  const [loadingVersions, setLoadingVersions] = useState({}) // { release_id: true/false }
  const [selectedAgent, setSelectedAgent] = useState('')
  const [releaseForm, setReleaseForm] = useState({
    github_url: '',
  })
  const [githubToken, setGithubToken] = useState('')
  const [githubTokenPreview, setGithubTokenPreview] = useState('')
  const [hasGitHubToken, setHasGitHubToken] = useState(false)
  const [showGitHubToken, setShowGitHubToken] = useState(false)
  const [columnFilters, setColumnFilters] = useState([])

  // TanStack Table setup for deployments
  const columnHelper = createColumnHelper()
  const columns = useMemo(
    () => [
      columnHelper.accessor('agent_name', {
        id: 'agent_name',
        header: () => <div className="font-medium">Agent</div>,
        cell: (info) => (
          <div className="font-medium">{info.getValue()}</div>
        ),
        filterFn: (row, columnId, filterValue) => {
          if (!filterValue || filterValue === '__all__') return true
          const deployment = row.original
          return deployment.agent_id === filterValue
        },
      }),
      columnHelper.accessor((row) => row.release_tags?.join(', ') || row.release_ids?.join(', ') || 'N/A', {
        id: 'releases',
        header: () => <div className="font-medium">Releases</div>,
        cell: (info) => info.getValue(),
        filterFn: (row, columnId, filterValue) => {
          if (!filterValue) return true
          const deployment = row.original
          const releaseTags = deployment.release_tags?.join(' ') || ''
          return releaseTags.toLowerCase().includes(filterValue.toLowerCase())
        },
      }),
      columnHelper.accessor('status', {
        header: () => <div className="font-medium">Status</div>,
        cell: (info) => {
          const status = info.getValue()
          return (
            <span
              className={`px-2 py-1 rounded text-xs font-medium ${
                status === 'success'
                  ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
                  : status === 'failed'
                  ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                  : status === 'pending'
                  ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
                  : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'
              }`}
            >
              {status}
            </span>
          )
        },
      }),
      columnHelper.accessor('created_at', {
        header: () => <div className="font-medium">Created</div>,
        cell: (info) => {
          const createdDate = new Date(info.getValue())
          const today = new Date()
          today.setHours(0, 0, 0, 0)
          const deployDateOnly = new Date(createdDate)
          deployDateOnly.setHours(0, 0, 0, 0)

          if (deployDateOnly.getTime() === today.getTime()) {
            return createdDate.toLocaleTimeString()
          } else {
            return createdDate.toLocaleDateString()
          }
        },
        filterFn: (row, columnId, filterValue) => {
          if (!filterValue) return true
          const filterDate = new Date(filterValue)
          const deployDate = new Date(row.original.created_at)
          return deployDate >= filterDate
        },
      }),
      columnHelper.accessor('error_message', {
        header: () => <div className="font-medium">Error</div>,
        cell: (info) => {
          const errorMessage = info.getValue()
          return errorMessage ? (
            <span className="text-red-600 text-sm">{errorMessage}</span>
          ) : (
            <span className="text-muted-foreground text-sm">-</span>
          )
        },
      }),
    ],
    [agents]
  )

  const table = useReactTable({
    data: deployments,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    state: {
      columnFilters,
    },
    onColumnFiltersChange: setColumnFilters,
  })

  // Load data
  useEffect(() => {
    updateHealth()
    loadReleases()
    loadAgents()
    loadDeployments()
    loadGitHubToken()

    const interval = setInterval(() => {
      updateHealth()
      if (currentSection === 'releases') loadReleases()
      if (currentSection === 'agents') loadAgents()
      if (currentSection === 'deployments') loadDeployments()
      if (currentSection === 'settings') loadGitHubToken()
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

  async function createRelease(e) {
    e.preventDefault()
    try {
      const releaseData = {
        github_url: releaseForm.github_url,
      }
      await axios.post(`${API_BASE}/releases`, releaseData)
      setReleaseModalOpen(false)
      setReleaseForm({ github_url: '' })
      await loadReleases()
    } catch (error) {
      console.error('Failed to create release:', error)
      alert('Failed to create release: ' + (error.response?.data?.detail || error.message))
    }
  }

  async function deleteRelease(releaseId) {
    if (!confirm('Are you sure you want to remove this release?')) {
      return
    }
    try {
      await axios.delete(`${API_BASE}/releases/${releaseId}`)
      await loadReleases()
    } catch (error) {
      console.error('Failed to delete release:', error)
      alert('Failed to delete release')
    }
  }

  async function deleteAgent(agentId) {
    if (!confirm('Are you sure you want to remove this agent?')) {
      return
    }
    try {
      await axios.delete(`${API_BASE}/agents/${agentId}`)
      await loadAgents()
    } catch (error) {
      console.error('Failed to delete agent:', error)
      alert('Failed to delete agent')
    }
  }

  async function createDeployment(e) {
    e.preventDefault()
    if (!selectedAgent || selectedReleases.length === 0) {
      alert('Please select an agent and at least one release')
      return
    }
    
    // Check if all selected releases have versions selected
    const missingVersions = selectedReleases.filter((id) => !selectedVersions[id])
    if (missingVersions.length > 0) {
      alert('Please select a version for all selected releases')
      return
    }
    
    try {
      const deploymentData = {
        agent_id: selectedAgent,
        release_ids: selectedReleases,
        release_versions: selectedReleases.map((id) => selectedVersions[id]),
      }
      await axios.post(`${API_BASE}/deployments`, deploymentData)
      setDeploymentModalOpen(false)
      setSelectedAgent('')
      setSelectedReleases([])
      setSelectedVersions({})
      await loadDeployments()
    } catch (error) {
      console.error('Failed to create deployment:', error)
      alert('Failed to create deployment: ' + (error.response?.data?.detail || error.message))
    }
  }

  async function handleReleaseToggle(releaseId) {
    const isSelected = selectedReleases.includes(releaseId)
    
    if (isSelected) {
      // Unselect release
      setSelectedReleases((prev) => prev.filter((id) => id !== releaseId))
      setSelectedVersions((prev) => {
        const newVersions = { ...prev }
        delete newVersions[releaseId]
        return newVersions
      })
    } else {
      // Select release and fetch versions
      setSelectedReleases((prev) => [...prev, releaseId])
      
      // Check if versions are already loaded
      if (!releaseVersions[releaseId]) {
        await fetchReleaseVersions(releaseId)
      }
    }
  }

  async function fetchReleaseVersions(releaseId) {
    setLoadingVersions((prev) => ({ ...prev, [releaseId]: true }))
    try {
      const response = await axios.get(`${API_BASE}/releases/${releaseId}/versions`)
      setReleaseVersions((prev) => ({ ...prev, [releaseId]: response.data }))
      // Auto-select first version if available
      if (response.data.length > 0) {
        setSelectedVersions((prev) => ({ ...prev, [releaseId]: response.data[0].tag_name }))
      }
    } catch (error) {
      console.error('Failed to fetch release versions:', error)
      alert('Failed to fetch release versions: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoadingVersions((prev) => ({ ...prev, [releaseId]: false }))
    }
  }

  async function loadGitHubToken() {
    try {
      const response = await axios.get(`${API_BASE}/settings/github-token`)
      setHasGitHubToken(response.data.has_token)
      if (response.data.has_token) {
        setGithubTokenPreview(response.data.token_preview)
      }
    } catch (error) {
      console.error('Failed to load GitHub token:', error)
    }
  }

  async function saveGitHubToken(e) {
    e.preventDefault()
    try {
      await axios.post(`${API_BASE}/settings/github-token`, { token: githubToken })
      setGithubToken('')
      await loadGitHubToken()
      alert('GitHub token saved successfully')
    } catch (error) {
      console.error('Failed to save GitHub token:', error)
      alert('Failed to save GitHub token: ' + (error.response?.data?.detail || error.message))
    }
  }

  async function updateGitHubToken(e) {
    e.preventDefault()
    try {
      await axios.post(`${API_BASE}/settings/github-token`, { token: githubToken })
      setGithubToken('')
      await loadGitHubToken()
      alert('GitHub token updated successfully')
    } catch (error) {
      console.error('Failed to update GitHub token:', error)
      alert('Failed to update GitHub token: ' + (error.response?.data?.detail || error.message))
    }
  }

  async function removeGitHubToken() {
    if (!confirm('Are you sure you want to remove the GitHub token?')) {
      return
    }
    try {
      await axios.delete(`${API_BASE}/settings/github-token`)
      setHasGitHubToken(false)
      setGithubTokenPreview('')
      alert('GitHub token removed successfully')
    } catch (error) {
      console.error('Failed to remove GitHub token:', error)
      alert('Failed to remove GitHub token')
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
                onClick={() => {
                  setCurrentSection(section.id)
                  localStorage.setItem('selectedSection', section.id)
                }}
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
                <Dialog open={releaseModalOpen} onOpenChange={setReleaseModalOpen}>
                  <DialogTrigger asChild>
                    <Button>Add Release</Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Add Release</DialogTitle>
                      <DialogDescription>
                        Add a new GitHub release to the system
                      </DialogDescription>
                    </DialogHeader>
                    <form onSubmit={createRelease} className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="github-url">GitHub Release URL *</Label>
                        <Input
                          id="github-url"
                          type="url"
                          value={releaseForm.github_url}
                          onChange={(e) => setReleaseForm({ ...releaseForm, github_url: e.target.value })}
                          placeholder="https://github.com/owner/repo/releases/"
                          required
                        />
                        <p className="text-xs text-muted-foreground">
                          Enter the GitHub releases page URL (e.g., https://github.com/jameskwon07/3project/releases/). The repository name will be used as the release name.
                        </p>
                      </div>
                      <div className="flex justify-end gap-2">
                        <Button
                          type="button"
                          variant="outline"
                          onClick={() => {
                            setReleaseModalOpen(false)
                            setReleaseForm({ github_url: '' })
                          }}
                        >
                          Cancel
                        </Button>
                        <Button type="submit">Add Release</Button>
                      </div>
                    </form>
                  </DialogContent>
                </Dialog>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {releases.length === 0 ? (
                  <p className="text-muted-foreground">No releases added</p>
                ) : (
                  releases.map((release) => (
                    <Card key={release.id} className="flex flex-col">
                      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle>{release.name}</CardTitle>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => deleteRelease(release.id)}
                        >
                          Remove
                        </Button>
                      </CardHeader>
                      <CardContent className="flex flex-col flex-1">
                        {release.description && (
                          <p className="text-sm text-muted-foreground mb-2">{release.description}</p>
                        )}
                        <div className="mt-auto">
                          {release.download_url && (
                            <a
                              href={release.download_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-sm text-primary hover:underline block"
                            >
                              Go to releases
                            </a>
                          )}
                        </div>
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
                      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle>{agent.name}</CardTitle>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => deleteAgent(agent.id)}
                        >
                          Remove
                        </Button>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-muted-foreground">Platform: {agent.platform}</p>
                        <p className="text-sm">
                          Status: <span className={`font-medium ${agent.status?.toLowerCase() === 'online' ? 'text-green-600' : 'text-red-600'}`}>
                            {agent.status}
                          </span>
                        </p>
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
                <Dialog open={deploymentModalOpen} onOpenChange={setDeploymentModalOpen}>
                  <DialogTrigger asChild>
                    <Button>New Deployment</Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-2xl">
                    <DialogHeader>
                      <DialogTitle>New Deployment</DialogTitle>
                      <DialogDescription>
                        Select an agent and one or more releases to deploy (Batch Deployment)
                      </DialogDescription>
                    </DialogHeader>
                    <form onSubmit={createDeployment} className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="deployment-agent">Agent *</Label>
                        <Select value={selectedAgent} onValueChange={setSelectedAgent} required>
                          <SelectTrigger id="deployment-agent">
                            <SelectValue placeholder="Select an agent..." />
                          </SelectTrigger>
                          <SelectContent>
                            {agents.map((agent) => (
                              <SelectItem key={agent.id} value={agent.id}>
                                {agent.name} ({agent.platform})
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-4">
                        <div className="space-y-2">
                          <Label>Releases * (Multiple selection)</Label>
                          <div className="border rounded-md p-4 max-h-60 overflow-y-auto space-y-2">
                            {releases.length === 0 ? (
                              <p className="text-sm text-muted-foreground">No releases available. Please add a release first.</p>
                            ) : (
                              releases.map((release) => (
                                <div key={release.id} className="flex items-center space-x-2">
                                  <Checkbox
                                    id={`release-${release.id}`}
                                    checked={selectedReleases.includes(release.id)}
                                    onCheckedChange={() => handleReleaseToggle(release.id)}
                                  />
                                  <label
                                    htmlFor={`release-${release.id}`}
                                    className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
                                  >
                                    {release.name}
                                    {release.version && ` - ${release.version}`}
                                    {release.tag_name && release.tag_name !== release.name && ` (${release.tag_name})`}
                                  </label>
                                </div>
                              ))
                            )}
                          </div>
                        </div>
                        
                        {/* Version Selection for Selected Releases */}
                        {selectedReleases.length > 0 && (
                          <div className="space-y-3">
                            <Label>Select Versions *</Label>
                            {selectedReleases.map((releaseId) => {
                              const release = releases.find((r) => r.id === releaseId)
                              const versions = releaseVersions[releaseId] || []
                              const isLoading = loadingVersions[releaseId]
                              
                              return (
                                <div key={releaseId} className="space-y-2">
                                  <Label htmlFor={`version-${releaseId}`} className="text-sm font-medium">
                                    {release?.name || releaseId}
                                  </Label>
                                  {isLoading ? (
                                    <p className="text-sm text-muted-foreground">Loading versions...</p>
                                  ) : versions.length === 0 ? (
                                    <p className="text-sm text-red-600">No versions available</p>
                                  ) : (
                                    <Select
                                      value={selectedVersions[releaseId] || ''}
                                      onValueChange={(value) => {
                                        setSelectedVersions((prev) => ({ ...prev, [releaseId]: value }))
                                      }}
                                    >
                                      <SelectTrigger id={`version-${releaseId}`}>
                                        <SelectValue placeholder="Select a version..." />
                                      </SelectTrigger>
                                      <SelectContent className="bg-white">
                                        {versions.map((version) => (
                                          <SelectItem key={version.tag_name} value={version.tag_name}>
                                            {version.name} ({version.tag_name})
                                          </SelectItem>
                                        ))}
                                      </SelectContent>
                                    </Select>
                                  )}
                                </div>
                              )
                            })}
                          </div>
                        )}
                      </div>
                      <div className="flex justify-end gap-2">
                        <Button
                          type="button"
                          variant="outline"
                          onClick={() => {
                            setDeploymentModalOpen(false)
                            setSelectedAgent('')
                            setSelectedReleases([])
                            setSelectedVersions({})
                          }}
                        >
                          Cancel
                        </Button>
                        <Button type="submit">Deploy</Button>
                      </div>
                    </form>
                  </DialogContent>
                </Dialog>
              </div>
              {/* Table Section */}
              <Card>
                <CardContent className="pt-6">
                  {deployments.length === 0 ? (
                    <p className="text-muted-foreground text-center py-8">No deployments yet</p>
                  ) : (
                    <Table>
                      <TableHeader>
                        {table.getHeaderGroups().map((headerGroup) => (
                          <TableRow key={headerGroup.id}>
                            {headerGroup.headers.map((header) => (
                              <TableHead key={header.id}>
                                {header.isPlaceholder
                                  ? null
                                  : flexRender(header.column.columnDef.header, header.getContext())}
                              </TableHead>
                            ))}
                          </TableRow>
                        ))}
                        <TableRow>
                          <TableHead>
                            <Select
                              value={table.getColumn('agent_name')?.getFilterValue() || '__all__'}
                              onValueChange={(value) => {
                                if (value === '__all__') {
                                  table.getColumn('agent_name')?.setFilterValue(undefined)
                                } else {
                                  table.getColumn('agent_name')?.setFilterValue(value)
                                }
                              }}
                            >
                              <SelectTrigger className="h-9 w-full">
                                <SelectValue placeholder="All agents" />
                              </SelectTrigger>
                              <SelectContent className="bg-white">
                                <SelectItem value="__all__">All agents</SelectItem>
                                {agents.map((agent) => (
                                  <SelectItem key={agent.id} value={agent.id}>
                                    {agent.name}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </TableHead>
                          <TableHead>
                            <Input
                              className="h-9"
                              placeholder="Search releases..."
                              value={String(table.getColumn('releases')?.getFilterValue() ?? '')}
                              onChange={(e) => {
                                const value = e.target.value
                                table.getColumn('releases')?.setFilterValue(value || undefined)
                              }}
                            />
                          </TableHead>
                          <TableHead></TableHead>
                          <TableHead>
                            <Input
                              className="h-9"
                              type="date"
                              value={String(table.getColumn('created_at')?.getFilterValue() ?? '')}
                              onChange={(e) => {
                                const value = e.target.value
                                table.getColumn('created_at')?.setFilterValue(value || undefined)
                              }}
                            />
                          </TableHead>
                          <TableHead></TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {table.getRowModel().rows.map((row) => (
                          <TableRow key={row.id}>
                            {row.getVisibleCells().map((cell) => (
                              <TableCell key={cell.id}>
                                {flexRender(cell.column.columnDef.cell, cell.getContext())}
                              </TableCell>
                            ))}
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  )}
                </CardContent>
              </Card>
            </div>
          )}

          {currentSection === 'settings' && (
            <div>
              <h2 className="text-2xl font-bold mb-6">Settings</h2>
              <Card>
                <CardHeader>
                  <CardTitle>GitHub Token</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {hasGitHubToken ? (
                    <div className="space-y-4">
                      <div>
                        <p className="text-sm text-muted-foreground mb-2">
                          Current token: {githubTokenPreview}
                        </p>
                      </div>
                      <form onSubmit={updateGitHubToken} className="space-y-4">
                        <div className="space-y-2">
                          <Label htmlFor="github-token-update">New GitHub Token</Label>
                          <div className="relative">
                            <Input
                              id="github-token-update"
                              type={showGitHubToken ? 'text' : 'password'}
                              value={githubToken}
                              onChange={(e) => setGithubToken(e.target.value)}
                              placeholder="Enter new GitHub token"
                              className="pr-10"
                            />
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                              onClick={() => setShowGitHubToken(!showGitHubToken)}
                            >
                              {showGitHubToken ? (
                                <EyeOff className="h-4 w-4 text-muted-foreground" />
                              ) : (
                                <Eye className="h-4 w-4 text-muted-foreground" />
                              )}
                            </Button>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button type="submit" variant="outline">
                            Update Token
                          </Button>
                          <Button
                            type="button"
                            variant="destructive"
                            onClick={removeGitHubToken}
                          >
                            Remove Token
                          </Button>
                        </div>
                      </form>
                    </div>
                  ) : (
                    <form onSubmit={saveGitHubToken} className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="github-token">GitHub Token</Label>
                        <div className="relative">
                          <Input
                            id="github-token"
                            type={showGitHubToken ? 'text' : 'password'}
                            value={githubToken}
                            onChange={(e) => setGithubToken(e.target.value)}
                            placeholder="Enter GitHub personal access token"
                            required
                            className="pr-10"
                          />
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                            onClick={() => setShowGitHubToken(!showGitHubToken)}
                          >
                            {showGitHubToken ? (
                              <EyeOff className="h-4 w-4 text-muted-foreground" />
                            ) : (
                              <Eye className="h-4 w-4 text-muted-foreground" />
                            )}
                          </Button>
                        </div>
                        <p className="text-xs text-muted-foreground">
                          Required for accessing GitHub releases
                        </p>
                      </div>
                      <Button type="submit">Add Token</Button>
                    </form>
                  )}
                </CardContent>
              </Card>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

export default App

