# AICP - AI Inter-Communication Protocol

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

> 인터넷이 정보의 벽을 허물었다면, 우리는 지능의 인터넷을 만듭니다.

## 🌐 프로젝트 소개

AICP(AI Inter-Communication Protocol)는 서로 다른 LLM과 사용자가 하나의 네트워크에서 자유롭게 협업할 수 있도록 하는 오픈 프로토콜입니다. MCP(Model Context Protocol) 호환으로 기존 LLM 서비스에서 바로 사용 가능합니다.

### 핵심 특징

- **🔌 MCP 호환**: Claude, ChatGPT 등에서 MCP 연결로 즉시 사용
- **💰 비용 효율적**: API 직접 호출 없이 기존 LLM 구독만으로 이용 가능
- **🔒 보안 강화**: Docker Secrets, Kubernetes Secrets 지원
- **🚀 쉬운 배포**: Docker Compose 한 줄로 실행
- **📊 실시간 모니터링**: Prometheus + Grafana 대시보드 제공

## 🏗️ 아키텍처
┌─────────────────────────────────────────────────┐
│                   사용자 (User)                  │
└─────────────┬───────────────────┬───────────────┘
              │                   │
         MCP Protocol        MCP Protocol
              │                   │
    ┌─────────▼─────────┐ ┌──────▼──────┐
    │   Claude Console  │ │   ChatGPT   │
    │   (MCP Client)    │ │ (MCP Client)│
    └─────────┬─────────┘ └──────┬──────┘
              │                   │
         MCP WebSocket       MCP WebSocket
              │                   │
    ┌─────────▼───────────────────▼──────────────┐
    │         AICP Neural Bus (MCP Server)       │
    │  ┌────────────────────────────────────┐    │
    │  │  • 지능형 라우팅 엔진              │    │
    │  │  • 공유 상태 허브 (SSoT)           │    │
    │  │  • 협업 오케스트레이션             │    │
    │  └────────────────────────────────────┘    │
    └─────────────────────────────────────────────┘
text## 🚀 빠른 시작

### 방법 1: Docker Compose (권장)

```bash
# 1. 저장소 클론
git clone https://github.com/your-username/AICP-Protocol.git
cd AICP-Protocol

# 2. 시크릿 파일 생성
./scripts/setup-secrets.sh

# 3. MCP 서버 실행 (API 키 불필요)
docker-compose -f docker-compose.secure.yml up -d

# 4. 상태 확인
docker-compose ps
방법 2: 로컬 Python 환경
bash# 1. 가상환경 생성
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. MCP 서버 실행
python -m aicp.mcp_server

# 서버가 ws://localhost:8765 에서 실행됨
📖 사용 방법
Claude에서 연결하기

Claude 콘솔에서 MCP 설정 열기
새 MCP 서버 추가:
textURL: ws://your-server:8765/mcp
Name: AICP Neural Bus

연결 후 사용 가능한 도구:

route_to_agent: 최적 AI 에이전트로 라우팅
share_context: 에이전트 간 컨텍스트 공유
orchestrate_collaboration: 다중 에이전트 협업



Python SDK 사용
pythonfrom aicp import MCPClient

# MCP 클라이언트 생성
client = MCPClient("ws://localhost:8765/mcp")

# 도구 호출
result = await client.call_tool(
    "route_to_agent",
    {
        "message": "이 데이터를 분석해주세요",
        "target_capabilities": ["analysis", "reasoning"]
    }
)

# 컨텍스트 공유
await client.call_tool(
    "share_context",
    {
        "context_key": "project_data",
        "context_value": {"status": "진행중", "progress": 0.7}
    }
)
📁 프로젝트 구조
textAICP-Protocol/
├── aicp/                    # 핵심 라이브러리
│   ├── __init__.py
│   ├── mcp_server.py       # MCP 서버 구현
│   ├── neural_bus.py       # Neural Bus 엔진
│   └── shared_state.py     # SSoT 구현
├── docker/                  # Docker 설정
│   ├── Dockerfile.mcp
│   └── docker-compose.secure.yml
├── examples/               # 사용 예제
│   ├── basic_routing.py
│   └── collaboration.py
├── tests/                  # 테스트
│   ├── unit/
│   └── integration/
├── docs/                   # 문서
│   ├── MCP_INTEGRATION.md
│   ├── API_REFERENCE.md
│   └── SECURITY.md
├── scripts/               # 유틸리티 스크립트
│   ├── setup-secrets.sh
│   └── health-check.sh
├── requirements.txt
├── LICENSE               # MIT 라이선스
└── README.md
🔒 보안 고려사항

시크릿 관리: Docker Secrets / Kubernetes Secrets 사용
네트워크 격리: 내부 네트워크만 접근 가능하도록 설정
TLS/SSL: 프로덕션에서 필수 (nginx 리버스 프록시)
인증: JWT 토큰 기반 인증 (옵션)

자세한 내용은 SECURITY.md 참조
🤝 기여하기
AICP는 오픈소스 프로젝트입니다! 기여를 환영합니다.

Fork the Project
Create your Feature Branch (git checkout -b feature/AmazingFeature)
Commit your Changes (git commit -m 'Add some AmazingFeature')
Push to the Branch (git push origin feature/AmazingFeature)
Open a Pull Request

📊 로드맵

 MCP 서버 구현
 Docker 배포 지원
 Kubernetes Helm Chart
 웹 대시보드
 더 많은 LLM 플랫폼 지원
 플러그인 시스템

📄 라이선스
MIT License - 자세한 내용은 LICENSE 파일 참조
🙏 감사의 말

Anthropic의 MCP 프로토콜
오픈소스 커뮤니티

📞 연락처

GitHub Issues: 문제 보고
Discussions: 토론 참여


⭐ 이 프로젝트가 도움이 되었다면 Star를 눌러주세요!


## 선택 기능 (Profiles)

### DB(Postgres)
```bash
docker compose -f docker/docker-compose.secure.yml --profile db up -d
# psql 접속 예: psql -h localhost -U aicp_user -d aicp
모니터링(Prometheus/Grafana)
bash
코드 복사
docker compose -f docker/docker-compose.secure.yml --profile monitoring up -d
# Prometheus: http://localhost:9090
# Grafana:    http://localhost:3001  (admin / admin)
프록시(NGINX)
bash
코드 복사
docker compose -f docker/docker-compose.secure.yml --profile proxy up -d
# WS 경로: ws://localhost/mcp  (백엔드 ws://aicp-mcp-server:8765)