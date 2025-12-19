# Deployment Automation and Version Management System

One-click deployment and version tracking system for developers. Deploy software to target PCs with a single button, automatically record all deployment history, and track software version changes on each PC in real-time.

## Overview

This project provides a Master-Agent architecture for automated software deployment and version management. It enables developers to deploy software to Windows PCs and manage firmware files with minimal effort while maintaining a complete audit trail of all deployments.

### Key Features

- **One-click deployment**: Deploy software to target PCs with a single button
- **Deployment history tracking**: Automatically record and track all deployment activities
- **Version monitoring**: Real-time tracking of software version changes on each PC
- **Firmware deployment**: Support for Windows executables and firmware files
- **Cross-platform**: Windows and macOS (Intel/Apple Silicon) support

### Architecture

- **Master**: Python-based web server + web frontend (Agent management and monitoring)
  - Deployed on Linux using Docker and Docker Compose
  - Provides Agent build artifacts for download
  - Follows Clean Architecture principles
- **Agent**: C# based client (Windows/macOS executables)
  - Auto-registration with Master and heartbeat transmission
  - Performs deployment tasks and reports status

## Quick Start

### Prerequisites

**Development Environment:**
- macOS 14+ (development environment)
- Cursor IDE (recommended) or any other IDE
- Git, GitHub

**Master:**
- Python 3.8+
- Node.js 18+ and npm
- Docker & Docker Compose (for production deployment)

**Agent:**
- .NET 8.0 SDK
- Windows or macOS (build environment)

### Running Master Server

**Option 1: Run both services together (Recommended for development)**

```bash
# Using Python script (macOS/Linux/Windows)
cd master
python run.py

# Or using shell script (macOS/Linux)
cd master
./run.sh

# Or using batch file (Windows)
cd master
run.bat
```

**Option 2: Run services separately**

```bash
# Terminal 1 - Backend
cd master/backend
python main.py

# Terminal 2 - Frontend
cd master/frontend
npm run dev
```

**Option 3: Using Docker Compose (Recommended for production)**

```bash
# Production mode
cd master
docker-compose up -d

# Development mode with hot reload
cd master
docker-compose -f docker-compose.dev.yml up
```

Services will be available at:
- Backend API: `http://localhost:8000`
- Frontend UI: `http://localhost:3000`

### Building and Running Agent

```bash
# Build Agent for all platforms
python deploy-agent.py --version 1.0.0

# Or build for specific platform
python deploy-agent.py --version 1.0.0 --platform windows

# Run Agent
# Windows:
dist/agent-windows/Agent.exe

# macOS:
dist/agent-macos-x64/Agent        # Intel Mac
dist/agent-macos-arm64/Agent      # Apple Silicon
```

## Tutorial

### Project Structure

```
3project/
├── master/                 # Master server and frontend
│   ├── backend/            # Python FastAPI server
│   │   ├── main.py
│   │   └── requirements.txt
│   ├── frontend/           # Web frontend (Vite)
│   │   ├── src/
│   │   ├── index.html
│   │   └── package.json
│   ├── run.py             # Python script to run both services
│   ├── run.sh             # Shell script to run both services (macOS/Linux)
│   ├── run.bat            # Batch script to run both services (Windows)
│   ├── docker-compose.yml # Docker Compose for production
│   ├── docker-compose.dev.yml # Docker Compose for development
│   ├── Dockerfile.backend # Backend Docker image
│   ├── Dockerfile.frontend # Frontend Docker image (production)
│   └── Dockerfile.frontend.dev # Frontend Docker image (development)
├── agent/                  # C# Agent client
│   ├── Program/
│   │   ├── Program.cs
│   │   ├── Agent.csproj
│   │   └── appsettings.json
│   ├── Tests/              # Agent unit tests
│   └── run.sh              # Agent run script
├── scripts/                # Build scripts
│   ├── build-agent.sh      # Agent build for Mac/Linux
│   ├── build-agent.bat     # Agent build for Windows
│   └── init.ps1            # Project initialization
├── config/                 # Configuration files
│   └── config.example.json # Configuration example
├── dist/                   # Build output (gitignore)
├── .github/                # GitHub Actions
│   └── workflows/
│       └── ci.yml         # CI/CD workflow
├── deploy.py              # Unified deployment script
├── deploy-master.py       # Master-only deployment
├── deploy-agent.py        # Agent-only deployment
├── version.py             # Version management utility
├── VERSION                # Current version file
└── LICENSE                # MIT License
```

### Master API Endpoints

- `GET /api/agents` - List all agents
- `GET /api/agents/{id}` - Get specific agent
- `POST /api/agents/register` - Register agent / heartbeat
- `DELETE /api/agents/{id}` - Unregister agent
- `GET /api/health` - Health check

### Agent Configuration

Configure Agent in `agent/appsettings.json`:

```json
{
  "MasterUrl": "http://localhost:8000",
  "AgentName": "",
  "HeartbeatInterval": 10000,
  "Version": "1.0.0"
}
```

### Version Management

The project uses automatic version management system.

**Version Tagging Rule:** `{deployment-stage}-{date}-{number}`

Examples:
- `production-20250115-001`
- `staging-20250115-002`
- `development-20250115-001`

**Usage:**
```bash
# Check current version
cat VERSION

# Manually update version
python -c "from version import VersionManager; vm = VersionManager(); vm.update_version('1.0.0')"

# Auto-increment version
python -c "from version import VersionManager; vm = VersionManager(); vm.increment_version('patch')"
```

### Development Workflow

**Local Deployment:**
1. Update version using `version.py`
2. Deploy Master using `deploy-master.py`
3. Build Agent using `deploy-agent.py`
4. Git tags are automatically created

**Production Deployment (Docker):**
Master is deployed on Linux using Docker and Docker Compose:

```bash
# Build and start services
cd master
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Agent build artifacts are deployed together and can be downloaded from Master server.

### CI/CD (GitHub Actions)

The project uses GitHub Actions for automated builds and deployments.

**Triggers:**
- Push events on `main`, `master`, `develop` branches
- Pull requests to `main`/`master` branches

**Current Workflow:**
1. Master Backend: Python linting and testing
2. Master Frontend: Node.js build and artifact storage
3. Agent Windows: Windows x64 executable build
4. Agent macOS: macOS x64/ARM64 executable build

**Build Artifacts:**
- Agent executables (Windows, macOS x64, macOS ARM64)
- Master Frontend build artifacts
- Stored as GitHub Actions artifacts (downloadable)

Workflow file: `.github/workflows/ci.yml`

**Testing Workflows Locally:**

Before pushing changes, test workflows locally using `act`:

```bash
# Install act (macOS)
brew install act

# Test all jobs
./scripts/test-workflow.sh

# Test specific job
act -j master-backend
act -j master-frontend

# List all available jobs
act -l
```

Windows users can install act from: https://github.com/nektos/act#installation

**Git Pre-Push Hook (Recommended):**

To automatically test workflows before every push, set up the pre-push hook:

```bash
# macOS/Linux
./scripts/setup-git-hooks.sh

# Windows
scripts\setup-git-hooks.bat
```

After setup, the pre-push hook will automatically test critical workflow jobs before allowing push. If tests fail, the push will be blocked.

To skip the hook temporarily (not recommended):
```bash
git push --no-verify
```

**Important:** Always test workflows locally before pushing to ensure they run successfully.

**Future Plans (to be added per requirements):**
1. Upload build artifacts to Master automatically
2. Master-Agent integration tests
3. Deployment pipeline automation

### Development Principles

**Architecture:**
- **Clean Architecture**: All code strictly follows Clean Architecture principles
- **Layer Separation**: Clear separation of domain, application, and infrastructure layers

**Testing:**
- **Unit tests required**: Always write unit tests when adding functions
- **Mock usage**: Use mocks for testing external system integrations
- **Test coverage**: Maintain test coverage for core logic

**Note:** This project is currently a personal development project, so there is no code review process in place.

## Important Notes

**Core features mentioned in requirements (please add detailed documentation):**
- One-click deployment workflow
- Deployment history and audit trail
- Version tracking per PC
- Firmware file deployment support
- Material Design theme for frontend (please add implementation details)

**Additional details to be added:**
- Detailed deployment procedures
- Configuration options
- Troubleshooting guide
- API documentation
- Agent capabilities and extensions

## License

Copyright (c) 2025 codingbridge.blog

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
