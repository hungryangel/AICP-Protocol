import os, json, asyncio, logging
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

import websockets
from websockets.server import WebSocketServerProtocol

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from aiohttp import web

try:
    from redis.asyncio import Redis
except Exception:
    Redis = None  # type: ignore

# ---- 프로젝트 내부 모듈 ----
from .shared_state import SharedState
from .neural_bus import NeuralBusMCP

# ---- 로깅 ----
logging.basicConfig(level=os.getenv("LOG_LEVEL","INFO"))
logger = logging.getLogger("AICP-MCP")

# ---- 메트릭 ----
HTTP_REQ = Counter("aicp_http_requests_total","HTTP requests",["method","path","status"])
HTTP_LAT = Histogram("aicp_http_latency_seconds","HTTP latency seconds")
WS_CONNS = Gauge("aicp_ws_connections","Active WS connections")
ROUTING_OK = Counter("aicp_routing_success_total","Routing success")
ERRORS = Counter("aicp_errors_total","Errors",["kind"])

# ---- MCP 메시지 ----
@dataclass
class MCPMessage:
    jsonrpc: str = "2.0"
    id: Optional[Union[str,int]] = None
    method: Optional[str] = None
    params: Optional[Dict[str,Any]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str,Any]] = None
    def to_dict(self): return {k:v for k,v in asdict(self).items() if v is not None}

# ---- 세션 & 레이트리밋 ----
class RateLimiter:
    def __init__(self, rate_per_sec: float = 10, burst: int = 20):
        import time
        self.rate = rate_per_sec
        self.capacity = burst
        self.tokens = burst
        self.updated = time.monotonic()
        self.time = time

    async def take(self, n: int = 1):
        now = self.time.monotonic()
        delta = now - self.updated
        self.updated = now
        self.tokens = min(self.capacity, self.tokens + delta * self.rate)
        if self.tokens >= n:
            self.tokens -= n
            return True
        wait = (n - self.tokens) / self.rate
        await asyncio.sleep(max(wait,0))
        self.tokens = 0
        return True

@dataclass
class MCPSession:
    session_id: str
    client_name: str = "unknown"
    client_version: str = "1.0"
    created_at: str = datetime.utcnow().isoformat()
    limiter: RateLimiter = RateLimiter()

# ---- 브리지 ----
class AICPMCPBridge:
    def __init__(self, neural_bus: NeuralBusMCP):
        self.bus = neural_bus

    async def handle(self, msg: Dict[str,Any], session: MCPSession) -> Dict[str,Any]:
        method = msg.get("method"); params = msg.get("params") or {}; msg_id = msg.get("id")
        try:
            if method == "initialize":
                ci = params.get("clientInfo") or {}
                session.client_name = ci.get("name","unknown")
                session.client_version = ci.get("version","1.0")
                return MCPMessage(id=msg_id, result={
                    "protocolVersion":"2025-06-18",
                    "serverInfo":{"name":"AICP-MCP-Server","version":"1.2.0"},
                    "capabilities":{"tools":{},"resources":{},"prompts":{},"logging":{}}
                }).to_dict()

            await session.limiter.take()

            if method == "tools/list":
                tools = [
                    {
                        "name":"route_to_agent",
                        "description":"Route message to optimal AI agent",
                        "inputSchema":{
                            "type":"object",
                            "properties":{
                                "message":{"type":"string"},
                                "target_capabilities":{"type":"array","items":{"type":"string"}},
                                "context":{"type":"object"}
                            },
                            "required":["message"]
                        }
                    },
                    {
                        "name":"share_context",
                        "description":"Share context across agents (SSoT)",
                        "inputSchema":{
                            "type":"object",
                            "properties":{
                                "context_key":{"type":"string"},
                                "context_value":{
                                    "oneOf":[
                                        {"type":"object"},{"type":"string"},
                                        {"type":"number"},{"type":"boolean"},
                                        {"type":"array"},{"type":"null"}
                                    ]
                                }
                            },
                            "required":["context_key","context_value"]
                        }
                    },
                    {
                        "name":"orchestrate_collaboration",
                        "description":"Orchestrate multi-agent collaboration",
                        "inputSchema":{
                            "type":"object",
                            "properties":{
                                "task":{"type":"string"},
                                "agents":{"type":"array","items":{"type":"string"}}
                            },
                            "required":["task"]
                        }
                    }
                ]
                return MCPMessage(id=msg_id, result={"tools":tools}).to_dict()

            if method == "tools/call":
                args = params.get("arguments") or {}
                name = params.get("name")
                if name == "route_to_agent":
                    payload = await self.bus.route_message(args.get("message",""), args.get("target_capabilities",[]), args.get("context",{}), session.session_id)
                    ROUTING_OK.inc()
                    return MCPMessage(id=msg_id, result={"content":[{"type":"text","text":json.dumps(payload,ensure_ascii=False)}]}).to_dict()
                if name == "share_context":
                    payload = await self.bus.share_context(args.get("context_key"), json.dumps(args.get("context_value"),ensure_ascii=False), session.session_id)
                    return MCPMessage(id=msg_id, result={"content":[{"type":"text","text":json.dumps(payload,ensure_ascii=False)}]}).to_dict()
                if name == "orchestrate_collaboration":
                    payload = await self.bus.orchestrate_collaboration(args.get("task",""), args.get("agents",[]), session.session_id)
                    return MCPMessage(id=msg_id, result={"content":[{"type":"text","text":json.dumps(payload,ensure_ascii=False)}]}).to_dict()
                return MCPMessage(id=msg_id, error={"code":-32602,"message":f"Unknown tool {name}"}).to_dict()

            if method == "resources/list":
                return MCPMessage(id=msg_id, result={"resources":[
                    {"uri":"aicp://shared-state","name":"Shared State","description":"SSoT snapshot","mimeType":"application/json"}
                ]}).to_dict()

            if method == "resources/read":
                uri = params.get("uri")
                if uri != "aicp://shared-state":
                    return MCPMessage(id=msg_id, error={"code":-32602,"message":f"Unknown resource {uri}"}).to_dict()
                snapshot = await self.bus.get_shared_state()
                return MCPMessage(id=msg_id, result={"contents":[{"uri":uri,"mimeType":"application/json","text":json.dumps(snapshot,ensure_ascii=False)}]}).to_dict()

            if method == "prompts/list":
                return MCPMessage(id=msg_id, result={"prompts":[
                    {"name":"analyze_task","description":"Analyze a task for optimal routing"},
                    {"name":"collaboration_request","description":"Ask agents to collaborate"}
                ]}).to_dict()

            if method == "prompts/get":
                name = params.get("name")
                if name == "analyze_task":
                    return MCPMessage(id=msg_id, result={
                        "name":"analyze_task",
                        "description":"Analyze a task for optimal agent routing",
                        "arguments":[{"name":"task","description":"The task","required":True}],
                        "messages":[{"role":"user","content":"Analyze this task and determine best agent(s): {{task}}"}]
                    }).to_dict()
                if name == "collaboration_request":
                    return MCPMessage(id=msg_id, result={
                        "name":"collaboration_request",
                        "description":"Orchestrate collaboration",
                        "arguments":[{"name":"task","required":True},{"name":"agents","required":False}],
                        "messages":[{"role":"user","content":"Coordinate {{agents}} to complete: {{task}}"}]
                    }).to_dict()
                return MCPMessage(id=msg_id, error={"code":-32602,"message":f"Unknown prompt {name}"}).to_dict()

            return MCPMessage(id=msg_id, error={"code":-32601,"message":"Method not found"}).to_dict()

        except Exception as e:
            ERRORS.labels("server").inc()
            logger.exception("error handling MCP")
            return MCPMessage(id=msg_id, error={"code":-32603,"message":str(e)}).to_dict()

# ---- HTTP(health/metrics) ----
class HttpApp:
    async def health(self, request):
        with HTTP_LAT.time():
            HTTP_REQ.labels(request.method,"/health","200").inc()
            return web.json_response({"status":"ok"})

    async def ready(self, request):
        with HTTP_LAT.time():
            HTTP_REQ.labels(request.method,"/ready","200").inc()
            return web.json_response({"status":"ready"})

    async def metrics(self, request):
        data = generate_latest()
        return web.Response(body=data, content_type=CONTENT_TYPE_LATEST)

    def make(self):
        app = web.Application()
        app.add_routes([
            web.get("/health", self.health),
            web.get("/ready", self.ready),
            web.get("/metrics", self.metrics),
        ])
        return app

# ---- WS 서버 ----
class MCPWebSocketServer:
    def __init__(self, bridge: AICPMCPBridge, max_msg_size=1<<20):
        self.bridge = bridge
        self.max_msg_size = max_msg_size

    async def handler(self, websocket: WebSocketServerProtocol, path: str):
        session_id = f"sess-{os.urandom(4).hex()}"
        WS_CONNS.inc()
        session = MCPSession(session_id=session_id)
        logger.info(f"ws_open session={session_id} path={path}")
        try:
            async for raw in websocket:
                if len(raw) > self.max_msg_size:
                    await websocket.send(json.dumps(MCPMessage(error={"code":-32000,"message":"message too large"}).to_dict(), ensure_ascii=False))
                    continue
                msg = json.loads(raw)
                resp = await self.bridge.handle(msg, session)
                await websocket.send(json.dumps(resp, ensure_ascii=False))
        except websockets.ConnectionClosed:
            pass
        finally:
            WS_CONNS.dec()
            logger.info(f"ws_close session={session_id}")

# ---- 메인 실행 ----
async def _run_http(port: int):
    app = HttpApp().make()
    runner = web.AppRunner(app); await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port); await site.start()

async def main():
    host = os.getenv("HOST","0.0.0.0")
    ws_port = int(os.getenv("PORT","8765"))
    http_port = int(os.getenv("HTTP_PORT","8080"))
    redis_url = os.getenv("REDIS_URL")  # 없으면 메모리 SSoT 사용

    # Redis 연결 시도
    redis_client = None
    if redis_url and Redis:
        try:
            redis_client = Redis.from_url(redis_url, decode_responses=True)
            await redis_client.ping()
            logger.info(f"Redis connected: {redis_url}")
        except Exception as e:
            logger.warning(f"Redis disabled (connection failed): {e}")
            redis_client = None

    ssot = SharedState(redis=redis_client)
    bus = NeuralBusMCP(ssot)
    bridge = AICPMCPBridge(bus)

    asyncio.create_task(_run_http(http_port))

    logger.info(f"Starting AICP-MCP Server on {host}:{ws_port}")
    logger.info(f"MCP endpoint: ws://{host}:{ws_port}/mcp")  # f-string 고정

    async with websockets.serve(MCPWebSocketServer(bridge).handler, host, ws_port, max_size=1<<20):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
