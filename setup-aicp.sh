#!/bin/bash
setup-aicp.sh
AICP 프로젝트 설치 및 실행 스크립트 (MCP 모드 중심)
set -e
색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'
프로젝트 정보
PROJECT_NAME="AICP-Protocol"
GITHUB_REPO="https://github.com/your-username/AICP-Protocol.git"
VERSION="1.0.0"
로고 출력
print_logo() {
    echo -e "${MAGENTA}"
    cat << "EOF"
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║     ░█████╗░██╗░█████╗░██████╗░                       ║
║     ██╔══██╗██║██╔══██╗██╔══██╗                       ║
║     ███████║██║██║░░╚═╝██████╔╝                       ║
║     ██╔══██║██║██║░░██╗██╔═══╝░                       ║
║     ██║░░██║██║╚█████╔╝██║░░░░░                       ║
║     ╚═╝░░╚═╝╚═╝░╚════╝░╚═╝░░░░░                       ║
║                                                       ║
║     AI Inter-Communication Protocol                   ║
║     지능의 인터넷을 만듭니다                                ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}
진행 상황 출력
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}
log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}
log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}
log_success() {
    echo -e "${CYAN}[✓]${NC} $1"
}
스피너 애니메이션
spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='|/-'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}
시스템 확인
check_system() {
    log_info "시스템 환경 확인 중..."

    # OS 확인
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
    else
        log_error "지원하지 않는 운영체제입니다: $OSTYPE"
        exit 1
    fi fi

    log_success "운영체제: $OS"
}
필수 도구 확인
check_prerequisites() {
    log_info "필수 도구 확인 중..."

    local missing_tools=()

    # Docker 확인
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | sed 's/,$//')
        log_success "Docker: $DOCKER_VERSION"
    else
        missing_tools+=("docker")
    fi

    # Docker Compose 확인
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | sed 's/,$//')
        log_success "Docker Compose: $COMPOSE_VERSION"
    elif docker compose version &> /dev/null 2>&1; then
        COMPOSE_VERSION=$(docker compose version | cut -d' ' -f4)
        log_success "Docker Compose: $COMPOSE_VERSION"
        DOCKER_COMPOSE="docker compose"
    else
        missing_tools+=("docker-compose")
    fi

    # Git 확인
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version | cut -d' ' -f3)
        log_success "Git: $GIT_VERSION"
    else
        missing_tools+=("git")
    fi

    # Python 확인 (옵션)
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_success "Python: $PYTHON_VERSION"
    else
        log_warn "Python이 설치되어 있지 않습니다. (Docker 모드에서는 불필요)"
    fi

    # 누락된 도구가 있으면 설치 안내
    if [ ${#missing_tools[@]} -gt 0 ]; then
        log_error "다음 도구들이 설치되어 있지 않습니다:"
        for tool in "${missing_tools[@]}"; do
            echo "  - $tool"
        done
        echo ""
        echo "설치 방법:"
        echo "  Docker: https://docs.docker.com/get-docker/"
        echo "  Git: https://git-scm.com/downloads"
        exit 1
    fi
}
프로젝트 설정
setup_project() {
    log_info "프로젝트 설정 중..."

    # 디렉토리 생성
    if [ ! -d "$PROJECT_NAME" ]; then
        log_info "프로젝트 디렉토리 생성..."
        mkdir -p $PROJECT_NAME
    fi

    cd $PROJECT_NAME

    # 필수 디렉토리 구조 생성
    mkdir -p {config,secrets,logs,data,static,monitoring}

    log_success "프로젝트 구조 생성 완료"
}
시크릿 파일 생성
setup_secrets() {
    log_info "보안 설정 중..."

    # secrets 디렉토리 권한 설정
    chmod 700 secrets

    # 시크릿 파일 생성 (존재하지 않는 경우만)
    if [ ! -f secrets/postgres_password.txt ]; then
        openssl rand -base64 32 > secrets/postgres_password.txt
        log_success "PostgreSQL 패스워드 생성"
    fi

    if [ ! -f secrets/redis_password.txt ]; then
        openssl rand -base64 32 > secrets/redis_password.txt
        log_success "Redis 패스워드 생성"
    fi

    if [ ! -f secrets/grafana_admin_password.txt ]; then
        echo "admin" > secrets/grafana_admin_password.txt  # 프로덕션에서 변경 필요
        log_warn "Grafana 기본 패스워드 사용 (프로덕션에서 변경 필요)"
    fi

    if [ ! -f secrets/auth_token.txt ]; then
        openssl rand -hex 32 > secrets/auth_token.txt
        log_success "인증 토큰 생성"
    fi

    # 시크릿 파일 권한 설정
    chmod 600 secrets/*.txt

    log_success "보안 설정 완료"
}
설정 파일 생성
create_config_files() {
    log_info "설정 파일 생성 중..."

    # AICP 설정 파일
    cat > config/aicp.yaml << 'EOF'
AICP Configuration
version: "1.0"
server:
  host: "0.0.0.0"
  port: 8765
  ssl: false
mcp:
  enabled: true
  protocol_version: "2025-06-18"

neural_bus:
  max_connections: 1000
  timeout: 30
  buffer_size: 10000
API 모드 (옵션 - 기본값 비활성화)
api_mode:
  enabled: false
  adapters:
    claude:
      enabled: false
      model: "claude-3-opus-20240229"
    gpt:
      enabled: false
      model: "gpt-4-turbo-preview"
    gemini:
      enabled: false
      model: "gemini-pro"
logging:
  level: "info"
  file: "logs/aicp.log"
EOF
    # Docker Compose 파일 생성
    cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  aicp-mcp-server:
    image: aicp/mcp-server:latest
    build:
      context: .
      dockerfile: docker/Dockerfile.mcp
    ports:
      - "8765:8765"
      - "8080:8080"
    environment:
      - USE_API=false
      - MCP_MODE=true
    volumes:
      - ./config:/app/config:ro
      - ./logs:/app/logs
    networks:
      - aicp-network
    restart: unless-stopped
  redis:
    image: redis:7-alpine
    ports:
      - "127.0.0.1:6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - aicp-network
    restart: unless-stopped
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=aicp
      - POSTGRES_USER=aicp_user
      - POSTGRES_PASSWORD=changeme
    ports:
      - "127.0.0.1:5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - aicp-network
    restart: unless-stopped
networks:
  aicp-network:
    driver: bridge
volumes:
  redis-data:
  postgres-data:
EOF
    log_success "설정 파일 생성 완료"
}
Docker 이미지 빌드
build_docker_images() {
    log_info "Docker 이미지 빌드 중..."

    # Dockerfile 생성
    mkdir -p docker
    cat > docker/Dockerfile.mcp << 'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY aicp /app/aicp
COPY config /app/config
EXPOSE 8765 8080
CMD ["python", "-m", "aicp.mcp_server"]
EOF
    # requirements.txt 생성
    cat > requirements.txt << 'EOF'
websockets==11.0.3
aiohttp==3.9.1
pyyaml==6.0.1
prometheus-client==0.19.0
python-dotenv==1.0.0
EOF
    # 이미지 빌드
    docker build -f docker/Dockerfile.mcp -t aicp/mcp-server:latest . &
    build_pid=$!

    echo -n "이미지 빌드 중"
    spinner $build_pid
    echo ""

    log_success "Docker 이미지 빌드 완료"
}
서비스 시작
start_services() {
    log_info "AICP 서비스 시작 중..."

    # Docker Compose 실행
    ${DOCKER_COMPOSE:-docker-compose} up -d

    # 헬스 체크 대기
    log_info "서비스 초기화 대기 중..."
    sleep 5

    # 상태 확인
    ${DOCKER_COMPOSE:-docker-compose} ps

    log_success "모든 서비스가 시작되었습니다"
}
연결 정보 출력
print_connection_info() {
    echo ""
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║           AICP 설치 완료! 🎉                            ║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}MCP 서버 엔드포인트:${NC}"
    echo "  ws://localhost:8765/mcp"
    echo ""
    echo -e "${GREEN}Claude에서 연결하기:${NC}"
    echo "  1. Claude 콘솔에서 MCP 설정 열기"
    echo "  2. 새 MCP 서버 추가:"
    echo "     - URL: ws://localhost:8765/mcp"
    echo "     - Name: AICP Neural Bus"
    echo ""
    echo -e "${GREEN}관리 도구:${NC}"
    echo "  - 헬스 체크: http://localhost:8080/health"
    echo "  - Prometheus: http://localhost:9090"
    echo "  - Grafana: http://localhost:3001 (admin/admin)"
    echo ""
    echo -e "${YELLOW}다음 단계:${NC}"
    echo "  1. Claude/ChatGPT에서 MCP 연결 설정"
    echo "  2. 'route_to_agent' 도구로 메시지 라우팅 테스트"
    echo "  3. 'share_context' 도구로 컨텍스트 공유 테스트"
    echo ""
    echo -e "${BLUE}문서:${NC} https://github.com/your-username/AICP-Protocol"
    echo ""
}
GitHub 초기화
init_github() {
    log_info "GitHub 저장소 초기화 중..."

    if [ ! -d .git ]; then
        git init
        git add .
        git commit -m "Initial commit: AICP v${VERSION}"
        log_success "Git 저장소 초기화 완료"
    fi

    # README 생성
    cat > README.md << 'EOF'
AICP - AI Inter-Communication Protocol
MCP 호환 AI 협업 프로토콜
빠른 시작
bash./setup-aicp.sh