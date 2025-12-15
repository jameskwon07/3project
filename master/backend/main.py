"""
Master Backend - Agent Management Web Server
FastAPI-based RESTful API server
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
from datetime import datetime
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uvicorn
import os

from database import get_db, init_db
from db_models import AgentDB, ReleaseDB, DeploymentDB, SettingsDB, AgentStatusEnum, DeploymentStatusEnum
from models import (
    Agent, AgentRegister, AgentStatus,
    Release, ReleaseCreate,
    Deployment, DeploymentCreate, DeploymentComplete, DeploymentStatus
)

app = FastAPI(title="Master Agent Manager", version="1.0.0")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()


# CORS configuration (for frontend connection)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (frontend build)
# Try different paths for different environments
frontend_dist_paths = [
    Path(__file__).parent.parent / "frontend" / "dist",
    Path("/app/frontend/dist"),  # Docker path
    Path("frontend/dist"),  # Alternative path
]

frontend_dist = None
for path in frontend_dist_paths:
    if path.exists():
        frontend_dist = path
        break

if frontend_dist:
    app.mount("/static", StaticFiles(directory=str(frontend_dist)), name="static")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Master Agent Manager API", "version": "1.0.0"}


# ==================== Agent Management ====================

@app.get("/api/agents", response_model=List[Agent])
async def get_agents(db: AsyncSession = Depends(get_db)):
    """List all agents"""
    result = await db.execute(select(AgentDB))
    agents_db = result.scalars().all()
    
    return [
        Agent(
            id=agent.id,
            name=agent.name,
            platform=agent.platform,
            version=agent.version,
            status=AgentStatus(agent.status.value),
            last_seen=agent.last_seen,
            ip_address=agent.ip_address,
        )
        for agent in agents_db
    ]


@app.get("/api/agents/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Get specific agent"""
    result = await db.execute(select(AgentDB).where(AgentDB.id == agent_id))
    agent_db = result.scalar_one_or_none()
    
    if not agent_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return Agent(
        id=agent_db.id,
        name=agent_db.name,
        platform=agent_db.platform,
        version=agent_db.version,
        status=AgentStatus(agent_db.status.value),
        last_seen=agent_db.last_seen,
        ip_address=agent_db.ip_address,
    )


@app.post("/api/agents/register", response_model=Agent)
async def register_agent(agent_data: AgentRegister, db: AsyncSession = Depends(get_db)):
    """Register agent / heartbeat"""
    import uuid
    
    # Check if agent exists
    result = await db.execute(select(AgentDB).where(AgentDB.name == agent_data.name))
    existing_agent = result.scalar_one_or_none()
    
    if existing_agent:
        # Update existing agent
        existing_agent.platform = agent_data.platform
        existing_agent.version = agent_data.version
        existing_agent.status = AgentStatusEnum.ONLINE
        existing_agent.last_seen = datetime.now()
        existing_agent.ip_address = agent_data.ip_address
        await db.commit()
        await db.refresh(existing_agent)
        
        return Agent(
            id=existing_agent.id,
            name=existing_agent.name,
            platform=existing_agent.platform,
            version=existing_agent.version,
            status=AgentStatus(existing_agent.status.value),
            last_seen=existing_agent.last_seen,
            ip_address=existing_agent.ip_address,
        )
    else:
        # Create new agent
        agent_id = str(uuid.uuid4())
        agent_db = AgentDB(
            id=agent_id,
            name=agent_data.name,
            platform=agent_data.platform,
            version=agent_data.version,
            status=AgentStatusEnum.ONLINE,
            last_seen=datetime.now(),
            ip_address=agent_data.ip_address,
        )
        db.add(agent_db)
        await db.commit()
        await db.refresh(agent_db)
        
        return Agent(
            id=agent_db.id,
            name=agent_db.name,
            platform=agent_db.platform,
            version=agent_db.version,
            status=AgentStatus(agent_db.status.value),
            last_seen=agent_db.last_seen,
            ip_address=agent_db.ip_address,
        )


@app.delete("/api/agents/{agent_id}")
async def delete_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Unregister agent"""
    result = await db.execute(select(AgentDB).where(AgentDB.id == agent_id))
    agent_db = result.scalar_one_or_none()
    
    if not agent_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    db.delete(agent_db)
    await db.commit()
    return {"message": "Agent deleted"}


# ==================== Release Management ====================

@app.get("/api/releases", response_model=List[Release])
async def get_releases(db: AsyncSession = Depends(get_db)):
    """List all releases"""
    result = await db.execute(select(ReleaseDB))
    releases_db = result.scalars().all()
    
    return [
        Release(
            id=release.id,
            tag_name=release.tag_name,
            name=release.name,
            version=release.version or "",
            release_date=release.release_date,
            download_url=release.download_url,
            description=release.description,
            assets=release.assets or [],
        )
        for release in releases_db
    ]


@app.get("/api/releases/{release_id}", response_model=Release)
async def get_release(release_id: str, db: AsyncSession = Depends(get_db)):
    """Get specific release"""
    result = await db.execute(select(ReleaseDB).where(ReleaseDB.id == release_id))
    release_db = result.scalar_one_or_none()
    
    if not release_db:
        raise HTTPException(status_code=404, detail="Release not found")
    
    return Release(
        id=release_db.id,
        tag_name=release_db.tag_name,
        name=release_db.name,
        version=release_db.version or "",
        release_date=release_db.release_date,
        download_url=release_db.download_url,
        description=release_db.description,
        assets=release_db.assets or [],
    )


@app.post("/api/releases", response_model=Release)
async def create_release(release_data: ReleaseCreate, db: AsyncSession = Depends(get_db)):
    """Create/add a release from GitHub URL"""
    import re
    
    # Extract owner and repo from GitHub URL
    # Example: https://github.com/jameskwon07/3project/releases/
    github_url = release_data.github_url.rstrip('/')
    pattern = r'https://github\.com/([^/]+)/([^/]+)'
    match = re.match(pattern, github_url)
    
    if not match:
        raise HTTPException(status_code=400, detail="Invalid GitHub URL format")
    
    owner, repo = match.groups()
    
    # Use repo name as the unique ID and display name
    release_id = repo
    release_name = repo
    
    # Check if release already exists
    result = await db.execute(select(ReleaseDB).where(ReleaseDB.id == release_id))
    existing_release = result.scalar_one_or_none()
    
    if existing_release:
        raise HTTPException(status_code=400, detail=f"Release for repository '{repo}' already exists")
    
    # TODO: Fetch actual releases from GitHub API using github_token
    # For now, create a placeholder release that will be populated when versions are fetched
    release_db = ReleaseDB(
        id=release_id,
        tag_name=repo,  # Use repo name as tag_name
        name=release_name,
        version="",  # Will be populated when fetching versions
        release_date=datetime.now(),
        description=f"GitHub: {owner}/{repo}",
        download_url=github_url,
        assets=[],  # Will be populated when fetching versions
    )
    
    db.add(release_db)
    await db.commit()
    await db.refresh(release_db)
    
    return Release(
        id=release_db.id,
        tag_name=release_db.tag_name,
        name=release_db.name,
        version=release_db.version or "",
        release_date=release_db.release_date,
        download_url=release_db.download_url,
        description=release_db.description,
        assets=release_db.assets or [],
    )


@app.delete("/api/releases/{release_id}")
async def delete_release(release_id: str, db: AsyncSession = Depends(get_db)):
    """Delete/remove a release"""
    result = await db.execute(select(ReleaseDB).where(ReleaseDB.id == release_id))
    release_db = result.scalar_one_or_none()
    
    if not release_db:
        raise HTTPException(status_code=404, detail="Release not found")
    
    db.delete(release_db)
    await db.commit()
    return {"message": "Release deleted"}


# ==================== Deployment Management ====================

@app.get("/api/deployments", response_model=List[Deployment])
async def get_deployments(db: AsyncSession = Depends(get_db)):
    """List all deployments"""
    result = await db.execute(select(DeploymentDB))
    deployments_db = result.scalars().all()
    
    return [
        Deployment(
            id=deployment.id,
            agent_id=deployment.agent_id,
            agent_name=deployment.agent_name,
            release_ids=deployment.release_ids or [],
            release_tags=deployment.release_tags or [],
            status=DeploymentStatus(deployment.status.value),
            created_at=deployment.created_at,
            started_at=deployment.started_at,
            completed_at=deployment.completed_at,
            error_message=deployment.error_message,
        )
        for deployment in deployments_db
    ]


@app.get("/api/deployments/history", response_model=List[Deployment])
async def get_deployment_history(limit: int = 50, db: AsyncSession = Depends(get_db)):
    """Get deployment history"""
    from sqlalchemy import desc
    
    result = await db.execute(
        select(DeploymentDB)
        .order_by(desc(DeploymentDB.created_at))
        .limit(limit)
    )
    deployments_db = result.scalars().all()
    
    return [
        Deployment(
            id=deployment.id,
            agent_id=deployment.agent_id,
            agent_name=deployment.agent_name,
            release_ids=deployment.release_ids or [],
            release_tags=deployment.release_tags or [],
            status=DeploymentStatus(deployment.status.value),
            created_at=deployment.created_at,
            started_at=deployment.started_at,
            completed_at=deployment.completed_at,
            error_message=deployment.error_message,
        )
        for deployment in deployments_db
    ]


@app.get("/api/deployments/{deployment_id}", response_model=Deployment)
async def get_deployment(deployment_id: str, db: AsyncSession = Depends(get_db)):
    """Get specific deployment"""
    result = await db.execute(select(DeploymentDB).where(DeploymentDB.id == deployment_id))
    deployment_db = result.scalar_one_or_none()
    
    if not deployment_db:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    return Deployment(
        id=deployment_db.id,
        agent_id=deployment_db.agent_id,
        agent_name=deployment_db.agent_name,
        release_ids=deployment_db.release_ids or [],
        release_tags=deployment_db.release_tags or [],
        status=DeploymentStatus(deployment_db.status.value),
        created_at=deployment_db.created_at,
        started_at=deployment_db.started_at,
        completed_at=deployment_db.completed_at,
        error_message=deployment_db.error_message,
    )


@app.post("/api/deployments", response_model=Deployment)
async def create_deployment(deployment_data: DeploymentCreate, db: AsyncSession = Depends(get_db)):
    """Create a deployment (can deploy multiple releases to an agent at once)"""
    # Validate agent exists
    result = await db.execute(select(AgentDB).where(AgentDB.id == deployment_data.agent_id))
    agent_db = result.scalar_one_or_none()
    
    if not agent_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Validate all releases exist
    release_tags = []
    for release_id in deployment_data.release_ids:
        result = await db.execute(select(ReleaseDB).where(ReleaseDB.id == release_id))
        release_db = result.scalar_one_or_none()
        if not release_db:
            raise HTTPException(status_code=404, detail=f"Release {release_id} not found")
        release_tags.append(release_db.tag_name)
    
    # Create deployment
    deployment_id = f"deploy-{agent_db.id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    deployment_db = DeploymentDB(
        id=deployment_id,
        agent_id=deployment_data.agent_id,
        agent_name=agent_db.name,
        release_ids=deployment_data.release_ids,
        release_tags=release_tags,
        status=DeploymentStatusEnum.PENDING,
        created_at=datetime.now()
    )
    
    db.add(deployment_db)
    await db.commit()
    await db.refresh(deployment_db)
    
    # Deployment is created in PENDING state
    # Agent will poll /api/deployments/pending/{agent_id} to retrieve and execute it
    
    return Deployment(
        id=deployment_db.id,
        agent_id=deployment_db.agent_id,
        agent_name=deployment_db.agent_name,
        release_ids=deployment_db.release_ids or [],
        release_tags=deployment_db.release_tags or [],
        status=DeploymentStatus(deployment_db.status.value),
        created_at=deployment_db.created_at,
        started_at=deployment_db.started_at,
        completed_at=deployment_db.completed_at,
        error_message=deployment_db.error_message,
    )


@app.get("/api/deployments/pending/{agent_id}", response_model=Optional[Deployment])
async def get_pending_deployment(agent_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get pending deployment for an agent (Agent polling endpoint)
    Returns the oldest PENDING deployment for the agent, or None if no pending deployment exists
    """
    # Verify agent exists
    result = await db.execute(select(AgentDB).where(AgentDB.id == agent_id))
    agent_db = result.scalar_one_or_none()
    
    if not agent_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Get oldest PENDING deployment for this agent
    from sqlalchemy import asc
    result = await db.execute(
        select(DeploymentDB)
        .where(DeploymentDB.agent_id == agent_id)
        .where(DeploymentDB.status == DeploymentStatusEnum.PENDING)
        .order_by(asc(DeploymentDB.created_at))
        .limit(1)
    )
    deployment_db = result.scalar_one_or_none()
    
    if not deployment_db:
        return None
    
    # Update status to IN_PROGRESS and set started_at
    deployment_db.status = DeploymentStatusEnum.IN_PROGRESS
    deployment_db.started_at = datetime.now()
    await db.commit()
    await db.refresh(deployment_db)
    
    return Deployment(
        id=deployment_db.id,
        agent_id=deployment_db.agent_id,
        agent_name=deployment_db.agent_name,
        release_ids=deployment_db.release_ids or [],
        release_tags=deployment_db.release_tags or [],
        status=DeploymentStatus(deployment_db.status.value),
        created_at=deployment_db.created_at,
        started_at=deployment_db.started_at,
        completed_at=deployment_db.completed_at,
        error_message=deployment_db.error_message,
    )


@app.post("/api/deployments/{deployment_id}/complete")
async def complete_deployment(
    deployment_id: str,
    completion_data: DeploymentComplete,
    db: AsyncSession = Depends(get_db)
):
    """
    Report deployment completion (Agent reports deployment result)
    """
    # Get deployment
    result = await db.execute(select(DeploymentDB).where(DeploymentDB.id == deployment_id))
    deployment_db = result.scalar_one_or_none()
    
    if not deployment_db:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    # Validate status
    if completion_data.status not in [DeploymentStatus.SUCCESS, DeploymentStatus.FAILED]:
        raise HTTPException(
            status_code=400,
            detail="Status must be either 'success' or 'failed'"
        )
    
    # Update deployment status
    deployment_db.status = DeploymentStatusEnum(completion_data.status.value)
    deployment_db.completed_at = datetime.now()
    if completion_data.error_message:
        deployment_db.error_message = completion_data.error_message
    
    await db.commit()
    await db.refresh(deployment_db)
    
    return {
        "message": "Deployment status updated",
        "deployment_id": deployment_id,
        "status": completion_data.status.value
    }


# ==================== User Settings (GitHub Token) ====================

@app.get("/api/settings/github-token")
async def get_github_token(db: AsyncSession = Depends(get_db)):
    """Get GitHub token (returns masked token if exists)"""
    result = await db.execute(select(SettingsDB).where(SettingsDB.key == "github_token"))
    settings_db = result.scalar_one_or_none()
    
    if settings_db and settings_db.value:
        # Return masked token for security (show only last 4 characters)
        token = settings_db.value
        masked_token = "***" + token[-4:] if len(token) > 4 else "***"
        return {"has_token": True, "token_preview": masked_token}
    return {"has_token": False}


@app.post("/api/settings/github-token")
async def set_github_token(token_data: dict, db: AsyncSession = Depends(get_db)):
    """Add or update GitHub token"""
    if "token" not in token_data:
        raise HTTPException(status_code=400, detail="Token is required")
    
    token_value = token_data["token"]
    
    # Check if token exists
    result = await db.execute(select(SettingsDB).where(SettingsDB.key == "github_token"))
    settings_db = result.scalar_one_or_none()
    
    if settings_db:
        # Update existing token
        settings_db.value = token_value
        settings_db.updated_at = datetime.now()
    else:
        # Create new token entry
        settings_db = SettingsDB(key="github_token", value=token_value)
        db.add(settings_db)
    
    await db.commit()
    return {"message": "GitHub token saved successfully"}


@app.delete("/api/settings/github-token")
async def delete_github_token(db: AsyncSession = Depends(get_db)):
    """Remove GitHub token"""
    result = await db.execute(select(SettingsDB).where(SettingsDB.key == "github_token"))
    settings_db = result.scalar_one_or_none()
    
    if settings_db:
        db.delete(settings_db)
        await db.commit()
    
    return {"message": "GitHub token removed successfully"}


# ==================== Health Check ====================

@app.get("/api/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check"""
    from sqlalchemy import func
    
    # Count records from database
    agents_count = await db.scalar(select(func.count(AgentDB.id)))
    releases_count = await db.scalar(select(func.count(ReleaseDB.id)))
    deployments_count = await db.scalar(select(func.count(DeploymentDB.id)))
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents_count": agents_count or 0,
        "releases_count": releases_count or 0,
        "deployments_count": deployments_count or 0
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Development mode
    )
