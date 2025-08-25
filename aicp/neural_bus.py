from typing import Dict, Any, List
from datetime import datetime, timezone

class RoutingEngine:
    """경량 점수화 라우팅"""
    def __init__(self):
        self.weights = {
            "Claude": {"analysis":0.9,"creative":0.4,"technical":0.5,"multimodal":0.3,"base_cost":0.4,"latency":0.5,"load":0.2},
            "GPT-4":  {"analysis":0.7,"creative":0.9,"technical":0.6,"multimodal":0.5,"base_cost":0.5,"latency":0.6,"load":0.3},
            "Gemini": {"analysis":0.6,"creative":0.6,"technical":0.9,"multimodal":0.9,"base_cost":0.6,"latency":0.6,"load":0.3},
        }

    def infer_task(self, text: str, caps: List[str]) -> str:
        s = (text or "").lower()
        if any(k in s for k in ["analyze","research","compare","insight"]): return "analysis"
        if any(k in s for k in ["design","write","story","create"]):       return "creative"
        if any(k in s for k in ["code","debug","implement","optimize"]):   return "technical"
        if any(k in s for k in ["image","video","audio"]):                  return "multimodal"
        return "analysis" if "analysis" in caps else "creative" if "creative" in caps else "technical" if "technical" in caps else "analysis"

    def score(self, agent: str, task: str) -> float:
        w = self.weights.get(agent, {"analysis":0.5,"creative":0.5,"technical":0.5,"multimodal":0.5,"base_cost":0.5,"latency":0.5,"load":0.5})
        return w[task]*0.7 + (1-w["base_cost"])*0.15 + (1-w["latency"])*0.1 + (1-w["load"])*0.05

    def pick(self, text: str, caps: List[str]) -> str:
        task = self.infer_task(text, caps)
        return max(self.weights.keys(), key=lambda a: self.score(a, task))

class NeuralBusMCP:
    """Neural Bus 엔진 (MCP 연동)"""
    def __init__(self, ssot):
        self.ssot = ssot
        self.routing = RoutingEngine()
        self.agent_registry: Dict[str, Dict] = {}
        self.routing_history: List[Dict] = []

    async def route_message(self, message: str, capabilities: List[str], context: Dict, session_id: str) -> Dict[str, Any]:
        agent = self.routing.pick(message, capabilities or [])
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "message": (message or "")[:100],
            "selected_agent": agent,
            "intent": {"primary_task": self.routing.infer_task(message, capabilities or [])}
        }
        self.routing_history.append(record)
        return {
            "status":"routed",
            "agent": agent,
            "intent": record["intent"],
            "suggestion": f"Use {agent} for this request",
            "timestamp": record["timestamp"]
        }

    async def share_context(self, key: str, value_text: str, session_id: str) -> Dict[str, Any]:
        await self.ssot.set(key, value_text)
        return {"status":"shared","key":key}

    async def orchestrate_collaboration(self, task: str, agents: List[str], session_id: str) -> Dict[str, Any]:
        if not agents: agents = ["Claude","GPT-4","Gemini"]
        subtasks = ["1. Understand task","2. Plan approach","3. Execute","4. Review"]
        assignments = {agents[i%len(agents)]: s for i,s in enumerate(subtasks)}
        return {"status":"orchestrated","task":task,"assignments":assignments}

    async def get_shared_state(self) -> Dict[str, Any]:
        return await self.ssot.dump_all()

    async def get_agent_registry(self) -> Dict[str, Any]:
        return self.agent_registry
