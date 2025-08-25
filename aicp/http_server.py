# aicp/http_server.py
from aiohttp import web
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

REQUESTS = Counter("aicp_http_requests_total","HTTP requests",["method","path","status"])
LATENCY  = Histogram("aicp_http_latency_seconds","HTTP latency seconds")
WS_CONNECTIONS = Gauge("aicp_ws_connections","Active WS connections")
ROUTING_SUCCESS = Counter("aicp_routing_success_total","Routing success")
ERRORS = Counter("aicp_errors_total","Errors",["kind"])

class HttpServer:
    def __init__(self, ready_flag):
        self.ready_flag = ready_flag

    async def health(self, request):
        with LATENCY.time():
            REQUESTS.labels(request.method,"/health","200").inc()
            return web.json_response({"status":"ok"})

    async def ready(self, request):
        with LATENCY.time():
            status = "ready" if self.ready_flag() else "starting"
            REQUESTS.labels(request.method,"/ready","200").inc()
            return web.json_response({"status":status})

    async def metrics(self, request):
        data = generate_latest()
        return web.Response(body=data, headers={"Content-Type": CONTENT_TYPE_LATEST})

    def app(self):
        app = web.Application()
        app.add_routes([
            web.get("/health", self.health),
            web.get("/ready", self.ready),
            web.get("/metrics", self.metrics),
        ])
        return app
