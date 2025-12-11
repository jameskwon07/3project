# Master-Agent 배포 자동화 시스템

개발자를 위한 Master-Agent 아키텍처 기반 배포 및 버전 관리 시스템입니다.

## 아키텍처

- **Master**: Python 기반 웹 서버 + 웹 프론트엔드 (Agent 관리 및 모니터링)
- **Agent**: C# 기반 클라이언트 (Windows/macOS 실행 파일)

## 주요 기능

- **Master 서버**: FastAPI 기반 RESTful API + React 기반 웹 인터페이스
- **Agent 클라이언트**: Master에 자동 등록 및 하트비트 전송
- **자동 배포**: 원클릭 배포 프로세스
- **버전 관리**: 자동 버전 태깅 및 관리
- **크로스 플랫폼**: Windows, macOS (Intel/Apple Silicon) 지원

## 프로젝트 구조

```
3project/
├── master/                 # Master 서버 및 프론트엔드
│   ├── backend/            # Python FastAPI 서버
│   │   ├── main.py
│   │   └── requirements.txt
│   └── frontend/           # 웹 프론트엔드 (Vite)
│       ├── src/
│       ├── index.html
│       └── package.json
├── agent/                  # C# Agent 클라이언트
│   ├── Program.cs
│   ├── Agent.csproj
│   └── appsettings.json
├── scripts/                # 빌드 스크립트
│   ├── build-agent.sh      # Mac/Linux용 Agent 빌드
│   ├── build-agent.bat     # Windows용 Agent 빌드
│   └── init.ps1
├── config/                 # 설정 파일
├── dist/                   # 빌드 출력 (gitignore)
├── deploy.py              # 통합 배포 스크립트
├── deploy-master.py       # Master 전용 배포
├── deploy-agent.py        # Agent 전용 배포
├── version.py             # 버전 관리 유틸리티
└── requirements.txt       # Python 의존성
```

## 빠른 시작

### Master 서버 실행

```bash
# Master 배포
python deploy-master.py --version 1.0.0

# Master 서버 실행
cd master/backend
python main.py

# 프론트엔드 개발 모드 (별도 터미널)
cd master/frontend
npm run dev
```

Master는 `http://localhost:8000`에서 실행됩니다.

### Agent 빌드 및 실행

```bash
# 모든 플랫폼용 Agent 빌드
python deploy-agent.py --version 1.0.0

# 또는 특정 플랫폼만
python deploy-agent.py --version 1.0.0 --platform windows

# Agent 실행
# Windows:
dist/agent-windows/Agent.exe

# macOS:
dist/agent-macos-x64/Agent        # Intel Mac
dist/agent-macos-arm64/Agent      # Apple Silicon
```

## 요구사항

### Master
- Python 3.8+
- Node.js 18+ 및 npm
- Git (버전 관리용)

### Agent
- .NET 8.0 SDK
- Windows 또는 macOS (빌드 환경)

## 개발 가이드

### Master API 엔드포인트

- `GET /api/agents` - 모든 Agent 목록 조회
- `GET /api/agents/{id}` - 특정 Agent 조회
- `POST /api/agents/register` - Agent 등록/하트비트
- `DELETE /api/agents/{id}` - Agent 등록 해제
- `GET /api/health` - 헬스 체크

### Agent 설정

`agent/appsettings.json`에서 Master URL 등을 설정할 수 있습니다.

```json
{
  "MasterUrl": "http://localhost:8000",
  "AgentName": "",
  "HeartbeatInterval": 10000
}
```

## 배포 워크플로우

1. **버전 업데이트**: `version.py`로 버전 관리
2. **Master 배포**: `deploy-master.py`로 웹 서버 및 프론트엔드 배포
3. **Agent 빌드**: `deploy-agent.py`로 실행 파일 생성
4. **Git 태그**: 자동으로 버전 태그 생성

