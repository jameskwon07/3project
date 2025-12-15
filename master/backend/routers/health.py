"""
Health Check and Monitoring Routes
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime

from database import get_db, engine, IS_SQLITE
from db_models import AgentDB, ReleaseDB, DeploymentDB
from monitoring import get_metrics_summary, get_pending_deployment_metrics

router = APIRouter(tags=["health"])


@router.get("/api/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check"""
    # Count records from database
    agents_count = await db.scalar(select(func.count(AgentDB.id)))
    releases_count = await db.scalar(select(func.count(ReleaseDB.id)))
    deployments_count = await db.scalar(select(func.count(DeploymentDB.id)))
    
    # Get database connection pool stats (only for PostgreSQL, SQLite doesn't use pooling)
    if IS_SQLITE:
        pool_stats = {
            "note": "SQLite does not use connection pooling",
            "size": None,
            "checked_in": None,
            "checked_out": None,
            "overflow": None,
        }
    else:
        pool = engine.pool
        pool_stats = {
            "size": pool.size() if hasattr(pool, 'size') else None,
            "checked_in": pool.checkedin() if hasattr(pool, 'checkedin') else None,
            "checked_out": pool.checkedout() if hasattr(pool, 'checkedout') else None,
            "overflow": pool.overflow() if hasattr(pool, 'overflow') else None,
        }
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents_count": agents_count or 0,
        "releases_count": releases_count or 0,
        "deployments_count": deployments_count or 0,
        "database_pool": pool_stats
    }


@router.get("/api/metrics")
async def get_metrics():
    """Get API metrics summary"""
    return get_metrics_summary()


@router.get("/api/metrics/pending-deployments")
async def get_pending_deployment_metrics_endpoint():
    """Get specific metrics for pending deployment endpoint"""
    return get_pending_deployment_metrics()

