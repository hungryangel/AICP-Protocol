# AICP - AI Inter-Communication Protocol

[English](README.md) | [한국어](README.ko.md) | [中文](README.zh.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

> If the internet broke down the walls of information, we're building the internet of intelligence.

[English](#english) | [한국어](#korean)

## 🌐 Introduction

AICP (AI Inter-Communication Protocol) is an open protocol that enables different LLMs and users to collaborate freely within a unified network. With MCP (Model Context Protocol) compatibility, it can be used immediately with existing LLM services.

### 🎯 Key Differentiators

- **MCP (Model Context Protocol)**: LLM ↔ Tools/Data connection
- **ACP (Agent Communication Protocol)**: AI ↔ AI direct communication
- **AICP (Our Innovation)**: [User+LLM] ↔ [User+LLM] network

AICP creates an "Intelligence Network" where users bring their own AI agents (Claude, GPT, Gemini, etc.) and collaborate in real-time, sharing context and distributing tasks intelligently.

## ✨ Key Features

- 🔌 **MCP Compatible**: Works instantly with Claude, ChatGPT, and other MCP-enabled clients
- 💰 **Cost Effective**: No API keys required - use your existing LLM subscriptions
- 🚀 **Easy Deployment**: One-line Docker Compose setup
- 🔒 **Security**: JWT authentication, TLS/SSL support
- 📊 **Real-time Monitoring**: Prometheus + Grafana dashboards
- 🤖 **Intelligent Routing**: Automatic selection of optimal AI for each task
- 🌍 **Multi-User Network**: Connect multiple users through their LLMs

## 🏗️ Architecture

### Core Concept: Intelligence Network

AICP implements a true **intelligence network where users connect through their own LLMs**, not just simple AI tool connections.

```
        [User A + Claude]              [User B + GPT-4]
                │                            │
                └──────────┬─────────────────┘
                           │
                    ┌──────▼──────┐
                    │  AICP Hub   │
                    │ (Neural Bus)│
                    └──────┬──────┘
                           │
                ┌──────────┴─────────────────┐
                │                            │
        [User C + Gemini]              [User D + Claude]
```

### Detailed Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    User Network Layer                     │
├──────────────────────────────────────────────────────────┤
│   User A                 User B                User C     │
│     ↓                      ↓                     ↓        │
│   Claude                ChatGPT              Gemini       │
└─────┬──────────────────────┬────────────────────┬────────┘
      │                      │                    │
      └──────────────────────┼────────────────────┘
                             │
                    MCP WebSocket Protocol
                             │
┌─────────────────────────────▼────────────────────────────┐
│                    AICP Neural Bus                       │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │           🧠 Intelligent Routing Engine          │   │
│  │                                                  │   │
│  │  • User intent analysis                         │   │
│  │  • Optimal AI agent matching                    │   │
│  │  • Load balancing & QoS management              │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │           🔄 Collaboration Orchestration         │   │
│  │                                                  │   │
│  │  • Multi-user session management                │   │
│  │  • Real-time message broadcasting               │   │
│  │  • Task distribution & synchronization          │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │           💾 Shared State Hub (SSoT)            │   │
│  │                                                  │   │
│  │  • Global context repository                    │   │
│  │  • Inter-user data sharing                      │   │
│  │  • Real-time state synchronization              │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────┬───────────────────────────────────┘
                       │
         ┌─────────────┴─────────────┐
         │                           │
    ┌────▼────┐              ┌──────▼──────┐
    │  Redis  │              │  PostgreSQL │
    │ (Cache) │              │  (Persist)  │
    └─────────┘              └─────────────┘
```

### Communication Flow

```
User1+Claude ─────► AICP Hub ─────► User2+GPT
     ▲                 │                 │
     │                 ▼                 ▼
     └──── Shared Context (SSoT) ◄──────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (optional)
- Git

### Installation

```bash
# 1. Clone repository
git clone https://github.com/your-username/AICP-Protocol.git
cd AICP-Protocol

# 2. Run setup script
chmod +x setup-aicp.sh
./setup-aicp.sh

# 3. Verify services
docker ps
curl http://localhost:8080/health
```

### Manual Setup (Docker Compose)

```bash
# Basic setup
docker-compose up -d

# Full stack with monitoring
docker-compose -f docker/docker-compose.secure.yml --profile monitoring up -d
```

## 📖 Usage

### 1. WebSocket Connection Test

```python
import asyncio
import websockets
import json

async def test_connection():
    uri = "ws://localhost:8765/mcp"
    async with websockets.connect(uri) as ws:
        # Initialize
        await ws.send(json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"clientInfo": {"name": "test", "version": "1.0"}}
        }))
        response = await ws.recv()
        print("Connected:", response)

asyncio.run(test_connection())
```

### 2. AI Routing

```python
# Route to optimal AI agent
await ws.send(json.dumps({
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "route_to_agent",
        "arguments": {
            "message": "Analyze this complex dataset",
            "target_capabilities": ["analysis", "reasoning"]
        }
    }
}))
```

### 3. Context Sharing

```python
# Share context between AI agents
await ws.send(json.dumps({
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
        "name": "share_context",
        "arguments": {
            "context_key": "project_status",
            "context_value": {"phase": "development", "progress": 75}
        }
    }
}))
```

## 🛠️ MCP Tools

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `route_to_agent` | Route message to optimal AI agent | `message`, `target_capabilities`, `context` |
| `share_context` | Share context between agents | `context_key`, `context_value` |
| `orchestrate_collaboration` | Orchestrate multi-agent collaboration | `task`, `agents` |

## 🎬 Use Cases

### Multi-AI Collaborative Project
```
Team Member A (Claude) → "Start project proposal"
         ↓
    AICP Hub → Distributes tasks
         ↓
Team Member B (GPT-4) → "Market research"
Team Member C (Gemini) → "Technical specifications"
         ↓
    AICP Hub → Integrates results
         ↓
    Shared document for all team members
```

### Real-time Translation Meeting
- Korean User (Claude) ↔ AICP ↔ US User (GPT-4)
- Real-time translation with cultural context
- Automatic meeting minutes generation

## 📊 Monitoring

- **Health Check**: `http://localhost:8080/health`
- **Metrics**: `http://localhost:8080/metrics`
- **Prometheus**: `http://localhost:9090` (optional)
- **Grafana**: `http://localhost:3001` (optional)

## 🔧 Configuration

### Environment Variables

```bash
# MCP Server Configuration
HOST=0.0.0.0
PORT=8765
HTTP_PORT=8080

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Logging
LOG_LEVEL=INFO

# Security (Production)
JWT_REQUIRED=true
JWT_SECRET=your-secret-key
```

### Docker Compose Profiles

```bash
# With database
docker-compose --profile db up -d

# With monitoring
docker-compose --profile monitoring up -d

# With proxy
docker-compose --profile proxy up -d
```

## 📁 Project Structure

```
AICP-Protocol/
├── aicp/                    # Core library
│   ├── __init__.py
│   ├── mcp_server.py       # MCP server implementation
│   ├── neural_bus.py       # Routing engine
│   ├── shared_state.py     # SSoT implementation
│   └── security.py         # Security module
├── docker/                  # Docker configuration
│   ├── Dockerfile.mcp
│   ├── docker-compose.secure.yml
│   └── nginx/              # Proxy configuration
├── examples/               # Usage examples
│   ├── basic_routing.py
│   └── collaboration.py
├── tests/                  # Tests
├── docs/                   # Documentation
├── scripts/                # Utilities
├── setup-aicp.sh          # Setup script
├── requirements.txt        # Python dependencies
└── README.md              # This document
```

## 🧪 Testing

```bash
# Unit tests
python -m pytest tests/

# Integration tests
python examples/basic_routing.py
python examples/collaboration.py

# Load testing
python tests/load_test.py
```

## 🔒 Security

- **JWT Authentication**: Required for production
- **TLS/SSL**: Encryption via NGINX proxy
- **Rate Limiting**: Per-session request limits
- **Docker Secrets**: Sensitive information management

See [SECURITY.md](docs/SECURITY.md) for details

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📈 Roadmap

- [x] MCP server implementation
- [x] Docker deployment support
- [x] Redis-based SSoT
- [x] Intelligent routing
- [ ] Kubernetes Helm Chart
- [ ] Web dashboard
- [ ] Official Claude Desktop support
- [ ] Plugin system
- [ ] Distributed architecture
- [ ] Multi-language support

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- [Anthropic](https://anthropic.com) for the MCP protocol
- Open source community
- All contributors

## 📞 Contact

- **GitHub Issues**: [Report bugs](https://github.com/hungryangel/AICP-Protocol/issues)
- **Discussions**: [Join discussions](https://github.com/hungryangel/AICP-Protocol/discussions)
- **Email**: sulpterazz1@gmail.com

## 📚 How to Cite AICP

If you use AICP in your research or project, please cite:

**BibTeX:**
```bibtex
@software{aicp2025protocol,
  title = {AICP: AI Inter-Communication Protocol - Building the Intelligence Internet},
  author = {AHN SANGHYO},
  year = {2025},
  url = {https://github.com/hungryangel/AICP-Protocol},
  note = {An open protocol for multi-user LLM collaboration networks}
}
```

**APA Style:**
hungryangel. (2025). *AICP: AI Inter-Communication Protocol* [Computer software]. 
GitHub. https://github.com/hungryangel/AICP-Protocol

---

<p align="center">
  ⭐ If this project helps you, please give it a star!
</p>

<p align="center">
  Made with ❤️ by the AICP Team
</p>

---

## Korean

<details>
<summary>한국어 문서 (클릭하여 펼치기)</summary>

## 🌐 소개

AICP(AI Inter-Communication Protocol)는 서로 다른 LLM과 사용자가 하나의 네트워크에서 자유롭게 협업할 수 있도록 하는 오픈 프로토콜입니다. MCP(Model Context Protocol) 호환으로 기존 LLM 서비스에서 바로 사용 가능합니다.

### 빠른 시작

```bash
# 저장소 클론
git clone https://github.com/your-username/AICP-Protocol.git
cd AICP-Protocol

# 설치 스크립트 실행
chmod +x setup-aicp.sh
./setup-aicp.sh
```

자세한 한국어 문서는 [README.ko.md]를 참조하세요.

</details>