#!/bin/bash
# setup-aicp.sh
# AICP 프로젝트 설치 및 실행 스크립트 (MCP 모드 중심)
set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# 프로젝트 정보
PROJECT_NAME="AICP-Protocol"
GITHUB_REPO="https://github.com/your-username/AICP-Protocol.git"
VERSION="1.0.0"

# 로고 출력
print_logo() {
    echo -e "${MAGENTA}"
    cat << "EOF"
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║     ░█████╗░██╗░█████╗░██████╗░                      ║
║     ██╔══██╗██║██╔══██╗██╔══██╗                      ║
║     ███████║██║██║░░╚═╝██████╔╝                      ║
║     ██╔══██║██║██║░░██╗██╔═══╝░                      ║
║     ██║░░██║██║╚█████╔╝██║░░░░░                      ║
║     ╚═╝░░╚═╝╚═╝░╚════╝░╚═╝░░░░░                      ║
║                                                       ║
║     AI Inter-Communication Protocol                  ║
║     지능의 인터넷을 만듭니다                         ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# 진행 상황 출력
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

# 스피너 애니메이션
spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='|/-\'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

# 시스템 확인
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
    fi  # ← fi 하나만!

    log_success "운영체제: $OS"
}

# 필수 도구 확인
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
        DOCKER_COMPOSE="docker-compose"
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

# 서비스 시작 (간단 버전)
start_services() {
    log_info "AICP 서비스 시작 중..."

    # Docker Compose 파일 찾기
    if [ -f "docker-compose.yml" ]; then
        ${DOCKER_COMPOSE:-docker-compose} up -d
    elif [ -f "docker/docker-compose.secure.yml" ]; then
        ${DOCKER_COMPOSE:-docker-compose} -f docker/docker-compose.secure.yml up -d
    else
        log_error "Docker Compose 파일을 찾을 수 없습니다"
        log_info "Python으로 직접 실행을 시도합니다..."

        # Python 직접 실행 시도
        if [ -f "aicp/mcp_server.py" ]; then
            python3 -m aicp.mcp_server &
            log_success "Python으로 MCP 서버 시작"
        else
            log_error "실행할 수 있는 파일이 없습니다"
            exit 1
        fi
    fi

    # 잠시 대기
    sleep 3

    log_success "서비스 시작 완료"
}

# 연결 정보 출력
print_connection_info() {
    echo ""
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║           AICP 설치 완료! 🎉                         ║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}MCP 서버 엔드포인트:${NC}"
    echo "  ws://localhost:8765/mcp"
    echo ""
    echo -e "${GREEN}테스트:${NC}"
    echo "  curl http://localhost:8080/health"
    echo ""
}

# ========== 메인 실행 부분 ==========
main() {
    print_logo
    check_system
    check_prerequisites
    start_services
    print_connection_info
}

# 스크립트 실행
main "$@"