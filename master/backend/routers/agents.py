"""
Agent Management Routes
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime
import uuid

from database import get_db
from db_models import AgentDB, AgentStatusEnum
from models import Agent, AgentRegister, AgentStatus

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("", response_model=List[Agent])
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


@router.get("/{agent_id}", response_model=Agent)
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


@router.post("/register", response_model=Agent)
async def register_agent(agent_data: AgentRegister, db: AsyncSession = Depends(get_db)):
    """Register agent / heartbeat"""
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


@router.delete("/{agent_id}")
async def delete_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Unregister agent"""
    result = await db.execute(select(AgentDB).where(AgentDB.id == agent_id))
    agent_db = result.scalar_one_or_none()
    
    if not agent_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    db.delete(agent_db)
    await db.commit()
    return {"message": "Agent deleted"}

