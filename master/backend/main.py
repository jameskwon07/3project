"""
Master Backend - Agent 관리 웹 서버
FastAPI 기반 RESTful API 서버
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uvicorn

app = FastAPI(title="Master Agent Manager", version="1.0.0")

# CORS 설정 (프론트엔드 연결용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙 (프론트엔드)
app.mount("/static", StaticFiles(directory="../frontend/dist"), name="static")


# 데이터 모델
class Agent(BaseModel):
    id: str
    name: str
    platform: str  # "windows" or "macos"
    version: str
    status: str  # "online", "offline", "error"
    last_seen: datetime
    ip_address: Optional[str] = None


class AgentRegister(BaseModel):
    name: str
    platform: str
    version: str
    ip_address: Optional[str] = None


# 임시 저장소 (실제로는 DB 사용)
agents_db: dict[str, Agent] = {}


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "Master Agent Manager API", "version": "1.0.0"}


@app.get("/api/agents", response_model=List[Agent])
async def get_agents():
    """모든 Agent 목록 조회"""
    return list(agents_db.values())


@app.get("/api/agents/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str):
    """특정 Agent 조회"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agents_db[agent_id]


@app.post("/api/agents/register", response_model=Agent)
async def register_agent(agent_data: AgentRegister):
    """Agent 등록/하트비트"""
    agent_id = f"{agent_data.platform}-{agent_data.name}"
    
    agent = Agent(
        id=agent_id,
        name=agent_data.name,
        platform=agent_data.platform,
        version=agent_data.version,
        status="online",
        last_seen=datetime.now(),
        ip_address=agent_data.ip_address
    )
    
    agents_db[agent_id] = agent
    return agent


@app.delete("/api/agents/{agent_id}")
async def unregister_agent(agent_id: str):
    """Agent 등록 해제"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    del agents_db[agent_id]
    return {"message": "Agent unregistered"}


@app.get("/api/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents_count": len(agents_db)
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # 개발 모드
    )

